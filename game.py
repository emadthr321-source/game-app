import streamlit as st

st.set_page_config(page_title="لعبة ترابيع الاحترافية", page_icon="🟩", layout="wide")

# تصميم زجاجي داكن وخطوط واضحة وكبيرة
st.markdown("""
    <style>
    .stButton>button {
        font-size: 20px !important;
        font-weight: bold !important;
        height: 60px !important;
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
    }
    h1, h2, h3, p, label, span {
        color: #ffffff !important;
        font-family: 'Tajawal', sans-serif, Arial;
    }
    .glass-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

rows = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح", "ط", "ي"]

# تهيئة حالة اللعبة
if "grid" not in st.session_state:
    st.session_state.grid = {
        (r, c): {"owner": None, "color": "rgba(255,255,255,0.05)"}
        for r in rows for c in range(1, 11)
    }

if "teams" not in st.session_state:
    st.session_state.teams = {
        "الإخاء": {"score": 0, "color": "#2980b9", "text_color": "white"},   # أزرق
        "المحبة": {"score": 0, "color": "#ecf0f1", "text_color": "black"},  # أبيض
        "الوفاق": {"score": 0, "color": "#c0392b", "text_color": "white"},   # أحمر
        "الوصال": {"score": 0, "color": "#2c3e50", "text_color": "white"}    # أسود
    }

if "current_team" not in st.session_state:
    st.session_state.current_team = list(st.session_state.teams.keys())[0]

# نظام حفظ التاريخ للتراجع (History stack)
if "history" not in st.session_state:
    st.session_state.history = []

st.title("🏔️ لعبة ترابيع - النظام الاحترافي")
st.markdown("---")

col_sidebar, col_game = st.columns([1, 3])

with col_sidebar:
    st.subheader("📊 لوحة المجموعات")
    for team, data in st.session_state.teams.items():
        is_current = (team == st.session_state.current_team)
        border_style = "border: 3px solid #f1c40f;" if is_current else "border: 1px solid rgba(255,255,255,0.2);"
        st.markdown(
            f"""
            <div class="glass-box" style="background-color: {data['color']}; color: {data['text_color']}; {border_style}">
                <b style="font-size: 18px; color: {data['text_color']} !important;">{team}</b><br>
                <span style="font-size: 16px; color: {data['text_color']} !important;">النقاط: {data['score']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown(f"<h3 style='font-size: 18px;'>الدور الحالي: <span style='color: #f1c40f;'>{st.session_state.current_team}</span></h3>", unsafe_allow_html=True)
    
    # زر التراجع خطوة
    if st.button("⬅️ تراجع عن الخطوة السابقة", use_container_width=True):
        if st.session_state.history:
            last_state = st.session_state.history.pop()
            st.session_state.grid = last_state["grid"]
            st.session_state.teams = last_state["teams"]
            st.session_state.current_team = last_state["current_team"]
            st.success("تم التراجع بنجاح!")
            st.rerun()
        else:
            st.warning("لا توجد خطوات للتراجع عنها!")

    if st.button("🔄 إعادة ضبط اللعبة", use_container_width=True):
        st.session_state.history = []
        for t in st.session_state.teams:
            st.session_state.teams[t]["score"] = 0
        for k in st.session_state.grid:
            st.session_state.grid[k] = {"owner": None, "color": "rgba(255,255,255,0.05)"}
        st.session_state.current_team = list(st.session_state.teams.keys())[0]
        st.rerun()

with col_game:
    st.subheader("🎯 لوحة المربعات التفاعلية")
    st.info("قاعدة اللعبة: المربع المختار ينشر الاستحواذ لـ 4 مربعات محيطة به على شكل علامة (+).")

    # رأس الأعمدة
    cols_header = st.columns(11)
    cols_header[0].markdown("<h3 style='text-align: center;'>#</h3>", unsafe_allow_html=True)
    for c in range(1, 11):
        cols_header[c].markdown(f"<h3 style='text-align: center;'>{c}</h3>", unsafe_allow_html=True)

    # رسم شبكة المربعات
    for r in rows:
        row_cols = st.columns(11)
        row_cols[0].markdown(f"<h3 style='text-align: center;'>{r}</h3>", unsafe_allow_html=True)
        for c in range(1, 11):
            cell_data = st.session_state.grid[(r, c)]
            owner = cell_data["owner"]
            bg_color = cell_data["color"]
            
            btn_label = f"{r}{c}" if not owner else "✓"
            
            # تخصيص لون زر المربع بناءً على المجموعة المالكة
            custom_style = f"background-color: {bg_color};" if owner else ""
            
            if row_cols[c].button(btn_label, key=f"btn_{r}_{c}", use_container_width=True):
                # حفظ الحالة الحالية قبل التعديل (من أجل التراجع)
                import copy
                st.session_state.history.append({
                    "grid": copy.deepcopy(st.session_state.grid),
                    "teams": copy.deepcopy(st.session_state.teams),
                    "current_team": st.session_state.current_team
                })

                current = st.session_state.current_team
                team_color = st.session_state.teams[current]["color"]
                
                # تحديد المربع والمربعات الأربعة المحيطة (+)
                target_coords = [(r, c)]
                r_idx = rows.index(r)
                
                if r_idx > 0: target_coords.append((rows[r_idx - 1], c))       # أعلى
                if r_idx < len(rows) - 1: target_coords.append((rows[r_idx + 1], c)) # أسفل
                if c > 1: target_coords.append((r, c - 1))                             # يسار
                if c < 10: target_coords.append((r, c + 1))                            # يمين
                
                # تحديث المربعات
                for coord in target_coords:
                    if coord in st.session_state.grid:
                        st.session_state.grid[coord]["owner"] = current
                        st.session_state.grid[coord]["color"] = team_color

                # تحديث النقاط
                for t in st.session_state.teams:
                    st.session_state.teams[t]["score"] = sum(
                        1 for k, v in st.session_state.grid.items() if v["owner"] == t
                    )
                
                # تدوير الدور للمجموعة التالية
                team_names = list(st.session_state.teams.keys())
                next_idx = (team_names.index(current) + 1) % len(team_names)
                st.session_state.current_team = team_names[next_idx]
                
                st.rerun()
