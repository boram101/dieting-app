import streamlit as st 
import json 
import datetime 
import matplotlib.pyplot as plt
import random

# -------------------- 초기 설정 -------------------- 
st.set_page_config(page_title="개인 맞춤 식단 설계 프로그램") 
st.title("🥗 개인 맞춤 식단 설계 프로그램")

# -------------------- 기본 음식 데이터 -------------------- 
foods = [
    {"name": "닭가슴살", "calories": 165, "protein": 31, "allergens": []},
    {"name": "현미밥", "calories": 220, "protein": 4, "allergens": []},
    {"name": "두부", "calories": 76, "protein": 8, "allergens": ["콩"]},
    {"name": "우유", "calories": 150, "protein": 8, "allergens": ["우유"]},
    {"name": "계란", "calories": 70, "protein": 6, "allergens": ["달걀"]},
    {"name": "사과", "calories": 52, "protein": 0.3, "allergens": []},
    {"name": "오트밀", "calories": 150, "protein": 5, "allergens": []},
    {"name": "그릭요거트", "calories": 100, "protein": 10, "allergens": ["우유"]},
]

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

# -------------------- 식사 기록 로드 및 저장 -------------------- 
def load_log():
    try:
        with open("meals_log.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_log(log):
    with open("meals_log.json", "w") as f: 
        json.dump(log, f, ensure_ascii=False, indent=2)

# -------------------- 사용자 정보 입력 -------------------- 
st.sidebar.header("사용자 정보 입력")
age = st.sidebar.number_input("나이", min_value=10, max_value=100, value=25)
gender = st.sidebar.selectbox("성별", ["남성", "여성"])
height = st.sidebar.number_input("키 (cm)", min_value=100, max_value=250, value=170)
weight = st.sidebar.number_input("몸무게 (kg)", min_value=30, max_value=200, value=70)

# 사용자 정의 알레르기 항목 포함
default_allergens = ["우유", "콩", "달걀"]
custom_allergen = st.sidebar.text_input("기타 알레르기 입력")
allergies = st.sidebar.multiselect("알레르기", default_allergens)
if custom_allergen:
    allergies.append(custom_allergen)

health = st.sidebar.text_input("건강 상태", placeholder="예: 고혈압")
goal = st.sidebar.selectbox("목표", ["다이어트", "근육 증가", "건강 유지"])

user_info = {
    "age": age, "gender": gender, "height": height,
    "weight": weight, "allergies": allergies,
    "health": health, "goal": goal
}

# -------------------- 권장 칼로리 계산 -------------------- 
bmr = calculate_bmr(gender, weight, height, age)
calorie_goal = get_calorie_goal(bmr, goal)
st.markdown(f"### 🧮 하루 권장 섭취 칼로리: {int(calorie_goal)} kcal")

# -------------------- 추천 식단 (알레르기 고려) -------------------- 
st.markdown("### 🥗 추천 식단 (알레르기 고려)")
recommended = [f for f in foods if not any(a in f["allergens"] for a in allergies)]
for food in recommended:
    st.write(f"- {food['name']} ({food['calories']} kcal, 단백질 {food['protein']}g)")

# -------------------- 음식 추가 기능 (탄단지로 칼로리 계산) -------------------- 
with st.expander("🍱 음식 추가하기"):
    new_name = st.text_input("음식 이름")
    carbs = st.number_input("탄수화물 (g)", 0.0, 200.0, step=1.0)
    fats = st.number_input("지방 (g)", 0.0, 100.0, step=1.0)
    protein = st.number_input("단백질 (g)", 0.0, 100.0, step=1.0)
    new_allergens = st.multiselect("알레르기 성분", default_allergens, key="add")

    calculated_calories = carbs * 4 + protein * 4 + fats * 9

    if st.button("음식 추가"):
        foods.append({
            "name": new_name,
            "calories": round(calculated_calories),
            "protein": protein,
            "allergens": new_allergens
        })
        st.success(f"'{new_name}'이(가) 추가되었습니다! 칼로리: {round(calculated_calories)} kcal")

# -------------------- 오늘 식단 입력 -------------------- 
st.markdown("### 🍽️ 오늘 하루 먹은 음식")
meal_names = [f["name"] for f in foods]
selected_meals = st.multiselect("음식 선택", meal_names)

if st.button("📊 칼로리 계산 및 저장"):
    intake = sum(f["calories"] for f in foods if f["name"] in selected_meals)
    st.success(f"오늘 총 섭취 칼로리: {intake} kcal")

    today = datetime.date.today().isoformat()
    log = load_log()
    log[today] = {"meals": selected_meals, "intake": intake}
    save_log(log)

# -------------------- 주간 섭취 히스토리 -------------------- 
log = load_log()
if log:
    st.markdown("### 📈 최근 7일 섭취 칼로리 차트")
    last_7_days = sorted(log.keys())[-7:]
    dates = last_7_days
    calories = [log[day]["intake"] for day in last_7_days]

    fig, ax = plt.subplots()
    ax.bar(dates, calories, color='skyblue')
    ax.axhline(calorie_goal, color='red', linestyle='--', label='권장 섭취량')
    plt.xticks(rotation=45)
    plt.ylabel("칼로리 (kcal)")
    plt.title("주간 섭취 칼로리")
    plt.legend()
    st.pyplot(fig)

    avg = sum(calories) / len(calories)
    st.info(f"📊 지난 7일 평균 섭취 칼로리: {int(avg)} kcal")

# -------------------- 아침/점심/저녁 식단 추천 -------------------- 
st.markdown("### 🧑‍🍳 하루 식단 추천 (아침/점심/저녁)")

def recommend_meal_by_time(foods, calorie_target, allergies):
    filtered = [f for f in foods if not any(a in f["allergens"] for a in allergies)]
    meal = []
    total = 0
    tries = 0
    max_tries = 100

    while total < calorie_target - 100 and tries < max_tries:
        food = random.choice(filtered)
        if food not in meal:
            meal.append(food)
            total += food["calories"]
        tries += 1

    return meal, total

if st.button("📌 하루 식단 추천받기"):
    breakfast_target = int(calorie_goal * 0.3)
    lunch_target = int(calorie_goal * 0.4)
    dinner_target = int(calorie_goal * 0.3)

    st.subheader("🍞 아침 식단")
    breakfast, cal_b = recommend_meal_by_time(foods, breakfast_target, allergies)
    for f in breakfast:
        st.write(f"- {f['name']} ({f['calories']} kcal, 단백질 {f['protein']}g)")
    st.info(f"아침 총 섭취: {cal_b} kcal")

    st.subheader("🍛 점심 식단")
    lunch, cal_l = recommend_meal_by_time(foods, lunch_target, allergies)
    for f in lunch:
        st.write(f"- {f['name']} ({f['calories']} kcal, 단백질 {f['protein']}g)")
    st.info(f"점심 총 섭취: {cal_l} kcal")

    st.subheader("🍚 저녁 식단")
    dinner, cal_d = recommend_meal_by_time(foods, dinner_target, allergies)
    for f in dinner:
        st.write(f"- {f['name']} ({f['calories']} kcal, 단백질 {f['protein']}g)")
    st.info(f"저녁 총 섭취: {cal_d} kcal")

    total_day = cal_b + cal_l + cal_d
    st.success(f"✅ 하루 총 섭취: {total_day} kcal (권장: {int(calorie_goal)} kcal)")
    
    # 기존 코드 위에 추가
if 'foods' not in st.session_state:
    try:
        with open("custom_foods.json", "r") as f:
            custom_foods = json.load(f)
    except:
        custom_foods = []

    st.session_state.foods = foods + custom_foods

# 전체 foods 리스트는 session_state를 사용
foods = st.session_state.foods

if st.button("음식 추가"):
    new_food = {
        "name": new_name,
        "calories": round(calculated_calories),
        "protein": protein,
        "allergens": new_allergens
    }
    st.session_state.foods.append(new_food)

    # 저장
    custom_foods = [f for f in st.session_state.foods if f["name"] not in [x["name"] for x in foods]]
    with open("custom_foods.json", "w") as f:
        json.dump(custom_foods, f, ensure_ascii=False, indent=2)

    st.success(f"'{new_name}'이(가) 추가되었습니다! 칼로리: {round(calculated_calories)} kcal")
