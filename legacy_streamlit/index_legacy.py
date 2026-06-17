import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import re
import json
import time
import logging
from datetime import datetime, date, timedelta
logger = logging.getLogger(__name__)
st.set_page_config(
    layout="wide",
    page_title="LIFE PAY",
    page_icon="🔵",
    initial_sidebar_state="expanded"
)
# ══════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════
def login_system():
    USERS = {
        "1121018100": ("АТМ АЛЬЯНС",    "АТМ"),
        "7734595315": ("Коритек",        "АРЕС-КОМПАНИ-М"),
        "5321203280": ("ООО БР",         "БР"),
        "9718146933": ("АБ",             "Автоматизация Бизнеса"),
        "061219966":  ("АДМИНИСТРАТОР",  "all"),
        "999999":     ("SUPER ADMIN",    "all"),
    }
    if "auth" not in st.session_state:
        st.session_state.auth         = False
        st.session_state.user         = ""
        st.session_state.filter       = "all"
        st.session_state.seen_ids     = set()
        st.session_state.last_refresh = time.time()
        st.session_state.range_from   = None
        st.session_state.range_to     = None
    if st.session_state.auth:
        return True, st.session_state.user, st.session_state.filter
    st.markdown("""
    <style>
        [data-testid="stSidebar"]      { display:none !important; }
        [data-testid="stHeader"]       { visibility:hidden; display:none; }
        #MainMenu                      { visibility:hidden; }
        footer                         { visibility:hidden; }
        [data-testid="stStatusWidget"] { visibility:hidden; display:none; }
        .stDeployButton                { display:none; }
        .stActionButton                { visibility:hidden; display:none; }
        .block-container {
            padding:0 !important;
            max-width:100% !important;
            margin-top:0 !important;
        }
        [data-testid="stDecoration"]   { display:none; }
    </style>""", unsafe_allow_html=True)
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;700;800&display=swap');
        _,_ ::before, *::after {
            font-family: 'Manrope', sans-serif;
            box-sizing: border-box;
            margin: 0; padding: 0;
        }
        .stApp {
            background:
                radial-gradient(ellipse at 10% 15%, rgba(0,82,255,0.22) 0%, transparent 46%),
                radial-gradient(ellipse at 90% 10%, rgba(6,182,212,0.20) 0%, transparent 44%),
                radial-gradient(ellipse at 55% 92%, rgba(99,102,241,0.18) 0%, transparent 48%),
                linear-gradient(148deg, #EBF3FF 0%, #EFF7FF 30%, #EAF0FF 60%, #EDF6FF 100%) !important;
            min-height: 100vh; overflow: hidden;
        }
        .block-container { padding:0 !important; max-width:100% !important; }
        .gl-bg { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
        .gl-orb { position: absolute; border-radius: 50%; filter: blur(80px); }
        .gl-orb-1 {
            width:640px; height:640px; top:-200px; left:-180px;
            background: radial-gradient(circle, rgba(0,82,255,0.22) 0%, rgba(6,182,212,0.12) 50%, transparent 70%);
            animation: go1 24s ease-in-out infinite;
        }
        .gl-orb-2 {
            width:520px; height:520px; top:40%; right:-160px;
            background: radial-gradient(circle, rgba(6,182,212,0.20) 0%, rgba(99,102,241,0.10) 50%, transparent 70%);
            animation: go2 30s ease-in-out infinite;
        }
        .gl-orb-3 {
            width:480px; height:480px; bottom:-160px; left:30%;
            background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, rgba(0,82,255,0.08) 50%, transparent 70%);
            animation: go3 26s ease-in-out infinite 5s;
        }
        .gl-shine {
            width:360px; height:360px; top:12%; left:28%;
            background: radial-gradient(circle, rgba(255,255,255,0.65) 0%, rgba(255,255,255,0.20) 45%, transparent 70%);
            filter: blur(50px); animation: go2 18s ease-in-out infinite 2s;
        }
        @keyframes go1 {
            0%,100% { transform: translate(0,0) scale(1); }
            30%     { transform: translate(36px,-52px) scale(1.07); }
            60%     { transform: translate(-24px,34px) scale(0.94); }
            80%     { transform: translate(20px,44px) scale(1.04); }
        }
        @keyframes go2 {
            0%,100% { transform: translate(0,0) scale(1); }
            35%     { transform: translate(-40px,48px) scale(1.08); }
            68%     { transform: translate(28px,-28px) scale(0.95); }
        }
        @keyframes go3 {
            0%,100% { transform: translate(0,0) scale(1) rotate(0deg); }
            45%     { transform: translate(44px,-42px) scale(1.06) rotate(-3deg); }
            72%     { transform: translate(-28px,30px) scale(0.96) rotate(2deg); }
        }
        .gl-card {
            width: 100%; max-width: 390px;
            background: linear-gradient(148deg, rgba(255,255,255,0.84) 0%, rgba(230,244,255,0.72) 50%, rgba(234,240,255,0.76) 100%);
            backdrop-filter: blur(52px) saturate(200%) brightness(1.05);
            -webkit-backdrop-filter: blur(52px) saturate(200%) brightness(1.05);
            border-radius: 32px; overflow: hidden;
            border-top: 1.5px solid rgba(255,255,255,0.96);
            border-left: 1px solid rgba(255,255,255,0.88);
            border-right: 1px solid rgba(255,255,255,0.60);
            border-bottom: 1px solid rgba(255,255,255,0.54);
            box-shadow: 0 48px 100px rgba(0,82,255,0.16), 0 18px 44px rgba(0,82,255,0.10), inset 0 1.5px 0 rgba(255,255,255,1);
            position: relative; z-index: 1;
            animation: cardIn 0.78s cubic-bezier(0.22,1,0.36,1) both;
        }
        @keyframes cardIn {
            from { opacity:0; transform:translateY(44px) scale(0.93); filter:blur(6px); }
            to   { opacity:1; transform:translateY(0) scale(1); filter:blur(0); }
        }
        .gl-card::before {
            content:""; position:absolute; top:0; left:0; right:0; height:46%;
            background: linear-gradient(180deg, rgba(255,255,255,0.58) 0%, rgba(255,255,255,0.04) 100%);
            border-radius:32px 32px 0 0; pointer-events:none;
        }
        .gl-card::after {
            content:""; position:absolute; bottom:-35px; right:-35px;
            width:180px; height:180px; border-radius:50%;
            background: radial-gradient(circle, rgba(6,182,212,0.14) 0%, transparent 70%);
            pointer-events:none;
        }
        .gl-head { padding:32px 36px 26px; position:relative; z-index:1; }
        .gl-logo-row { display:flex; align-items:center; gap:13px; margin-bottom:20px; }
        .gl-logo-box {
            width:54px; height:54px; border-radius:18px; flex-shrink:0;
            background: linear-gradient(135deg, #0052FF 0%, #0080FF 48%, #06B6D4 100%);
            display:flex; align-items:center; justify-content:center; font-size:24px;
            box-shadow: 0 14px 36px rgba(0,82,255,0.34), inset 0 1px 0 rgba(255,255,255,0.28);
        }
        .gl-logo-name {
            font-size:30px; font-weight:800; letter-spacing:-2px; line-height:1;
            background: linear-gradient(135deg, #0042CC 0%, #0066FF 48%, #06B6D4 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        }
        .gl-logo-sub { font-size:10px; font-weight:700; color:#94A3B8; letter-spacing:1.8px; text-transform:uppercase; margin-top:2px; }
        .gl-sep {
            height:1px; margin-bottom:20px;
            background: linear-gradient(90deg, transparent, rgba(0,82,255,0.18) 30%, rgba(6,182,212,0.14) 70%, transparent);
        }
        .gl-title { font-size:20px; font-weight:800; color:#0F172A; letter-spacing:-0.5px; margin-bottom:4px; }
        .gl-sub   { font-size:12px; font-weight:500; color:#64748B; }
        .gl-body  { padding:0 36px 26px; position:relative; z-index:1; }
        .pin-label {
            font-size:10px; font-weight:800; color:#0052FF;
            text-transform:uppercase; letter-spacing:1px;
            margin:18px 0 8px; display:flex; align-items:center; gap:5px;
        }
        .stTextInput > label { display:none !important; }
        .stTextInput input {
            background: linear-gradient(148deg, rgba(255,255,255,0.94) 0%, rgba(238,247,255,0.88) 100%) !important;
            border: 1.5px solid rgba(0,82,255,0.15) !important;
            border-radius:16px !important;
            font-size:22px !important; font-weight:800 !important;
            text-align:center !important; letter-spacing:7px !important;
            color:#0F172A !important; padding:13px 16px !important;
            height:58px !important;
            box-shadow: 0 6px 20px rgba(0,82,255,0.08), inset 0 1.5px 0 rgba(255,255,255,1) !important;
            transition: all 0.32s cubic-bezier(0.22,1,0.36,1) !important;
        }
        .stTextInput input::placeholder { color: rgba(148,163,184,0.50) !important; letter-spacing:5px; font-size:18px !important; }
        .stTextInput input:focus {
            border-color: rgba(0,82,255,0.46) !important;
            background: rgba(255,255,255,1) !important;
            box-shadow: 0 0 0 5px rgba(0,82,255,0.10), inset 0 1.5px 0 rgba(255,255,255,1) !important;
            transform: scale(1.01);
        }
        .stButton > button {
            background: linear-gradient(135deg, #0042CC 0%, #0061FF 40%, #0099EE 70%, #06B6D4 100%) !important;
            color:white !important; border:none !important;
            border-radius:16px !important; height:52px !important;
            font-weight:800 !important; font-size:14px !important;
            width:100% !important; letter-spacing:1px; text-transform:uppercase;
            box-shadow: 0 16px 44px rgba(0,82,255,0.28), inset 0 1px 0 rgba(255,255,255,0.26) !important;
            margin-top:12px;
            transition: all 0.30s cubic-bezier(0.22,1,0.36,1) !important;
        }
        .stButton > button:hover  { transform:translateY(-3px) scale(1.01) !important; }
        .stButton > button:active { transform:scale(0.98) !important; }
        .stAlert {
            border-radius:14px !important;
            border:1px solid rgba(255,255,255,0.70) !important;
            backdrop-filter:blur(14px) !important;
            font-size:13px !important; margin-top:10px;
        }
    </style>
    <div class="gl-bg">
        <div class="gl-orb gl-orb-1"></div>
        <div class="gl-orb gl-orb-2"></div>
        <div class="gl-orb gl-orb-3"></div>
        <div class="gl-orb gl-shine"></div>
    </div>""", unsafe_allow_html=True)
    _, col,_ = st.columns([1, 1.35, 1])
    with col:
        st.markdown("""
        <div class="gl-card">
          <div class="gl-head">
            <div class="gl-logo-row">
              <div class="gl-logo-box">💳</div>
              <div>
                <div class="gl-logo-name">LIFE PAY</div>
                <div class="gl-logo-sub">Enterprise ERP</div>
              </div>
            </div>
            <div class="gl-sep"></div>
            <div class="gl-title">Добро пожаловать 👋</div>
            <div class="gl-sub">Введите PIN-код для входа в систему</div>
          </div>
          <div class="gl-body">""", unsafe_allow_html=True)
        st.markdown('<div class="pin-label">🔐 PIN-код</div>', unsafe_allow_html=True)
        pin = st.text_input(
            "pin", type="password", placeholder="• • • • •",
            max_chars=10, label_visibility="collapsed"
        )
        if st.button("ВОЙТИ В СИСТЕМУ →", use_container_width=True):
            if pin in USERS:
                st.session_state.auth         = True
                st.session_state.user         = USERS[pin][0]
                st.session_state.filter       = USERS[pin][1]
                st.session_state.seen_ids     = set()
                st.session_state.last_refresh = time.time()
                st.session_state.range_from   = None
                st.session_state.range_to     = None
                st.rerun()
            else:
                st.error("❌ Неверный PIN-код")
        st.markdown("</div></div>", unsafe_allow_html=True)
    return False, "", ""
# ══════════════════════════════════════════════════════════════
# ТОЧКА ВХОДА
# ══════════════════════════════════════════════════════════════
is_auth, user_login, user_filter = login_system()
if not is_auth:
    st.stop()
# ══════════════════════════════════════════════════════════════
# ОСНОВНОЕ ПРИЛОЖЕНИЕ
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    [data-testid="stHeader"]       { visibility:hidden; display:none; }
    #MainMenu                      { visibility:hidden; }
    footer                         { visibility:hidden; }
    [data-testid="stStatusWidget"] { visibility:hidden; display:none; }
    .stDeployButton                { display:none; }
    .stActionButton                { visibility:hidden; display:none; }
    [data-testid="stDecoration"]   { display:none; }
    .block-container { padding-top:1rem !important; padding-bottom:3rem; }
    [data-testid="stSidebar"] { display:flex !important; visibility:visible !important; opacity:1 !important; }
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            display:flex !important; position:fixed !important;
            z-index:9990 !important; min-width:280px !important;
            width:85vw !important; max-width:340px !important;
        }
        [data-testid="stSidebarCollapsedControl"] {
            display:flex !important; position:fixed !important;
            top:12px !important; left:12px !important;
            z-index:9991 !important;
            background:linear-gradient(135deg,#0042CC,#06B6D4) !important;
            border-radius:14px !important; width:44px !important; height:44px !important;
            box-shadow:0 8px 24px rgba(0,82,255,0.35) !important;
        }
        [data-testid="stSidebarCollapsedControl"] svg { fill:white !important; color:white !important; }
        .block-container { padding-left:8px !important; padding-right:8px !important; }
    }
    @media (min-width: 769px) {
        [data-testid="stSidebarCollapsedControl"] { display:none !important; }
    }
</style>""", unsafe_allow_html=True)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
    * { font-family: 'Manrope', sans-serif; }
    .stApp {
        background:
            radial-gradient(circle at 8% 12%, rgba(0,82,255,0.13), transparent 30%),
            radial-gradient(circle at 88% 10%, rgba(6,182,212,0.14), transparent 32%),
            radial-gradient(circle at 55% 92%, rgba(99,102,241,0.10), transparent 34%),
            linear-gradient(145deg, #F6F9FF 0%, #EEF4FF 45%, #F4F6FF 100%) !important;
        color: #0F172A;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, rgba(255,255,255,0.82) 0%, rgba(228,242,255,0.70) 50%, rgba(232,238,255,0.74) 100%) !important;
        backdrop-filter: blur(40px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(200%) !important;
        border-right: 1.5px solid rgba(255,255,255,0.90) !important;
        box-shadow: 12px 0 52px rgba(0,82,255,0.10) !important;
    }
    [data-testid="stSidebar"] > div { background:transparent !important; }
    .sb-brand-card {
        position:relative;
        background: linear-gradient(135deg, #0042CC 0%, #0061FF 40%, #0099EE 72%, #06B6D4 100%);
        border-radius:24px; padding:22px 20px 18px; margin-bottom:16px; overflow:hidden;
        box-shadow: 0 20px 52px rgba(0,82,255,0.30), inset 0 1px 0 rgba(255,255,255,0.28);
    }
    .sb-brand-card::before {
        content:""; position:absolute; top:0; left:0; right:0; height:52%;
        background: linear-gradient(180deg, rgba(255,255,255,0.28) 0%, rgba(255,255,255,0.02) 100%);
        border-radius:24px 24px 0 0; pointer-events:none;
    }
    .sb-brand-card::after {
        content:""; position:absolute; bottom:-40px; right:-40px;
        width:160px; height:160px; border-radius:50%;
        background: radial-gradient(circle, rgba(255,255,255,0.16) 0%, transparent 70%);
        pointer-events:none;
    }
    .sb-brand-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; position:relative; z-index:1; }
    .sb-brand-name { font-size:26px; font-weight:800; letter-spacing:-1.8px; color:#FFFFFF; line-height:1; }
    .sb-brand-badge {
        background:rgba(255,255,255,0.20); border:1px solid rgba(255,255,255,0.36);
        border-radius:10px; padding:4px 10px; font-size:10px; font-weight:800;
        color:rgba(255,255,255,0.90); letter-spacing:1px; text-transform:uppercase;
    }
    .sb-brand-hr { height:1px; background:rgba(255,255,255,0.18); margin-bottom:14px; position:relative; z-index:1; }
    .sb-brand-user { display:flex; align-items:center; gap:11px; position:relative; z-index:1; }
    .sb-brand-avatar {
        width:42px; height:42px; border-radius:50%;
        background:rgba(255,255,255,0.22); border:2px solid rgba(255,255,255,0.42);
        display:flex; align-items:center; justify-content:center; font-size:19px; flex-shrink:0;
    }
    .sb-brand-uname { font-size:15px; font-weight:800; color:#FFFFFF; letter-spacing:-0.3px; line-height:1; }
    .sb-brand-role  { font-size:11px; font-weight:600; color:rgba(255,255,255,0.65); margin-top:3px; }
    .sb-brand-online { display:flex; align-items:center; gap:5px; margin-top:12px; position:relative; z-index:1; }
    .sb-online-dot {
        width:7px; height:7px; border-radius:50%; background:#34D399;
        animation: pulsedot 2.4s ease-in-out infinite;
    }
    @keyframes pulsedot {
        0%,100% { box-shadow:0 0 0 2px rgba(52,211,153,0.28); }
        50%     { box-shadow:0 0 0 5px rgba(52,211,153,0.14); }
    }
    .sb-online-text { font-size:11px; font-weight:700; color:rgba(255,255,255,0.65); }
    .sb-label {
        font-size:10px; font-weight:800; color:#0052FF; text-transform:uppercase;
        letter-spacing:0.9px; margin:16px 0 7px; display:flex; align-items:center; gap:5px;
    }
    div[data-baseweb="select"] > div {
        background: linear-gradient(145deg, rgba(255,255,255,0.84) 0%, rgba(228,242,255,0.70) 100%) !important;
        border: 1.5px solid rgba(255,255,255,0.92) !important;
        border-radius:16px !important; backdrop-filter:blur(20px);
    }
    .stTextInput input, .stNumberInput input, .stDateInput input, textarea {
        background: linear-gradient(145deg, rgba(255,255,255,0.86) 0%, rgba(228,242,255,0.72) 100%) !important;
        border: 1.5px solid rgba(255,255,255,0.92) !important;
        border-radius:14px !important; color:#0F172A !important; backdrop-filter:blur(16px);
    }
    .stTextInput input:focus, textarea:focus {
        border-color: rgba(0,82,255,0.40) !important;
        box-shadow: 0 0 0 4px rgba(0,82,255,0.10) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #0042CC 0%, #0061FF 42%, #0099EE 72%, #06B6D4 100%) !important;
        color:white !important; border:1px solid rgba(255,255,255,0.30) !important;
        border-radius:16px !important; font-weight:800 !important; font-size:13px !important;
        box-shadow: 0 14px 38px rgba(0,82,255,0.26), inset 0 1px 0 rgba(255,255,255,0.26) !important;
        transition: all 0.28s cubic-bezier(0.22,1,0.36,1) !important;
    }
    .stButton > button:hover  { transform:translateY(-2px) !important; }
    .stButton > button:active { transform:scale(0.98) !important; }
    .stDownloadButton > button {
        background: linear-gradient(145deg, rgba(255,255,255,0.82) 0%, rgba(228,242,255,0.67) 100%) !important;
        color:#0052FF !important;
        border-top: 1.5px solid rgba(255,255,255,0.96) !important;
        border-left: 1px solid rgba(255,255,255,0.88) !important;
        border-right: 1px solid rgba(255,255,255,0.60) !important;
        border-bottom: 1px solid rgba(0,82,255,0.14) !important;
        border-radius:16px !important; font-weight:800 !important; backdrop-filter:blur(18px);
        transition: all 0.28s cubic-bezier(0.22,1,0.36,1) !important;
    }
    .stDownloadButton > button:hover {
        background:rgba(255,255,255,0.94) !important; transform:translateY(-2px) !important;
    }
    .metric-box {
        background: linear-gradient(145deg, rgba(255,255,255,0.80) 0%, rgba(228,242,255,0.64) 52%, rgba(232,238,255,0.68) 100%);
        backdrop-filter:blur(28px) saturate(180%);
        border-top: 1.5px solid rgba(255,255,255,0.96);
        border-left: 1px solid rgba(255,255,255,0.88);
        border-right: 1px solid rgba(255,255,255,0.60);
        border-bottom: 1px solid rgba(255,255,255,0.54);
        border-radius:28px; padding:26px 20px 22px; text-align:center; min-height:168px;
        position:relative; overflow:hidden;
        box-shadow: 0 18px 52px rgba(0,82,255,0.10), inset 0 1.5px 0 rgba(255,255,255,1);
        transition: all 0.32s cubic-bezier(0.22,1,0.36,1);
    }
    .metric-box::before {
        content:""; position:absolute; top:0; left:0; right:0; height:50%;
        background: linear-gradient(180deg, rgba(255,255,255,0.52) 0%, rgba(255,255,255,0.04) 100%);
        border-radius:28px 28px 0 0; pointer-events:none;
    }
    .metric-box::after {
        content:""; position:absolute; width:130px; height:130px; top:-65px; right:-50px;
        background: radial-gradient(circle, rgba(0,82,255,0.14) 0%, transparent 70%);
        border-radius:50%; pointer-events:none;
    }
    .metric-box:hover {
        transform: translateY(-7px) scale(1.02);
        box-shadow: 0 32px 72px rgba(0,82,255,0.16), inset 0 1.5px 0 rgba(255,255,255,1);
    }
    .metric-icon-wrap {
        width:46px; height:46px; border-radius:15px;
        background: linear-gradient(135deg, rgba(0,82,255,0.12), rgba(6,182,212,0.09));
        border: 1.5px solid rgba(255,255,255,0.80);
        display:flex; align-items:center; justify-content:center; font-size:20px;
        margin:0 auto 13px; position:relative; z-index:2;
    }
    .metric-num {
        background: linear-gradient(135deg, #0042CC 0%, #0066FF 48%, #06B6D4 100%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        font-size:48px; font-weight:800; letter-spacing:-2.5px; line-height:1;
        position:relative; z-index:2;
    }
    .metric-title {
        color:#334155; font-size:13px; font-weight:800; text-transform:uppercase;
        letter-spacing:0.8px; margin-top:8px; position:relative; z-index:2;
    }
    .metric-sub {
        color:#94A3B8; font-size:10px; font-weight:600; margin-top:3px;
        position:relative; z-index:2;
    }
    .page-title-wrap {
        background: linear-gradient(145deg, rgba(255,255,255,0.78) 0%, rgba(228,242,255,0.64) 100%);
        backdrop-filter:blur(26px);
        border-top: 1.5px solid rgba(255,255,255,0.94);
        border-left: 1px solid rgba(255,255,255,0.86);
        border-right: 1px solid rgba(255,255,255,0.58);
        border-bottom: 1px solid rgba(255,255,255,0.52);
        border-radius:24px; padding:20px 28px; margin-bottom:24px;
        display:flex; align-items:center;
        box-shadow: 0 10px 36px rgba(0,82,255,0.08), inset 0 1.5px 0 rgba(255,255,255,1);
    }
    .ptw-left { display:flex; align-items:center; gap:14px; }
    .ptw-dot {
        width:14px; height:14px; border-radius:50%;
        background:linear-gradient(135deg,#0052FF,#06B6D4);
        box-shadow:0 0 0 5px rgba(0,82,255,0.12); flex-shrink:0;
    }
    .ptw-title { font-size:20px; font-weight:800; color:#0F172A; letter-spacing:-0.5px; }
    .ptw-sub   { font-size:12px; color:#64748B; font-weight:600; margin-top:2px; }
    .section-hdr {
        display:flex; align-items:center; gap:12px; margin:28px 0 16px; padding:16px 22px;
        background: linear-gradient(145deg, rgba(255,255,255,0.70) 0%, rgba(228,242,255,0.56) 100%);
        backdrop-filter:blur(22px);
        border-top: 1.5px solid rgba(255,255,255,0.92);
        border-left: 1px solid rgba(255,255,255,0.82);
        border-right: 1px solid rgba(255,255,255,0.56);
        border-bottom: 1px solid rgba(255,255,255,0.50);
        border-radius:20px;
        box-shadow: 0 10px 32px rgba(0,82,255,0.07), inset 0 1.5px 0 rgba(255,255,255,1);
    }
    .section-hdr-bar { width:4px; height:30px; border-radius:999px; background:linear-gradient(180deg,#0052FF,#06B6D4); flex-shrink:0; }
    .section-hdr-icon { font-size:20px; }
    .section-hdr-text { font-size:17px; font-weight:800; color:#0F172A; letter-spacing:-0.3px; }
    .section-hdr-badge {
        margin-left:auto;
        background: linear-gradient(135deg, rgba(0,82,255,0.10), rgba(6,182,212,0.08));
        color:#0052FF; font-size:12px; font-weight:800;
        padding:5px 14px; border-radius:999px; border:1px solid rgba(0,82,255,0.16);
    }
    .stock-row {
        background: linear-gradient(145deg, rgba(255,255,255,0.76) 0%, rgba(228,242,255,0.60) 100%);
        backdrop-filter:blur(24px);
        border-top: 1.5px solid rgba(255,255,255,0.92);
        border-left: 1px solid rgba(255,255,255,0.84);
        border-right: 1px solid rgba(255,255,255,0.56);
        border-bottom: 1px solid rgba(255,255,255,0.50);
        border-radius:20px; padding:16px 22px; margin-bottom:10px;
        display:flex; align-items:center; position:relative; overflow:hidden;
        box-shadow: 0 8px 28px rgba(0,82,255,0.07), inset 0 1.5px 0 rgba(255,255,255,1);
        transition: all 0.26s cubic-bezier(0.22,1,0.36,1);
    }
    .stock-row::before {
        content:""; position:absolute; top:0; left:0; right:0; height:50%;
        background: linear-gradient(180deg, rgba(255,255,255,0.46) 0%, rgba(255,255,255,0.02) 100%);
        border-radius:20px 20px 0 0; pointer-events:none;
    }
    .stock-row:hover {
        transform:translateY(-3px);
        box-shadow: 0 18px 48px rgba(0,82,255,0.12), inset 0 1.5px 0 rgba(255,255,255,1);
    }
    .sr-index { font-size:12px; font-weight:800; color:#CBD5E1; width:32px; flex-shrink:0; position:relative; z-index:1; }
    .sr-region {
        font-size:10px; font-weight:800; color:#0052FF; background:rgba(0,82,255,0.07);
        padding:3px 10px; border-radius:999px; border:1px solid rgba(0,82,255,0.13);
        white-space:nowrap; margin-right:14px; flex-shrink:0; position:relative; z-index:1;
    }
    .sr-city { font-size:15px; font-weight:800; color:#0F172A; letter-spacing:-0.3px; min-width:120px; flex-shrink:0; position:relative; z-index:1; }
    .sr-partner { font-size:12px; font-weight:600; color:#64748B; flex:1; padding:0 16px; position:relative; z-index:1; }
    .sr-divider-v {
        width:1px; height:36px; flex-shrink:0;
        background:linear-gradient(180deg, transparent, rgba(0,82,255,0.14), transparent);
        margin:0 16px 0 0; position:relative; z-index:1;
    }
    .sr-stats { display:flex; gap:10px; flex-shrink:0; position:relative; z-index:1; }
    .sr-stat {
        text-align:center;
        background: linear-gradient(145deg, rgba(255,255,255,0.82), rgba(228,242,255,0.68));
        border-top: 1px solid rgba(255,255,255,0.94);
        border-left: 1px solid rgba(255,255,255,0.82);
        border-right: 1px solid rgba(255,255,255,0.57);
        border-bottom: 1px solid rgba(255,255,255,0.52);
        border-radius:12px; padding:8px 14px; min-width:54px;
    }
    .sr-stat-num {
        font-size:18px; font-weight:800; letter-spacing:-0.8px; line-height:1;
        background:linear-gradient(135deg,#0042CC,#06B6D4);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    }
    .sr-stat-lbl { font-size:9px; font-weight:800; color:#94A3B8; text-transform:uppercase; letter-spacing:0.6px; margin-top:2px; }
    .ship-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.78) 0%, rgba(228,242,255,0.62) 52%, rgba(232,238,255,0.66) 100%);
        backdrop-filter:blur(26px);
        border-top: 1.5px solid rgba(255,255,255,0.96);
        border-left: 1px solid rgba(255,255,255,0.88);
        border-right: 1px solid rgba(255,255,255,0.60);
        border-bottom: 1px solid rgba(255,255,255,0.54);
        border-radius:24px; padding:22px 24px; margin-bottom:14px;
        position:relative; overflow:hidden;
        box-shadow: 0 16px 46px rgba(0,82,255,0.08), inset 0 1.5px 0 rgba(255,255,255,1);
        transition: all 0.28s cubic-bezier(0.22,1,0.36,1);
    }
    .ship-card::before {
        content:""; position:absolute; top:0; left:0; right:0; height:48%;
        background: linear-gradient(180deg, rgba(255,255,255,0.48) 0%, rgba(255,255,255,0.02) 100%);
        border-radius:24px 24px 0 0; pointer-events:none;
    }
    .ship-card::after {
        content:""; position:absolute; bottom:-40px; right:-40px;
        width:160px; height:160px; border-radius:50%;
        background: radial-gradient(circle, rgba(6,182,212,0.12) 0%, transparent 70%);
        pointer-events:none;
    }
    .ship-card:hover {
        transform:translateY(-4px);
        box-shadow: 0 26px 64px rgba(0,82,255,0.13), inset 0 1.5px 0 rgba(255,255,255,1);
    }
    .equip-chips {
        display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; padding-top:12px;
        border-top:1px solid rgba(0,82,255,0.07);
    }
    .badge {
        display:inline-flex; align-items:center; padding:5px 13px;
        border-radius:999px; font-size:11px; font-weight:800; letter-spacing:0.3px;
    }
    .badge-way   { background:rgba(245,158,11,0.12); color:#92400E; border:1px solid rgba(245,158,11,0.26); }
    .badge-deliv { background:rgba(16,185,129,0.12); color:#065F46; border:1px solid rgba(16,185,129,0.26); }
    .fn-tag { display:inline-block; font-size:10px; font-weight:800; padding:2px 7px; border-radius:6px; margin-right:4px; }
    .fn-36  { background:rgba(99,102,241,0.14); color:#3730A3; border:1px solid rgba(99,102,241,0.22); }
    .fn-15  { background:rgba(16,185,129,0.13); color:#065F46; border:1px solid rgba(16,185,129,0.22); }
    div[data-testid="stTabs"] [role="tablist"] { gap:6px; border-bottom:none !important; flex-wrap:wrap; }
    div[data-testid="stTabs"] button {
        background: linear-gradient(145deg, rgba(255,255,255,0.76) 0%, rgba(228,242,255,0.60) 100%) !important;
        color:#475569 !important; border-radius:16px !important;
        padding:10px 18px !important; height:44px !important;
        border-top: 1.5px solid rgba(255,255,255,0.94) !important;
        border-left: 1px solid rgba(255,255,255,0.84) !important;
        border-right: 1px solid rgba(255,255,255,0.57) !important;
        border-bottom: 1px solid rgba(255,255,255,0.52) !important;
        font-weight:800 !important; font-size:13px !important;
        backdrop-filter:blur(20px); transition:all 0.25s ease !important;
    }
    div[data-testid="stTabs"] button:hover {
        background:rgba(255,255,255,0.92) !important; color:#0052FF !important;
        transform:translateY(-2px);
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #0042CC 0%, #0066FF 48%, #06B6D4 100%) !important;
        color:#fff !important; border:1px solid rgba(255,255,255,0.35) !important;
        box-shadow: 0 16px 42px rgba(0,82,255,0.30);
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color:transparent !important; }
    div[data-testid="stExpander"] {
        background: linear-gradient(145deg, rgba(255,255,255,0.68) 0%, rgba(228,242,255,0.54) 100%);
        border-radius:18px;
        border-top: 1.5px solid rgba(255,255,255,0.90) !important;
        border-left: 1px solid rgba(255,255,255,0.80) !important;
        border-right: 1px solid rgba(255,255,255,0.54) !important;
        border-bottom: 1px solid rgba(255,255,255,0.48) !important;
        backdrop-filter:blur(20px);
    }
    .stDataFrame { border-radius:20px !important; overflow:hidden; border:1px solid rgba(255,255,255,0.82) !important; }
    .stAlert { border-radius:16px !important; backdrop-filter:blur(14px) !important; border:1px solid rgba(255,255,255,0.64) !important; }
    h1, h2, h3 { color:#0F172A !important; letter-spacing:-0.5px; font-weight:800 !important; }
    hr {
        border:none !important; height:1px !important;
        background: linear-gradient(90deg, transparent, rgba(0,82,255,0.18), rgba(6,182,212,0.14), transparent) !important;
        margin:1.2rem 0 !important;
    }
    ::-webkit-scrollbar       { width:8px; height:8px; }
    ::-webkit-scrollbar-track { background:rgba(255,255,255,0.30); border-radius:999px; }
    ::-webkit-scrollbar-thumb { background:linear-gradient(180deg,rgba(0,82,255,0.28),rgba(6,182,212,0.22)); border-radius:999px; }
    @media (max-width: 768px) {
        .stock-row     { flex-wrap:wrap; gap:8px; padding:14px 16px; }
        .sr-region     { margin-right:0; }
        .sr-partner    { width:100%; padding:4px 0; }
        .sr-divider-v  { display:none; }
        .sr-stats      { width:100%; justify-content:space-around; }
        .metric-box    { min-height:130px; padding:18px 14px 16px; }
        .metric-num    { font-size:32px; }
        div[data-testid="stTabs"] [role="tablist"] { gap:4px; }
        div[data-testid="stTabs"] button { padding:8px 12px !important; height:38px !important; font-size:11px !important; }
        .ship-card   { padding:16px 14px; }
        .section-hdr { padding:12px 16px; flex-wrap:wrap; gap:8px; }
        .section-hdr-badge { margin-left:0; }
        .page-title-wrap { padding:14px 16px; border-radius:18px; }
        .ptw-title { font-size:16px; }
    }
</style>""", unsafe_allow_html=True)
import html as _html_mod
MONTHS_RU = {
    1:"января", 2:"февраля", 3:"марта", 4:"апреля",
    5:"мая", 6:"июня", 7:"июля", 8:"августа",
    9:"сентября", 10:"октября", 11:"ноября", 12:"декабря"
}
def fmt_date_ru(d):
    if not d or not hasattr(d, 'day'): return "—"
    try: return f"{d.day} {MONTHS_RU[d.month]} {d.year}"
    except: return str(d)
def fmt_datetime_ru(d):
    if not d or not hasattr(d, 'day'): return "—"
    try: return f"{d.day} {MONTHS_RU[d.month]} {d.year}, {d.strftime('%H:%M')}"
    except: return str(d)
def fmt_date_short(d):
    if d is None: return "—"
    try: return f"{d.day} {MONTHS_RU[d.month]}"
    except: return str(d)
def safe_int(val):
    try:
        v = pd.to_numeric(val, errors='coerce')
        return 0 if pd.isna(v) else int(v)
    except: return 0
def clean_num(val):
    v = str(val).strip()
    if v.lower() in ("", "nan", "none"): return ""
    try:
        f = float(v)
        return str(int(f)) if f == int(f) else v
    except: return v
def clean_phone(val):
    v = str(val).strip()
    if v.endswith(".0"): v = v[:-2]
    return v if v not in ("", "nan", "None") else ""
def parse_serials_html(raw):
    lines = str(raw).replace("\r", "").split("\n")
    out = []
    for line in lines:
        line = line.strip()
        if not line or line.lower() in ("nan", "none"): continue
        if line.startswith("7381") or line.startswith("7385"):
            tag = '<span class="fn-tag fn-36">ФН-36</span>'
        elif line.startswith("7380") or line.startswith("7384"):
            tag = '<span class="fn-tag fn-15">ФН-15</span>'
        else:
            tag = ""
        out.append(f'<div style="padding:3px 0;">{tag}{_html_mod.escape(line)}</div>')
    return "".join(out) if out else '<span style="color:#94A3B8;">Не указаны</span>'
def equip_chips_archive(raw):
    text = str(raw).strip()
    if not text or text.lower() in ("nan", "none", ""):
        return '<span style="color:#94A3B8;font-size:13px;">—</span>'
    COLOR_MAP = {
        "ккт":    ("🖨️", "rgba(0,82,255,0.09)",   "rgba(0,82,255,0.16)",   "#0042CC"),
        "фн-36":  ("🗂️", "rgba(99,102,241,0.11)",  "rgba(99,102,241,0.22)", "#3730A3"),
        "фн36":   ("🗂️", "rgba(99,102,241,0.11)",  "rgba(99,102,241,0.22)", "#3730A3"),
        "фн-15":  ("🗂️", "rgba(16,185,129,0.11)",  "rgba(16,185,129,0.22)", "#065F46"),
        "фн15":   ("🗂️", "rgba(16,185,129,0.11)",  "rgba(16,185,129,0.22)", "#065F46"),
        "sim":    ("📶", "rgba(6,182,212,0.10)",   "rgba(6,182,212,0.20)",  "#0E7490"),
        "сим":    ("📶", "rgba(6,182,212,0.10)",   "rgba(6,182,212,0.20)",  "#0E7490"),
        "наклей": ("🏷️", "rgba(245,158,11,0.10)",  "rgba(245,158,11,0.20)", "#92400E"),
        "кабел":  ("🔌", "rgba(99,102,241,0.10)",  "rgba(99,102,241,0.18)", "#3730A3"),
        "бумаг":  ("🧾", "rgba(16,185,129,0.09)",  "rgba(16,185,129,0.18)", "#065F46"),
        "термо":  ("🧾", "rgba(16,185,129,0.09)",  "rgba(16,185,129,0.18)", "#065F46"),
        "термин": ("🖥️", "rgba(0,82,255,0.09)",    "rgba(0,82,255,0.16)",   "#0042CC"),
    }
    DEFAULT = ("📦", "rgba(0,82,255,0.07)", "rgba(0,82,255,0.14)", "#0052FF")
    pattern = re.findall(
        r'([А-Яа-яA-Za-z][А-Яа-яA-Za-z0-9\s\-]*?):\s*([\d.,]+)\s*([^\d,;|·\n]*)', text
    )
    if not pattern:
        return f'<span style="font-size:13px;color:#334155;">{_html_mod.escape(text)}</span>'
    chips = []
    for name, qty, unit in pattern:
        name   = name.strip()
        unit_c = unit.strip().replace("шт", "").replace("шт.", "").strip().rstrip(".,;")
        icon, bg, border, color = DEFAULT
        for k, v in COLOR_MAP.items():
            if k in name.lower():
                icon, bg, border, color = v
                break
        try:
            qty_str = str(int(float(qty.replace(",", "."))))
        except:
            qty_str = qty
        label = f"{name}{' ' + unit_c if unit_c else ''}"
        chips.append(
            f'<div style="display:inline-flex;align-items:center;gap:7px;background:{bg};'
            f'border:1px solid {border};border-radius:14px;padding:7px 14px;'
            f'margin-right:8px;margin-bottom:8px;box-shadow:0 2px 8px rgba(0,82,255,0.06);">'
            f'<span style="font-size:18px;line-height:1;">{icon}</span>'
            f'<div><div style="font-size:17px;font-weight:800;color:{color};line-height:1.1;">{qty_str}</div>'
            f'<div style="font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase;'
            f'letter-spacing:0.5px;margin-top:2px;">{_html_mod.escape(label)}</div></div></div>'
        )
    return "".join(chips)
def ret_card_style(org_from, org_to):
    combo = (str(org_from) + str(org_to)).upper()
    if "БР"   in combo: return "rgba(254,243,199,0.62)", "rgba(253,224,71,0.44)"
    if "АТМ"  in combo: return "rgba(186,230,253,0.57)", "rgba(56,189,248,0.40)"
    if "LIFE PAY" in combo: return "rgba(224,242,255,0.60)", "rgba(0,82,255,0.28)"
    if "АВТОМАТИЗАЦИЯ" in combo: return "rgba(220,252,231,0.60)", "rgba(16,185,129,0.28)"
    return "rgba(228,242,255,0.47)", "rgba(0,82,255,0.17)"
def org_css_icon(org):
    o = str(org).upper()
    if "БР"           in o: return "org-br",  "🏭"
    if "АТМ"          in o: return "org-atm", "🏢"
    if "LIFE PAY"     in o: return "org-lp",  "💳"
    if "АВТОМАТИЗАЦИЯ" in o: return "org-ab",  "📊"
    if "АРЕС" in o or "КОРИТЕК" in o: return "org-def", "🏗️"
    return "org-def", "🏢"
def safe_iloc(row, idx, default=""):
    try:
        val = row.iloc[idx]
        return default if pd.isna(val) else val
    except (IndexError, KeyError):
        return default
def make_excel(df_in):
    output = io.BytesIO()
    try:
        if df_in.empty:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                pd.DataFrame({"Статус": ["Нет данных"]}).to_excel(writer, index=False)
            output.seek(0)
            return output.getvalue()
        rows = []
        for _, r in df_in.iterrows():
            st_raw = str(safe_iloc(r, 11)).strip().upper()
            status = "В ПУТИ" if "В ПУТИ" in st_raw or "ПУТ" in st_raw else "ДОСТАВЛЕНО"
            d_val  = safe_iloc(r, 12)
            d_str  = d_val.strftime('%d.%m.%Y') if hasattr(d_val, 'strftime') and pd.notnull(d_val) else str(d_val)
            rows.append({
                "Дата": d_str, "Город": str(safe_iloc(r, 1)),
                "Клиент": str(safe_iloc(r, 2)), "Оборудование": str(safe_iloc(r, 7)),
                "Серийники": str(safe_iloc(r, 10)), "Статус": status
            })
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(rows).to_excel(writer, index=False, sheet_name='Отгрузки')
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        logger.error(f"Ошибка Excel: {e}")
        return b""
def make_excel_return(df_in):
    output = io.BytesIO()
    try:
        if df_in.empty:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                pd.DataFrame({"Статус": ["Нет данных"]}).to_excel(writer, index=False)
            output.seek(0)
            return output.getvalue()
        rows = []
        for _, r in df_in.iterrows():
            d_val = r.get("date", "")
            d_str = d_val.strftime('%d.%m.%Y') if hasattr(d_val, 'strftime') and pd.notnull(d_val) else ""
            rows.append({
                "Дата": d_str,
                "Город (откуда)": str(r.get("city_from", "")),
                "Отправитель": str(r.get("org_from", "")),
                "Адрес (откуда)": str(r.get("addr_from", "")),
                "ФИО отправителя": str(r.get("person_from", "")),
                "Город (куда)": str(r.get("city_to", "")),
                "Получатель": str(r.get("org_to", "")),
                "Адрес (куда)": str(r.get("addr_to", "")),
                "ФИО получателя": str(r.get("person_to", "")),
                "Телефон": clean_phone(str(r.get("phone_to", ""))),
                "ККТ": clean_num(str(r.get("kkt", ""))),
                "ФН-15": clean_num(str(r.get("fn15", ""))),
                "ФН-36": clean_num(str(r.get("fn36", ""))),
                "Серийные номера": str(r.get("serials", "")).replace("\n", " | "),
                "Комментарий": str(r.get("comment", "")),
                "Трек": str(r.get("track", ""))
            })
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(rows).to_excel(writer, index=False, sheet_name='Возвраты')
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        logger.error(f"Ошибка Excel возвратов: {e}")
        return b""
# ══════════════════════════════════════════════════════════════
# URLS
# ══════════════════════════════════════════════════════════════
URL_REESTR = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv"
URL_STOCK  = "https://docs.google.com/spreadsheets/d/1subRa0xO9jezmbWyIEkamw2f3-5yWmeXEmFOGQZyvLg/export?format=csv"
URL_RETURN = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv&gid=226066513"
URL_DEBTS  = "https://docs.google.com/spreadsheets/d/1Q4MGhp0KsLb57Ouqu58j_Md5zoFgAhFd3ld15cyOHrU/export?format=csv&gid=1820118704"
# ══════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=60, show_spinner="Загрузка данных...")
def get_data():
    try:
        s_df = pd.read_csv(URL_STOCK, nrows=80).fillna(0)
    except Exception as e:
        logger.error(f"Ошибка загрузки остатков: {e}")
        s_df = pd.DataFrame()
    try:
        r_df = pd.read_csv(URL_REESTR).fillna("")
    except Exception as e:
        logger.error(f"Ошибка загрузки реестра: {e}")
        r_df = pd.DataFrame()
    mapping = {
        "АБ": "Автоматизация Бизнеса",
        "АТМ": "ООО АТМ АЛЬЯНС СОЛЮШИНС",
        "БР": "ООО БР",
        "ЛП": "LIFE PAY",
        "Коритек": "ООО АРЕС-КОМПАНИ-М"
    }
    if not s_df.empty and s_df.shape[1] > 1:
        s_df.iloc[:, 1] = s_df.iloc[:, 1].astype(str).replace(mapping)
    if not r_df.empty and r_df.shape[1] > 12:
        r_df.iloc[:, 2] = r_df.iloc[:, 2].astype(str).replace(mapping)
        r_df[r_df.columns[12]] = pd.to_datetime(r_df[r_df.columns[12]], dayfirst=True, errors='coerce')
        r_df = r_df.sort_values(by=r_df.columns[12], ascending=False)
    return s_df, r_df
@st.cache_data(ttl=60, show_spinner="Загрузка перемещений...")
def get_return_data():
    try:
        raw = pd.read_csv(URL_RETURN, header=0)
    except Exception as e:
        logger.error(f"Ошибка загрузки возвратов: {e}")
        return pd.DataFrame()
    if raw.empty:
        return pd.DataFrame()
    total_cols = raw.shape[1]
    start_col  = 2 if total_cols >= 5 else 0
    end_col    = min(start_col + 19, total_cols)
    raw = raw.iloc[:, start_col:end_col].copy()
    n = raw.shape[1]
    base_names = [
        "city_from", "org_from", "addr_from", "person_from",
        "city_to",   "org_to",   "addr_to",   "person_to",
        "phone_to",  "info_to",  "comment",
        "kkt", "fn15", "fn36", "serials",
        "col_r", "col_s", "date", "track"
    ]
    raw.columns = base_names[:n]
    raw = raw.fillna("")
    if "date" in raw.columns:
        raw["date"] = pd.to_datetime(raw["date"], dayfirst=True, errors='coerce')
    else:
        raw["date"] = pd.NaT
    def has_data(r):
        for f in ["org_from", "city_from", "org_to", "city_to"]:
            if f in r.index:
                v = str(r[f]).strip().lower()
                if v and v not in ("nan", "none", "", "0"):
                    return True
        return False
    raw_filtered = raw[raw.apply(has_data, axis=1)].copy()
    if raw_filtered.empty:
        mask = raw.apply(
            lambda r: any(str(v).strip() not in ("", "nan", "none", "0") for v in r.values), axis=1
        )
        raw_filtered = raw[mask].copy()
    if raw_filtered.empty:
        return pd.DataFrame()
    org_map = {
        "life pay": "LIFE PAY", "лп": "LIFE PAY",
        "автоматизация бизнеса": "Автоматизация Бизнеса", "аб": "Автоматизация Бизнеса",
        "ооо бр": "ООО БР", "бр": "ООО БР", 'ооо "бр"': "ООО БР",
        "ооо атм альянс солюшинс": "ООО АТМ АЛЬЯНС СОЛЮШИНС",
        'ооо "атм альянс солюшинс"': "ООО АТМ АЛЬЯНС СОЛЮШИНС",
        "атм": "ООО АТМ АЛЬЯНС СОЛЮШИНС", "атм альянс": "ООО АТМ АЛЬЯНС СОЛЮШИНС",
    }
    for col in ["org_from", "org_to"]:
        if col in raw_filtered.columns:
            raw_filtered[col] = raw_filtered[col].apply(
                lambda x: org_map.get(str(x).strip().lower(), str(x).strip())
            )
    if "date" in raw_filtered.columns:
        return raw_filtered.sort_values(
            "date", ascending=False, na_position='last'
        ).reset_index(drop=True)
    return raw_filtered.reset_index(drop=True)
@st.cache_data(ttl=60, show_spinner="Загрузка долгов партнёров...")
def get_debts_data():
    try:
        df = pd.read_csv(URL_DEBTS, header=0).fillna("")
        return df
    except Exception as e:
        logger.error(f"Ошибка загрузки долгов: {e}")
        return pd.DataFrame()
df_stock_raw, df_ship_raw = get_data()
df_return_raw = get_return_data()
df_debts_raw  = get_debts_data()
if df_stock_raw.empty:
    st.warning("⚠️ Не удалось загрузить данные остатков.")
if df_ship_raw.empty:
    st.warning("⚠️ Не удалось загрузить данные отгрузок.")
if time.time() - st.session_state.last_refresh > 120:
    st.session_state.last_refresh = time.time()
    if len(st.session_state.seen_ids) > 500:
        st.session_state.seen_ids = set(list(st.session_state.seen_ids)[-200:])
    get_data.clear()
    get_return_data.clear()
    get_debts_data.clear()
    st.rerun()
# ══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ
# ══════════════════════════════════════════════════════════════
def safe_date_col(df, col_idx):
    if df is None or df.empty or df.shape[1] <= col_idx:
        return pd.Series(False, index=df.index if df is not None else [])
    col = df.iloc[:, col_idx]
    if not pd.api.types.is_datetime64_any_dtype(col):
        return pd.Series(False, index=df.index)
    return col.notna()
# ══════════════════════════════════════════════════════════════
# АВТО-НОВОСТИ
# ══════════════════════════════════════════════════════════════
def auto_generate_news(df_ship, df_ret, org_filter):
    today = date.today()
    news  = []
    if (df_ship is None or df_ship.empty) and (df_ret is None or df_ret.empty):
        return news
    def filter_ship(df):
        if df is None or df.empty: return pd.DataFrame()
        if org_filter != "all":
            return df[df.iloc[:, 2].astype(str).str.contains(org_filter, case=False, na=False)]
        return df
    def filter_ret(df):
        if df is None or df.empty or org_filter == "all":
            return df if df is not None else pd.DataFrame()
        cf = df.get("org_from", pd.Series(dtype=str)).astype(str)
        ct = df.get("org_to",   pd.Series(dtype=str)).astype(str)
        return df[
            cf.str.contains(org_filter, case=False, na=False) |
            ct.str.contains(org_filter, case=False, na=False)
        ]
    df_s = filter_ship(df_ship)
    df_r = filter_ret(df_ret)
    if not df_s.empty and df_s.shape[1] > 12:
        dm    = safe_date_col(df_s, 12)
        tm    = dm & (df_s.iloc[:, 12].dt.date == today)
        ts    = df_s[tm]
        way_s = ts[ts.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False)]
        del_s = ts[~ts.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False)]
        if len(way_s) > 0:
            cl = list(set(way_s.iloc[:, 2].astype(str).tolist()))[:2]
            ci = list(set(way_s.iloc[:, 1].astype(str).tolist()))[:2]
            news.append({
                "icon": "🚚", "title": f"{len(way_s)} новых отправок сегодня",
                "text": f"Клиенты: {', '.join(cl)}. Города: {', '.join(ci)}",
                "color": "#0052FF", "bg": "rgba(0,82,255,0.07)",
                "border": "rgba(0,82,255,0.18)", "today": True
            })
        if len(del_s) > 0:
            news.append({
                "icon": "✅", "title": f"{len(del_s)} доставлений сегодня",
                "text": f"Доставлено: {', '.join(list(set(del_s.iloc[:,2].astype(str).tolist()))[:2])}",
                "color": "#065F46", "bg": "rgba(16,185,129,0.07)",
                "border": "rgba(16,185,129,0.20)", "today": True
            })
    if df_r is not None and not df_r.empty and "date" in df_r.columns:
        tr = df_r[df_r["date"].notna() & (df_r["date"].dt.date == today)]
        if len(tr) > 0:
            routes = []
            for _, r in tr.head(3).iterrows():
                cf2 = str(r.get("city_from", "")).strip()
                ct2 = str(r.get("city_to",   "")).strip()
                if (cf2 and ct2 and
                        cf2.lower() not in ("nan", "") and
                        ct2.lower() not in ("nan", "")):
                    routes.append(f"{cf2}→{ct2}")
            news.append({
                "icon": "🔄", "title": f"{len(tr)} перемещений сегодня",
                "text": "Маршруты: " + (", ".join(routes) if routes else "—"),
                "color": "#7C3AED", "bg": "rgba(99,102,241,0.07)",
                "border": "rgba(99,102,241,0.20)", "today": True
            })
    if not df_s.empty and df_s.shape[1] > 12:
        wa  = today - timedelta(days=7)
        dm  = safe_date_col(df_s, 12)
        ws  = df_s[dm & (df_s.iloc[:, 12].dt.date >= wa) & (df_s.iloc[:, 12].dt.date < today)]
        if len(ws) > 0:
            news.append({
                "icon": "📊", "title": f"Итоги недели: {len(ws)} отправок",
                "text": f"Клиентов: {ws.iloc[:,2].nunique()}, городов: {ws.iloc[:,1].nunique()}.",
                "color": "#0E7490", "bg": "rgba(6,182,212,0.07)",
                "border": "rgba(6,182,212,0.20)", "today": False
            })
        wa_all = df_s[df_s.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False)]
        if len(wa_all) > 0:
            ci2 = list(set(wa_all.iloc[:, 1].astype(str).tolist()))[:4]
            news.append({
                "icon": "🚚", "title": f"Сейчас в пути: {len(wa_all)} отправок",
                "text": "Города: " + ", ".join(ci2),
                "color": "#0052FF", "bg": "rgba(0,82,255,0.07)",
                "border": "rgba(0,82,255,0.18)", "today": True
            })
    return news
auto_news = auto_generate_news(df_ship_raw, df_return_raw, user_filter)
# ══════════════════════════════════════════════════════════════
# УВЕДОМЛЕНИЯ
# ══════════════════════════════════════════════════════════════
def get_new_items(df_ship, df_ret, auto_news_list, user_filter_val):
    today      = date.today()
    new_toasts = []
    for n in auto_news_list[:2]:
        uid = "news_" + str(n.get("title", ""))[:30]
        if uid not in st.session_state.seen_ids:
            st.session_state.seen_ids.add(uid)
            new_toasts.append({
                "type": "news", "icon": n.get("icon", "📰"),
                "title": n.get("title", "Новость"),
                "date": fmt_date_short(today),
                "line1": n.get("text", "")[:90], "line2": "", "tag": "НОВОСТЬ"
            })
    if df_ship is not None and not df_ship.empty and df_ship.shape[1] > 12:
        dm = safe_date_col(df_ship, 12)
        wt = df_ship[
            df_ship.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False) &
            dm & (df_ship.iloc[:, 12].dt.date == today)
        ]
        if user_filter_val != "all":
            wt = wt[wt.iloc[:, 2].astype(str).str.contains(user_filter_val, case=False, na=False)]
        for _, r in wt.iterrows():
            uid = (
                "ship_" + str(safe_iloc(r, 2)) + "_" +
                str(safe_iloc(r, 1)) + "_" + str(safe_iloc(r, 12))[:10]
            )
            if uid not in st.session_state.seen_ids:
                st.session_state.seen_ids.add(uid)
                equip = str(safe_iloc(r, 7))
                equip = equip[:60] + "..." if len(equip) > 60 else equip
                new_toasts.append({
                    "type": "ship", "icon": "🚚",
                    "title": str(safe_iloc(r, 2)),
                    "date": fmt_date_ru(safe_iloc(r, 12)),
                    "line1": "📍 " + str(safe_iloc(r, 1)),
                    "line2": ("📋 " + equip if equip.lower() not in ("nan", "") else ""),
                    "tag": "НОВАЯ ОТПРАВКА"
                })
    return new_toasts
def show_notifications(df_ship, df_ret, auto_news_list, user_filter_val):
    today = date.today()
    if df_ship is not None and not df_ship.empty and df_ship.shape[1] > 12:
        way_df = df_ship[df_ship.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False)]
        if user_filter_val != "all":
            way_df = way_df[
                way_df.iloc[:, 2].astype(str).str.contains(user_filter_val, case=False, na=False)
            ]
        dm        = safe_date_col(way_df, 12)
        new_today = way_df[dm & (way_df.iloc[:, 12].dt.date == today)]
    else:
        way_df = pd.DataFrame()
        new_today = pd.DataFrame()
    ret_today = pd.DataFrame()
    if df_ret is not None and not df_ret.empty and "date" in df_ret.columns:
        ret_today = df_ret[df_ret["date"].notna() & (df_ret["date"].dt.date == today)]
        if user_filter_val != "all" and not ret_today.empty:
            cf = ret_today.get("org_from", pd.Series(dtype=str)).astype(str)
            ct = ret_today.get("org_to",   pd.Series(dtype=str)).astype(str)
            ret_today = ret_today[
                cf.str.contains(user_filter_val, case=False, na=False) |
                ct.str.contains(user_filter_val, case=False, na=False)
            ]
    new_count  = len(new_today)
    ret_count  = len(ret_today)
    news_count = len(auto_news_list)
    badge_num    = new_count + ret_count + news_count
    badge_html    = f'<div class="nf-badge">{badge_num}</div>' if badge_num > 0 else ""
    has_notif_cls = "has-notif" if badge_num > 0 else ""
    bell_ring_cls = "bell-ring" if badge_num > 0 else ""
    new_toasts = get_new_items(df_ship, df_ret, auto_news_list, user_filter_val)
    toasts_js  = json.dumps(new_toasts, ensure_ascii=False)
    show_js    = "true" if new_toasts else "false"
    date_ru    = fmt_datetime_ru(datetime.now())
    html_out = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
.nf-wrap {{ position:fixed; top:16px; right:20px; z-index:9999; }}
.nf-glass-outer {{
    position:relative; width:62px; height:62px; border-radius:22px; cursor:pointer;
    background:linear-gradient(145deg,rgba(255,255,255,0.82),rgba(218,238,255,0.68));
    backdrop-filter:blur(48px);
    border-top:1.5px solid rgba(255,255,255,0.98); border-left:1.5px solid rgba(255,255,255,0.90);
    border-right:1px solid rgba(255,255,255,0.55); border-bottom:1px solid rgba(255,255,255,0.48);
    box-shadow:0 24px 70px rgba(0,82,255,0.24);
    display:flex; align-items:center; justify-content:center;
    transition:all 0.38s; overflow:visible; animation:btnFloat 4s ease-in-out infinite;
}}
@keyframes btnFloat {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-3px); }} }}
.nf-glass-outer:hover {{ transform:scale(1.12) translateY(-4px); animation:none; }}
.nf-glass-outer.has-notif {{ box-shadow:0 24px 70px rgba(0,82,255,0.36),0 0 0 2.5px rgba(0,82,255,0.22); }}
.bell-emoji {{ font-size:28px; z-index:3; filter:drop-shadow(0 3px 10px rgba(0,82,255,0.50)); }}
.bell-ring {{ animation:bellSwing 3s ease-in-out infinite !important; }}
@keyframes bellSwing {{ 0%,45%,100% {{ transform:rotate(0); }} 48% {{ transform:rotate(-28deg); }} 52% {{ transform:rotate(28deg); }} 56% {{ transform:rotate(-20deg); }} 60% {{ transform:rotate(20deg); }} }}
.nf-badge {{
    position:absolute; top:-10px; right:-10px; min-width:24px; height:24px; border-radius:12px;
    background:linear-gradient(135deg,#FF3D54,#FF6B35); color:white; font-size:11px; font-weight:800;
    display:flex; align-items:center; justify-content:center;
    border:3px solid rgba(255,255,255,0.97); padding:0 5px;
    box-shadow:0 5px 18px rgba(255,61,84,0.62); z-index:10;
}}
.nf-panel {{
    position:fixed; top:88px; right:20px; z-index:9998; width:400px; max-height:calc(100vh - 108px);
    background:linear-gradient(152deg,rgba(255,255,255,0.96),rgba(220,240,255,0.89));
    backdrop-filter:blur(70px); border-radius:32px; overflow:hidden;
    box-shadow:0 52px 140px rgba(0,82,255,0.28); display:flex; flex-direction:column;
    animation:panelIn 0.46s cubic-bezier(0.22,1,0.36,1);
    border-top:1.5px solid rgba(255,255,255,1); border-left:1.5px solid rgba(255,255,255,0.92);
    border-right:1px solid rgba(255,255,255,0.62); border-bottom:1px solid rgba(255,255,255,0.56);
}}
@keyframes panelIn {{ from {{ opacity:0; transform:translateY(-24px) scale(0.90); }} to {{ opacity:1; transform:translateY(0) scale(1); }} }}
.nf-head {{ padding:18px 22px 14px; border-bottom:1px solid rgba(0,82,255,0.08); }}
.nf-head-row1 {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }}
.nf-head-title {{ font-size:15px; font-weight:800; color:#0F172A; }}
.nf-close {{ width:30px; height:30px; border-radius:10px; cursor:pointer; background:rgba(0,82,255,0.06); border:1px solid rgba(0,82,255,0.12); display:flex; align-items:center; justify-content:center; font-size:14px; color:#64748B; }}
.nf-close:hover {{ background:rgba(239,68,68,0.10); color:#EF4444; }}
.nf-feed {{ overflow-y:auto; flex:1; padding:10px 14px 16px; min-height:200px; }}
.feed-empty {{ text-align:center; padding:36px 16px; color:#94A3B8; font-size:13px; font-weight:600; }}
.nf-foot {{ padding:12px 22px; border-top:1px solid rgba(0,82,255,0.07); background:rgba(255,255,255,0.28); font-size:10px; font-weight:700; color:#94A3B8; }}
#toast-wrap {{ position:fixed; bottom:32px; right:32px; z-index:99999; display:flex; flex-direction:column-reverse; gap:16px; pointer-events:none; width:380px; }}
.gl-toast {{ pointer-events:auto; border-radius:24px; background:linear-gradient(152deg,rgba(255,255,255,0.98),rgba(220,240,255,0.92)); backdrop-filter:blur(60px); border-top:1.5px solid rgba(255,255,255,1); box-shadow:0 32px 80px rgba(0,82,255,0.22); overflow:hidden; position:relative; cursor:pointer; }}
.gl-toast.toast-enter {{ animation:toastIn 0.68s cubic-bezier(0.22,1,0.36,1) both; }}
.gl-toast.toast-exit  {{ animation:toastOut 0.40s cubic-bezier(0.55,0,1,0.45) both; }}
@keyframes toastIn {{ from {{ opacity:0; transform:translateX(120px) scale(0.84); }} to {{ opacity:1; transform:translateX(0) scale(1); }} }}
@keyframes toastOut {{ from {{ opacity:1; }} to {{ opacity:0; transform:translateX(120px) scale(0.84); }} }}
.gl-stripe {{ position:absolute; left:0; top:0; bottom:0; width:4px; }}
.gl-toast-header {{ display:flex; align-items:center; gap:10px; padding:10px 14px 9px; border-bottom:1px solid rgba(0,82,255,0.07); }}
.gl-toast-brand-icon {{ width:28px; height:28px; border-radius:9px; background:linear-gradient(135deg,#0042CC,#06B6D4); display:flex; align-items:center; justify-content:center; font-size:14px; }}
.gl-toast-brand-name {{ font-size:11px; font-weight:800; background:linear-gradient(135deg,#0042CC,#06B6D4); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.gl-toast-tag {{ font-size:9px; font-weight:800; text-transform:uppercase; padding:2px 8px; border-radius:6px; margin-left:6px; }}
.gl-toast-time {{ margin-left:auto; font-size:10px; font-weight:700; color:#94A3B8; }}
.gl-toast-close {{ width:22px; height:22px; border-radius:7px; background:rgba(0,82,255,0.06); border:1px solid rgba(0,82,255,0.12); display:flex; align-items:center; justify-content:center; font-size:10px; color:#94A3B8; cursor:pointer; margin-left:6px; }}
.gl-body-toast {{ display:flex; align-items:flex-start; gap:12px; padding:12px 14px 13px; }}
.gl-icon {{ width:46px; height:46px; border-radius:15px; display:flex; align-items:center; justify-content:center; font-size:22px; box-shadow:0 6px 18px rgba(0,82,255,0.18); }}
.gl-content {{ flex:1; min-width:0; }}
.gl-title-toast {{ font-size:13px; font-weight:800; color:#0F172A; margin-bottom:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.gl-date-badge {{ font-size:10px; font-weight:700; padding:2px 8px; border-radius:7px; margin-bottom:5px; display:inline-flex; }}
.gl-line  {{ font-size:11px; font-weight:700; color:#1E293B; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.gl-line2 {{ font-size:10px; color:#64748B; margin-top:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.gl-bar {{ position:absolute; bottom:0; left:0; height:3px; animation:glBar linear both; }}
@keyframes glBar {{ from {{ width:100%; }} to {{ width:0%; }} }}
.toast-ship .gl-stripe {{ background:linear-gradient(180deg,#0052FF,#06B6D4); }}
.toast-ship .gl-icon {{ background:rgba(0,82,255,0.12); border:1.5px solid rgba(0,82,255,0.20); }}
.toast-ship .gl-toast-tag {{ color:#0052FF; background:rgba(0,82,255,0.09); border:1px solid rgba(0,82,255,0.20); }}
.toast-ship .gl-date-badge {{ color:#0052FF; background:rgba(0,82,255,0.06); border:1px solid rgba(0,82,255,0.14); }}
.toast-ship .gl-bar {{ background:linear-gradient(90deg,#0052FF,#06B6D4); }}
.toast-news .gl-stripe {{ background:linear-gradient(180deg,#10B981,#06B6D4); }}
.toast-news .gl-icon {{ background:rgba(16,185,129,0.12); border:1.5px solid rgba(16,185,129,0.24); }}
.toast-news .gl-toast-tag {{ color:#065F46; background:rgba(16,185,129,0.10); border:1px solid rgba(16,185,129,0.22); }}
.toast-news .gl-date-badge {{ color:#065F46; background:rgba(16,185,129,0.07); border:1px solid rgba(16,185,129,0.18); }}
.toast-news .gl-bar {{ background:linear-gradient(90deg,#10B981,#06B6D4); }}
@media (max-width:768px) {{
    .nf-wrap {{ top:12px; right:12px; }}
    .nf-glass-outer {{ width:48px; height:48px; border-radius:16px; }}
    .bell-emoji {{ font-size:22px; }}
    .nf-panel {{ width:calc(100vw - 24px); right:12px; top:72px; border-radius:24px; }}
    #toast-wrap {{ width:calc(100vw - 24px); right:12px; bottom:16px; }}
}}
</style>
<div class="nf-wrap" id="nfWrap">
  <div class="nf-glass-outer {has_notif_cls}" onclick="nfToggle()" id="nfBtnEl">
    <span class="bell-emoji {bell_ring_cls}">🔔</span>
    {badge_html}
  </div>
</div>
<div class="nf-panel" id="nfPanel" style="display:none;">
  <div class="nf-head">
    <div class="nf-head-row1">
      <div class="nf-head-title">🔔 Лента событий</div>
      <div class="nf-close" onclick="nfToggle()">✕</div>
    </div>
  </div>
  <div class="nf-feed"><div class="feed-empty">Нет активных событий 🌙</div></div>
  <div class="nf-foot">🕐 {date_ru}</div>
</div>
<div id="toast-wrap"></div>
<script>
var nfOpen = false;
function nfToggle() {{
    nfOpen = !nfOpen;
    var p = document.getElementById('nfPanel');
    if (p) p.style.display = nfOpen ? 'flex' : 'none';
}}
document.addEventListener('click', function(e) {{
    var w = document.getElementById('nfWrap');
    var p = document.getElementById('nfPanel');
    if (nfOpen && p && !p.contains(e.target) && w && !w.contains(e.target)) {{
        nfOpen = false; p.style.display = 'none';
    }}
}});
function escH(s) {{
    return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}
function removeToast(el) {{
    if (!el || el._r) return; el._r = true;
    el.classList.add('toast-exit');
    setTimeout(function() {{ if (el.parentNode) el.parentNode.removeChild(el); }}, 420);
}}
var TOASTS = {toasts_js};
var SHOW   = {show_js};
if (SHOW && TOASTS.length > 0) {{
    TOASTS.forEach(function(item, i) {{
        setTimeout(function() {{
            var wrap = document.getElementById('toast-wrap');
            if (!wrap) return;
            var tc  = item.type === 'ship' ? 'toast-ship' : 'toast-news';
            var now = new Date();
            var ts  = String(now.getHours()).padStart(2,'0') + ':' + String(now.getMinutes()).padStart(2,'0');
            var t   = document.createElement('div');
            t.className = 'gl-toast toast-enter ' + tc;
            t.innerHTML =
                '<div class="gl-stripe"></div>' +
                '<div class="gl-toast-header">' +
                  '<div class="gl-toast-brand-icon">💳</div>' +
                  '<div class="gl-toast-brand-name">LIFE PAY</div>' +
                  '<div class="gl-toast-tag">' + item.icon + ' ' + (item.tag||'') + '</div>' +
                  '<div class="gl-toast-time">' + ts + '</div>' +
                  '<div class="gl-toast-close" onclick="event.stopPropagation();removeToast(this.closest(\\'.gl-toast\\'))">✕</div>' +
                '</div>' +
                '<div class="gl-body-toast">' +
                  '<div class="gl-icon">' + item.icon + '</div>' +
                  '<div class="gl-content">' +
                    '<div class="gl-title-toast">' + escH(item.title) + '</div>' +
                    '<div class="gl-date-badge">📅 ' + escH(item.date) + '</div>' +
                    '<div class="gl-line">'  + escH(item.line1) + '</div>' +
                    (item.line2 ? '<div class="gl-line2">' + escH(item.line2) + '</div>' : '') +
                  '</div>' +
                '</div>' +
                '<div class="gl-bar" style="animation-duration:10000ms;"></div>';
            wrap.appendChild(t);
            setTimeout(function() {{ removeToast(t); }}, 10000);
        }}, 500 + i * 700);
    }});
}}
</script>"""
    st.markdown(html_out, unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════
# CSS КАРТОЧЕК ПЕРЕМЕЩЕНИЙ
# ══════════════════════════════════════════════════════════════
CARD_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
_,_ ::before, *::after { font-family:'Manrope',sans-serif; box-sizing:border-box; margin:0; padding:0; }
html, body { background:transparent; padding:2px; margin:0; overflow:hidden; }
.card {
    background:linear-gradient(148deg,rgba(255,255,255,0.88) 0%,rgba(224,242,255,0.76) 50%,rgba(228,236,255,0.80) 100%);
    backdrop-filter:blur(48px) saturate(210%);
    border-top:1.5px solid rgba(255,255,255,0.98); border-left:1px solid rgba(255,255,255,0.92);
    border-right:1px solid rgba(255,255,255,0.66); border-bottom:1px solid rgba(255,255,255,0.60);
    border-radius:24px; padding:20px 22px; position:relative; overflow:hidden;
    box-shadow:0 22px 60px rgba(0,82,255,0.12), inset 0 1.5px 0 rgba(255,255,255,1);
}
.card-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; position:relative; z-index:1; }
.badge-move { display:inline-flex; align-items:center; gap:5px; padding:5px 14px; border-radius:999px; font-size:11px; font-weight:800; background:rgba(99,102,241,0.13); color:#3730A3; border:1px solid rgba(99,102,241,0.28); }
.date-pill { font-size:12px; font-weight:800; color:#334155; background:rgba(0,82,255,0.06); padding:5px 13px; border-radius:10px; border:1px solid rgba(0,82,255,0.12); }
.route-wrap { display:flex; align-items:stretch; gap:10px; margin-bottom:16px; position:relative; z-index:1; }
.route-box { flex:1; min-width:0; border-radius:16px; padding:13px 15px; box-shadow:inset 0 1px 0 rgba(255,255,255,0.92); }
.route-lbl { font-size:9px; font-weight:800; color:#94A3B8; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px; }
.route-city { font-size:16px; font-weight:800; color:#0F172A; letter-spacing:-0.3px; margin-bottom:7px; line-height:1.2; }
.route-info { font-size:12px; color:#64748B; margin-top:4px; line-height:1.5; }
.badge-org { display:inline-flex; align-items:center; gap:4px; padding:4px 11px; border-radius:999px; font-size:11px; font-weight:800; margin-bottom:4px; }
.org-br  { background:rgba(234,179,8,0.14);  color:#854D0E; border:1px solid rgba(234,179,8,0.28); }
.org-atm { background:rgba(14,165,233,0.14); color:#075985; border:1px solid rgba(14,165,233,0.28); }
.org-lp  { background:rgba(0,82,255,0.11);   color:#1E3A8A; border:1px solid rgba(0,82,255,0.22); }
.org-ab  { background:rgba(16,185,129,0.12); color:#065F46; border:1px solid rgba(16,185,129,0.24); }
.org-def { background:rgba(99,102,241,0.11); color:#3730A3; border:1px solid rgba(99,102,241,0.22); }
.arrow-wrap { flex-shrink:0; display:flex; align-items:center; justify-content:center; }
.arrow-circle { width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#0052FF,#06B6D4); display:flex; align-items:center; justify-content:center; color:white; font-size:16px; font-weight:800; box-shadow:0 6px 18px rgba(0,82,255,0.32); }
.equip-section { padding-top:14px; border-top:1px solid rgba(0,82,255,0.08); position:relative; z-index:1; }
.equip-lbl { font-size:9px; font-weight:800; color:#94A3B8; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }
.equip-chips { display:flex; flex-wrap:wrap; gap:8px; }
.eq-chip { display:inline-flex; align-items:center; gap:7px; border-radius:14px; padding:7px 14px; box-shadow:0 3px 10px rgba(0,82,255,0.07); }
.eq-num { font-size:17px; font-weight:800; line-height:1; }
.eq-lbl { font-size:9px; font-weight:800; color:#94A3B8; text-transform:uppercase; letter-spacing:0.6px; margin-top:2px; }
"""
# ══════════════════════════════════════════════════════════════
# САЙДБАР
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="sb-brand-card">
        <div class="sb-brand-top">
            <div class="sb-brand-name">LIFE PAY</div>
            <div class="sb-brand-badge">ERP</div>
        </div>
        <div class="sb-brand-hr"></div>
        <div class="sb-brand-user">
            <div class="sb-brand-avatar">👤</div>
            <div>
                <div class="sb-brand-uname">{_html_mod.escape(user_login)}</div>
                <div class="sb-brand-role">Enterprise ERP</div>
            </div>
        </div>
        <div class="sb-brand-online">
            <div class="sb-online-dot"></div>
            <div class="sb-online-text">В системе</div>
        </div>
    </div>""", unsafe_allow_html=True)
    search_q = st.text_input("🔍 Поиск", placeholder="SN, город, клиент...")
    if user_filter != "all":
        df_st_f = (
            df_stock_raw[
                df_stock_raw.iloc[:, 1].astype(str).str.contains(user_filter, case=False)
            ]
            if not df_stock_raw.empty and df_stock_raw.shape[1] > 1
            else pd.DataFrame()
        )
        sel_org = user_filter
    else:
        df_st_f  = df_stock_raw
        org_list = ["Все"]
        if not df_ship_raw.empty and df_ship_raw.shape[1] > 2:
            org_list += sorted(df_ship_raw.iloc[:, 2].unique().astype(str).tolist())
        sel_org = st.selectbox("🏢 Организация", org_list)
    all_cities_list = ["Все"]
    if not df_ship_raw.empty and df_ship_raw.shape[1] > 1:
        all_cities_list += sorted(set(
            df_ship_raw.iloc[:, 1].unique().astype(str).tolist() +
            (
                df_stock_raw.iloc[:, 2].unique().astype(str).tolist()
                if not df_stock_raw.empty and df_stock_raw.shape[1] > 2
                else []
            )
        ))
    sel_city = st.selectbox("📍 Город", all_cities_list)
    st.markdown('<div class="sb-label">📆 Период</div>', unsafe_allow_html=True)
    today_date = date.today()
    if not df_ship_raw.empty and df_ship_raw.shape[1] > 12:
        valid_dates = df_ship_raw.iloc[:, 12].dropna()
        d_min = valid_dates.min().date() if len(valid_dates) > 0 else date(2020, 1, 1)
    else:
        d_min = date(2020, 1, 1)
    d_max_limit = date(2030, 12, 31)
    date_mode = st.radio(
        "Режим", ["Весь период", "Конкретная дата", "Диапазон"],
        horizontal=True, label_visibility="collapsed", index=0
    )
    if date_mode == "Конкретная дата":
        sd = st.date_input("📅 Дата", value=today_date, min_value=d_min, max_value=d_max_limit)
        date_from = date_to = sd
    elif date_mode == "Диапазон":
        if st.session_state.range_from is None: st.session_state.range_from = today_date
        if st.session_state.range_to   is None: st.session_state.range_to   = today_date
        c1, c2 = st.columns(2)
        with c1:
            date_from = st.date_input(
                "С", value=st.session_state.range_from,
                min_value=d_min, max_value=d_max_limit, key="df"
            )
            st.session_state.range_from = date_from
        with c2:
            date_to = st.date_input(
                "По", value=st.session_state.range_to,
                min_value=d_min, max_value=d_max_limit, key="dt"
            )
            st.session_state.range_to = date_to
    else:
        date_from = d_min
        date_to   = today_date
    st.divider()
    dl_df = df_ship_raw.copy()
    if user_filter != "all":
        if not dl_df.empty and dl_df.shape[1] > 2:
            dl_df = dl_df[dl_df.iloc[:, 2].astype(str).str.contains(user_filter, case=False)]
    elif sel_org != "Все":
        if not dl_df.empty and dl_df.shape[1] > 2:
            dl_df = dl_df[dl_df.iloc[:, 2] == sel_org]
    if sel_city != "Все" and not dl_df.empty and dl_df.shape[1] > 1:
        dl_df = dl_df[dl_df.iloc[:, 1] == sel_city]
    excel_data = make_excel(dl_df)
    if excel_data:
        st.download_button(
            label="📦 Скачать отгрузки", data=excel_data,
            file_name="Otgruzki.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
show_notifications(df_ship_raw, df_return_raw, auto_news, user_filter)
# ══════════════════════════════════════════════════════════════
# УТИЛИТЫ ДЛЯ ДОЛГОВ
# ══════════════════════════════════════════════════════════════
def is_junk_value(val):
    v = str(val).strip()
    if not v or v.lower() in ('', 'nan', 'none'): return True
    if re.match(r'^[█░▓▒\s]+$', v):               return True
    if re.match(r'^\[.*\]$', v):                   return True
    if re.match(r'^[\s\-_=+|/\\.,;:!?#*&^%$@~`]+$', v): return True
    return False
def is_real_number(val):
    v = str(val).strip().replace(",", ".").replace(" ", "")
    if not v or v.lower() in ('', 'nan', 'none'): return False, 0
    try:
        num         = float(v)
        digits_only = v.replace(".", "").replace("-", "").replace("+", "")
        if len(digits_only) > 10: return False, 0
        return True, num
    except ValueError:
        return False, 0
def clean_debts_dataframe(df_raw):
    if df_raw is None or df_raw.empty:
        return df_raw if df_raw is not None else pd.DataFrame()
    clean_cols = [c for c in df_raw.columns if not str(c).startswith("Unnamed")]
    df = df_raw[clean_cols].copy()
    cols_keep = []
    for c in df.columns:
        vals      = df[c].astype(str).str.strip()
        non_empty = vals[vals.apply(lambda v: v.lower() not in ('', 'nan', 'none'))]
        if len(non_empty) == 0: continue
        junk_count = non_empty.apply(is_junk_value).sum()
        if junk_count / max(len(non_empty), 1) > 0.5: continue
        cols_keep.append(c)
    df = df[cols_keep].copy()
    for c in df.columns:
        df[c] = df[c].apply(lambda v: "" if is_junk_value(v) else str(v).strip())
    df = df[df.apply(
        lambda r: any(
            str(v).strip() not in ('', 'nan', 'none', '0', '0.0') for v in r.values
        ), axis=1
    )]
    return df.reset_index(drop=True)
# ══════════════════════════════════════════════════════════════
# РЕНДЕР КАРТОЧКИ ДОЛГА
# ══════════════════════════════════════════════════════════════
def render_debt_cards(debt_df_in):
    """Рендерит glassmorphism-карточки для переданного DataFrame."""
    cols = debt_df_in.columns.tolist()
    for _, row in debt_df_in.iterrows():
        fields_html = ""
        for col_name in cols:
            val = str(row[col_name]).strip()
            if not val or val.lower() in ("nan", "none", ""):
                continue
            col_label = _html_mod.escape(re.sub(r'\.\d+$', '', str(col_name).strip()))
            is_num, num_val = is_real_number(val)
            val_lower = val.lower()
            is_status = any(w in val_lower for w in [
                "оплачен", "закрыт", "выполнен", "готов", "замен", "долг",
                "задолж", "не оплачен", "просроч", "ожидан", "частичн",
                "в процесс", "в работ"
            ])
            if is_status:
                if any(w in val_lower for w in ["оплачен", "закрыт", "выполнен", "готов"]):
                    b_bg, b_color, b_border, b_icon = (
                        "rgba(16,185,129,0.12)", "#065F46", "rgba(16,185,129,0.26)", "✅"
                    )
                elif any(w in val_lower for w in ["долг", "задолж", "не оплачен", "просроч"]):
                    b_bg, b_color, b_border, b_icon = (
                        "rgba(239,68,68,0.12)", "#991B1B", "rgba(239,68,68,0.26)", "⚠️"
                    )
                else:
                    b_bg, b_color, b_border, b_icon = (
                        "rgba(245,158,11,0.12)", "#92400E", "rgba(245,158,11,0.26)", "🔄"
                    )
                val_html = (
                    f'<span style="display:inline-flex;align-items:center;padding:5px 14px;'
                    f'border-radius:999px;font-size:12px;font-weight:800;background:{b_bg};'
                    f'color:{b_color};border:1px solid {b_border};">'
                    f'{b_icon} {_html_mod.escape(val)}</span>'
                )
            elif is_num:
                formatted = (
                    f"{int(num_val):,}".replace(",", " ")
                    if num_val == int(num_val)
                    else f"{num_val:,.1f}".replace(",", " ")
                )
                val_html = (
                    f'<span style="font-size:22px;font-weight:800;letter-spacing:-1px;'
                    f'background:linear-gradient(135deg,#0042CC,#06B6D4);'
                    f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
                    f'background-clip:text;">{formatted}</span>'
                )
            else:
                escaped_val = _html_mod.escape(val)
                escaped_val = re.sub(
                    r'(D\d+K\d+)',
                    r'<span style="background:rgba(99,102,241,0.12);color:#3730A3;padding:2px 8px;'
                    r'border-radius:6px;font-weight:800;font-size:11px;'
                    r'border:1px solid rgba(99,102,241,0.22);">\1</span>',
                    escaped_val
                )
                escaped_val = re.sub(
                    r'(738[0-5]\d{8,})',
                    r'<span style="background:rgba(0,82,255,0.08);color:#0042CC;padding:2px 8px;'
                    r'border-radius:6px;font-weight:800;font-size:11px;'
                    r'border:1px solid rgba(0,82,255,0.16);">\1</span>',
                    escaped_val
                )
                val_html = (
                    f'<span style="font-size:14px;font-weight:600;color:#334155;'
                    f'word-break:break-all;">{escaped_val}</span>'
                )
            fields_html += (
                f'<div style="min-width:160px;flex:1;padding:10px 0;'
                f'border-bottom:1px solid rgba(0,82,255,0.05);">'
                f'<div style="font-size:10px;font-weight:800;color:#94A3B8;'
                f'text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">'
                f'{col_label}</div>{val_html}</div>'
            )
        if fields_html:
            st.markdown(
                f'<div style="background:linear-gradient(145deg,rgba(255,255,255,0.82),'
                f'rgba(228,242,255,0.66));backdrop-filter:blur(24px);'
                f'border-top:1.5px solid rgba(255,255,255,0.96);'
                f'border-left:1px solid rgba(255,255,255,0.88);'
                f'border-right:1px solid rgba(255,255,255,0.60);'
                f'border-bottom:1px solid rgba(255,255,255,0.54);'
                f'border-radius:24px;padding:22px 26px;margin-bottom:14px;'
                f'box-shadow:0 12px 36px rgba(0,82,255,0.08),'
                f'inset 0 1.5px 0 rgba(255,255,255,1);"><div style="display:flex;'
                f'flex-wrap:wrap;gap:20px;">{fields_html}</div></div>',
                unsafe_allow_html=True
            )
# ══════════════════════════════════════════════════════════════
# ВКЛАДКИ
# ══════════════════════════════════════════════════════════════
t_stock, t_debts, t_stat, t_reestr, t_returns, t_news = st.tabs([
    "📦 Остатки",
    "💰 Долги / Замены",
    "📊 Статистика остатки долгов и замены",
    "📑 Архив отгрузок",
    "🔄 Перемещения",
    "📰 Новости",
])
# ════════════════════════════════════════════════════════════
# ВКЛ 1: ОСТАТКИ
# ════════════════════════════════════════════════════════════
with t_stock:
    org_label = (
        user_login if user_filter != "all"
        else (sel_org if sel_org != "Все" else "Все партнёры")
    )
    st.markdown(
        f'<div class="page-title-wrap"><div class="ptw-left"><div class="ptw-dot"></div>'
        f'<div><div class="ptw-title">Сводные показатели</div>'
        f'<div class="ptw-sub">{_html_mod.escape(org_label)}</div>'
        f'</div></div></div>',
        unsafe_allow_html=True
    )
    st_filtered = df_st_f.copy()
    if sel_city != "Все" and not st_filtered.empty and st_filtered.shape[1] > 2:
        st_filtered = st_filtered[
            st_filtered.iloc[:, 2].astype(str).str.contains(sel_city, case=False, na=False)
        ]
    if search_q and not st_filtered.empty:
        st_filtered = st_filtered[
            st_filtered.apply(
                lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1
            )
        ]
    c1, c2, c3 = st.columns(3)
    for i, (col_idx, icon, title, sub) in enumerate([
        (5, "🖨️", "ККТ",   "Кассовые терминалы"),
        (6, "🗂️", "ФН-15", "Фискальный накопитель 15"),
        (7, "🗂️", "ФН-36", "Фискальный накопитель 36"),
    ]):
        val = (
            safe_int(pd.to_numeric(st_filtered.iloc[:, col_idx], errors='coerce').sum())
            if not st_filtered.empty and st_filtered.shape[1] > col_idx
            else 0
        )
        with [c1, c2, c3][i]:
            st.markdown(
                f'<div class="metric-box">'
                f'<div class="metric-icon-wrap">{icon}</div>'
                f'<div class="metric-num">{val}</div>'
                f'<div class="metric-title">{title}</div>'
                f'<div class="metric-sub">{sub}</div></div>',
                unsafe_allow_html=True
            )
    st.write("")
    st.markdown(
        f'<div class="section-hdr"><div class="section-hdr-bar"></div>'
        f'<div class="section-hdr-icon">🛠</div>'
        f'<div class="section-hdr-text">Детальный список складов</div>'
        f'<div class="section-hdr-badge">{len(st_filtered)} позиций</div></div>',
        unsafe_allow_html=True
    )
    if st_filtered.empty:
        st.info("📭 Ничего не найдено.")
    else:
        rows_html = ""
        for i, (_, row) in enumerate(st_filtered.iterrows(), 1):
            region  = _html_mod.escape(str(safe_iloc(row, 0)))
            city    = _html_mod.escape(str(safe_iloc(row, 2)))
            partner = _html_mod.escape(str(safe_iloc(row, 1)))
            kkt  = safe_int(safe_iloc(row, 5, 0))
            fn15 = safe_int(safe_iloc(row, 6, 0))
            fn36 = safe_int(safe_iloc(row, 7, 0))
            rows_html += (
                f'<div class="stock-row">'
                f'<div class="sr-index">#{i}</div>'
                f'<div class="sr-region">{region}</div>'
                f'<div class="sr-city">{city}</div>'
                f'<div class="sr-partner">{partner}</div>'
                f'<div class="sr-divider-v"></div>'
                f'<div class="sr-stats">'
                f'<div class="sr-stat"><div class="sr-stat-num">{kkt}</div>'
                f'<div class="sr-stat-lbl">ККТ</div></div>'
                f'<div class="sr-stat"><div class="sr-stat-num">{fn15}</div>'
                f'<div class="sr-stat-lbl">ФН-15</div></div>'
                f'<div class="sr-stat"><div class="sr-stat-num">{fn36}</div>'
                f'<div class="sr-stat-lbl">ФН-36</div></div>'
                f'</div></div>'
            )
        st.markdown(rows_html, unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════
# ВКЛ 2: ДОЛГИ / ЗАМЕНЫ (столбцы A–L, индексы 0–11)
# ════════════════════════════════════════════════════════════
with t_debts:
    st.markdown(
        '<div class="page-title-wrap"><div class="ptw-left"><div class="ptw-dot"></div>'
        '<div><div class="ptw-title">Долги партнёров / Статусы замен</div>'
        '<div class="ptw-sub">Данные по задолженностям и заменам оборудования</div>'
        '</div></div></div>',
        unsafe_allow_html=True
    )
    if df_debts_raw is None or df_debts_raw.empty:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;">'
            '<div style="font-size:52px;margin-bottom:14px;">📭</div>'
            '<div style="font-size:16px;font-weight:700;color:#64748B;">Нет данных о долгах</div></div>',
            unsafe_allow_html=True
        )
    else:
        debt_df = clean_debts_dataframe(df_debts_raw)
        # Берём только первые 12 столбцов (A–L)
        if debt_df.shape[1] > 12:
            debt_df = debt_df.iloc[:, :12]
        if user_filter != "all":
            mask = debt_df.apply(
                lambda r: r.astype(str).str.contains(user_filter, case=False, na=False).any(),
                axis=1
            )
            debt_df = debt_df[mask]
        elif sel_org != "Все":
            mask = debt_df.apply(
                lambda r: r.astype(str).str.contains(sel_org, case=False, na=False).any(),
                axis=1
            )
            debt_df = debt_df[mask]
        if search_q and not debt_df.empty:
            debt_df = debt_df[
                debt_df.apply(
                    lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1
                )
            ]
        if debt_df.empty:
            msg = (
                "Данных по вашей организации не найдено."
                if user_filter != "all"
                else "Нет записей по выбранным фильтрам."
            )
            st.info(f"📭 {msg}")
        else:
            st.markdown(
                f'<div class="section-hdr"><div class="section-hdr-bar"></div>'
                f'<div class="section-hdr-icon">📋</div>'
                f'<div class="section-hdr-text">Детальные записи</div>'
                f'<div class="section-hdr-badge">{len(debt_df)} записей</div></div>',
                unsafe_allow_html=True
            )
            render_debt_cards(debt_df)
            output_debts = io.BytesIO()
            try:
                with pd.ExcelWriter(output_debts, engine='openpyxl') as writer:
                    debt_df.to_excel(writer, index=False, sheet_name='Долги')
                output_debts.seek(0)
                st.download_button(
                    label="📥 Скачать долги (Excel)",
                    data=output_debts.getvalue(),
                    file_name="Dolgi_Zameny.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_debts"
                )
            except Exception as ex:
                logger.error(f"Ошибка экспорта долгов: {ex}")
# ════════════════════════════════════════════════════════════
# ВКЛ 3: СТАТИСТИКА (столбцы M–AB, индексы 12–27)
# ════════════════════════════════════════════════════════════
with t_stat:
    org_label_stat = (
        user_login if user_filter != "all"
        else (sel_org if sel_org != "Все" else "Все партнёры")
    )
    st.markdown(
        f'<div class="page-title-wrap"><div class="ptw-left"><div class="ptw-dot"></div>'
        f'<div><div class="ptw-title">Статистика остатки долгов и замены</div>'
        f'<div class="ptw-sub">{_html_mod.escape(org_label_stat)}</div>'
        f'</div></div></div>',
        unsafe_allow_html=True
    )

    if df_debts_raw is None or df_debts_raw.empty:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;">'
            '<div style="font-size:52px;margin-bottom:14px;">📭</div>'
            '<div style="font-size:16px;font-weight:700;color:#64748B;">'
            'Нет данных для статистики</div></div>',
            unsafe_allow_html=True
        )
    else:
        debt_full    = df_debts_raw.copy()
        total_cols_d = debt_full.shape[1]
        end_col      = min(28, total_cols_d)

        if end_col <= 12:
            st.info("📭 Столбцы M–AB отсутствуют в таблице.")
        else:
            # ── Берём столбцы M–AB (индексы 12–27)
            stat_full = debt_full.iloc[:, 12:end_col].copy()

            # Переименование Unnamed-столбцов
            new_cols = []
            for i, c in enumerate(stat_full.columns):
                new_cols.append(
                    f"Столбец {12 + i + 1}"
                    if str(c).startswith("Unnamed")
                    else str(c).strip()
                )
            stat_full.columns = new_cols

            # Очистка мусора
            for c in stat_full.columns:
                stat_full[c] = stat_full[c].apply(
                    lambda v: "" if is_junk_value(v) else str(v).strip()
                )

            # Удаляем полностью пустые строки
            stat_full = stat_full[
                stat_full.apply(
                    lambda r: any(
                        str(v).strip() not in ('', 'nan', 'none', '0', '0.0')
                        for v in r.values
                    ), axis=1
                )
            ].reset_index(drop=True)

            # Удаляем пустые столбцы
            cols_keep = [
                c for c in stat_full.columns
                if stat_full[c].apply(lambda v: v not in ('', 'nan', 'none')).any()
            ]
            stat_full = stat_full[cols_keep]

            # ══════════════════════════════════════════════════
            # ФИЛЬТРАЦИЯ ПО ПАРТНЁРУ
            # Ищем столбец "Сервис Партнер" (или похожий) в stat_full
            # ══════════════════════════════════════════════════

            # Маппинг user_filter → названия в таблице
            PARTNER_MAP = {
                "АТМ":                    ["ООО АТМ", "АТМ АЛЬЯНС"],
                "АРЕС-КОМПАНИ-М":         ["АРЕС", "КОРИТЕК", "ООО АРЕС"],
                "БР":                     ["ООО БР", "БР"],
                "Автоматизация Бизнеса":  ["АВТОМАТИЗАЦИЯ", "АБ", "Автоматизация Бизнеса"],
            }

            def row_matches_partner(row_series, filter_val):
                """True если хотя бы одна ячейка строки содержит партнёра."""
                aliases = PARTNER_MAP.get(filter_val, [filter_val])
                row_str = " ".join(str(v) for v in row_series.values).upper()
                for alias in aliases:
                    if alias.upper() in row_str:
                        return True
                # Прямое вхождение filter_val
                if filter_val.upper() in row_str:
                    return True
                return False

            if user_filter != "all":
                # Партнёр видит ТОЛЬКО свои строки
                mask_p = stat_full.apply(
                    lambda r: row_matches_partner(r, user_filter), axis=1
                )
                stat_df = stat_full[mask_p].copy()
            elif sel_org != "Все":
                # Админ выбрал конкретную организацию
                mask_p = stat_full.apply(
                    lambda r: row_matches_partner(r, sel_org), axis=1
                )
                stat_df = stat_full[mask_p].copy()
            else:
                # Админ видит всё
                stat_df = stat_full.copy()

            # Поисковый фильтр
            if search_q and not stat_df.empty:
                stat_df = stat_df[
                    stat_df.apply(
                        lambda r: r.astype(str).str.contains(search_q, case=False).any(),
                        axis=1
                    )
                ]

            if stat_df.empty:
                if user_filter != "all":
                    st.info(
                        f"📭 Данных статистики по «{_html_mod.escape(user_login)}» не найдено."
                    )
                else:
                    st.info("📭 Нет записей по выбранным фильтрам.")
            else:
                # ── Числовые сводные метрики
                num_metrics = []
                for c in stat_df.columns:
                    col_vals = [is_real_number(v) for v in stat_df[c]]
                    total    = sum(nv for ok, nv in col_vals if ok)
                    count    = sum(1 for ok, _ in col_vals if ok)
                    if count > 0:
                        num_metrics.append((c, total, count))

                if num_metrics:
                    icons_cycle  = ["📊", "💰", "🔄", "📦", "🏷️", "📋", "🗂️", "🖨️"]
                    cols_per_row = min(len(num_metrics), 4)
                    for chunk_start in range(0, min(len(num_metrics), 8), cols_per_row):
                        chunk  = num_metrics[chunk_start:chunk_start + cols_per_row]
                        cols_w = st.columns(len(chunk))
                        for j, (col_name, total_val, cnt) in enumerate(chunk):
                            ic = icons_cycle[(chunk_start + j) % len(icons_cycle)]
                            formatted_val = (
                                f"{int(total_val):,}".replace(",", " ")
                                if total_val == int(total_val)
                                else f"{total_val:,.1f}".replace(",", " ")
                            )
                            short_name = col_name[:20] + ("..." if len(col_name) > 20 else "")
                            with cols_w[j]:
                                st.markdown(
                                    f'<div class="metric-box" style="min-height:140px;">'
                                    f'<div class="metric-icon-wrap">{ic}</div>'
                                    f'<div class="metric-num" style="font-size:32px;">'
                                    f'{formatted_val}</div>'
                                    f'<div class="metric-title" style="font-size:11px;">'
                                    f'{_html_mod.escape(short_name)}</div>'
                                    f'<div class="metric-sub">{cnt} записей</div></div>',
                                    unsafe_allow_html=True
                                )
                    st.write("")

                # ── Детальные карточки
                st.markdown(
                    f'<div class="section-hdr"><div class="section-hdr-bar"></div>'
                    f'<div class="section-hdr-icon">📋</div>'
                    f'<div class="section-hdr-text">Детальные данные (M–AB)</div>'
                    f'<div class="section-hdr-badge">{len(stat_df)} записей</div></div>',
                    unsafe_allow_html=True
                )
                render_debt_cards(stat_df)

                # ── Экспорт Excel
                output_stat = io.BytesIO()
                try:
                    with pd.ExcelWriter(output_stat, engine='openpyxl') as writer:
                        stat_df.to_excel(writer, index=False, sheet_name='Статистика')
                    output_stat.seek(0)
                    st.download_button(
                        label="📥 Скачать статистику (Excel)",
                        data=output_stat.getvalue(),
                        file_name="Statistika_Ostatki_Dolgi_Zameny.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_stat"
                    )
                except Exception as ex:
                    logger.error(f"Ошибка экспорта статистики: {ex}")

# ════════════════════════════════════════════════════════════
# ВКЛ 4: АРХИВ ОТГРУЗОК
# ════════════════════════════════════════════════════════════
with t_reestr:
    if df_ship_raw is None or df_ship_raw.empty:
        st.info("📭 Нет данных об отгрузках.")
    else:
        final_df = df_ship_raw.copy()
        if user_filter != "all" and final_df.shape[1] > 2:
            final_df = final_df[
                final_df.iloc[:, 2].astype(str).str.contains(user_filter, case=False)
            ]
        elif sel_org != "Все" and final_df.shape[1] > 2:
            final_df = final_df[final_df.iloc[:, 2] == sel_org]
        if sel_city != "Все" and final_df.shape[1] > 1:
            final_df = final_df[final_df.iloc[:, 1] == sel_city]
        if date_mode != "Весь период" and final_df.shape[1] > 12:
            dm = safe_date_col(final_df, 12)
            final_df = final_df[
                dm &
                (final_df.iloc[:, 12].dt.date >= date_from) &
                (final_df.iloc[:, 12].dt.date <= date_to)
            ]
        if search_q and not final_df.empty:
            final_df = final_df[
                final_df.apply(
                    lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1
                )
            ]
        st.markdown(
            f'<div class="section-hdr"><div class="section-hdr-bar"></div>'
            f'<div class="section-hdr-icon">📑</div>'
            f'<div class="section-hdr-text">Архив отгрузок</div>'
            f'<div class="section-hdr-badge">{len(final_df)} записей</div></div>',
            unsafe_allow_html=True
        )
        if final_df.empty:
            st.info("📭 Нет отгрузок по выбранным фильтрам.")
        else:
            for idx, row in final_df.iterrows():
                dv     = safe_iloc(row, 12)
                ds     = fmt_date_ru(dv) if hasattr(dv, 'day') and pd.notnull(dv) else "—"
                is_way = "ПУТ" in str(safe_iloc(row, 11)).upper()
                st_txt = "🚚 В ПУТИ" if is_way else "✅ ДОСТАВЛЕНО"
                st_css = "badge-way"  if is_way else "badge-deliv"
                city   = _html_mod.escape(str(safe_iloc(row, 1)))
                client = _html_mod.escape(str(safe_iloc(row, 2)))
                rec_id = _html_mod.escape(str(safe_iloc(row, 14)))
                chips  = equip_chips_archive(str(safe_iloc(row, 7)))
                st.markdown(
                    f'<div class="ship-card">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'margin-bottom:13px;position:relative;z-index:1;">'
                    f'<span class="badge {st_css}">{st_txt}</span>'
                    f'<span style="color:#94A3B8;font-size:11px;font-weight:700;'
                    f'background:rgba(0,82,255,0.05);padding:3px 10px;border-radius:8px;'
                    f'border:1px solid rgba(0,82,255,0.10);">ID: {rec_id}</span></div>'
                    f'<div style="font-size:18px;font-weight:800;color:#0F172A;'
                    f'position:relative;z-index:1;">{ds} &nbsp;·&nbsp; {city}</div>'
                    f'<div style="font-size:14px;font-weight:700;color:#0052FF;margin-top:3px;'
                    f'position:relative;z-index:1;">{client}</div>'
                    f'<div class="equip-chips" style="position:relative;z-index:1;">'
                    f'{chips}</div></div>',
                    unsafe_allow_html=True
                )
                with st.expander("📝 Серийные номера", expanded=False):
                    shtml = parse_serials_html(str(safe_iloc(row, 10)))
                    st.markdown(
                        f'<div style="font-size:13px;line-height:2.0;">{shtml}</div>',
                        unsafe_allow_html=True
                    )
                    b1, b2, _ = st.columns([1.1, 1.1, 2.2])
                    with b1:
                        tu = str(safe_iloc(row, 13))
                        if "http" in tu:
                            st.link_button("🚀 Трек", tu, use_container_width=True, key=f"t_{idx}")
                        else:
                            st.button(
                                "Нет трека", disabled=True,
                                use_container_width=True, key=f"nt_{idx}"
                            )
                    with b2:
                        row_excel = make_excel(pd.DataFrame([row]))
                        if row_excel:
                            st.download_button(
                                "📑 Excel", data=row_excel,
                                file_name=f"Shipment_{idx}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"ex_{idx}", use_container_width=True
                            )
# ════════════════════════════════════════════════════════════
# ВКЛ 5: ПЕРЕМЕЩЕНИЯ
# ════════════════════════════════════════════════════════════
with t_returns:
    if df_return_raw is None or df_return_raw.empty:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;">'
            '<div style="font-size:52px;margin-bottom:14px;">📭</div>'
            '<div style="font-size:16px;font-weight:700;color:#64748B;">'
            'Нет данных о перемещениях</div></div>',
            unsafe_allow_html=True
        )
    else:
        ret_df = df_return_raw.copy()
        if user_filter != "all":
            mask = (
                ret_df.get("org_from", pd.Series(dtype=str)).astype(str)
                .str.contains(user_filter, case=False, na=False) |
                ret_df.get("org_to", pd.Series(dtype=str)).astype(str)
                .str.contains(user_filter, case=False, na=False)
            )
            ret_df = ret_df[mask]
        elif sel_org != "Все":
            mask = (
                ret_df.get("org_from", pd.Series(dtype=str)).astype(str)
                .str.contains(sel_org, case=False, na=False) |
                ret_df.get("org_to", pd.Series(dtype=str)).astype(str)
                .str.contains(sel_org, case=False, na=False)
            )
            ret_df = ret_df[mask]
        if "date" in ret_df.columns and date_mode != "Весь период":
            ret_df = ret_df[
                ret_df["date"].notna() &
                (ret_df["date"] >= pd.Timestamp(date_from)) &
                (ret_df["date"] <= pd.Timestamp(date_to) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
            ]
        if sel_city != "Все":
            mc = (
                ret_df.get("city_from", pd.Series(dtype=str)).astype(str)
                .str.contains(sel_city, case=False, na=False) |
                ret_df.get("city_to", pd.Series(dtype=str)).astype(str)
                .str.contains(sel_city, case=False, na=False)
            )
            ret_df = ret_df[mc]
        if search_q and not ret_df.empty:
            ret_df = ret_df[
                ret_df.apply(
                    lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1
                )
            ]
        st.markdown(
            f'<div class="section-hdr"><div class="section-hdr-bar"></div>'
            f'<div class="section-hdr-icon">🔄</div>'
            f'<div class="section-hdr-text">Возврат / Перемещение</div>'
            f'<div class="section-hdr-badge">{len(ret_df)} записей</div></div>',
            unsafe_allow_html=True
        )
        if not ret_df.empty:
            ret_excel_all = make_excel_return(ret_df)
            if ret_excel_all:
                st.download_button(
                    label="📦 Скачать все (Excel)", data=ret_excel_all,
                    file_name="Vozvrat_Peremeschenie.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_ret_all"
                )
        if ret_df.empty:
            st.info("📭 Нет записей по выбранным фильтрам.")
        else:
            for idx, row in ret_df.iterrows():
                dv  = row.get("date", "")
                ds  = fmt_date_ru(dv) if hasattr(dv, 'day') and pd.notnull(dv) else "—"
                cf2 = _html_mod.escape(str(row.get("city_from", "")))
                of  = str(row.get("org_from", ""))
                af  = str(row.get("addr_from", "")).strip()
                pf  = str(row.get("person_from", "")).strip()
                ct2 = _html_mod.escape(str(row.get("city_to", "")))
                ot  = str(row.get("org_to", ""))
                at_ = str(row.get("addr_to", "")).strip()
                pt  = str(row.get("person_to", "")).strip()
                ph  = clean_phone(str(row.get("phone_to", "")))
                tr2 = str(row.get("track", "")).strip()
                ht  = "http" in tr2.lower()
                k   = clean_num(str(row.get("kkt", "")))
                f1  = clean_num(str(row.get("fn15", "")))
                f3  = clean_num(str(row.get("fn36", "")))
                ac, br2  = ret_card_style(of, ot)
                csf, icf = org_css_icon(of)
                cst, ict = org_css_icon(ot)
                ch = ""
                if k  not in ("0", "", "nan"):
                    ch += (
                        f'<div class="eq-chip" style="background:linear-gradient(135deg,'
                        f'rgba(0,82,255,0.09),rgba(6,182,212,0.06));border:1px solid rgba(0,82,255,0.16);">'
                        f'<span style="font-size:18px;">🖨️</span>'
                        f'<div><div class="eq-num" style="color:#0042CC;">{k}</div>'
                        f'<div class="eq-lbl">ККТ</div></div></div>'
                    )
                if f1 not in ("0", "", "nan"):
                    ch += (
                        f'<div class="eq-chip" style="background:linear-gradient(135deg,'
                        f'rgba(16,185,129,0.10),rgba(16,185,129,0.05));border:1px solid rgba(16,185,129,0.20);">'
                        f'<span style="font-size:18px;">🗂️</span>'
                        f'<div><div class="eq-num" style="color:#065F46;">{f1}</div>'
                        f'<div class="eq-lbl">ФН-15</div></div></div>'
                    )
                if f3 not in ("0", "", "nan"):
                    ch += (
                        f'<div class="eq-chip" style="background:linear-gradient(135deg,'
                        f'rgba(99,102,241,0.11),rgba(99,102,241,0.05));border:1px solid rgba(99,102,241,0.20);">'
                        f'<span style="font-size:18px;">🗂️</span>'
                        f'<div><div class="eq-num" style="color:#3730A3;">{f3}</div>'
                        f'<div class="eq-lbl">ФН-36</div></div></div>'
                    )
                if not ch:
                    ch = '<span style="color:#94A3B8;font-size:13px;">—</span>'
                def opt(ic, vl):
                    v = str(vl).strip()
                    if not v or v.lower() in ("nan", "0", "", "none"): return ""
                    return f'<div class="route-info">{ic} {_html_mod.escape(v)}</div>'
                ex = sum([
                    1 if af  and af.lower()  not in ("nan", "", "none") else 0,
                    1 if pf  and pf.lower()  not in ("nan", "", "none") else 0,
                    1 if at_ and at_.lower() not in ("nan", "", "none") else 0,
                    1 if pt  and pt.lower()  not in ("nan", "", "none") else 0,
                    1 if ph  and ph          not in ("", "nan", "0", "none") else 0,
                ])
                card_h    = 310 + ex * 26
                card_html = f"""<!DOCTYPE html>
<html><head><style>{CARD_CSS}</style></head><body>
<div class="card">
  <div class="card-head">
    <div class="badge-move">🔄 ПЕРЕМЕЩЕНИЕ</div>
    <div class="date-pill">📅 {ds}</div>
  </div>
  <div class="route-wrap">
    <div class="route-box" style="background:{ac};border:1px solid {br2};">
      <div class="route-lbl">📤 Откуда</div>
      <div class="route-city">{cf2 if cf2 and cf2.lower() not in ('nan','') else '—'}</div>
      <div class="badge-org {csf}">{icf} {_html_mod.escape(of) if of and of.lower() not in ('nan','') else '—'}</div>
      {opt("📍", af)}{opt("👤", pf)}
    </div>
    <div class="arrow-wrap"><div class="arrow-circle">→</div></div>
    <div class="route-box" style="background:{ac};border:1px solid {br2};">
      <div class="route-lbl">📥 Куда</div>
      <div class="route-city">{ct2 if ct2 and ct2.lower() not in ('nan','') else '—'}</div>
      <div class="badge-org {cst}">{ict} {_html_mod.escape(ot) if ot and ot.lower() not in ('nan','') else '—'}</div>
      {opt("📍", at_)}{opt("👤", pt)}{opt("📞", ph)}
    </div>
  </div>
  <div class="equip-section">
    <div class="equip-lbl">📦 Оборудование</div>
    <div class="equip-chips">{ch}</div>
  </div>
</div>
</body></html>"""
                components.html(card_html, height=card_h, scrolling=False)
                with st.expander("📝 Серийные номера", expanded=False):
                    sr = str(row.get("serials", ""))
                    if sr and sr.lower() not in ("", "nan", "none"):
                        shtml = parse_serials_html(sr)
                        st.markdown(
                            f'<div style="font-size:13px;line-height:2.2;">{shtml}</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.caption("Серийные номера не указаны")
                    rb1, rb2, _ = st.columns([1.2, 1.6, 1.6])
                    with rb1:
                        if ht:
                            st.link_button(
                                "🚀 Трек", tr2,
                                use_container_width=True, key=f"rt_{idx}"
                            )
                        else:
                            st.button(
                                "Нет трека", disabled=True,
                                use_container_width=True, key=f"rnt_{idx}"
                            )
                    with rb2:
                        row_ret_excel = make_excel_return(pd.DataFrame([row]))
                        if row_ret_excel:
                            st.download_button(
                                "📑 Excel", data=row_ret_excel,
                                file_name=f"Return_{idx}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"rdl_{idx}", use_container_width=True
                            )
# ════════════════════════════════════════════════════════════
# ВКЛ 6: НОВОСТИ
# ════════════════════════════════════════════════════════════
with t_news:
    st.markdown(
        '<div class="section-hdr"><div class="section-hdr-bar"></div>'
        '<div class="section-hdr-icon">📰</div>'
        '<div class="section-hdr-text">Лента новостей</div>'
        '<div class="section-hdr-badge" style="background:rgba(16,185,129,0.10);'
        'color:#065F46;border-color:rgba(16,185,129,0.22);">🤖 Авто</div></div>',
        unsafe_allow_html=True
    )
    if not auto_news:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;color:#94A3B8;">'
            '<div style="font-size:52px;margin-bottom:14px;opacity:0.6;">📭</div>'
            '<div style="font-size:16px;font-weight:700;color:#64748B;">'
            'Нет данных для отображения</div></div>',
            unsafe_allow_html=True
        )
    else:
        for n in auto_news:
            icon_n   = n.get("icon",   "📰")
            title_n  = _html_mod.escape(str(n.get("title",  "")))
            text_n   = _html_mod.escape(str(n.get("text",   "")))
            color_n  = n.get("color",  "#0052FF")
            bg_n     = n.get("bg",     "rgba(0,82,255,0.07)")
            border_n = n.get("border", "rgba(0,82,255,0.18)")
            is_tod   = n.get("today",  False)
            today_b  = (
                '<span style="font-size:10px;font-weight:800;color:white;'
                'background:linear-gradient(135deg,#EF4444,#F97316);'
                'padding:3px 10px;border-radius:7px;">🆕 СЕГОДНЯ</span>'
                if is_tod else ""
            )
            st.markdown(
                f'<div style="background:linear-gradient(145deg,rgba(255,255,255,0.82),'
                f'rgba(224,242,255,0.66));backdrop-filter:blur(22px);'
                f'border-top:1.5px solid rgba(255,255,255,0.96);'
                f'border-left:4px solid {color_n};border-right:1px solid rgba(255,255,255,0.60);'
                f'border-bottom:1px solid rgba(255,255,255,0.54);border-radius:20px;'
                f'padding:20px 22px;margin-bottom:14px;'
                f'box-shadow:0 10px 32px rgba(0,82,255,0.07);">'
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
                f'<div style="width:48px;height:48px;border-radius:15px;background:{bg_n};'
                f'border:1px solid {border_n};display:flex;align-items:center;'
                f'justify-content:center;font-size:24px;">{icon_n}</div>'
                f'<div style="flex:1;"><div style="margin-bottom:5px;">{today_b}</div>'
                f'<div style="font-size:15px;font-weight:800;color:#0F172A;">{title_n}</div>'
                f'</div></div>'
                f'<div style="font-size:13px;font-weight:600;color:#64748B;line-height:1.6;'
                f'padding:12px 14px;background:{bg_n};border-radius:12px;'
                f'border:1px solid {border_n};">{text_n}</div></div>',
                unsafe_allow_html=True
            )
    st.markdown(
        '<div class="section-hdr" style="margin-top:28px;"><div class="section-hdr-bar"></div>'
        '<div class="section-hdr-icon">📊</div>'
        '<div class="section-hdr-text">Статистика</div></div>',
        unsafe_allow_html=True
    )
    def _fs(df):
        if df is None or df.empty or df.shape[1] <= 2:
            return df if df is not None else pd.DataFrame()
        if user_filter != "all":
            return df[df.iloc[:, 2].astype(str).str.contains(user_filter, case=False, na=False)]
        return df
    df_sf = _fs(df_ship_raw)
    if df_sf is not None and not df_sf.empty and df_sf.shape[1] > 12:
        dm       = safe_date_col(df_sf, 12)
        ts_count = len(df_sf[dm & (df_sf.iloc[:, 12].dt.date == date.today())])
        ws_count = len(df_sf[dm & (df_sf.iloc[:, 12].dt.date >= date.today() - timedelta(days=7))])
        wa_count = len(df_sf[df_sf.iloc[:, 11].astype(str).str.upper().str.contains("ПУТ", na=False)])
    else:
        ts_count = ws_count = wa_count = 0
    tr_count = 0
    if df_return_raw is not None and not df_return_raw.empty and "date" in df_return_raw.columns:
        tr_count = len(
            df_return_raw[
                df_return_raw["date"].notna() &
                (df_return_raw["date"].dt.date == date.today())
            ]
        )
    c1, c2, c3, c4 = st.columns(4)
    for col_w, val, lbl, sub, icon in [
        (c1, ts_count, "Сегодня",  "отправок", "🚚"),
        (c2, ws_count, "Неделя",   "отправок", "📅"),
        (c3, tr_count, "Перемещ.", "сегодня",  "🔄"),
        (c4, wa_count, "В пути",   "сейчас",   "📍"),
    ]:
        with col_w:
            st.markdown(
                f'<div class="metric-box" style="min-height:130px;">'
                f'<div class="metric-icon-wrap">{icon}</div>'
                f'<div class="metric-num" style="font-size:36px;">{val}</div>'
                f'<div class="metric-title">{lbl}</div>'
                f'<div class="metric-sub">{sub}</div></div>',
                unsafe_allow_html=True
            )
