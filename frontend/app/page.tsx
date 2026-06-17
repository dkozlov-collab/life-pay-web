"use client";

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  Archive,
  Bell,
  Boxes,
  Building2,
  CalendarDays,
  ChevronDown,
  Download,
  FileSpreadsheet,
  Home,
  Loader2,
  LogOut,
  Menu,
  Moon,
  Monitor,
  Palette,
  Play,
  Radio,
  Smartphone,
  RefreshCw,
  Search,
  Settings,
  Shield,
  Sparkles,
  Sun,
  Truck,
  Users,
  Volume2,
  VolumeX,
  X,
} from "lucide-react";
import { API_URL, apiFetch, exportUrl } from "../lib/api";

type User = { name: string; filter: string; role: string; login_time?: string };
type ThemeMode = "light" | "dark" | "system";
type VisualTheme = "life" | "aurora" | "mint" | "graphite" | "neo" | "ocean";
type SoundPreset = "crystal" | "soft" | "neo" | "success" | "alert" | "minimal";
type Filters = {
  organizations: string[];
  cities: string[];
  date_min: string;
  date_max: string;
};

type FilterState = {
  search: string;
  org: string;
  city: string;
  date_mode: string;
  date_from: string;
  date_to: string;
};

const pageNames: any = {
  dashboard: "Обзор системы",
  stock: "Остатки",
  debts: "Долги / Замены",
  statistics: "Статистика остатки долгов и замены",
  shipments: "Архив отгрузок",
  movements: "Возврат / Перемещение",
  news: "Новости",
  analytics: "Админ аналитика",
  settings: "Настройки",
};

const nav = [
  ["dashboard", "Обзор", Home],
  ["stock", "Остатки", Boxes],
  ["debts", "Долги / Замены", Archive],
  ["statistics", "Статистика", Activity],
  ["shipments", "Архив отгрузок", Truck],
  ["movements", "Перемещения", RefreshCw],
  ["news", "Новости", Bell],
  ["analytics", "Админ", Shield],
  ["settings", "Настройки", Settings],
] as const;

function useSound(enabled: boolean, preset: SoundPreset = "crystal") {
  return (type = "ok") => {
    if (!enabled || typeof window === "undefined") return;
    try {
      const Ctx = (window as any).AudioContext || (window as any).webkitAudioContext;
      const ctx = new Ctx();
      const base: Record<string, number> = {
        ok: 560, login: 760, error: 220, shipment: 610, movement: 440, news: 690, admin: 520,
      };
      const patterns: Record<SoundPreset, number[]> = {
        crystal: [1, 1.5],
        soft: [0.8, 1.05],
        neo: [0.7, 1.2, 1.7],
        success: [1, 1.25, 1.6],
        alert: [1, 0.72, 1],
        minimal: [1],
      };
      const wave: OscillatorType = preset === "neo" || preset === "alert" ? "triangle" : "sine";
      const seq = patterns[preset] || patterns.crystal;
      seq.forEach((m, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const start = ctx.currentTime + i * 0.09;
        const end = start + (preset === "minimal" ? 0.08 : 0.13);
        osc.type = wave;
        osc.frequency.value = (base[type] || 520) * m;
        gain.gain.setValueAtTime(0.0001, start);
        gain.gain.exponentialRampToValueAtTime(preset === "alert" ? 0.05 : 0.035, start + 0.018);
        gain.gain.exponentialRampToValueAtTime(0.0001, end);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(start);
        osc.stop(end);
      });
    } catch {}
  };
}

function paramsFromFilters(f: FilterState) {
  const p = new URLSearchParams();
  if (f.search) p.set("search", f.search);
  if (f.org && f.org !== "Все") p.set("org", f.org);
  if (f.city && f.city !== "Все") p.set("city", f.city);
  p.set("date_mode", f.date_mode);
  if (f.date_from) p.set("date_from", f.date_from);
  if (f.date_to) p.set("date_to", f.date_to);
  return p.toString();
}

