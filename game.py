import streamlit as st
import copy

st.set_page_config(page_title="لعبة ترابيع المطورّة", page_icon="♦️", layout="wide")

# تصميم زجاجي وخطوط كبيرة ومعينات (Diamonds)
st.markdown("""
    <style>
    /* تحويل الأزرار إلى شكل معين */
    .stButton>button {
        width: 60px !important;
        height: 60px !important;
        transform: rotate(45deg);
        display: flex;
        justify-content: center;
        align-items: center;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        margin: 5px !important;
    }
    /* إعادة النص للوضع الطبيعي داخل المعين */
    .stButton>button span {
        transform: rotate(-45deg);
        font-weight: bold;
        font-size: 18px;
    }
    .glass-box {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

rows = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح", "ط", "ي"]

# تهيئة الحالة
if "grid" not in st.session_state:
    st.session_state.grid = {(r, c): {"owner": None, "color": "rgba(255,255,255,0.05)"} for r in rows for c in range(1, 11)}
    st.session_state.history = []

if "teams" not in st.session_state:
    st.session_state.teams = {
        "الإخاء": {"score": 0, "color": "#2980b9", "text": "blue"},
        "المحبة": {"score": 0, "color": "#ffffff", "text": "black"},
        "الوفاق": {"score": 0, "color": "#c0392b", "text": "white"},
        "الوصال": {"score": 0, "color": "#000000", "text": "white"}
    }
    st.session_state.current_team = "الإخاء"

st.title("♦️ لعبة ترابيع - النسخة الماسية")

col_sidebar, col_game = st.columns([1, 4])

with col_sidebar:
    st.subheader("📊 لوحة المجموعات")
    for team, data in st.session_state.teams.items():
        st.markdown(f"""<div class="glass-box" style="border-left: 10px solid {data['color']}">
            <b>{team}</b><br>النقاط: {data['score']}
        </div>""", unsafe_allow_html=True)
    
    st.markdown(f"**الدور الحالي:** {st.session_state.current_team}")
    
    if st.button("⬅️ تراجع"):
        if st.session_state.history:
            prev = st.session_state.history.pop()
            st.session_state.grid = prev["grid"]
            st.session_state.teams = prev["teams"]
            st.session_state.current_team = prev["team"]
            st.rerun()

with col_game:
    # رسم المعينات
    for r in rows:
        cols = st.columns(10)
        for i, c in enumerate(range(1, 11)):
            cell = st.session_state.grid[(r, c)]
            btn_color = cell["color"]
            
            # زر المعين
            if cols[i].button(f"{r}{c}", key=f"{r}{c}"):
                # حفظ التاريخ
                st.session_state.history.append({
                    "grid": copy.deepcopy(st.session_state.grid),
                    "teams": copy.deepcopy(st.session_state.teams),
                    "team": st.session_state.current_team
                })
                
                # تنفيذ الاستحواذ
                team_info = st.session_state.teams[st.session_state.current_team]
                coords = [(r, c)] # القاعدة (+)
                r_idx = rows.index(r)
                
                # إضافة المربعات المحيطة
                if r_idx > 0: coords.append((rows[r_idx-1], c))
                if r_idx < 9: coords.append((rows[r_idx+1], c))
                if c > 1: coords.append((r, c-1))
                if c < 10: coords.append((r, c+1))
                
                for co in coords:
                    st.session_state.grid[co].update({"owner": st.session_state.current_team, "color": team_info["color"]})
                
                # تحديث النقاط
                for t in st.session_state.teams:
                    st.session_state.teams[t]["score"] = sum(1 for v in st.session_state.grid.values() if v["owner"] == t)
                
                # الدور التالي
                team_list = list(st.session_state.teams.keys())
                st.session_state.current_team = team_list[(team_list.index(st.session_state.current_team) + 1) % 4]
                st.rerun()
            
            # تطبيق اللون على الزر برمجياً (تحديث التنسيق)
            st.markdown(f"""
                <style>
                button[key="b_{r}_{c}"] {{ background-color: {btn_color} !important; }}
                </style>
            """, unsafe_allow_html=True)
