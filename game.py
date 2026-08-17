import streamlit as st

st.set_page_config(page_title="لعبة ترابيع", page_icon="🟩", layout="wide")

# تهيئة حالة اللعبة (لوحة 10×10 ونتائج المجموعات)
if "grid" not in st.session_state:
    st.session_state.grid = {
        (r, c): {"owner": None, "color": "#2c2c3c"}
        for r in ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح", "ط", "ي"]
        for c in range(1, 11)
    }

if "teams" not in st.session_state:
    st.session_state.teams = {
        "نورة": {"score": 0, "color": "#2ecc71"},       # أخضر
        "سارة": {"score": 0, "color": "#e67e22"},       # برتقالي
        "عبدالرحمن": {"score": 0, "color": "#3498db"}, # أزرق
        "عبدالله": {"score": 0, "color": "#95a5a6"}     # رمادي
    }

if "current_team" not in st.session_state:
    st.session_state.current_team = list(st.session_state.teams.keys())[0]

# تصميم الواجهة
st.title("🟩 لعبة ترابيع الاحترافية")
st.markdown("---")

# لوحة النتائج الجانبية
col_sidebar, col_game = st.columns([1, 3])

with col_sidebar:
    st.subheader("📊 لوحة النتائج")
    for team, data in st.session_state.teams.items():
        is_current = (team == st.session_state.current_team)
        border_style = "border: 2px solid gold;" if is_current else ""
        st.markdown(
            f"""
            <div style="padding: 10px; margin-bottom: 8px; border-radius: 8px; background-color: {data['color']}; color: white; {border_style}">
                <b>{team}</b><br>النقاط: {data['score']}
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown(f"**الدور الحالي:** `{st.session_state.current_team}`")
    
    if st.button("🔄 إعادة ضبط اللعبة", use_container_width=True):
        for t in st.session_state.teams:
            st.session_state.teams[t]["score"] = 0
        for k in st.session_state.grid:
            st.session_state.grid[k] = {"owner": None, "color": "#2c2c3c"}
        st.rerun()

with col_game:
    st.subheader("🎯 لوحة المربعات (اضغط على أي مربع للاستحواذ)")
    st.info("قاعدة اللعبة: كل مربع تملكه يمنحك مربعات إضافية على شكل علامة (+) إذا كانت متوفرة.")

    rows = ["أ", "ب", "ج", "د", "هـ", "و", "ز", "ح", "ط", "ي"]
    
    # صف رأس الأعمدة
    cols_header = st.columns(11)
    cols_header[0].markdown("**#**")
    for c in range(1, 11):
        cols_header[c].markdown(f"**{c}**")

    # رسم شبكة الأزرار
    for r in rows:
        row_cols = st.columns(11)
        row_cols[0].markdown(f"**{r}**")
        for c in range(1, 11):
            cell_data = st.session_state.grid[(r, c)]
            owner = cell_data["owner"]
            
            btn_label = f"{r}{c}" if not owner else f"✓"
            
            # زر لكل مربع
            if row_cols[c].button(btn_label, key=f"btn_{r}_{c}", use_container_width=True):
                current = st.session_state.current_team
                team_color = st.session_state.teams[current]["color"]
                
                # تنفيذ الاستحواذ على المربع الأساسي والمربعات الأربعة المحيطة (+)
                target_coords = [(r, c)]
                row_indices = rows
                r_idx = row_indices.index(r)
                
                if r_idx > 0: target_coords.append((row_indices[r_idx - 1], c))       # فوق
                if r_idx < len(row_indices) - 1: target_coords.append((row_indices[r_idx + 1], c)) # تحت
                if c > 1: target_coords.append((r, c - 1))                             # يسار
                if c < 10: target_coords.append((r, c + 1))                            # يمين
                
                # تحديث المربعات
                for coord in target_coords:
                    if coord in st.session_state.grid:
                        st.session_state.grid[coord]["owner"] = current
                        st.session_state.grid[coord]["color"] = team_color

                # إعادة حساب النقاط لكل المجموعات
                for t in st.session_state.teams:
                    st.session_state.teams[t]["score"] = sum(
                        1 for k, v in st.session_state.grid.items() if v["owner"] == t
                    )
                
                # نقل الدور للمجموعة التالية
                team_names = list(st.session_state.teams.keys())
                next_idx = (team_names.index(current) + 1) % len(team_names)
                st.session_state.current_team = team_names[next_idx]
                
                st.rerun()
