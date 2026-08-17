import json
import os
import streamlit as st
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="لعبة ترابيع - النظام الاحترافي", page_icon="🔲", layout="wide"
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

    /* تنسيق أزرار المربعات في اللوحة */
    .grid-btn {
        font-size: 18px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 10px !important;
        transition: all 0.3s ease;
    }
    
    /* تأثير الزجاج المعتم للعناصر */
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

# إعداد المجموعات وألوانها الرسمية
TEAMS = {
    "الإخاء": {"color": "#00d2ff", "bg": "🔵", "score": 0},
    "المحبة": {"color": "#ffffff", "bg": "⚪️", "score": 0},
    "الوفاق": {"color": "#ff4d4d", "bg": "🔴", "score": 0},
    "الوصال": {"color": "#333333", "bg": "⚫️", "score": 0},
}

if "board" not in st.session_state:
    # تخزين لون/اسم المجموعة المسيطرة على كل مربع
    st.session_state.board = {f"{r}{c}": None for r in GRID_ROWS for c in GRID_COLS}

if "history" not in st.session_state:
    # قائمة لحفظ الخطوات بهدف التراجع (Undo)
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
    "<p style='text-align: center; font-size: 1.2rem; color: #d8b4fe;'>استحوذ على أكبر قدر من المربعات، كل مربع يمنحك 4 مربعات إضافية (+)!</p>",
    unsafe_allow_html=True,
)

# --- الشريط الجانبي أو لوحة التحكم الجانبية لإدارة الدور والمجموعات ---
col_control, col_board = st.columns([1, 3])

with col_control:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📊 لوحة التحكم والمجموعات")

    # عرض الدور الحالي
    current_info = TEAMS[current_team_name]
    st.markdown(
        f"**دور الفريق الحالي:** <span style='color: {current_info['color']}; font-size: 1.5rem; font-weight: bold;'>{current_info['bg']} {current_team_name}</span>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### 🏆 النقاط الحالية:")

    # حساب النقاط بناءً على المربعات المسيطر عليها
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
    if st.button("↩️ تراجع عن الخطوة السابقة", use_container_width=True):
        if st.session_state.history:
            last_state = st.session_state.history.pop()
            st.session_state.board = last_state["board"]
            st.session_state.current_team_idx = last_state["team_idx"]
            st.success("تم التراجع عن آخر خطوة بنجاح!")
            st.rerun()
        else:
            st.warning("لا توجد خطوات للتراجع عنها!")

    # زر إعادة ضبط اللعبة
    if st.button("🔄 إعادة ضبط اللعبة", use_container_width=True):
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
    st.markdown("### 🔲 لوحة المربعات (اضغط على المربع للاستحواذ)")

    # رسم الأعمدة كأرقام في الأعلى
    cols_ui = st.columns(len(GRID_COLS) + 1)
    cols_ui[0].markdown(
        "<p style='text-align:center; font-weight:bold;'>الصف/العمود</p>",
        unsafe_allow_html=True,
    )
    for idx, c in enumerate(GRID_COLS):
        cols_ui[idx + 1].markdown(
            f"<p style='text-align:center; font-weight:bold; font-size:1.1rem;'>{c}</p>",
            unsafe_allow_html=True,
        )

    # رسم الصفوف والمربعات
    for r in GRID_ROWS:
        row_cols = st.columns(len(GRID_COLS) + 1)
        row_cols[0].markdown(
            f"<p style='text-align:center; font-weight:bold; font-size:1.2rem; color:#f3e8ff;'>{r}</p>",
            unsafe_allow_html=True,
        )

        for idx, c in enumerate(GRID_COLS):
            cell_key = f"{r}{c}"
            owner = st.session_state.board[cell_key]

            # تحديد لون المربع بناءً على المجموعة المالكة أو الافتراضي
            if owner and owner in TEAMS:
                team_color = TEAMS[owner]["color"]
                btn_label = f"{TEAMS[owner]['bg']}"
                # تلوين الخلفية والزر بناءً على الفريق
                button_style = f"background-color: {team_color}; color: #000; border: 2px solid #fff;"
            else:
                button_style = "background-color: rgba(255, 255, 255, 0.1); color: #fff; border: 1px solid rgba(255, 255, 255, 0.2);"
                btn_label = f"{cell_key}"

            # استخدام زر لكل مربع
            with row_cols[idx + 1]:
                if st.button(
                    btn_label, key=f"btn_{cell_key}", use_container_width=True
                ):
                    # حفظ الحالة الحالية في الـ history قبل التغيير (لأجل الـ Undo)
                    import copy

                    st.session_state.history.append(
                        {
                            "board": copy.deepcopy(st.session_state.board),
                            "team_idx": st.session_state.current_team_idx,
                        }
                    )

                    # تطبيق الاستحواذ على المربع الأساسي ومحيطه (قاعدة + 4 مربعات أو حسب اللعبة)
                    # هنا يتم تغيير لون المربع المختار فوراً للمجموعة الحالية
                    st.session_state.board[cell_key] = current_team_name

                    # تطبيق ميزة الاستحواذ المتقاطع (+) للمربعات المجاورة (أعلى، أسفل، يمين، يسار) لو رغبت:
                    neighbors = [
                        (
                            GRID_ROWS[GRID_ROWS.index(r) - 1]
                            if GRID_ROWS.index(r) > 0
                            else None
                        ),
                        (
                            GRID_ROWS[GRID_ROWS.index(r) + 1]
                            if GRID_ROWS.index(r) < len(GRID_ROWS) - 1
                            else None
                        ),
                    ]
                    # تفعيل الدور للفريق التالي تلقائياً
                    st.session_state.current_team_idx = (
                        st.session_state.current_team_idx + 1
                    ) % len(TEAMS)
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
