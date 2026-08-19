import streamlit as st
import copy

st.set_page_config(page_title="لعبة ترابيع الماسية", page_icon="♦️", layout="wide")

# تصميم المجموعات والألوان
TEAMS = {
    "الإخاء": {"color": "#2980b9", "text": "white"},   # أزرق
    "المحبة": {"color": "#ecf0f1", "text": "black"},  # أبيض
    "الوفاق": {"color": "#c0392b", "text": "white"},   # أحمر
    "الوصال": {"color": "#111111", "text": "white"}    # أسود
}

rows = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح", "ط", "ي"]

# تهيئة الحالة
if "grid" not in st.session_state:
    st.session_state.grid = {
        (r, c): {"owner": None, "color": "rgba(255, 255, 255, 0.1)", "text": "white"} 
        for r in rows for c in range(1, 11)
    }
    st.session_state.history = []

if "current_team" not in st.session_state:
    st.session_state.current_team = list(TEAMS.keys())[0]

# التعامل مع الضغط على المعين عبر الـ Query Params أو الأزرار المصغرة
query_params = st.query_params
if "click" in query_params:
    clicked_cell = query_params["click"]
    r, c_str = clicked_cell[0], clicked_cell[1:]
    c = int(c_str)
    
    # حفظ التاريخ للتراجع
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
    
    # تدوير الدور
    team_list = list(TEAMS.keys())
    st.session_state.current_team = team_list[(team_list.index(current) + 1) % len(team_list)]
    
    # مسح البارامتر وإعادة التحميل
    st.query_params.clear()
    st.rerun()

st.title("♦️ لعبة ترابيع - النسخة المتلاصقة بالكامل")
st.markdown("---")

col_sidebar, col_game = st.columns([1, 3])

with col_sidebar:
    st.subheader("📊 لوحة المجموعات")
    for team, data in TEAMS.items():
        # حساب النقاط مباشرة
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
    st.subheader("🎯 شبكة المعينات المتلاصقة")
    
    # بناء شبكة HTML متلاصقة تماماً بدون مساحات لتوفير الشكل المطلوب بدقة
    html_grid = """
    <style>
    .diamond-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
    }
    .diamond-row {
        display: flex;
        gap: 2px;
    }
    .diamond-btn {
        width: 45px;
        height: 45px;
        transform: rotate(45deg);
        display: flex;
        justify-content: center;
        align-items: center;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 4px;
        transition: 0.2s;
        margin: 6px;
    }
    .diamond-btn span {
        transform: rotate(-45deg);
    }
    .diamond-btn:hover {
        border-color: #f1c40f;
        transform: rotate(45deg) scale(1.05);
    }
    </style>
    <div class="diamond-container">
    """
    
    # رأس الأعمدة أرقام
    html_grid += '<div class="diamond-row">'
    html_grid += '<div style="width:45px; height:45px; display:flex; align-items:center; justify-content:center; font-weight:bold;">#</div>'
    for c in range(1, 11):
        html_grid += f'<div style="width:45px; height:45px; display:flex; align-items:center; justify-content:center; font-weight:bold;">{c}</div>'
    html_grid += '</div>'

    for r in rows:
        html_grid += '<div class="diamond-row">'
        # حرف الصف
        html_grid += f'<div style="width:45px; height:45px; display:flex; align-items:center; justify-content:center; font-weight:bold;">{r}</div>'
        for c in range(1, 11):
            cell = st.session_state.grid[(r, c)]
            bg = cell["color"]
            txt_color = cell["text"]
            label = f"{r}{c}" if not cell["owner"] else "✓"
            
            html_grid += f'''
            <a href="?click={r}{c}" class="diamond-btn" style="background-color: {bg}; color: {txt_color};">
                <span style="color: {txt_color};">{label}</span>
            </a>
            '''
        html_grid += '</div>'
    
    html_grid += "</div>"
    
    st.markdown(html_grid, unsafe_allow_html=True)
