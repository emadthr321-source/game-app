import streamlit as st
import json
import os

st.set_page_config(page_title="رواد القرآن - المسابقات التفاعلية", layout="wide")

DATA_FILE = "league_data.json"
LOGO_PATH = "logo.png"

DEFAULT_DATA = {
    "round": "الجولة 1",
    "groups": {g: [] for g in ["تبوك", "مؤتة", "خيبر", "اليرموك", "الخندق", "القادسية", "أحد", "حطين"]},
    "eliminated": []
}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=4)
        return DEFAULT_DATA
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

# --- عرض الشعار في الأعلى ---
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, use_container_width=True)
else:
    st.title("🏆 رواد القرآن - المرحلة الثانوية")

# --- الشريط الجانبي: تسجيل الدخول وأدوات التحكم ---
st.sidebar.title("🔐 صلاحيات الدخول")
user_role = st.sidebar.radio("اختر نمط الدخول:", ["طالب 👨‍🎓", "معلم / مشرف 👨‍🏫"])

is_teacher = False
if user_role == "معلم / مشرف 👨‍🏫":
    password = st.sidebar.text_input("رمز مرور المعلم:", type="password")
    if password == "1234":
        is_teacher = True
        st.sidebar.success("تم تفعيل صلاحيات المعلم ✅")
    else:
        st.sidebar.warning("أدخل رمز المرور الصحيح للتحكم")

st.sidebar.write("---")
if st.sidebar.button("🔄 تحديث الشاشة"):
    st.rerun()

