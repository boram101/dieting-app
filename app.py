import streamlit as st
import json
import datetime
import matplotlib.pyplot as plt

# -------------------- 페이지 설정 --------------------
st.set_page_config(page_title="개인 맞춤 식단 설계 프로그램")
st.title("🥗 개인 맞춤 식단 설계 프로그램")

# -------------------- 세션 상태 초기화 --------------------
if 'foods' not in st.session_state:
    st.session_state.foods = [
        {"name": "닭가슴살", "calories": 165, "protein": 31, "allergens": []},
        {"name": "현미밥", "calories": 220, "protein": 4, "allergens": []},
        {"name": "두부", "calories": 76, "protein": 8, "allergens": ["콩"]},
        {"name": "우유", "calories": 150, "protein": 8, "allergens": ["우유"]},
        {"name": "계란", "calories": 70, "protein": 6, "allergens": ["달걀"]},
        {"name": "사과", "calories": 52, "protein": 0.3, "allergens": []},
        {"name": "오트밀", "calories": 150, "protein": 5, "allergens": []},
        {"name": "그릭요거트", "calories": 100, "protein": 10, "allergens": ["우유"]},
    ]

foods = st.session_state.foods

# -------------------- BMR 계산 --------------------
def calculate_bmr(gender, weight, height, age):
    if gender == "남성":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

# -------------------- 목표별 칼로리 --------------------
def get_calorie_goal(bmr, goal):
    if goal == "다이어트":
        return bmr - 300
    elif goal == "근육 증가":
        return bmr + 300
    else:
        return bmr

# -------------------- 식사 기록 불러오기 --------------------
def load_log():
    try:
        with open("meals_log.json", "r") as f:
            return json.load(f)
    except:
        return {}

# -------------------- 식사 기록 저장 --------------------
def save_log(log):
    with open("meals_log.json", "w") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

# -------------------- 사용자 정보 입력 --------------------
st.sidebar.header("사용자 정보 입력")
age = st.sidebar.number_input("나이", min_value=10, max_value=100, value=25)
gender = st.sidebar.selectbox("성별", ["남성", "여성"])
height = st.sidebar.number_input("키 (cm)", min_value=100, max_value=250, value=170)
weight = st.sidebar.number_input("몸무게 (kg)", min_value=30, max_value=200, value=70)

base_allergens = ["우유", "콩", "달걀"]
custom_allergen = st.sidebar.text_input("알레르기 직접 추가")
allergen_options = base_allergens + ([custom_allergen] if custom_allergen else [])
allergies = st.sidebar.multiselect("알레르기", allergen_options)

health = st.sidebar.text_input("건강 상태", placeholder="예: 고혈압")
goal = st.sidebar.selectbox("목표", ["다이어트", "근육 증가", "건강 유지"])

bmr = calculate_bmr(gender, weight, height, age)
calorie_goal = get_calorie_goal(bmr, goal)
st.markdown(f"### 🧮 하루 권장 섭취 칼로리: {int(calorie_goal)} kcal")

# -------------------- 아침/점심/저녁 추천 식단 --------------------
st.markdown("### 🍽️ 아침/점심/저녁 추천 식단 (알레르기 고려)")

meal_times = {
    "아침": [],
    "점심": [],
    "저녁": []
}

filtered = [f for f in foods if not any(a in f["allergens"] for a in allergies)]

# 간단한 분할 (3개씩 나눔)
for i, food in enumerate(filtered):
    if i % 3 == 0:
        meal_times["아침"].append(food)
    elif i % 3 == 1:
        meal_times["점심"].append(food)
    else:
        meal_times["저녁"].append(food)

for time, meals in meal_times.items():
    st.markdown(f"**{time} 추천 식단:**")
    for m in meals:
        st.write(f"- {m['name']} ({m['calories']} kcal, 단백질 {m['protein']}g)")

# -------------------- 음식 직접 추가 --------------------
st.markdown("### 🍱 음식 직접 등록하기")
new_name = st.text_input("음식 이름")
carbs = st.number_input("탄수화물 (g)", 0.0, 200.0, step=0.1)
protein = st.number_input("단백질 (g)", 0.0, 100.0, step=0.1)
fat = st.number_input("지방 (g)", 0.0, 100.0, step=0.1)
new_allergens = st.multiselect("알레르기 성분", base_allergens, key="add")

calories = carbs * 4 + protein * 4 + fat * 9

if st.button("음식 추가"):
    new_food = {
        "name": new_name,
        "calories": round(calories, 1),
        "protein": round(protein, 1),
        "allergens": new_allergens
    }
    st.session_state.foods.append(new_food)
    st.success(f"'{new_name}'이(가) 추가되었습니다! 총 {round(calories, 1)} kcal")

# -------------------- 오늘 섭취한 식단 입력 --------------------
st.markdown("### 🍽️ 오늘 먹은 음식 기록")
meal_names = [f["name"] for f in st.session_state.foods]
selected_meals = st.multiselect("음식 선택", meal_names)

if st.button("📊 칼로리 계산 및 저장"):
    intake = sum(f["calories"] for f in st.session_state.foods if f["name"] in selected_meals)
    st.success(f"오늘 총 섭취 칼로리: {intake} kcal")

    today = datetime.date.today().isoformat()
    log = load_log()
    log[today] = {"meals": selected_meals, "intake": intake}
    save_log(log)

# -------------------- 주간 섭취 칼로리 차트 --------------------
log = load_log()
if log:
    st.markdown("### 📈 최근 7일 섭취 칼로리")
    last_7_days = sorted(log.keys())[-7:]
    calories = [log[day]["intake"] for day in last_7_days]

    fig, ax = plt.subplots()
    ax.bar(last_7_days, calories, color='skyblue')
    ax.axhline(calorie_goal, color='red', linestyle='--', label='권장 섭취량')
    plt.xticks(rotation=45)
    plt.ylabel("칼로리 (kcal)")
    plt.title("주간 섭취 칼로리")
    plt.legend()
    st.pyplot(fig)

    avg = sum(calories) / len(calories)
    st.info(f"📊 지난 7일 평균 섭취 칼로리: {int(avg)} kcal")