function Section({ children, className = "" }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 22 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

function Spinner({ label = "Загрузка данных..." }: any) {
  return (
    <div className="loading glass">
      <Loader2 className="spin" size={22} />
      <span>{label}</span>
    </div>
  );
}

function LifePayLogo({ compact = false }: any) {
  return (
    <div className={`lp-logo ${compact ? "compact" : ""}`}>
      <div className="lp-mark">
        <span>LP</span>
        <i />
      </div>
      <div>
        <h1>LIFE PAY</h1>
        <p>Enterprise ERP</p>
      </div>
    </div>
  );
}

function Login({ onLogin, theme, setTheme, sound, soundPreset }: any) {
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const play = useSound(sound, soundPreset);

  async function submit() {
    setError("");
    setLoading(true);
    try {
      const data = await apiFetch("/api/auth/login", "", {
        method: "POST",
        body: JSON.stringify({ pin }),
      });
      play("login");
      onLogin(data.token, data.user);
    } catch (e: any) {
      play("error");
      setError(e.message || "Ошибка входа");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <AnimatedBackdrop />
      <motion.div
        initial={{ opacity: 0, scale: 0.92, y: 30 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="login-card glass-xl"
      >
        <LifePayLogo />
        <div className="login-copy">
          <span className="eyebrow">Secure workspace</span>
          <h2>Добро пожаловать 👋</h2>
          <p>Введите PIN-код для входа в LIFE PAY ERP.</p>
        </div>
        <label className="pin-label">🔐 PIN-код</label>
        <input
          className="pin-input"
          type="password"
          maxLength={10}
          placeholder="••••••"
          value={pin}
          onChange={(e) => setPin(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") submit();
          }}
          autoFocus
        />
        <button className="btn primary big" onClick={submit} disabled={loading}>
          {loading ? <Loader2 className="spin" size={18} /> : null} Войти в
          систему →
        </button>
        {error ? <div className="error">❌ {error}</div> : null}
        <div className="login-actions">
          <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />} Сменить
            тему
          </button>
        </div>
      </motion.div>
    </main>
  );
}

function AnimatedBackdrop() {
  return (
    <div className="app-bg">
      <div className="orb one" />
      <div className="orb two" />
      <div className="orb three" />
      <div className="grid-glow" />
      <div className="particles">
        {Array.from({ length: 18 }).map((_, i) => (
          <i key={i} />
        ))}
      </div>
    </div>
  );
}

function FilterBar({ filters, setFilters, meta, showDate = true }: any) {
  const update = (k: string, v: string) =>
    setFilters((s: FilterState) => ({ ...s, [k]: v }));
  return (
    <div className="filter-bar glass">
      <div className="filter search-filter">
        <Search size={17} />
        <input
          value={filters.search}
          placeholder="SN, город, клиент..."
          onChange={(e) => update("search", e.target.value)}
        />
      </div>
      <div className="filter">
        <Building2 size={17} />
        <select
          value={filters.org}
          onChange={(e) => update("org", e.target.value)}
        >
          {(meta?.organizations || ["Все"]).map((x: string) => (
            <option key={x}>{x}</option>
          ))}
        </select>
      </div>
      <div className="filter">
        <Archive size={17} />
        <select
          value={filters.city}
          onChange={(e) => update("city", e.target.value)}
        >
          {(meta?.cities || ["Все"]).map((x: string) => (
            <option key={x}>{x}</option>
          ))}
        </select>
      </div>
      {showDate ? (
        <>
          <div className="filter">
            <CalendarDays size={17} />
            <select
              value={filters.date_mode}
              onChange={(e) => update("date_mode", e.target.value)}
            >
              <option>Весь период</option>
              <option>Конкретная дата</option>
              <option>Диапазон</option>
            </select>
          </div>
          {filters.date_mode !== "Весь период" ? (
            <div className="date-pair">
              <input
                type="date"
                value={filters.date_from}
                min={meta?.date_min}
                max={meta?.date_max}
                onChange={(e) => update("date_from", e.target.value)}
              />
              {filters.date_mode === "Диапазон" ? (
                <input
                  type="date"
                  value={filters.date_to}
                  min={meta?.date_min}
                  max={meta?.date_max}
                  onChange={(e) => update("date_to", e.target.value)}
                />
              ) : null}
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  );
}

function Kpi({ icon, value, label, sub, tone = "blue", delay = 0 }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 28, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.45, delay }}
      whileHover={{ y: -7, scale: 1.02 }}
      className={`kpi glass tone-${tone}`}
    >
      <div className="kpi-shine" />
      <div className="kpi-icon">{icon}</div>
      <b>{value}</b>
      <span>{label}</span>
      <small>{sub}</small>
    </motion.div>
  );
}

function PageHead({ title, subtitle, actions }: any) {
  return (
    <div className="page-head">
      <div>
        <span className="eyebrow">LIFE PAY ERP</span>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
      <div className="head-actions">{actions}</div>
    </div>
  );
}

function ExportButton({ path, token, label = "Excel" }: any) {
  const href = `${exportUrl(path, token)}`;
  return (
    <a className="btn secondary" href={href} target="_blank">
      <FileSpreadsheet size={16} />
      {label}
    </a>
  );
}


function NewEventsPanel({ events }: any) {
  const items = events || [];
  if (!items.length) return null;
  return (
    <motion.div
      className="new-events-panel glass"
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28 }}
    >
      <div className="new-events-head">
        <div>
          <span className="eyebrow">Новые сверху</span>
          <h3>Новые отгрузки, перемещения и замены</h3>
          <p>Самые свежие события всегда отображаются первыми.</p>
        </div>
        <span className="new-count">{items.length} новых</span>
      </div>
      <div className="new-events-grid">
        {items.map((x: any, i: number) => (
          <motion.div
            key={`${x.type}-${x.row_id}-${i}`}
            className={`new-event-card ${x.type}`}
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
          >
            <span>{x.icon}</span>
            <div>
              <b>{x.title}</b>
              <p>{x.text}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

function Dashboard({ token, data, reload }: any) {
  if (!data) return <Spinner />;
  const k = data.kpis || {};
  return (
    <Section>
      <PageHead
        title="Обзор системы"
        subtitle="Актуальные показатели за текущий период"
        actions={
          <button className="btn secondary" onClick={reload}>
            <RefreshCw size={16} /> Обновить
          </button>
        }
      />
      <NewEventsPanel events={data.new_events || []} />
      <div className="kpi-grid">
        <Kpi
          icon="🏪"
          value={k.total_stock || 0}
          label="Всего на остатках"
          sub="ККТ + ФН"
          tone="blue"
          delay={0}
        />
        <Kpi
          icon="🚚"
          value={k.in_way || 0}
          label="В пути"
          sub="активные отгрузки"
          tone="cyan"
          delay={0.04}
        />
        <Kpi
          icon="📅"
          value={k.shipments_today || 0}
          label="Сегодня"
          sub="отгрузок"
          tone="mint"
          delay={0.08}
        />
        <Kpi
          icon="🔄"
          value={k.movements || 0}
          label="Перемещения"
          sub="записей"
          tone="purple"
          delay={0.12}
        />
      </div>
      <div className="dash-grid">
        <div className="glass card">
          <h3>Активность по городам</h3>
          <p className="muted">по складам и остаткам</p>
          <div className="bar-chart">
            {(data.city_counts || []).map((x: any, i: number) => (
              <div key={i} className="bar-item">
                <span>{x.city}</span>
                <div>
                  <motion.i
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, x.count * 12)}%` }}
                    transition={{ delay: 0.1 + i * 0.05 }}
                  />
                </div>
                <b>{x.count}</b>
              </div>
            ))}
          </div>
        </div>
        <div className="glass card">
          <h3>Лента новостей</h3>
          <p className="muted">автоматически</p>
          <div className="news-mini">
            {(data.news || []).slice(0, 4).map((n: any, i: number) => (
              <motion.div
                key={i}
                className={`news-row ${n.type}`}
                initial={{ opacity: 0, x: 18 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <span>{n.icon}</span>
                <div>
                  <b>{n.title}</b>
                  <p>{n.text}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
      <div className="two-cols">
        <div className="glass card">
          <h3>Последние отгрузки</h3>
          <ShipmentList
            token={token}
            rows={data.recent_shipments || []}
            compact
          />
        </div>
        <div className="glass card">
          <h3>Последние перемещения</h3>
          <MovementList
            token={token}
            rows={data.recent_movements || []}
            compact
          />
        </div>
      </div>
    </Section>
  );
}

function StockPage({
  token,
  filters,
  setFilters,
  meta,
  data,
  loading,
  reload,
}: any) {
  const qs = paramsFromFilters(filters);
  const summary = data?.summary || {};
  return (
    <Section>
      <PageHead
        title="Остатки"
        subtitle="Подробный склад: итоги, города, партнёры, раскрытие каждой строки и Excel по одной записи"
        actions={
          <>
            <a
              className="btn secondary"
              target="_blank"
              href={`${API_URL}/api/export/stock?token=${encodeURIComponent(token)}&${qs}`}
            >
              <FileSpreadsheet size={16} />
              Скачать остатки
            </a>
            <button className="btn secondary" onClick={reload}>
              <RefreshCw size={16} />
              Обновить
            </button>
          </>
        }
      />
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        meta={meta}
        showDate={false}
      />
      {loading ? (
        <Spinner />
      ) : (
        <>
          <div className="kpi-grid three">
            <Kpi
              icon="🖨️"
              value={data?.kpis?.kkt || 0}
              label="ККТ"
              sub="кассовые терминалы"
              tone="blue"
            />
            <Kpi
              icon="🗂️"
              value={data?.kpis?.fn15 || 0}
              label="ФН-15"
              sub="фискальный накопитель 15"
              tone="mint"
            />
            <Kpi
              icon="🗂️"
              value={data?.kpis?.fn36 || 0}
              label="ФН-36"
              sub="фискальный накопитель 36"
              tone="purple"
            />
          </div>

          <div className="stock-insight-grid">
            <motion.div className="stock-insight glass" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }}>
              <span>📦</span><b>{data?.kpis?.total || 0}</b><small>Всего оборудования</small>
            </motion.div>
            <motion.div className="stock-insight glass" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .03 }}>
              <span>🏙️</span><b>{summary.cities || 0}</b><small>Городов в остатках</small>
            </motion.div>
            <motion.div className="stock-insight glass" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .06 }}>
              <span>🏢</span><b>{summary.partners || 0}</b><small>Организаций / партнёров</small>
            </motion.div>
            <motion.div className="stock-insight glass warn" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .09 }}>
              <span>⚠️</span><b>{summary.low_stock || 0}</b><small>Низкий / нулевой остаток</small>
            </motion.div>
          </div>

          <div className="two-cols stock-analytics-row">
            <StockTopCard title="Топ городов по остаткам" icon="📍" rows={data?.by_city || []} />
            <StockTopCard title="Топ организаций по остаткам" icon="🏢" rows={data?.by_partner || []} />
          </div>

          <div className="section-title">
            <span>🛠</span>
            <b>Подробный список складов</b>
            <em>{data?.count || 0} позиций</em>
          </div>
          <StockList rows={data?.rows || []} token={token} qs={qs} />
        </>
      )}
    </Section>
  );
}

function StockTopCard({ title, icon, rows }: any) {
  const max = Math.max(...(rows || []).map((r: any) => r.total || 0), 1);
  return (
    <div className="card stock-top-card">
      <h3>{icon} {title}</h3>
      <div className="stock-top-list">
        {(rows || []).slice(0, 6).map((r: any, i: number) => (
          <div key={`${r.name}-${i}`} className="stock-top-line">
            <div>
              <b>{r.name || "—"}</b>
              <span>{r.count} строк</span>
            </div>
            <i><em style={{ width: `${Math.max(6, ((r.total || 0) / max) * 100)}%` }} /></i>
            <strong>{r.total || 0}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

function StockList({ rows, token, qs }: any) {
  const [open, setOpen] = useState<string | null>(null);
  if (!rows?.length) return <div className="empty">📭 Нет остатков по выбранным фильтрам</div>;
  return (
    <div className="stock-list v6-stock-list">
      {rows.map((r: any, i: number) => {
        const rowKey = String(r.row_id ?? i);
        const isOpen = open === rowKey;
        return (
          <motion.div
            key={rowKey}
            className={`stock-card glass ${isOpen ? "open" : ""}`}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.014 }}
            whileHover={{ y: -3 }}
          >
            <button className="stock-main" onClick={() => setOpen(isOpen ? null : rowKey)}>
              <div className="stock-left">
                <div className="stock-avatar">{r.status === "Нет остатка" ? "0" : "LP"}</div>
                <div>
                  <span className={`stock-status ${r.status === "В наличии" ? "good" : r.status === "Низкий остаток" ? "warn" : "bad"}`}>{r.status}</span>
                  <h3>{r.city || "—"}</h3>
                  <p>{r.partner || "—"}</p>
                  <small>{r.region || "Регион не указан"}</small>
                </div>
              </div>
              <div className="stock-total-ring">
                <b>{r.total || 0}</b>
                <span>всего</span>
              </div>
              <div className="stock-stats stock-stats-v6">
                <i>ККТ <strong>{r.kkt}</strong></i>
                <i>ФН-15 <strong>{r.fn15}</strong></i>
                <i>ФН-36 <strong>{r.fn36}</strong></i>
              </div>
              <ChevronDown className={isOpen ? "rot" : ""} />
            </button>
            <AnimatePresence>
              {isOpen && (
                <motion.div className="stock-details" initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }}>
                  <div className="stock-detail-grid">
                    <div>
                      <h4>📋 Основная информация</h4>
                      <div className="stock-mini-fields">
                        <div><label>Город</label><b>{r.city || "—"}</b></div>
                        <div><label>Организация</label><b>{r.partner || "—"}</b></div>
                        <div><label>Регион</label><b>{r.region || "—"}</b></div>
                      </div>
                      <div className="detail-actions">
                        <a className="btn secondary" href={`${API_URL}/api/export/stock/${r.row_id}?token=${encodeURIComponent(token)}&${qs}`} target="_blank">
                          <Download size={16} />
                          Excel по этой строке
                        </a>
                      </div>
                    </div>
                    <div>
                      <h4>🔎 Все поля из Google Sheets</h4>
                      <div className="stock-raw-grid">
                        {(r.details || [])
                          .filter((d: any) => !String(d.label || "").toLowerCase().includes("ответств"))
                          .map((d: any, j: number) => (
                            <div key={j}>
                              <label>{d.label}</label>
                              <span>{d.value}</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        );
      })}
    </div>
  );
}

function GenericCards({ rows, columns }: any) {
  return (
    <div className="debt-grid">
      {(rows || []).map((r: any, i: number) => (
        <motion.div
          key={i}
          className="debt-card glass"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.02 }}
        >
          {(columns || Object.keys(r)).map((c: string) => {
            const v = r[c];
            if (!v) return null;
            return (
              <div key={c} className="field">
                <label>{c.replace(/\.\d+$/, "")}</label>
                <ValueText value={v} />
              </div>
            );
          })}
        </motion.div>
      ))}
    </div>
  );
}

function ValueText({ value }: any) {
  const s = String(value);
  const lower = s.toLowerCase();
  const isStatus = [
    "оплачен",
    "закрыт",
    "выполнен",
    "готов",
    "замен",
    "долг",
    "задолж",
    "не оплачен",
    "просроч",
    "ожидан",
    "частичн",
    "в процесс",
    "в работ",
  ].some((w) => lower.includes(w));
  const isNum =
    /^[-+]?\d+[\d\s,.]*$/.test(s) && s.replace(/\D/g, "").length <= 10;
  if (isStatus)
    return (
      <span
        className={`status-pill ${lower.includes("долг") || lower.includes("просроч") ? "bad" : lower.includes("закры") || lower.includes("готов") || lower.includes("выполн") ? "good" : "warn"}`}
      >
        {s}
      </span>
    );
  if (isNum) return <strong className="num-text">{s}</strong>;
  return <span>{s}</span>;
}

function DebtsPage({
  token,
  filters,
  setFilters,
  meta,
  data,
  loading,
  reload,
}: any) {
  return (
    <Section>
      <PageHead
        title="Долги партнёров / Статусы замен"
        subtitle="Данные по задолженностям и заменам оборудования"
        actions={
          <>
            <ExportButton
              path="/api/export/debts"
              token={token}
              label="Скачать долги"
            />
            <button className="btn secondary" onClick={reload}>
              <RefreshCw size={16} />
              Обновить
            </button>
          </>
        }
      />
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        meta={meta}
        showDate={false}
      />
      {loading ? (
        <Spinner />
      ) : (
        <>
          <div className="section-title">
            <span>📋</span>
            <b>Детальные записи</b>
            <em>{data?.count || 0} записей · новые сверху</em>
          </div>
          <GenericCards rows={data?.rows || []} columns={data?.columns || []} />
        </>
      )}
    </Section>
  );
}

function StatisticsPage({
  token,
  filters,
  setFilters,
  meta,
  data,
  loading,
  reload,
}: any) {
  return (
    <Section>
      <PageHead
        title="Статистика остатки долгов и замены"
        subtitle="Столбцы M–AB, фильтрация по партнёру как в исходном Streamlit"
        actions={
          <>
            <ExportButton
              path="/api/export/statistics"
              token={token}
              label="Скачать статистику"
            />
            <button className="btn secondary" onClick={reload}>
              <RefreshCw size={16} />
              Обновить
            </button>
          </>
        }
      />
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        meta={meta}
        showDate={false}
      />
      {loading ? (
        <Spinner />
      ) : (
        <>
          <div className="kpi-grid">
            {(data?.metrics || []).slice(0, 8).map((m: any, i: number) => (
              <Kpi
                key={i}
                icon={["📊", "💰", "🔄", "📦", "🏷️", "📋", "🗂️", "🖨️"][i % 8]}
                value={m.total}
                label={m.name}
                sub={`${m.count} записей`}
                tone={["blue", "mint", "purple", "cyan"][i % 4]}
              />
            ))}
          </div>
          <div className="section-title">
            <span>📋</span>
            <b>Детальные данные M–AB</b>
            <em>{data?.count || 0} записей</em>
          </div>
          <GenericCards rows={data?.rows || []} columns={data?.columns || []} />
        </>
      )}
    </Section>
  );
}

function EquipmentChips({ chips }: any) {
  if (!chips || !chips.length) return <span className="muted">—</span>;
  return (
    <div className="chips">
      {chips.map((c: any, i: number) => (
        <span key={i} className={`chip ${c.type}`}>
          <b>{c.qty}</b>
          {c.label}
        </span>
      ))}
    </div>
  );
}

function SerialList({ serials }: any) {
  if (!serials || !serials.length)
    return <p className="muted">Серийные номера не указаны</p>;
  return (
    <div className="serials">
      {serials.map((s: any, i: number) => (
        <span key={i}>
          {s.tag ? <b>{s.tag}</b> : null}
          {s.serial}
        </span>
      ))}
    </div>
  );
}

function ShipmentList({ rows, token, compact = false }: any) {
  const [open, setOpen] = useState<string | null>(compact ? null : "");
  if (!rows?.length)
    return <div className="empty">📭 Нет отгрузок по выбранным фильтрам</div>;
  return (
    <div className="ship-list">
      {rows.map((r: any, i: number) => {
        const isOpen = open === r.row_id;
        return (
          <motion.div
            key={r.row_id || i}
            className={`ship-card glass ${isOpen ? "open" : ""}`}
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.018 }}
            whileHover={{ y: -3 }}
          >
            <button
              className="ship-main"
              onClick={() => setOpen(isOpen ? null : r.row_id)}
            >
              <div>
                <span className={`badge ${r.is_way ? "way" : "done"}`}>
                  {r.status_icon} {r.status}
                </span>
                <h3>
                  {r.date} · {r.city || "—"}
                </h3>
                <p>{r.client}</p>
                <EquipmentChips chips={r.equipment_chips} />
              </div>
              <div className="ship-side">
                <small>ID: {r.record_id || "—"}</small>
                <ChevronDown className={isOpen ? "rot" : ""} />
              </div>
            </button>
            <AnimatePresence>
              {isOpen && (
                <motion.div
                  className="ship-details"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                >
                  <div className="details-grid">
                    <div>
                      <h4>📝 Серийные номера</h4>
                      <SerialList serials={r.serials} />
                    </div>
                    <div>
                      <h4>📦 Оборудование</h4>
                      <p>{r.equipment || "—"}</p>
                      <div className="detail-actions">
                        {r.track?.toLowerCase().includes("http") ? (
                          <a
                            className="btn secondary"
                            href={r.track}
                            target="_blank"
                          >
                            🚀 Трек
                          </a>
                        ) : (
                          <button className="btn secondary" disabled>
                            Нет трека
                          </button>
                        )}
                        <a
                          className="btn secondary"
                          href={`${API_URL}/api/export/shipments/${r.row_id}?token=${encodeURIComponent(token)}`}
                          target="_blank"
                        >
                          <Download size={16} />
                          Excel
                        </a>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        );
      })}
    </div>
  );
}

function ShipmentsPage({
  token,
  filters,
  setFilters,
  meta,
  data,
  loading,
  reload,
}: any) {
  const qs = paramsFromFilters(filters);
  return (
    <Section>
      <PageHead
        title="Архив отгрузок"
        subtitle="Карточки открываются: серийные номера, трек и Excel по каждой отгрузке"
        actions={
          <>
            <a
              className="btn secondary"
              target="_blank"
              href={`${API_URL}/api/export/shipments?token=${encodeURIComponent(token)}&${qs}`}
            >
              <FileSpreadsheet size={16} />
              Скачать отгрузки
            </a>
            <button className="btn secondary" onClick={reload}>
              <RefreshCw size={16} />
              Обновить
            </button>
          </>
        }
      />
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        meta={meta}
        showDate
      />
      {loading ? (
        <Spinner />
      ) : (
        <>
          <div className="section-title">
            <span>📑</span>
            <b>Архив отгрузок</b>
            <em>{data?.count || 0} записей · новые сверху</em>
          </div>
          <ShipmentList rows={data?.rows || []} token={token} />
        </>
      )}
    </Section>
  );
}

function MovementList({ rows, token, compact = false }: any) {
  const [open, setOpen] = useState<string | null>(null);
  if (!rows?.length) return <div className="empty">📭 Нет перемещений</div>;
  return (
    <div className="move-list">
      {rows.map((r: any, i: number) => {
        const isOpen = open === r.row_id;
        return (
          <motion.div
            className="move-card glass"
            key={r.row_id || i}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.02 }}
          >
            <button
              className="move-main"
              onClick={() => setOpen(isOpen ? null : r.row_id)}
            >
              <div className="move-route">
                <div>
                  <label>📤 Откуда</label>
                  <h3>{r.city_from || "—"}</h3>
                  <p>{r.org_from || "—"}</p>
                </div>
                <span>→</span>
                <div>
                  <label>📥 Куда</label>
                  <h3>{r.city_to || "—"}</h3>
                  <p>{r.org_to || "—"}</p>
                </div>
              </div>
              <div className="ship-side">
                <small>📅 {r.date}</small>
                <ChevronDown className={isOpen ? "rot" : ""} />
              </div>
            </button>
            <AnimatePresence>
              {isOpen && (
                <motion.div
                  className="ship-details"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                >
                  <div className="details-grid">
                    <div>
                      <h4>📦 Оборудование</h4>
                      <div className="chips">
                        <span className="chip kkt">
                          <b>{r.kkt || 0}</b>ККТ
                        </span>
                        <span className="chip fn15">
                          <b>{r.fn15 || 0}</b>ФН-15
                        </span>
                        <span className="chip fn36">
                          <b>{r.fn36 || 0}</b>ФН-36
                        </span>
                      </div>
                      <p>{r.comment}</p>
                    </div>
                    <div>
                      <h4>📝 Серийные номера</h4>
                      <SerialList serials={r.serials} />
                      <div className="detail-actions">
                        {r.track?.toLowerCase().includes("http") ? (
                          <a
                            className="btn secondary"
                            href={r.track}
                            target="_blank"
                          >
                            🚀 Трек
                          </a>
                        ) : null}
                        <a
                          className="btn secondary"
                          href={`${API_URL}/api/export/movements/${r.row_id}?token=${encodeURIComponent(token)}`}
                          target="_blank"
                        >
                          <Download size={16} />
                          Excel
                        </a>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        );
      })}
    </div>
  );
}

function MovementsPage({
  token,
  filters,
  setFilters,
  meta,
  data,
  loading,
  reload,
}: any) {
  const qs = paramsFromFilters(filters);
  return (
    <Section>
      <PageHead
        title="Возврат / Перемещение"
        subtitle="Маршрут, оборудование, серийники и трек по каждой записи"
        actions={
          <>
            <a
              className="btn secondary"
              target="_blank"
              href={`${API_URL}/api/export/movements?token=${encodeURIComponent(token)}&${qs}`}
            >
              <FileSpreadsheet size={16} />
              Скачать все
            </a>
            <button className="btn secondary" onClick={reload}>
              <RefreshCw size={16} />
              Обновить
            </button>
          </>
        }
      />
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        meta={meta}
        showDate
      />
      {loading ? (
        <Spinner />
      ) : (
        <>
          <div className="section-title">
            <span>🔄</span>
            <b>Возврат / Перемещение</b>
            <em>{data?.count || 0} записей · новые сверху</em>
          </div>
          <MovementList rows={data?.rows || []} token={token} />
        </>
      )}
    </Section>
  );
}

function NewsPage({ data, loading, reload }: any) {
  if (loading) return <Spinner />;
  const s = data?.stats || {};
  return (
    <Section>
      <PageHead
        title="Лента новостей"
        subtitle="Автоматические новости из отгрузок и перемещений"
        actions={
          <button className="btn secondary" onClick={reload}>
            <RefreshCw size={16} />
            Обновить
          </button>
        }
      />
      <div className="news-page">
        {(data?.items || []).map((n: any, i: number) => (
          <motion.div
            key={i}
            className={`news-card glass ${n.type}`}
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <div className="news-icon">{n.icon}</div>
            <div>
              <div>
                {n.today ? <span className="new-pill">🆕 сегодня</span> : null}
              </div>
              <h3>{n.title}</h3>
              <p>{n.text}</p>
            </div>
          </motion.div>
        ))}
      </div>
      <div className="kpi-grid">
        <Kpi
          icon="🚚"
          value={s.today_shipments || 0}
          label="Сегодня"
          sub="отправок"
        />
        <Kpi
          icon="📅"
          value={s.week_shipments || 0}
          label="Неделя"
          sub="отправок"
          tone="cyan"
        />
        <Kpi
          icon="🔄"
          value={s.today_movements || 0}
          label="Перемещ."
          sub="сегодня"
          tone="purple"
        />
        <Kpi
          icon="📍"
          value={s.in_way || 0}
          label="В пути"
          sub="сейчас"
          tone="mint"
        />
      </div>
    </Section>
  );
}

function AnalyticsPage({ data, loading }: any) {
  if (loading) return <Spinner />;
  return (
    <Section>
      <PageHead
        title="Админ аналитика"
        subtitle="Кто заходит, активность страниц и организаций"
      />
      <div className="kpi-grid two">
        <Kpi
          icon="👥"
          value={data?.online_users || 0}
          label="Онлайн"
          sub="пользователей"
        />
        <Kpi
          icon="🏢"
          value={data?.active_organizations || 0}
          label="Организации"
          sub="активные"
          tone="mint"
        />
      </div>
      <div className="two-cols">
        <div className="glass card">
          <h3>Последние входы</h3>
          <Table rows={data?.login_events || []} />
        </div>
        <div className="glass card">
          <h3>Посещённые страницы</h3>
          <Table rows={data?.page_events || []} />
        </div>
      </div>
      <div className="two-cols admin-extra">
        <div className="glass card">
          <h3>Пользователи и доступ</h3>
          <Table rows={data?.users_access || []} />
        </div>
        <div className="glass card">
          <h3>Админ инструменты</h3>
          <div className="admin-tool-list">
            {(data?.admin_tools || []).map((x: any, i: number) => (
              <div key={i}><span>{x.name}</span><b>{x.status}</b></div>
            ))}
          </div>
        </div>
      </div>
    </Section>
  );
}

function Table({ rows }: any) {
  if (!rows?.length) return <div className="empty">Нет данных</div>;
  const cols = Object.keys(rows[0]).filter((c) => c !== "token");
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            {cols.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r: any, i: number) => (
            <tr key={i}>
              {cols.map((c) => (
                <td key={c}>{String(r[c] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function OrgAccessCard({ user, dashboard, mobile = false }: any) {
  const isAdmin = user?.filter === "all";
  const currentOrg = isAdmin ? "Все организации" : user?.filter || user?.name || "—";
  const k = dashboard?.kpis || {};
  const quick = [
    { label: "Остатки", value: k.total_stock ?? k.kkt ?? 0 },
    { label: "В пути", value: k.in_way ?? 0 },
    { label: "Событий", value: (k.shipments_today ?? 0) + (k.movements ?? 0) },
  ];
  return (
    <div className={`org-card-v5 glass ${mobile ? "mobile" : ""}`}>
      <div className="org-card-shine" />
      <div className="org-card-top">
        <div className="org-avatar-v5">{isAdmin ? "A" : "LP"}</div>
        <div>
          <b>{user?.name || "Пользователь"}</b>
          <span>{user?.role || "USER"}</span>
        </div>
      </div>
      <div className="org-status-row">
        <span className="online-dot" /> <em>Онлайн</em>
        {isAdmin ? <i>Полный доступ</i> : null}
      </div>
      <div className="org-current">
        <small>Текущая организация</small>
        <strong>{currentOrg}</strong>
      </div>
      <div className="org-quick-grid">
        {quick.map((x) => (
          <div key={x.label}>
            <b>{x.value}</b>
            <span>{x.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MobileMenu({ open, setOpen, page, setPage, logout, user }: any) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="mobile-dim"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setOpen(false)}
          />
          <motion.div
            className="mobile-menu glass-xl"
            initial={{ opacity: 0, y: 80, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 60, scale: 0.96 }}
            transition={{ type: "spring", stiffness: 260, damping: 25 }}
          >
            <div className="mobile-menu-head">
              <LifePayLogo compact />
              <button className="icon-btn" onClick={() => setOpen(false)}>
                <X size={18} />
              </button>
            </div>
            <OrgAccessCard user={user} mobile />
            <div className="mobile-menu-grid">
              {nav.map(([id, label, Icon]) => (
                <button
                  key={id}
                  onClick={() => {
                    setPage(id);
                    setOpen(false);
                  }}
                  className={page === id ? "active" : ""}
                >
                  <Icon size={19} />
                  <span>{label}</span>
                </button>
              ))}
            </div>
            <button className="logout mobile-logout" onClick={logout}>
              <LogOut size={16} /> Выйти
            </button>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

function MobileBottomNav({ page, setPage, setOpen }: any) {
  const items = nav.filter(([id]) =>
    ["dashboard", "stock", "shipments", "movements"].includes(id as string),
  );
  return (
    <div className="mobile-bottom-wrap">
      <div className="mobile-bottom glass-xl">
        {items.map(([id, label, Icon]) => (
          <button
            key={id}
            onClick={() => setPage(id)}
            className={page === id ? "active" : ""}
          >
            <Icon size={18} />
            <span>{label.split(" ")[0]}</span>
          </button>
        ))}
        <button onClick={() => setOpen(true)}>
          <Menu size={19} />
          <span>Меню</span>
        </button>
      </div>
    </div>
  );
}

function SkeletonCards({ count = 4 }: any) {
  return (
    <div className="skeleton-grid">
      {Array.from({ length: count }).map((_, i) => (
        <div className="skeleton-card glass" key={i}>
          <i />
          <b />
          <span />
        </div>
      ))}
    </div>
  );
}

function SettingsPage({ theme, setTheme, sound, setSound, visualTheme, setVisualTheme, soundPreset, setSoundPreset, playSound }: any) {
  const themeOptions = [
    { id: "light", label: "Светлая", icon: Sun, desc: "чистый бело-синий интерфейс" },
    { id: "dark", label: "Тёмная", icon: Moon, desc: "глубокий navy + glow" },
    { id: "system", label: "Системная", icon: Monitor, desc: "автоматически по телефону/браузеру" },
  ];
  const styleOptions = [
    { id: "neo", label: "Neo‑Tactile", desc: "основной: глубина, мягкие тени, стекло" },
    { id: "life", label: "Life Pay", desc: "синий + cyan, корпоративно" },
    { id: "aurora", label: "Aurora", desc: "purple glow + премиум" },
    { id: "mint", label: "Mint Glass", desc: "зелёный mint + cyan" },
    { id: "graphite", label: "Graphite", desc: "строгий dark ERP" },
    { id: "ocean", label: "Ocean Glass", desc: "светлый blue glass" },
  ];
  const soundOptions = [
    { id: "crystal", label: "Crystal", desc: "чистый стеклянный сигнал" },
    { id: "soft", label: "Soft Bell", desc: "мягкий офисный звук" },
    { id: "neo", label: "Neo Pulse", desc: "технологичный короткий pulse" },
    { id: "success", label: "Success", desc: "приятный звук успеха" },
    { id: "alert", label: "Alert", desc: "для ошибок и проверок" },
    { id: "minimal", label: "Minimal", desc: "очень короткий click" },
  ];
  return (
    <Section>
      <PageHead
        title="Настройки"
        subtitle="Темы, Neo‑Tactile Liquid Glass и звуки уведомлений LIFE PAY"
      />
      <div className="settings-grid pro v5-settings">
        <div className="setting glass settings-wide">
          <div className="setting-title"><Palette size={20}/><div><h3>Тема интерфейса</h3><p>System автоматически переключается по теме телефона или браузера.</p></div></div>
          <div className="theme-picker">
            {themeOptions.map(({ id, label, icon: Icon, desc }: any) => (
              <button
                key={id}
                onClick={() => setTheme(id)}
                className={theme === id ? "active" : ""}
              >
                <Icon size={18}/>
                <b>{label}</b>
                <span>{desc}</span>
              </button>
            ))}
          </div>
        </div>
        <div className="setting glass settings-wide">
          <div className="setting-title"><Sparkles size={20}/><div><h3>Визуальный стиль</h3><p>Добавлен основной стиль Neo‑Tactile как в твоём референсе.</p></div></div>
          <div className="theme-picker visual v5-visual">
            {styleOptions.map((x: any) => (
              <button key={x.id} onClick={() => setVisualTheme(x.id)} className={visualTheme === x.id ? "active" : ""}>
                <i className={`style-dot ${x.id}`}/>
                <b>{x.label}</b>
                <span>{x.desc}</span>
              </button>
            ))}
          </div>
        </div>
        <div className="setting glass settings-wide sound-card">
          <div className="setting-title"><Bell size={20}/><div><h3>Звук уведомлений</h3><p>Выбор звука для входа, отгрузок, перемещений, новостей и ошибок.</p></div></div>
          <div className="toggle pill-toggle">
            <button className={sound ? "active" : ""} onClick={() => setSound(true)}><Volume2 size={16} /> Включить</button>
            <button className={!sound ? "active" : ""} onClick={() => setSound(false)}><VolumeX size={16} /> Выключить</button>
          </div>
          <div className="sound-choice-grid">
            {soundOptions.map((x: any) => (
              <button key={x.id} className={soundPreset === x.id ? "active" : ""} onClick={() => { setSoundPreset(x.id); setSound(true); setTimeout(() => playSound?.("ok"), 10); }}>
                <Radio size={16}/><b>{x.label}</b><span>{x.desc}</span>
              </button>
            ))}
          </div>
          <button className="btn secondary test-sound" onClick={() => playSound?.("shipment")}><Play size={16}/> Проверить звук</button>
        </div>
        <div className="setting glass settings-wide">
          <div className="setting-title"><Smartphone size={20}/><div><h3>Мобильный интерфейс</h3><p>Компактное меню, нижняя навигация, скролл таблиц и более аккуратные карточки.</p></div></div>
          <div className="mobile-feature-row"><span>Liquid Glass cards</span><b>ON</b></div>
          <div className="mobile-feature-row"><span>Bottom navigation</span><b>ON</b></div>
          <div className="mobile-feature-row"><span>Neo‑Tactile motion</span><b>ON</b></div>
        </div>
      </div>
    </Section>
  );
}


export default function Page() {
  const [token, setToken] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [theme, setTheme] = useState<ThemeMode>("system");
  const [visualTheme, setVisualTheme] = useState<VisualTheme>("neo");
  const [sound, setSound] = useState(true);
  const [soundPreset, setSoundPreset] = useState<SoundPreset>("crystal");
  const [page, setPage] = useState("dashboard");
  const [filters, setFilters] = useState<FilterState>({
    search: "",
    org: "Все",
    city: "Все",
    date_mode: "Весь период",
    date_from: new Date().toISOString().slice(0, 10),
    date_to: new Date().toISOString().slice(0, 10),
  });
  const [meta, setMeta] = useState<Filters | null>(null);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [reloadId, setReloadId] = useState(0);
  const [menuOpen, setMenuOpen] = useState(false);
  const play = useSound(sound, soundPreset);

  useEffect(() => {
    const t = localStorage.getItem("lp_token");
    const u = localStorage.getItem("lp_user");
    const th = localStorage.getItem("lp_theme") as ThemeMode | null;
    const vt = localStorage.getItem("lp_visual_theme") as VisualTheme | null;
    const sp = localStorage.getItem("lp_sound_preset") as SoundPreset | null;
    if (th) setTheme(th);
    if (vt) setVisualTheme(vt);
    if (sp) setSoundPreset(sp);
    if (t && u) {
      setToken(t);
      setUser(JSON.parse(u));
    }
  }, []);
  useEffect(() => {
    if (typeof window === "undefined") return;
    const root = document.documentElement;
    const apply = () => {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      const effective = theme === "system" ? (prefersDark ? "dark" : "light") : theme;
      root.classList.remove("light", "dark", "skin-life", "skin-aurora", "skin-mint", "skin-graphite", "skin-neo", "skin-ocean");
      root.classList.add(effective, `skin-${visualTheme}`);
      root.dataset.theme = effective;
      root.dataset.themeMode = theme;
      root.dataset.visual = visualTheme;
      document.body.className = `${effective} skin-${visualTheme}`;
    };
    apply();
    localStorage.setItem("lp_theme", theme);
    localStorage.setItem("lp_visual_theme", visualTheme);
    localStorage.setItem("lp_sound_preset", soundPreset);
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = () => apply();
    media.addEventListener?.("change", listener);
    return () => media.removeEventListener?.("change", listener);
  }, [theme, visualTheme, soundPreset]);
  useEffect(() => {
    if (!token) return;
    apiFetch("/api/filters", token)
      .then(setMeta)
      .catch(() => {});
  }, [token]);
  useEffect(() => {
    if (!token) return;
    setLoading(true);
    const q = paramsFromFilters(filters);
    const paths: any = {
      dashboard: "/api/dashboard",
      stock: `/api/stock?${q}`,
      debts: `/api/debts?${q}`,
      statistics: `/api/statistics?${q}`,
      shipments: `/api/shipments?${q}`,
      movements: `/api/movements?${q}`,
      news: "/api/news",
      analytics: "/api/admin/analytics",
    };
    apiFetch(paths[page] || "/api/dashboard", token)
      .then((d) => {
        setData(d);
        if (page === "shipments") play("shipment");
        if (page === "movements") play("movement");
        if (page === "news") play("news");
      })
      .catch((e) => setData({ error: e.message }))
      .finally(() => setLoading(false));
    apiFetch("/api/track", token, {
      method: "POST",
      body: JSON.stringify({ page }),
    }).catch(() => {});
  }, [token, page, filters, reloadId]);

  function onLogin(t: string, u: User) {
    setToken(t);
    setUser(u);
    localStorage.setItem("lp_token", t);
    localStorage.setItem("lp_user", JSON.stringify(u));
  }
  function logout() {
    localStorage.removeItem("lp_token");
    localStorage.removeItem("lp_user");
    setToken("");
    setUser(null);
  }
  const reload = () => setReloadId((x) => x + 1);
  const cycleTheme = () => setTheme((t) => (t === "light" ? "dark" : t === "dark" ? "system" : "light"));

  if (!token || !user)
    return (
      <Login
        onLogin={onLogin}
        theme={theme}
        setTheme={setTheme}
        sound={sound}
        soundPreset={soundPreset}
      />
    );

  return (
    <div className="app-shell">
      <AnimatedBackdrop />
      <aside className="sidebar glass-xl">
        <LifePayLogo compact />
        <OrgAccessCard user={user} dashboard={data} />
        <nav>
          {nav.map(([id, label, Icon]) => (
            <button
              key={id}
              onClick={() => setPage(id)}
              className={page === id ? "active" : ""}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </nav>
        <button className="logout" onClick={logout}>
          <LogOut size={16} /> Выйти
        </button>
      </aside>
      <main className="main">
        <div className="topbar glass">
          <div className="mobile-brand">
            <LifePayLogo compact />
          </div>
          <div className="top-title">
            <Sparkles size={18} />
            <span>{pageNames[page]}</span>
          </div>
          <div className="top-actions">
            <button
              onClick={() => setMenuOpen(true)}
              className="icon-btn mobile-menu-btn"
            >
              <Menu size={18} />
            </button>
            <button onClick={() => setSound(!sound)} className="icon-btn">
              {sound ? <Volume2 size={18} /> : <VolumeX size={18} />}
            </button>
            <button onClick={cycleTheme} className="icon-btn" title={`Тема: ${theme}`}>
              {theme === "system" ? <Monitor size={18} /> : theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button onClick={reload} className="icon-btn">
              <RefreshCw size={18} />
            </button>
          </div>
        </div>
        {data?.error ? <div className="error big">{data.error}</div> : null}
        <AnimatePresence mode="wait">
          <motion.div
            key={page}
            initial={{ opacity: 0, y: 16, filter: "blur(5px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0)" }}
            exit={{ opacity: 0, y: -10, filter: "blur(4px)" }}
            transition={{ duration: 0.28 }}
          >
            {page === "dashboard" && (
              <Dashboard token={token} data={data} reload={reload} />
            )}{" "}
            {page === "stock" && (
              <StockPage
                token={token}
                filters={filters}
                setFilters={setFilters}
                meta={meta}
                data={data}
                loading={loading}
                reload={reload}
              />
            )}{" "}
            {page === "debts" && (
              <DebtsPage
                token={token}
                filters={filters}
                setFilters={setFilters}
                meta={meta}
                data={data}
                loading={loading}
                reload={reload}
              />
            )}{" "}
            {page === "statistics" && (
              <StatisticsPage
                token={token}
                filters={filters}
                setFilters={setFilters}
                meta={meta}
                data={data}
                loading={loading}
                reload={reload}
              />
            )}{" "}
            {page === "shipments" && (
              <ShipmentsPage
                token={token}
                filters={filters}
                setFilters={setFilters}
                meta={meta}
                data={data}
                loading={loading}
                reload={reload}
              />
            )}{" "}
            {page === "movements" && (
              <MovementsPage
                token={token}
                filters={filters}
                setFilters={setFilters}
                meta={meta}
                data={data}
                loading={loading}
                reload={reload}
              />
            )}{" "}
            {page === "news" && (
              <NewsPage data={data} loading={loading} reload={reload} />
            )}{" "}
            {page === "analytics" && (
              <AnalyticsPage data={data} loading={loading} />
            )}{" "}
            {page === "settings" && (
              <SettingsPage
                theme={theme}
                setTheme={setTheme}
                sound={sound}
                setSound={setSound}
                visualTheme={visualTheme}
                setVisualTheme={setVisualTheme}
                soundPreset={soundPreset}
                setSoundPreset={setSoundPreset}
                playSound={play}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </main>
      <MobileBottomNav page={page} setPage={setPage} setOpen={setMenuOpen} />
      <MobileMenu
        open={menuOpen}
        setOpen={setMenuOpen}
        page={page}
        setPage={setPage}
        logout={logout}
        user={user}
      />
    </div>
  );
}
