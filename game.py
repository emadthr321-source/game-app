import streamlit as st
import copy

st.set_page_config(page_title="لعبة ترابيع المطورّة", page_icon="♦️", layout="wide")

# تصميم شبكة متلاصقة بدون مساحات، وتنسيق المعينات والخطوط الزجاجية الكبيرة
st.markdown("""
    <style>
    .stButton > button {
        width: 55px !important;
        height: 55px !important;
        min-height: 55px !important;
        padding: 0px !important;
        transform: rotate(45deg);
        display: inline-flex;
        justify-content: center;
        align-items: center;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 6px !important;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        margin: 4px auto !important;
    }
    .stButton > button p, .stButton > button span {
        transform: rotate(-45deg);
        font-weight: bold;
        font-size: 16px;
        color: white !important;
    }
    div[data-testid="column"] {
        width: max-content !important;
        flex: 1 !important;
        min-width: unset !important;
        padding: 0px !important;
    }
    .glass-box {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

rows = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح", "ط", "ي"]

# تهيئة الحالة
if "grid" not in st.session_state:
    st.session_state.grid = {(r, c): {"owner": None, "color": "rgba(255, 255, 255, 0.08)"} for r in rows for c in range(1, 11)}
    st.session_state.history = []

if "teams" not in st.session_state:
    st.session_state.teams = {
        "الإخاء": {"score": 0, "color": "#2980b9"},   # أزرق
        "المحبة": {"score": 0, "color": "#ecf0f1"},  # أبيض (النص سيظهر داكناً ليتناسب معه)
        "الوفاق": {"score": 0, "color": "#c0392b"},  # أحمر
        "الوصال": {"score": 0, "color": "#111111"}   # أسود
    }
    st.session_state.current_team = "الإخاء"

st.title("♦️ لعبة ترابيع - النسخة الماسية الاحترافية")
st.markdown("---")

col_sidebar, col_game = st.columns([1, 4])

with col_sidebar:
    st.subheader("📊 لوحة المجموعات")
    for team, data in st.session_state.teams.items():
        is_current = (team == st.session_state.current_team)
        border_glow = "border: 3px solid #f1c40f;" if is_current else f"border-left: 8px solid {data['color']}"
        st.markdown(f"""
            <div class="glass-box" style="{border_glow}">
                <b style="font-size: 18px;">{team}</b><br>
                <span style="font-size: 16px;">النقاط: {data['score']}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='font-size: 18px;'>الدور الحالي: <span style='color: #f1c40f;'>{st.session_state.current_team}</span></h3>", unsafe_allow_html=True)
    
    if st.button("⬅️ تراجع عن الخطوة", use_container_width=True):
        if st.session_state.history:
            prev = st.session_state.history.pop()
            st.session_state.grid = prev["grid"]
            st.session_state.teams = prev["teams"]
            st.session_state.current_team = prev["team"]
            st.success("تم التراجع بنجاح!")
            st.rerun()
        else:
            st.warning("لا توجد خطوات للتراجع عنها!")

    if st.button("🔄 إعادة ضبط اللعبة", use_container_width=True):
        st.session_state.history = []
        for t in st.session_state.teams:
            st.session_state.teams[t]["score"] = 0
        for k in st.session_state.grid:
            st.session_state.grid[k] = {"owner": None, "color": "rgba(255, 255, 255, 0.08)"}
        st.session_state.current_team = list(st.session_state.teams.keys())[0]
        st.rerun()

with col_game:
    st.subheader("🎯 لوحة المعينات التفاعلية")
    st.info("قاعدة اللعبة: الضغط على أي معين يستحوذ عليه وعلى المعينات الأربعة المحيطة به على شكل (+).")

    # رأس الأعمدة
    cols_header = st.columns(11)
    cols_header[0].markdown("<div style='text-align: center; font-weight: bold;'>#</div>", unsafe_allow_html=True)
    for c in range(1, 11):
        cols_header[c].markdown(f"<div style='text-align: center; font-weight: bold;'>{c}</div>", unsafe_allow_html=True)

    # رسم شبكة المعينات
    for r in rows:
        row_cols = st.columns(11)
        row_cols[0].markdown(f"<div style='text-align: center; font-weight: bold; padding-top: 15px;'>{r}</div>", unsafe_allow_html=True)
        for i, c in enumerate(range(1, 11)):
            cell = st.session_state.grid[(r, c)]
            owner = cell["owner"]
            btn_label = f"{r}{c}" if not owner else "✓"
            
            # حقن اللون بشكل مباشر لكل زر عبر حقن الـ CSS الديناميكي الخاص به
            cell_bg = cell["color"]
            text_color_style = "color: black !important;" if (owner == "المحبة") else "color: white !important;"
            
            st.markdown(f"""
                <style>
                div[data-testid="column"] button[kind="secondary"]:has(p:contains("{btn_label}")) {{
                    background-color: {cell_bg} !important;
                }}
                </style>
            """, unsafe_allow_html=True)

            if row_cols[i+1].button(btn_label, key=f"btn_{r}_{c}", use_container_width=True):
                # حفظ الحالة للتراجع
                st.session_state.history.append({
                    "grid": copy.deepcopy(st.session_state.grid),
                    "teams": copy.deepcopy(st.session_state.teams),
                    "team": st.session_state.current_team
                })
                
                current = st.session_state.current_team
                team_color = st.session_state.teams[current]["color"]
                
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
                        "color": team_color
                    })
                
                # إعادة حساب النقاط
                for t in st.session_state.teams:
                st.session_state.teams[t]["score"] = sum(1 for v in st.session_state.grid.values() if v["owner"] == t)
                
                # تدوير الدور للمجموعة التالية
                team_list = list(st.session_state.teams.keys())
                st.session_state.current_team = team_list[(team_list.index(current) + 1) % len(team_list)]
                st.rerun()