# --- زر إعادة الضبط الشامل للمعلم ---
if is_teacher:
    st.sidebar.write("### ⚙️ إعدادات التحكم")
    if st.sidebar.button("⚠️ إعادة ضبط اللعبة بالكامل", type="primary"):
        if st.sidebar.checkbox("تأكيد رغبتك في مسح وتصفير جميع البيانات؟"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("تمت إعادة ضبط اللعبة بنجاح!")
            st.rerun()

# مواجهات الجولات
rounds_info = {
    "الجولة 1": "تبوك + مؤتة + خيبر + اليرموك   VS   الخندق + القادسية + أحد + حطين",
    "الجولة 2": "تبوك + خيبر + أحد + حطين   VS   مؤتة + اليرموك + الخندق + القادسية",
    "الجولة 3": "مؤتة + اليرموك + أحد + حطين   VS   تبوك + خيبر + الخندق + القادسية"
}

if is_teacher:
    selected_round = st.selectbox("اختر الجولة الحالية:", list(rounds_info.keys()), index=list(rounds_info.keys()).index(data.get("round", "الجولة 1")))
    if selected_round != data.get("round"):
        data["round"] = selected_round
        save_data(data)
        st.rerun()
else:
    st.info(f"🔥 **{data['round']}:** {rounds_info[data['round']]}")

tab1, tab2 = st.tabs(["⚔️ الفرق والمجموعات", "🚫 المقصيين والإحصائيات"])

with tab1:
    cols = st.columns(4)
    group_names = list(data["groups"].keys())
    
    for idx, g_name in enumerate(group_names):
        with cols[idx % 4]:
            st.subheader(f"أسرة {g_name}")
            
            with st.form(key=f"add_{g_name}", clear_on_submit=True):
                s_name = st.text_input("اسم الطالب الجديد", key=f"in_{g_name}")
                btn_add = st.form_submit_button("+ تسجيل الاسم")
                if btn_add and s_name.strip():
                    data["groups"][g_name].append({"name": s_name.strip(), "points": 0, "custom": False})
                    total = len(data["groups"][g_name])
                    if total > 0:
                        base_p = round(100 / total, 1)
                        for s in data["groups"][g_name]:
                            if not s.get("custom", False):
                                s["points"] = base_p
                    save_data(data)
                    st.rerun()

            st.write("---")
            for s_idx, student in enumerate(data["groups"][g_name]):
                st.write(f"• **{student['name']}** ({student['points']} ن)")
                
                if is_teacher:
                    # تقسيم الأزرار بشكل متناسق (إضافة، خصم، إقصاء، حذف خطأ)
                    c1, c2, c3, c4 = st.columns(4)
                    if c1.button("➕", key=f"p_{g_name}_{s_idx}"):
                        student["points"] = round(student["points"] + 1, 1)
                        student["custom"] = True
                        save_data(data)
                        st.rerun()
                    if c2.button("➖", key=f"m_{g_name}_{s_idx}"):
                        student["points"] = round(max(0, student["points"] - 1), 1)
                        student["custom"] = True
                        save_data(data)
                        st.rerun()
                    if c3.button("إقصاء", key=f"e_{g_name}_{s_idx}"):
                        st.session_state.pending_elimination = {
                            "group": g_name,
                            "index": s_idx,
                            "student": student
                        }
                        st.rerun()
                    if c4.button("❌", key=f"del_{g_name}_{s_idx}", help="إلغاء الطالب المضاف بالخطأ بدون خصم نقاط"):
                        # حذف الطالب وإعادة توزيع النقاط المتبقية على باقي طلاب الأسرة بالتساوي
                        data["groups"][g_name].pop(s_idx)
                        total = len(data["groups"][g_name])
                        if total > 0:
                            base_p = round(100 / total, 1)
                            for s in data["groups"][g_name]:
                                if not s.get("custom", False):
                                    s["points"] = base_p
                        save_data(data)
                        st.rerun()

    # --- نافذة الإقصاء وتحويل النقاط ---
    if is_teacher and 'pending_elimination' in st.session_state and st.session_state.pending_elimination:
        pending = st.session_state.pending_elimination
        elim_student = pending["student"]
        src_group = pending["group"]
        
        st.write("---")
        st.warning(f"⚠️ جاري إقصاء الطالب **{elim_student['name']}** من أسرة ({src_group}) ولديه ({elim_student['points']} نقطة).")
        
        target_group = st.selectbox("اختر المجموعة الفائزة/الخصم لتوزيع نقاط الطالب عليها بالتساوي:", [g for g in group_names if g != src_group])
        
        c_confirm, c_cancel = st.columns(2)
        if c_confirm.button("✅ تأكيد الإقصاء وتحويل النقاط"):
            elim_data = data["groups"][src_group].pop(pending["index"])
            data["eliminated"].append({
                "name": elim_data["name"], 
                "group": src_group, 
                "points": elim_data["points"]
            })
            
            # إعادة حساب توزيع النقاط المتبقية للأسرة الأصلية
            total_src = len(data["groups"][src_group])
            if total_src > 0:
                base_p = round(100 / total_src, 1)
                for s in data["groups"][src_group]:
                    if not s.get("custom", False):
                        s["points"] = base_p

            # توزيع نقاط الطالب المقصي على الأسرة الفائزة
            target_students = data["groups"][target_group]
            if target_students and elim_data["points"] > 0:
                bonus = round(elim_data["points"] / len(target_students), 1)
                for ts in target_students:
                    ts["points"] = round(ts["points"] + bonus, 1)
                    ts["custom"] = True
            
            save_data(data)
            st.session_state.pending_elimination = None
            st.rerun()
            
        if c_cancel.button("❌ إلغاء أمر الإقصاء"):
            st.session_state.pending_elimination = None
            st.rerun()

with tab2:
    st.subheader("📊 النقاط المفقودة بالإقصاء لكل مجموعة")
    totals = {g: 0 for g in group_names}
    for item in data.get("eliminated", []):
        totals[item["group"]] += item["points"]
    
    t_cols = st.columns(4)
    for idx, (g, pts) in enumerate(totals.items()):
        t_cols[idx % 4].metric(f"مجموعة {g}", f"{round(pts, 1)} ن مفقودة")

    st.write("---")
    st.subheader("🚫 قائمة الطلاب المقصيين")
    if data.get("eliminated"):
        st.table(data["eliminated"])
    else:
        st.write("لا يوجد مقصيين حالياً.")
