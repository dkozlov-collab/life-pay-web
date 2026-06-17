from __future__ import annotations

import io
import re
import time
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

APP_NAME = "LIFE PAY ERP API"

# Exact PIN login from the Streamlit app.
USERS: Dict[str, tuple[str, str]] = {
    "1121018100": ("АТМ АЛЬЯНС", "АТМ"),
    "7734595315": ("Коритек", "АРЕС-КОМПАНИ-М"),
    "5321203280": ("ООО БР", "БР"),
    "9718146933": ("АБ", "Автоматизация Бизнеса"),
    "061219966": ("АДМИНИСТРАТОР", "all"),
    "999999": ("SUPER ADMIN", "all"),
}

URL_REESTR = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"
URL_STOCK = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_RETURN = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv&gid=226066513"
URL_DEBTS = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv&gid=1820118704"

ORG_MAPPING = {
    "АБ": "Автоматизация Бизнеса",
    "АТМ": "ООО АТМ АЛЬЯНС СОЛЮШИНС",
    "БР": "ООО БР",
    "ЛП": "LIFE PAY",
    "Коритек": "ООО АРЕС-КОМПАНИ-М",
}
ORG_MAP_RETURN = {
    "life pay": "LIFE PAY", "лп": "LIFE PAY",
    "автоматизация бизнеса": "Автоматизация Бизнеса", "аб": "Автоматизация Бизнеса",
    "ооо бр": "ООО БР", "бр": "ООО БР", 'ооо "бр"': "ООО БР",
    "ооо атм альянс солюшинс": "ООО АТМ АЛЬЯНС СОЛЮШИНС",
    'ооо "атм альянс солюшинс"': "ООО АТМ АЛЬЯНС СОЛЮШИНС",
    "атм": "ООО АТМ АЛЬЯНС СОЛЮШИНС", "атм альянс": "ООО АТМ АЛЬЯНС СОЛЮШИНС",
}
PARTNER_MAP = {
    "АТМ": ["ООО АТМ", "АТМ АЛЬЯНС"],
    "АРЕС-КОМПАНИ-М": ["АРЕС", "КОРИТЕК", "ООО АРЕС"],
    "БР": ["ООО БР", "БР"],
    "Автоматизация Бизнеса": ["АВТОМАТИЗАЦИЯ", "АБ", "Автоматизация Бизнеса"],
}

TOKENS: Dict[str, Dict[str, Any]] = {}
LOGIN_EVENTS: List[Dict[str, Any]] = []
PAGE_EVENTS: List[Dict[str, Any]] = []
CACHE: Dict[str, tuple[float, Any]] = {}
CACHE_TTL = 60

