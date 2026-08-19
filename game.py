import streamlit as st
import copy

# --- إعدادات الصفحة ---
st.set_page_config(page_title="لعبة ترابيع الاحترافية", page_icon="🔲", layout="wide")

# --- تنسيق التصميم (Dark Glassmorphism) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    .stApp { background: linear-gradient(135deg, #2c1624 0%, #1a0c17 100%); color: #ffffff; }
    .glass-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    h1, h2, h3 { font-weight: 900 !important; color: #f3e8ff; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- إعدادات اللعبة ---
GRID_ROWS = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح", "ط", "ي"]
GRID_COLS = list(range(1, 11))

# تحديث الأسر لتصبح: الهمة والعطاء فقط
TEAMS = {
    "الهمة": {"color": "#00d2ff", "bg": "🔵"},
    "العطاء": {"color": "#ff4d4d", "bg": "🔴"},
}

if "board" not in st.session_state:
    st.session_state.board = {f"{r}{c}": None for r in GRID_ROWS for c in GRID_COLS}
if "history" not in st.session_state:
    st.session_state.history = []

# --- العنوان ---
st.markdown("<h1 style='text-align: center;'>🔲 لعبة ترابيع الاحترافية 🔲</h1>", unsafe_allow_html=True)

col_control, col_board = st.columns([1, 3])

with col_control:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🛠️ لوحة التحكم")
    
    # القائمة المسندلة لاختيار أسرة الهمة أو العطاء
    selected_team = st.selectbox(
        "اختر الأسرة المشاركة حالياً:",
        options=list(TEAMS.keys()),
        format_func=lambda x: f"{TEAMS[x]['bg']} أسرة {x}"
    )
    
    st.markdown("---")
    st.markdown("#### 🏆 النقاط الحالية:")
    team_scores = {t: 0 for t in TEAMS}
    for owner in st.session_state.board.values():
        if owner in team_scores: team_scores[owner] += 1
    for t, info in TEAMS.items():
        st.markdown(f"- <span style='color: {info['color']};'>{info['bg']} أسرة {t}</span>: **{team_scores[t]}** مربعات", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("↩️ تراجع عن آخر خطوة", use_container_width=True):
        if st.session_state.history:
            st.session_state.board = st.session_state.history.pop()
            st.rerun()
    
    if st.button("🔄 إعادة ضبط اللعبة", use_container_width=True):
        st.session_state.board = {f"{r}{c}": None for r in GRID_ROWS for c in GRID_COLS}
        st.session_state.history = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_board:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(f"### 📍 لوحة اللعب - دور: <span style='color: {TEAMS[selected_team]['color']}'>{TEAMS[selected_team]['bg']} أسرة {selected_team}</span>", unsafe_allow_html=True)
    
    # رأس الأعمدة (أرقام)
    cols_header = st.columns(len(GRID_COLS) + 1)
    cols_header[0].markdown("<p style='text-align:center;'>الصف</p>", unsafe_allow_html=True)
    for idx, col_num in enumerate(GRID_COLS):
        cols_header[idx + 1].markdown(f"<p style='text-align:center; font-weight:bold;'>{col_num}</p>", unsafe_allow_html=True)

    # بناء اللوحة الصفوف والأعمدة
    for r_idx, r in enumerate(GRID_ROWS):
        row_cols = st.columns(len(GRID_COLS) + 1)
        row_cols[0].markdown(f"<p style='text-align:center; font-weight:bold; color:#f3e8ff;'>{r}</p>", unsafe_allow_html=True)
        
        for c_idx, c in enumerate(GRID_COLS):
            cell_key = f"{r}{c}"
            owner = st.session_state.board[cell_key]
            
            # تحديد شكل الزر ولونه إذا كان مملوكاً
            btn_label = TEAMS[owner]["bg"] if owner else f"{cell_key}"
            
            with row_cols[c_idx + 1]:
                if st.button(btn_label, key=f"btn_{cell_key}", use_container_width=True):
                    # حفظ الحالة الحالية للـ Undo
                    st.session_state.history.append(copy.deepcopy(st.session_state.board))
                    
                    # تحديد المربعات (المربع الأساسي + الأربعة المحيطة شكل +)
                    target_cells = [cell_key]
                    if r_idx > 0: target_cells.append(f"{GRID_ROWS[r_idx-1]}{c}")
                    if r_idx < len(GRID_ROWS)-1: target_cells.append(f"{GRID_ROWS[r_idx+1]}{c}")
                    if c_idx > 0: target_cells.append(f"{r}{GRID_COLS[c_idx-1]}")
                    if c_idx < len(GRID_COLS)-1: target_cells.append(f"{r}{GRID_COLS[c_idx+1]}")
                    
                    # تلوين المربعات بالأسرة المختارة من القائمة المسندلة
                    for target in target_cells:
                        st.session_state.board[target] = selected_team
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
