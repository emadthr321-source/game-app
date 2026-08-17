import json
import os
import streamlit as st
import pandas as pd
import copy

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="لعبة ترابيع الاحترافية", page_icon="🔲", layout="wide"
)

# --- تنسيق التصميم (Dark Glassmorphism & Custom Fonts) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #2c1624 0%, #1a0c17 100%);
        color: #ffffff;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    h1, h2, h3 {
        font-weight: 900 !important;
        color: #f3e8ff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- تهيئة حالة اللعبة (Session State) ---
GRID_ROWS = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح", "ط", "ي"]
GRID_COLS = list(range(1, 11))  # من 1 إلى 10

# إعداد المجموعات وألوانها الرسمية حسب طلبك
TEAMS = {
    "الإخاء": {"color": "#00d2ff", "bg": "🔵", "name_ar": "الإخاء"},
    "المحبة": {"color": "#ffffff", "bg": "⚪️", "name_ar": "المحبة"},
    "الوفاق": {"color": "#ff4d4d", "bg": "🔴", "name_ar": "الوفاق"},
    "الوصال": {"color": "#555555", "bg": "⚫️", "name_ar": "الوصال"},
}

if "board" not in st.session_state:
    st.session_state.board = {f"{r}{c}": None for r in GRID_ROWS for c in GRID_COLS}

if "history" not in st.session_state:
    st.session_state.history = []

if "current_team_idx" not in st.session_state:
    st.session_state.current_team_idx = 0

team_names = list(TEAMS.keys())
current_team_name = team_names[st.session_state.current_team_idx]

# --- العنوان الرئيسي ---
st.markdown(
    "<h1 style='text-align: center; font-size: 3rem;'>🔲 لعبة ترابيع الاحترافية 🔲</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size: 1.2rem; color: #d8b4fe;'>قاعدة الاستحواذ (+): كل مربع تختاره يمنحك 4 مربعات إضافية حوله لتصبح 5 مربعات!</p>",
    unsafe_allow_html=True,
)

col_control, col_board = st.columns([1, 3])

# --- لوحة التحكم الجانبية ---
with col_control:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📊 لوحة التحكم والمجموعات")

    current_info = TEAMS[current_team_name]
    st.markdown(
        f"**دور الأسرة الحالية:** <span style='color: {current_info['color']}; font-size: 1.4rem; font-weight: bold;'>{current_info['bg']} {current_team_name}</span>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### 🏆 النقاط (المربعات المسيطر عليها):")

    team_scores = {t: 0 for t in TEAMS}
    for cell, owner in st.session_state.board.items():
        if owner in team_scores:
            team_scores[owner] += 1

    for t, info in TEAMS.items():
        score = team_scores[t]
        st.markdown(
            f"- <span style='color: {info['color']}; font-weight: bold;'>{info['bg']} {t}</span>: **{score}** مربع",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # زر التراجع عن آخر خطوة (Undo)
    if st.button("↩️ تراجع خطوة للخلف", use_container_width=True):
        if st.session_state.history:
            last_state = st.session_state.history.pop()
            st.session_state.board = last_state["board"]
            st.session_state.current_team_idx = last_state["team_idx"]
            st.success("تم التراجع بنجاح!")
            st.rerun()
        else:
            st.warning("لا توجد خطوات للتراجع عنها!")

    # زر إعادة الضبط
    if st.button("🔄 إعادة ضبط اللوحة", use_container_width=True):
        st.session_state.board = {
            f"{r}{c}": None for r in GRID_ROWS for c in GRID_COLS
        }
        st.session_state.history = []
        st.session_state.current_team_idx = 0
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# --- لوحة اللعب (Grid) ---
with col_board:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🔲 لوحة المربعات (نظام الاستحواذ التلقائي)")

    # رأس الأعمدة
    cols_ui = st.columns(len(GRID_COLS) + 1)
    cols_ui[0].markdown(
        "<p style='text-align:center; font-weight:bold;'>ج/ص</p>",
        unsafe_allow_html=True,
    )
    for idx, c in enumerate(GRID_COLS):
        cols_ui[idx + 1].markdown(
            f"<p style='text-align:center; font-weight:bold; font-size:1.1rem;'>{c}</p>",
            unsafe_allow_html=True,
        )

    # صفوف اللوحة
    for r_idx, r in enumerate(GRID_ROWS):
        row_cols = st.columns(len(GRID_COLS) + 1)
        row_cols[0].markdown(
            f"<p style='text-align:center; font-weight:bold; font-size:1.2rem; color:#f3e8ff;'>{r}</p>",
            unsafe_allow_html=True,
        )

        for c_idx, c in enumerate(GRID_COLS):
            cell_key = f"{r}{c}"
            owner = st.session_state.board[cell_key]

            # تلوين المربع بناءً على الأسرة المسيطرة
            if owner and owner in TEAMS:
                team_color = TEAMS[owner]["color"]
                btn_label = f"{TEAMS[owner]['bg']}"
            else:
                btn_label = f"{cell_key}"

            with row_cols[c_idx + 1]:
                if st.button(
                    btn_label, key=f"btn_{cell_key}", use_container_width=True
                ):
                    # حفظ الحالة الحالية للـ Undo
                    st.session_state.history.append(
                        {
                            "board": copy.deepcopy(st.session_state.board),
                            "team_idx": st.session_state.current_team_idx,
                        }
                    )

                    # تحديد المربعات الخمسة (المربع الأساسي + الأربعة المجاورة على شكل +)
                    target_cells = [cell_key]  # المربع الأساسي

                    # إضافة المجاورة (أعلى، أسفل، يمين، يسار إن وجدت ضمن الحدود)
                    # الأعلى
                    if r_idx > 0:
                        target_cells.append(f"{GRID_ROWS[r_idx - 1]}{c}")
                    # الأسفل
                    if r_idx < len(GRID_ROWS) - 1:
                        target_cells.append(f"{GRID_ROWS[r_idx + 1]}{c}")
                    # اليسار (العمود السابق)
                    if c_idx > 0:
                        target_cells.append(f"{r}{GRID_COLS[c_idx - 1]}")
                    # اليمين (العمود اللاحق)
                    if c_idx < len(GRID_COLS) - 1:
                        target_cells.append(f"{r}{GRID_COLS[c_idx + 1]}")

                    # تطبيق التلطيخ/الاستحواذ للمجموعة الحالية على المربعات المشمولة
                    for target in target_cells:
                        st.session_state.board[target] = current_team_name

                    # انتقال الدور تلقائياً للأسرة التالية
                    st.session_state.current_team_idx = (
                        st.session_state.current_team_idx + 1
                    ) % len(TEAMS)
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