app = FastAPI(title=APP_NAME, version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    pin: str

class TrackRequest(BaseModel):
    page: str


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def cache_get(key: str):
    item = CACHE.get(key)
    if not item:
        return None
    ts, value = item
    if time.time() - ts > CACHE_TTL:
        CACHE.pop(key, None)
        return None
    return value


def cache_set(key: str, value: Any):
    CACHE[key] = (time.time(), value)
    return value


def safe_iloc(row: pd.Series, idx: int, default: Any = "") -> Any:
    try:
        val = row.iloc[idx]
        return default if pd.isna(val) else val
    except Exception:
        return default


def safe_str(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and pd.isna(v):
        return ""
    if pd.isna(v) if not isinstance(v, (list, dict, tuple)) else False:
        return ""
    return str(v).strip()


def fmt_date_ru(v: Any) -> str:
    if v is None or safe_str(v) == "":
        return "—"
    if isinstance(v, str):
        dt = pd.to_datetime(v, dayfirst=True, errors="coerce")
    else:
        dt = pd.to_datetime(v, errors="coerce")
    if pd.isna(dt):
        return safe_str(v) or "—"
    months = ["", "января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    return f"{dt.day} {months[dt.month]} {dt.year}"


def fmt_iso_date(v: Any) -> str:
    dt = pd.to_datetime(v, dayfirst=True, errors="coerce")
    return "" if pd.isna(dt) else dt.date().isoformat()


def clean_num(v: Any) -> str:
    s = safe_str(v)
    if s.endswith(".0"):
        s = s[:-2]
    if s.lower() in ("", "nan", "none", "0.0"):
        return "" if s != "0.0" else "0"
    try:
        f = float(s.replace(",", "."))
        return str(int(f)) if f == int(f) else s
    except Exception:
        return s


def clean_phone(v: Any) -> str:
    s = safe_str(v)
    if s.endswith(".0"):
        s = s[:-2]
    return "" if s.lower() in ("", "nan", "none") else s


def safe_int(v: Any) -> int:
    try:
        n = pd.to_numeric(v, errors="coerce")
        return 0 if pd.isna(n) else int(n)
    except Exception:
        return 0


def contains_any(row: pd.Series, needle: str) -> bool:
    if not needle or needle == "Все":
        return True
    return row.astype(str).str.contains(needle, case=False, na=False).any()


def df_records(df: pd.DataFrame, limit: int = 500) -> List[Dict[str, Any]]:
    if df is None or df.empty:
        return []
    out = df.head(limit).copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].apply(fmt_date_ru)
    out = out.where(pd.notna(out), "")
    out.columns = [str(c) for c in out.columns]
    return out.to_dict(orient="records")


def require_user(authorization: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
    raw_token = token
    if not raw_token and authorization and authorization.startswith("Bearer "):
        raw_token = authorization.replace("Bearer ", "", 1).strip()
    if not raw_token or raw_token not in TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = TOKENS[raw_token]
    user["last_activity"] = now_iso()
    return user


def read_csv(url: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(url, **kwargs)


def get_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    cached = cache_get("data")
    if cached is not None:
        return cached
    try:
        s_df = read_csv(URL_STOCK, nrows=500).fillna(0)
    except Exception:
        s_df = pd.DataFrame()
    try:
        r_df = read_csv(URL_REESTR).fillna("")
    except Exception:
        r_df = pd.DataFrame()
    if not s_df.empty and s_df.shape[1] > 1:
        s_df.iloc[:, 1] = s_df.iloc[:, 1].astype(str).replace(ORG_MAPPING)
    if not r_df.empty and r_df.shape[1] > 12:
        r_df.iloc[:, 2] = r_df.iloc[:, 2].astype(str).replace(ORG_MAPPING)
        r_df[r_df.columns[12]] = pd.to_datetime(r_df[r_df.columns[12]], dayfirst=True, errors="coerce")
        r_df = r_df.sort_values(by=r_df.columns[12], ascending=False)
    return cache_set("data", (s_df, r_df))


def get_return_data() -> pd.DataFrame:
    cached = cache_get("return")
    if cached is not None:
        return cached
    try:
        raw = read_csv(URL_RETURN, header=0)
    except Exception:
        return pd.DataFrame()
    if raw.empty:
        return pd.DataFrame()
    start_col = 2 if raw.shape[1] >= 5 else 0
    end_col = min(start_col + 19, raw.shape[1])
    raw = raw.iloc[:, start_col:end_col].copy().fillna("")
    names = [
        "city_from", "org_from", "addr_from", "person_from",
        "city_to", "org_to", "addr_to", "person_to",
        "phone_to", "info_to", "comment",
        "kkt", "fn15", "fn36", "serials", "col_r", "col_s", "date", "track",
    ]
    raw.columns = names[: raw.shape[1]]
    raw["date"] = pd.to_datetime(raw["date"], dayfirst=True, errors="coerce") if "date" in raw.columns else pd.NaT

    def has_data(r: pd.Series) -> bool:
        for f in ["org_from", "city_from", "org_to", "city_to"]:
            if f in r.index:
                v = safe_str(r[f]).lower()
                if v and v not in ("nan", "none", "0"):
                    return True
        return False

    filtered = raw[raw.apply(has_data, axis=1)].copy()
    if filtered.empty:
        mask = raw.apply(lambda r: any(safe_str(v).lower() not in ("", "nan", "none", "0") for v in r.values), axis=1)
        filtered = raw[mask].copy()
    for col in ["org_from", "org_to"]:
        if col in filtered.columns:
            filtered[col] = filtered[col].apply(lambda x: ORG_MAP_RETURN.get(safe_str(x).lower(), safe_str(x)))
    if "date" in filtered.columns:
        filtered = filtered.sort_values("date", ascending=False, na_position="last")
    return cache_set("return", filtered.reset_index(drop=True))


def get_debts_data() -> pd.DataFrame:
    cached = cache_get("debts")
    if cached is not None:
        return cached
    try:
        df = read_csv(URL_DEBTS, header=0).fillna("")
    except Exception:
        df = pd.DataFrame()
    return cache_set("debts", df)


def is_junk_value(v: Any) -> bool:
    s = safe_str(v)
    if not s or s.lower() in ("", "nan", "none"):
        return True
    if re.match(r"^[█░▓▒\s]+$", s):
        return True
    if re.match(r"^\[.*\]$", s):
        return True
    if re.match(r"^[\s\-_=+|/\\.,;:!?#*&^%$@~`]+$", s):
        return True
    return False


def is_real_number(v: Any) -> tuple[bool, float]:
    s = safe_str(v).replace(",", ".").replace(" ", "")
    if not s or s.lower() in ("", "nan", "none"):
        return False, 0
    try:
        num = float(s)
        digits = s.replace(".", "").replace("-", "").replace("+", "")
        if len(digits) > 10:
            return False, 0
        return True, num
    except Exception:
        return False, 0


def clean_debts_dataframe(df_raw: pd.DataFrame) -> pd.DataFrame:
    if df_raw is None or df_raw.empty:
        return pd.DataFrame()
    clean_cols = [c for c in df_raw.columns if not str(c).startswith("Unnamed")]
    df = df_raw[clean_cols].copy()
    keep: List[Any] = []
    for c in df.columns:
        vals = df[c].astype(str).str.strip()
        non_empty = vals[vals.apply(lambda v: v.lower() not in ("", "nan", "none"))]
        if len(non_empty) == 0:
            continue
        if non_empty.apply(is_junk_value).sum() / max(len(non_empty), 1) > 0.5:
            continue
        keep.append(c)
    df = df[keep].copy()
    for c in df.columns:
        df[c] = df[c].apply(lambda v: "" if is_junk_value(v) else safe_str(v))
    df = df[df.apply(lambda r: any(safe_str(v).lower() not in ("", "nan", "none", "0", "0.0") for v in r.values), axis=1)]
    return df.reset_index(drop=True)


def row_matches_partner(row: pd.Series, filter_val: str) -> bool:
    if not filter_val or filter_val == "Все" or filter_val == "all":
        return True
    aliases = PARTNER_MAP.get(filter_val, [filter_val])
    row_str = " ".join(safe_str(v) for v in row.values).upper()
    return any(alias.upper() in row_str for alias in aliases) or filter_val.upper() in row_str


def apply_common_filters(
    df: pd.DataFrame,
    user: Dict[str, Any],
    org: Optional[str] = None,
    city: Optional[str] = None,
    search: Optional[str] = None,
    date_mode: str = "Весь период",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    kind: str = "shipments",
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    org_val = user.get("filter", "all") if user.get("filter") != "all" else (org or "Все")
    if kind == "stock":
        if org_val not in ("all", "Все", None) and out.shape[1] > 1:
            out = out[out.iloc[:, 1].astype(str).str.contains(str(org_val), case=False, na=False)]
        if city and city != "Все" and out.shape[1] > 2:
            out = out[out.iloc[:, 2].astype(str).str.contains(city, case=False, na=False)]
    elif kind == "movements":
        if org_val not in ("all", "Все", None):
            mask = out.get("org_from", pd.Series(dtype=str)).astype(str).str.contains(str(org_val), case=False, na=False) | out.get("org_to", pd.Series(dtype=str)).astype(str).str.contains(str(org_val), case=False, na=False)
            out = out[mask]
        if city and city != "Все":
            mask = out.get("city_from", pd.Series(dtype=str)).astype(str).str.contains(city, case=False, na=False) | out.get("city_to", pd.Series(dtype=str)).astype(str).str.contains(city, case=False, na=False)
            out = out[mask]
        if date_mode != "Весь период" and "date" in out.columns:
            start = pd.Timestamp(date_from) if date_from else pd.Timestamp(date.today())
            end = pd.Timestamp(date_to) if date_to else start
            out = out[out["date"].notna() & (out["date"] >= start) & (out["date"] <= end + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))]
    else:
        if org_val not in ("all", "Все", None) and out.shape[1] > 2:
            out = out[out.iloc[:, 2].astype(str).str.contains(str(org_val), case=False, na=False)]
        if city and city != "Все" and out.shape[1] > 1:
            out = out[out.iloc[:, 1].astype(str).str.contains(city, case=False, na=False)]
        if date_mode != "Весь период" and out.shape[1] > 12 and pd.api.types.is_datetime64_any_dtype(out.iloc[:, 12]):
            start = pd.Timestamp(date_from) if date_from else pd.Timestamp(date.today())
            end = pd.Timestamp(date_to) if date_to else start
            out = out[out.iloc[:, 12].notna() & (out.iloc[:, 12] >= start) & (out.iloc[:, 12] <= end + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))]
    if search:
        out = out[out.apply(lambda r: r.astype(str).str.contains(search, case=False, na=False).any(), axis=1)]
    return out.reset_index(drop=True)


def equipment_chips_from_text(text: Any) -> List[Dict[str, Any]]:
    s = safe_str(text)
    if not s:
        return []
    pattern = re.findall(r"([А-Яа-яA-Za-z][А-Яа-яA-Za-z0-9\s\-]*?):\s*([\d.,]+)\s*([^\d,;|·\n]*)", s)
    if not pattern:
        return [{"label": s, "qty": "", "type": "default"}]
    chips = []
    for name, qty, unit in pattern:
        label = safe_str(name)
        unit_s = safe_str(unit).replace("шт.", "").replace("шт", "").strip().rstrip(".,;")
        type_ = "default"
        l = label.lower()
        if "ккт" in l or "термин" in l:
            type_ = "kkt"
        elif "фн-15" in l or "фн15" in l:
            type_ = "fn15"
        elif "фн-36" in l or "фн36" in l:
            type_ = "fn36"
        elif "sim" in l or "сим" in l:
            type_ = "sim"
        chips.append({"label": f"{label}{' ' + unit_s if unit_s else ''}", "qty": clean_num(qty), "type": type_})
    return chips


def serial_tags(raw: Any) -> List[Dict[str, str]]:
    result = []
    for line in safe_str(raw).replace("\r", "").split("\n"):
        line = line.strip()
        if not line or line.lower() in ("nan", "none"):
            continue
        tag = ""
        if line.startswith("7381") or line.startswith("7385"):
            tag = "ФН-36"
        elif line.startswith("7380") or line.startswith("7384"):
            tag = "ФН-15"
        result.append({"serial": line, "tag": tag})
    return result


def shipment_row(row: pd.Series, idx: int) -> Dict[str, Any]:
    date_val = safe_iloc(row, 12)
    status_raw = safe_str(safe_iloc(row, 11)).upper()
    is_way = "ПУТ" in status_raw
    return {
        "row_id": str(idx),
        "record_id": safe_str(safe_iloc(row, 14)),
        "date": fmt_date_ru(date_val),
        "date_iso": fmt_iso_date(date_val),
        "city": safe_str(safe_iloc(row, 1)),
        "client": safe_str(safe_iloc(row, 2)),
        "equipment": safe_str(safe_iloc(row, 7)),
        "equipment_chips": equipment_chips_from_text(safe_iloc(row, 7)),
        "serials": serial_tags(safe_iloc(row, 10)),
        "track": safe_str(safe_iloc(row, 13)),
        "status": "В ПУТИ" if is_way else "ДОСТАВЛЕНО",
        "status_icon": "🚚" if is_way else "✅",
        "is_way": is_way,
        "raw": {str(k): (fmt_date_ru(v) if isinstance(v, (pd.Timestamp, datetime)) else safe_str(v)) for k, v in row.items()},
    }


def movement_row(row: pd.Series, idx: int) -> Dict[str, Any]:
    return {
        "row_id": str(idx),
        "date": fmt_date_ru(row.get("date", "")),
        "date_iso": fmt_iso_date(row.get("date", "")),
        "city_from": safe_str(row.get("city_from", "")),
        "org_from": safe_str(row.get("org_from", "")),
        "addr_from": safe_str(row.get("addr_from", "")),
        "person_from": safe_str(row.get("person_from", "")),
        "city_to": safe_str(row.get("city_to", "")),
        "org_to": safe_str(row.get("org_to", "")),
        "addr_to": safe_str(row.get("addr_to", "")),
        "person_to": safe_str(row.get("person_to", "")),
        "phone_to": clean_phone(row.get("phone_to", "")),
        "comment": safe_str(row.get("comment", "")),
        "kkt": clean_num(row.get("kkt", "")),
        "fn15": clean_num(row.get("fn15", "")),
        "fn36": clean_num(row.get("fn36", "")),
        "serials": serial_tags(row.get("serials", "")),
        "track": safe_str(row.get("track", "")),
        "raw": {str(k): (fmt_date_ru(v) if isinstance(v, (pd.Timestamp, datetime)) else safe_str(v)) for k, v in row.items()},
    }


def debt_event_row(row: pd.Series, idx: int) -> Dict[str, Any]:
    data = {str(k): safe_str(v) for k, v in row.items()}
    values = [v for v in data.values() if v]
    title = values[0] if values else "Замена / долг"
    text = " · ".join(values[1:4]) if len(values) > 1 else "Новая запись"
    return {
        "row_id": str(idx),
        "title": title,
        "text": text,
        "raw": data,
    }


def make_excel_exact(df: pd.DataFrame, sheet_name: str) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        if df is None or df.empty:
            pd.DataFrame({"Статус": ["Нет данных"]}).to_excel(writer, index=False, sheet_name=sheet_name)
        else:
            clean = df.copy()
            for col in clean.columns:
                if pd.api.types.is_datetime64_any_dtype(clean[col]):
                    clean[col] = clean[col].dt.strftime("%d.%m.%Y")
            clean.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    return output.getvalue()


def make_excel_shipments(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    rows = []
    if df is not None and not df.empty:
        for _, r in df.iterrows():
            status = "В ПУТИ" if "ПУТ" in safe_str(safe_iloc(r, 11)).upper() else "ДОСТАВЛЕНО"
            rows.append({
                "Дата": fmt_date_ru(safe_iloc(r, 12)),
                "Город": safe_str(safe_iloc(r, 1)),
                "Клиент": safe_str(safe_iloc(r, 2)),
                "Оборудование": safe_str(safe_iloc(r, 7)),
                "Серийники": safe_str(safe_iloc(r, 10)),
                "Трек": safe_str(safe_iloc(r, 13)),
                "ID": safe_str(safe_iloc(r, 14)),
                "Статус": status,
            })
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        (pd.DataFrame(rows) if rows else pd.DataFrame({"Статус": ["Нет данных"]})).to_excel(writer, index=False, sheet_name="Отгрузки")
    output.seek(0)
    return output.getvalue()


def make_excel_return(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    rows = []
    if df is not None and not df.empty:
        for _, r in df.iterrows():
            rows.append({
                "Дата": fmt_date_ru(r.get("date", "")),
                "Город (откуда)": safe_str(r.get("city_from", "")),
                "Отправитель": safe_str(r.get("org_from", "")),
                "Адрес (откуда)": safe_str(r.get("addr_from", "")),
                "ФИО отправителя": safe_str(r.get("person_from", "")),
                "Город (куда)": safe_str(r.get("city_to", "")),
                "Получатель": safe_str(r.get("org_to", "")),
                "Адрес (куда)": safe_str(r.get("addr_to", "")),
                "ФИО получателя": safe_str(r.get("person_to", "")),
                "Телефон": clean_phone(r.get("phone_to", "")),
                "ККТ": clean_num(r.get("kkt", "")),
                "ФН-15": clean_num(r.get("fn15", "")),
                "ФН-36": clean_num(r.get("fn36", "")),
                "Серийные номера": safe_str(r.get("serials", "")).replace("\n", " | "),
                "Комментарий": safe_str(r.get("comment", "")),
                "Трек": safe_str(r.get("track", "")),
            })
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        (pd.DataFrame(rows) if rows else pd.DataFrame({"Статус": ["Нет данных"]})).to_excel(writer, index=False, sheet_name="Возвраты")
    output.seek(0)
    return output.getvalue()


def build_news(df_ship: pd.DataFrame, df_ret: pd.DataFrame, user: Dict[str, Any]) -> List[Dict[str, Any]]:
    today = date.today()
    news: List[Dict[str, Any]] = []
    df_s = apply_common_filters(df_ship, user, kind="shipments")
    df_r = apply_common_filters(df_ret, user, kind="movements")
    if df_s is not None and not df_s.empty and df_s.shape[1] > 12 and pd.api.types.is_datetime64_any_dtype(df_s.iloc[:, 12]):
        ts = df_s[df_s.iloc[:, 12].notna() & (df_s.iloc[:, 12].dt.date == today)]
        way = ts[ts.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False)] if ts.shape[1] > 11 else pd.DataFrame()
        delivered = ts[~ts.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False)] if ts.shape[1] > 11 else pd.DataFrame()
        if len(way):
            news.append({"icon": "🚚", "title": f"{len(way)} новых отправок сегодня", "text": f"Клиенты: {', '.join(list(set(way.iloc[:,2].astype(str).tolist()))[:2])}. Города: {', '.join(list(set(way.iloc[:,1].astype(str).tolist()))[:2])}", "type": "shipment", "today": True})
        if len(delivered):
            news.append({"icon": "✅", "title": f"{len(delivered)} доставлений сегодня", "text": f"Доставлено: {', '.join(list(set(delivered.iloc[:,2].astype(str).tolist()))[:2])}", "type": "success", "today": True})
        week = df_s[df_s.iloc[:, 12].notna() & (df_s.iloc[:, 12].dt.date >= today - timedelta(days=7)) & (df_s.iloc[:, 12].dt.date < today)]
        if len(week):
            news.append({"icon": "📊", "title": f"Итоги недели: {len(week)} отправок", "text": f"Клиентов: {week.iloc[:,2].nunique()}, городов: {week.iloc[:,1].nunique()}.", "type": "info", "today": False})
        in_way_all = df_s[df_s.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False)] if df_s.shape[1] > 11 else pd.DataFrame()
        if len(in_way_all):
            news.append({"icon": "🚚", "title": f"Сейчас в пути: {len(in_way_all)} отправок", "text": "Города: " + ", ".join(list(set(in_way_all.iloc[:, 1].astype(str).tolist()))[:4]), "type": "shipment", "today": True})
    if df_r is not None and not df_r.empty and "date" in df_r.columns:
        tr = df_r[df_r["date"].notna() & (df_r["date"].dt.date == today)]
        if len(tr):
            routes = []
            for _, r in tr.head(3).iterrows():
                cf = safe_str(r.get("city_from", "")); ct = safe_str(r.get("city_to", ""))
                if cf and ct:
                    routes.append(f"{cf}→{ct}")
            news.append({"icon": "🔄", "title": f"{len(tr)} перемещений сегодня", "text": "Маршруты: " + (", ".join(routes) if routes else "—"), "type": "movement", "today": True})
    return news or [{"icon": "ℹ️", "title": "Система работает штатно", "text": "Новых событий нет", "type": "info", "today": False}]


def file_response(data: bytes, filename: str):
    return StreamingResponse(io.BytesIO(data), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@app.get("/")
def root():
    return {"status": "LIFE PAY backend is running", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "ok", "app": APP_NAME, "time": now_iso()}


@app.post("/api/auth/login")
def login(payload: LoginRequest, x_forwarded_for: Optional[str] = Header(None)):
    if payload.pin not in USERS:
        raise HTTPException(status_code=401, detail="Неверный PIN-код")
    name, filt = USERS[payload.pin]
    token = uuid.uuid4().hex
    user = {
        "token": token, "name": name, "filter": filt,
        "role": "SUPER ADMIN" if name == "SUPER ADMIN" else ("ADMIN" if filt == "all" else "USER"),
        "login_time": now_iso(), "last_activity": now_iso(), "ip": x_forwarded_for or "unknown",
    }
    TOKENS[token] = user
    LOGIN_EVENTS.insert(0, {k: v for k, v in user.items() if k != "token"})
    return {"token": token, "user": {k: v for k, v in user.items() if k != "token"}}


@app.post("/api/track")
def track(payload: TrackRequest, authorization: Optional[str] = Header(None)):
    user = require_user(authorization)
    PAGE_EVENTS.insert(0, {"user": user["name"], "organization": user["filter"], "page": payload.page, "time": now_iso()})
    return {"ok": True}


@app.get("/api/filters")
def filters(authorization: Optional[str] = Header(None)):
    user = require_user(authorization)
    stock, ship = get_data(); mov = get_return_data()
    orgs = ["Все"]
    if user["filter"] == "all" and ship is not None and not ship.empty and ship.shape[1] > 2:
        orgs += sorted([safe_str(x) for x in ship.iloc[:, 2].dropna().unique().tolist() if safe_str(x)])
    cities = set()
    if ship is not None and not ship.empty and ship.shape[1] > 1:
        cities.update([safe_str(x) for x in ship.iloc[:, 1].dropna().unique().tolist() if safe_str(x)])
    if stock is not None and not stock.empty and stock.shape[1] > 2:
        cities.update([safe_str(x) for x in stock.iloc[:, 2].dropna().unique().tolist() if safe_str(x)])
    if mov is not None and not mov.empty:
        for c in ["city_from", "city_to"]:
            if c in mov.columns:
                cities.update([safe_str(x) for x in mov[c].dropna().unique().tolist() if safe_str(x)])
    date_min = "2020-01-01"
    if ship is not None and not ship.empty and ship.shape[1] > 12 and pd.api.types.is_datetime64_any_dtype(ship.iloc[:, 12]):
        d = ship.iloc[:, 12].dropna()
        if len(d):
            date_min = d.min().date().isoformat()
    return {"organizations": orgs, "cities": ["Все"] + sorted(cities), "date_min": date_min, "date_max": "2030-12-31"}


@app.get("/api/dashboard")
def dashboard(authorization: Optional[str] = Header(None)):
    user = require_user(authorization)
    stock, ship = get_data(); mov = get_return_data(); debts = get_debts_data()
    stock_f = apply_common_filters(stock, user, kind="stock")
    ship_f = apply_common_filters(ship, user, kind="shipments")
    mov_f = apply_common_filters(mov, user, kind="movements")
    kkt = int(pd.to_numeric(stock_f.iloc[:, 5], errors="coerce").sum()) if stock_f is not None and not stock_f.empty and stock_f.shape[1] > 5 else 0
    fn15 = int(pd.to_numeric(stock_f.iloc[:, 6], errors="coerce").sum()) if stock_f is not None and not stock_f.empty and stock_f.shape[1] > 6 else 0
    fn36 = int(pd.to_numeric(stock_f.iloc[:, 7], errors="coerce").sum()) if stock_f is not None and not stock_f.empty and stock_f.shape[1] > 7 else 0
    today = date.today()
    ts_count = ws_count = wa_count = 0
    if ship_f is not None and not ship_f.empty and ship_f.shape[1] > 12 and pd.api.types.is_datetime64_any_dtype(ship_f.iloc[:, 12]):
        dm = ship_f.iloc[:, 12].notna()
        ts_count = len(ship_f[dm & (ship_f.iloc[:, 12].dt.date == today)])
        ws_count = len(ship_f[dm & (ship_f.iloc[:, 12].dt.date >= today - timedelta(days=7))])
        wa_count = len(ship_f[ship_f.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False)]) if ship_f.shape[1] > 11 else 0
    city_counts = []
    if stock_f is not None and not stock_f.empty and stock_f.shape[1] > 2:
        vc = stock_f.iloc[:, 2].astype(str).value_counts().head(8)
        city_counts = [{"city": k, "count": int(v)} for k, v in vc.items()]
    debts_clean = clean_debts_dataframe(debts) if debts is not None else pd.DataFrame()
    if user["filter"] != "all" and not debts_clean.empty:
        debts_clean = debts_clean[debts_clean.apply(lambda r: contains_any(r, user["filter"]), axis=1)]

    recent_shipments = [shipment_row(r, i) for i, r in ship_f.head(6).iterrows()] if ship_f is not None else []
    recent_movements = [movement_row(r, i) for i, r in mov_f.head(6).iterrows()] if mov_f is not None else []
    recent_debts = [debt_event_row(r, i) for i, r in debts_clean.head(6).iterrows()] if debts_clean is not None and not debts_clean.empty else []
    new_events = []
    for x in recent_shipments[:4]:
        new_events.append({"type": "shipment", "icon": "🚚", "title": f"Новая отгрузка: {x.get('city') or '—'}", "text": f"{x.get('date') or '—'} · {x.get('client') or '—'}", "date_iso": x.get("date_iso"), "row_id": x.get("row_id")})
    for x in recent_movements[:4]:
        route = f"{x.get('city_from') or '—'} → {x.get('city_to') or '—'}"
        new_events.append({"type": "movement", "icon": "🔄", "title": f"Новое перемещение: {route}", "text": f"{x.get('date') or '—'} · {x.get('org_from') or ''} → {x.get('org_to') or ''}", "date_iso": x.get("date_iso"), "row_id": x.get("row_id")})
    for x in recent_debts[:4]:
        new_events.append({"type": "debt", "icon": "🧾", "title": "Новая замена / долг", "text": f"{x.get('title') or ''} · {x.get('text') or ''}", "date_iso": "", "row_id": x.get("row_id")})
    new_events = new_events[:8]

    return {
        "user": {"name": user["name"], "filter": user["filter"], "role": user["role"]},
        "kpis": {"kkt": kkt, "fn15": fn15, "fn36": fn36, "total_stock": kkt + fn15 + fn36, "shipments_today": ts_count, "shipments_week": ws_count, "in_way": wa_count, "movements": len(mov_f), "debts": len(debts_clean) if debts_clean is not None else 0},
        "city_counts": city_counts,
        "recent_shipments": recent_shipments,
        "recent_movements": recent_movements,
        "recent_debts": recent_debts,
        "new_events": new_events,
        "news": build_news(ship, mov, user),
    }


@app.get("/api/stock")
def stock(org: Optional[str] = None, city: Optional[str] = None, search: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization)
    df, _ = get_data()
    df = apply_common_filters(df, user, org=org, city=city, search=search, kind="stock")
    kpis = {"kkt": 0, "fn15": 0, "fn36": 0, "total": 0}
    columns = [str(c) for c in df.columns] if df is not None and not df.empty else []
    rows: List[Dict[str, Any]] = []

    if df is not None and not df.empty:
        if df.shape[1] > 5: kpis["kkt"] = int(pd.to_numeric(df.iloc[:, 5], errors="coerce").sum())
        if df.shape[1] > 6: kpis["fn15"] = int(pd.to_numeric(df.iloc[:, 6], errors="coerce").sum())
        if df.shape[1] > 7: kpis["fn36"] = int(pd.to_numeric(df.iloc[:, 7], errors="coerce").sum())
        kpis["total"] = kpis["kkt"] + kpis["fn15"] + kpis["fn36"]

        for i, (_, r) in enumerate(df.iterrows(), 1):
            kkt = safe_int(safe_iloc(r, 5))
            fn15 = safe_int(safe_iloc(r, 6))
            fn36 = safe_int(safe_iloc(r, 7))
            total = kkt + fn15 + fn36
            details = []
            for label, value in zip(columns, r.values):
                val = safe_str(value)
                if val.lower() in ("", "nan", "none"):
                    continue
                if "ответств" in str(label).lower():
                    continue
                details.append({"label": str(label), "value": val})
            rows.append({
                "idx": i,
                "row_id": i - 1,
                "region": safe_str(safe_iloc(r, 0)),
                "partner": safe_str(safe_iloc(r, 1)),
                "city": safe_str(safe_iloc(r, 2)),
                "address": safe_str(safe_iloc(r, 3)),
                "kkt": kkt,
                "fn15": fn15,
                "fn36": fn36,
                "total": total,
                "status": "Нет остатка" if total <= 0 else ("Низкий остаток" if total <= 3 else "В наличии"),
                "raw": {str(k): safe_str(v) for k, v in r.items()},
                "details": details,
            })

    def top_counts(col_idx: int, value_name: str = "total") -> List[Dict[str, Any]]:
        if df is None or df.empty or df.shape[1] <= col_idx:
            return []
        tmp = []
        for label, group in df.groupby(df.iloc[:, col_idx].astype(str), dropna=True):
            if not safe_str(label):
                continue
            total = 0
            if group.shape[1] > 5: total += int(pd.to_numeric(group.iloc[:, 5], errors="coerce").sum())
            if group.shape[1] > 6: total += int(pd.to_numeric(group.iloc[:, 6], errors="coerce").sum())
            if group.shape[1] > 7: total += int(pd.to_numeric(group.iloc[:, 7], errors="coerce").sum())
            tmp.append({"name": safe_str(label), "count": len(group), value_name: total})
        return sorted(tmp, key=lambda x: x[value_name], reverse=True)[:10]

    summary = {
        "cities": len(set([r["city"] for r in rows if r.get("city")])) if rows else 0,
        "partners": len(set([r["partner"] for r in rows if r.get("partner")])) if rows else 0,
        "regions": len(set([r["region"] for r in rows if r.get("region")])) if rows else 0,
        "low_stock": len([r for r in rows if r.get("total", 0) <= 3]),
        "zero_stock": len([r for r in rows if r.get("total", 0) <= 0]),
    }
    return {
        "kpis": kpis,
        "summary": summary,
        "count": len(rows),
        "columns": columns,
        "by_city": top_counts(2),
        "by_partner": top_counts(1),
        "rows": rows,
    }


@app.get("/api/debts")
def debts(org: Optional[str] = None, search: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization)
    raw = get_debts_data(); df = clean_debts_dataframe(raw)
    if df.shape[1] > 12:
        df = df.iloc[:, :12]
    filt = user["filter"] if user["filter"] != "all" else (org or "Все")
    if filt not in ("all", "Все", None) and not df.empty:
        df = df[df.apply(lambda r: contains_any(r, str(filt)), axis=1)]
    if search and not df.empty:
        df = df[df.apply(lambda r: contains_any(r, search), axis=1)]
    return {"count": len(df), "columns": [str(c) for c in df.columns], "rows": df_records(df, 500)}


@app.get("/api/statistics")
def statistics(org: Optional[str] = None, search: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization)
    raw = get_debts_data()
    if raw is None or raw.empty or raw.shape[1] <= 12:
        return {"count": 0, "columns": [], "rows": [], "metrics": []}
    end = min(28, raw.shape[1])
    df = raw.iloc[:, 12:end].copy()
    df.columns = [f"Столбец {12+i+1}" if str(c).startswith("Unnamed") else safe_str(c) for i, c in enumerate(df.columns)]
    for c in df.columns:
        df[c] = df[c].apply(lambda v: "" if is_junk_value(v) else safe_str(v))
    df = df[df.apply(lambda r: any(safe_str(v).lower() not in ("", "nan", "none", "0", "0.0") for v in r.values), axis=1)]
    df = df[[c for c in df.columns if df[c].apply(lambda v: safe_str(v).lower() not in ("", "nan", "none")).any()]] if not df.empty else df
    filt = user["filter"] if user["filter"] != "all" else (org or "Все")
    if filt not in ("all", "Все", None) and not df.empty:
        df = df[df.apply(lambda r: row_matches_partner(r, str(filt)), axis=1)]
    if search and not df.empty:
        df = df[df.apply(lambda r: contains_any(r, search), axis=1)]
    metrics = []
    for c in df.columns:
        vals = [is_real_number(v) for v in df[c]]
        total = sum(n for ok, n in vals if ok)
        count = sum(1 for ok, _ in vals if ok)
        if count:
            metrics.append({"name": str(c), "total": int(total) if total == int(total) else round(total, 1), "count": count})
    return {"count": len(df), "columns": [str(c) for c in df.columns], "rows": df_records(df, 500), "metrics": metrics[:8]}


@app.get("/api/shipments")
def shipments(org: Optional[str] = None, city: Optional[str] = None, search: Optional[str] = None, date_mode: str = "Весь период", date_from: Optional[str] = None, date_to: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization)
    _, df = get_data()
    df = apply_common_filters(df, user, org=org, city=city, search=search, date_mode=date_mode, date_from=date_from, date_to=date_to, kind="shipments")
    rows = [shipment_row(r, i) for i, r in df.iterrows()] if df is not None and not df.empty else []
    return {"count": len(rows), "rows": rows}


@app.get("/api/movements")
def movements(org: Optional[str] = None, city: Optional[str] = None, search: Optional[str] = None, date_mode: str = "Весь период", date_from: Optional[str] = None, date_to: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization)
    df = get_return_data()
    df = apply_common_filters(df, user, org=org, city=city, search=search, date_mode=date_mode, date_from=date_from, date_to=date_to, kind="movements")
    if df is not None and not df.empty and "date" in df.columns:
        df = df.sort_values("date", ascending=False, na_position="last").reset_index(drop=True)
    rows = [movement_row(r, i) for i, r in df.iterrows()] if df is not None and not df.empty else []
    return {"count": len(rows), "rows": rows, "newest_on_top": True}


@app.get("/api/news")
def news(authorization: Optional[str] = Header(None)):
    user = require_user(authorization)
    _, ship = get_data(); mov = get_return_data()
    news_items = build_news(ship, mov, user)
    today = date.today()
    df_s = apply_common_filters(ship, user, kind="shipments")
    df_r = apply_common_filters(mov, user, kind="movements")
    ts = ws = wa = 0
    if df_s is not None and not df_s.empty and df_s.shape[1] > 12 and pd.api.types.is_datetime64_any_dtype(df_s.iloc[:, 12]):
        dm = df_s.iloc[:, 12].notna()
        ts = len(df_s[dm & (df_s.iloc[:, 12].dt.date == today)])
        ws = len(df_s[dm & (df_s.iloc[:, 12].dt.date >= today - timedelta(days=7))])
        wa = len(df_s[df_s.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False)]) if df_s.shape[1] > 11 else 0
    tr = 0
    if df_r is not None and not df_r.empty and "date" in df_r.columns:
        tr = len(df_r[df_r["date"].notna() & (df_r["date"].dt.date == today)])
    return {"items": news_items, "stats": {"today_shipments": ts, "week_shipments": ws, "today_movements": tr, "in_way": wa}}


@app.get("/api/admin/analytics")
def admin_analytics(authorization: Optional[str] = Header(None)):
    user = require_user(authorization)
    if user["filter"] != "all":
        raise HTTPException(status_code=403, detail="Only admin can access analytics")
    org_counts: Dict[str, int] = {}
    for u in TOKENS.values():
        org_counts[u["filter"]] = org_counts.get(u["filter"], 0) + 1
    page_counts: Dict[str, int] = {}
    for p in PAGE_EVENTS[:300]:
        page_counts[p["page"]] = page_counts.get(p["page"], 0) + 1
    users_access = []
    for pin, (name, filt) in USERS.items():
        users_access.append({
            "user": name,
            "access": "Все организации" if filt == "all" else filt,
            "role": "ADMIN" if filt == "all" else "PARTNER",
            "status": "Активен",
            "pin_length": len(pin),
        })
    return {
        "online_users": len(TOKENS),
        "active_organizations": len(org_counts),
        "login_events": LOGIN_EVENTS[:80],
        "page_events": PAGE_EVENTS[:150],
        "organization_activity": [{"organization": k, "count": v} for k, v in org_counts.items()],
        "page_activity": [{"page": k, "count": v} for k, v in page_counts.items()],
        "users_access": users_access,
        "admin_tools": [
            {"name": "Мониторинг входов", "status": "ON"},
            {"name": "Журнал страниц", "status": "ON"},
            {"name": "Контроль доступа", "status": "ON"},
            {"name": "Активность организаций", "status": "ON"},
        ],
    }


def filtered_ship_for_export(user: Dict[str, Any], org=None, city=None, search=None, date_mode="Весь период", date_from=None, date_to=None) -> pd.DataFrame:
    _, df = get_data()
    return apply_common_filters(df, user, org=org, city=city, search=search, date_mode=date_mode, date_from=date_from, date_to=date_to, kind="shipments")


@app.get("/api/export/stock")
def export_stock(token: Optional[str] = None, org: Optional[str] = None, city: Optional[str] = None, search: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization, token)
    df, _ = get_data(); df = apply_common_filters(df, user, org=org, city=city, search=search, kind="stock")
    return file_response(make_excel_exact(df, "Остатки"), "LifePay_Stock_Filtered.xlsx")


@app.get("/api/export/stock/{row_id}")
def export_stock_row(row_id: int, token: Optional[str] = None, org: Optional[str] = None, city: Optional[str] = None, search: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization, token)
    df, _ = get_data(); df = apply_common_filters(df, user, org=org, city=city, search=search, kind="stock")
    try:
        row = df.iloc[[row_id]]
    except Exception:
        row = pd.DataFrame()
    return file_response(make_excel_exact(row, "Остаток"), f"LifePay_Stock_Row_{row_id + 1}.xlsx")


@app.get("/api/export/debts")
def export_debts(token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization, token)
    raw = get_debts_data(); df = clean_debts_dataframe(raw)
    if df.shape[1] > 12: df = df.iloc[:, :12]
    if user["filter"] != "all": df = df[df.apply(lambda r: contains_any(r, user["filter"]), axis=1)]
    return file_response(make_excel_exact(df, "Долги"), "Dolgi_Zameny.xlsx")


@app.get("/api/export/statistics")
def export_statistics(token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization, token)
    raw = get_debts_data(); df = raw.iloc[:, 12:min(28, raw.shape[1])].copy() if raw is not None and not raw.empty and raw.shape[1] > 12 else pd.DataFrame()
    return file_response(make_excel_exact(df, "Статистика"), "Statistika_Ostatki_Dolgi_Zameny.xlsx")


@app.get("/api/export/shipments")
def export_shipments(token: Optional[str] = None, org: Optional[str] = None, city: Optional[str] = None, search: Optional[str] = None, date_mode: str = "Весь период", date_from: Optional[str] = None, date_to: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization, token)
    df = filtered_ship_for_export(user, org, city, search, date_mode, date_from, date_to)
    return file_response(make_excel_shipments(df), "Otgruzki.xlsx")


@app.get("/api/export/shipments/{row_id}")
def export_shipment_row(row_id: int, token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization, token)
    _, df = get_data(); df = apply_common_filters(df, user, kind="shipments")
    try:
        row = df.iloc[[row_id]]
    except Exception:
        row = pd.DataFrame()
    return file_response(make_excel_shipments(row), f"Shipment_{row_id}.xlsx")


@app.get("/api/export/movements")
def export_movements(token: Optional[str] = None, org: Optional[str] = None, city: Optional[str] = None, search: Optional[str] = None, date_mode: str = "Весь период", date_from: Optional[str] = None, date_to: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization, token)
    df = get_return_data(); df = apply_common_filters(df, user, org=org, city=city, search=search, date_mode=date_mode, date_from=date_from, date_to=date_to, kind="movements")
    return file_response(make_excel_return(df), "Vozvrat_Peremeschenie.xlsx")


@app.get("/api/export/movements/{row_id}")
def export_movement_row(row_id: int, token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    user = require_user(authorization, token)
    df = get_return_data(); df = apply_common_filters(df, user, kind="movements")
    try:
        row = df.iloc[[row_id]]
    except Exception:
        row = pd.DataFrame()
    return file_response(make_excel_return(row), f"Return_{row_id}.xlsx")
