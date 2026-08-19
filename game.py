import streamlit as st
import copy

st.set_page_config(page_title="لعبة ترابيع الماسية", page_icon="♦️", layout="wide")

TEAMS = {
    "الإخاء": {"color": "#2980b9", "text": "white"},   # أزرق
    "المحبة": {"color": "#ecf0f1", "text": "black"},  # أبيض
    "الوفاق": {"color": "#c0392b", "text": "white"},   # أحمر
    "الوصال": {"color": "#111111", "text": "white"}    # أسود
}

rows = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح", "ط", "ي"]

if "grid" not in st.session_state:
    st.session_state.grid = {
        (r, c): {"owner": None, "color": "rgba(255, 255, 255, 0.1)", "text": "white"} 
        for r in rows for c in range(1, 11)
    }
    st.session_state.history = []

if "current_team" not in st.session_state:
    st.session_state.current_team = list(TEAMS.keys())[0]

st.title("♦️ لعبة ترابيع - النسخة المستقرة والمتلاصقة")
st.markdown("---")

col_sidebar, col_game = st.columns([1, 3])

with col_sidebar:
    st.subheader("📊 لوحة المجموعات")
    for team, data in TEAMS.items():
        score = sum(1 for v in st.session_state.grid.values() if v["owner"] == team)
        is_current = (team == st.session_state.current_team)
        border_glow = "border: 3px solid #f1c40f;" if is_current else f"border-left: 8px solid {data['color']}"
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.08); backdrop-filter: blur(10px); padding: 12px; border-radius: 10px; margin-bottom: 8px; {border_glow}">
                <b style="font-size: 16px; color: white;">{team}</b><br>
                <span style="font-size: 14px; color: #ddd;">النقاط: {score}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"<h4 style='color: #f1c40f;'>الدور الحالي: {st.session_state.current_team}</h4>", unsafe_allow_html=True)
    
    if st.button("⬅️ تراجع عن الخطوة", use_container_width=True):
        if st.session_state.history:
            prev = st.session_state.history.pop()
            st.session_state.grid = prev["grid"]
            st.session_state.current_team = prev["team"]
            st.rerun()

    if st.button("🔄 إعادة ضبط اللعبة", use_container_width=True):
        st.session_state.history = []
        st.session_state.grid = {
            (r, c): {"owner": None, "color": "rgba(255, 255, 255, 0.1)", "text": "white"} 
            for r in rows for c in range(1, 11)
        }
        st.session_state.current_team = list(TEAMS.keys())[0]
        st.rerun()

with col_game:
    st.subheader("🎯 شبكة المعينات التفاعلية المتلاصقة")
    
    # استخدام نظام أزرار Streamlit المحسنة بتنسيق المعينات لضمان الأمان وعدم حدوث خطأ 400
    st.markdown("""
    <style>
    .stButton > button {
        width: 48px !important;
        height: 48px !important;
        min-height: 48px !important;
        padding: 0px !important;
        transform: rotate(45deg);
        display: flex;
        justify-content: center;
        align-items: center;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 6px !important;
        margin: 2px auto !important;
    }
    .stButton > button p, .stButton > button span {
        transform: rotate(-45deg);
        font-weight: bold;
        font-size: 13px;
    }
    div[data-testid="column"] {
        width: max-content !important;
        flex: 1 !important;
        min-width: unset !important;
        padding: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # رأس الأعمدة
    cols_header = st.columns(11)
    cols_header[0].markdown("<div style='text-align: center; font-weight: bold;'>#</div>", unsafe_allow_html=True)
    for c in range(1, 11):
        cols_header[c].markdown(f"<div style='text-align: center; font-weight: bold;'>{c}</div>", unsafe_allow_html=True)

    # رسم الشبكة بأزرار امنة ومتلاصقة
    for r in rows:
        row_cols = st.columns(11)
        row_cols[0].markdown(f"<div style='text-align: center; font-weight: bold; padding-top: 10px;'>{r}</div>", unsafe_allow_html=True)
        for i, c in enumerate(range(1, 11)):
            cell = st.session_state.grid[(r, c)]
            owner = cell["owner"]
            btn_label = f"{r}{c}" if not owner else "✓"
            
            cell_bg = cell["color"]
            txt_color = cell["text"]
            
            # حقن لون الخلفية والنص مباشرة لكل معين
            st.markdown(f"""
                <style>
                button[key="btn_{r}_{c}"] {{
                    background-color: {cell_bg} !important;
                    color: {txt_color} !important;
                }}
                </style>
            """, unsafe_allow_html=True)

            if row_cols[i+1].button(btn_label, key=f"btn_{r}_{c}", use_container_width=True):
                # حفظ الحالة للتراجع
                st.session_state.history.append({
                    "grid": copy.deepcopy(st.session_state.grid),
                    "team": st.session_state.current_team
                })
                
                current = st.session_state.current_team
                team_info = TEAMS[current]
                
                # قاعدة التمدد (+)
                coords = [(r, c)]
                r_idx = rows.index(r)
                if r_idx > 0: coords.append((rows[r_idx-1], c))
                if r_idx < len(rows)-1: coords.append((rows[r_idx+1], c))
                if c > 1: coords.append((r, c-1))
                if c < 10: coords.append((r, c+1))
                
                for co in coords:
                    st.session_state.grid[co].update({
                        "owner": current,
                        "color": team_info["color"],
                        "text": team_info["text"]
                    })
                
                # تدوير الدور للمجموعة التالية
                team_list = list(TEAMS.keys())
                st.session_state.current_team = team_list[(team_list.index(current) + 1) % len(team_list)]
                st.rerun()
