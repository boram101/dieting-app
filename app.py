import streamlit as st
import json
import datetime
import matplotlib.pyplot as plt
import os

# -------------------- 초기 설정 --------------------
st.set_page_config(page_title="개인 맞춤 식단 설계 프로그램")
st.title("🥗 개인 맞춤 식단 설계 프로그램")

# -------------------- 기본 음식 데이터 --------------------
default_foods = [
    {"name": "닭가슴살", "calories": 165, "protein": 31, "allergens": []},
    {"name": "현미밥", "calories": 220, "protein": 4, "allergens": []},
    {"name": "두부", "calories": 76, "protein": 8, "allergens": ["콩"]},
    {"name": "우유", "calories": 150, "protein": 8, "allergens": ["우유"]},
    {"name": "계란", "calories": 70, "protein": 6, "allergens": ["달걀"]},
    {"name": "사과", "calories": 52, "protein": 0.3, "allergens": []},
    {"name": "오트밀", "calories": 68, "protein": 2.4, "allergens": []},
    {"name": "그릭요거트", "calories": 59, "protein": 10, "allergens": ["우유"]},
]

FOODS_FILE = "foods_custom.json"

# -------------------- 사용자 음식 저장 및 불러오기 --------------------
def load_custom_foods():
    if os.path.exists(FOODS_FILE):
        with open(FOODS_FILE, "r") as f:
            return json.load(f)
    return []

def save_custom_food(food):
    foods = load_custom_foods()
    foods.append(food)
    with open(FOODS_FILE, "w") as f:
        json.dump(foods, f, ensure_ascii=False, indent=2)

# 모든 음식 합치기
foods = default_foods + load_custom_foods()

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

# -------------------- 식사 기록 --------------------
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
age = st.sidebar.number_input("나이", 10, 100, 25)
gender = st.sidebar.selectbox("성별", ["남성", "여성"])
height = st.sidebar.number_input("키 (cm)", 100, 250, 170)
weight = st.sidebar.number_input("몸무게 (kg)", 30, 200, 70)
allergy_options = ["우유", "콩", "달걀"]
custom_allergen = st.sidebar.text_input("기타 알레르기 직접 입력")
allergies = st.sidebar.multiselect("알레르기", allergy_options)
if custom_allergen:
    allergies.append(custom_allergen)
health = st.sidebar.text_input("건강 상태", placeholder="예: 고혈압")
goal = st.sidebar.selectbox("목표", ["다이어트", "근육 증가", "건강 유지"])

user_info = {
    "age": age, "gender": gender, "height": height,
    "weight": weight, "allergies": allergies,
    "health": health, "goal": goal
}

# -------------------- 권장 칼로리 --------------------
bmr = calculate_bmr(gender, weight, height, age)
calorie_goal = get_calorie_goal(bmr, goal)
st.markdown(f"### 🧮 하루 권장 섭취 칼로리: {int(calorie_goal)} kcal")

# -------------------- 추천 식단 --------------------
st.markdown("### 🥗 추천 식단 (알레르기 고려)")
recommended = [f for f in foods if not any(a in f["allergens"] for a in allergies)]
for food in recommended:
    st.write(f"- {food['name']} ({food['calories']} kcal, 단백질 {food['protein']}g)")

# -------------------- 음식 추가 --------------------
with st.expander("🍱 음식 추가하기"):
    new_name = st.text_input("음식 이름")
    input_mode = st.radio("입력 방식 선택", ["칼로리 직접 입력", "영양소 기반 계산"])
    if input_mode == "칼로리 직접 입력":
        new_cal = st.number_input("칼로리", 0, 1000, step=10)
    else:
        carbs = st.number_input("탄수화물 (g)", 0.0, 200.0, step=0.1)
        fats = st.number_input("지방 (g)", 0.0, 100.0, step=0.1)
        protein = st.number_input("단백질 (g)", 0.0, 100.0, step=0.1)
        new_cal = round(carbs * 4 + protein * 4 + fats * 9, 1)
    new_protein = st.number_input("단백질 (g)", 0.0, 100.0, step=0.1) if input_mode == "칼로리 직접 입력" else protein
    new_allergens = st.multiselect("알레르기 성분", allergy_options, key="add")
    if st.button("음식 추가"):
        new_food = {
            "name": new_name, "calories": new_cal,
            "protein": new_protein, "allergens": new_allergens
        }
        save_custom_food(new_food)
        st.success(f"'{new_name}'이(가) 추가되었습니다. 새로고침 후 사용 가능합니다.")

# -------------------- 오늘 식단 입력 --------------------
st.markdown("### 🍽️ 오늘 하루 먹은 음식")
meal_names = [f["name"] for f in foods]
selected_meals = st.multiselect("음식 선택", meal_names)
direct_meal = st.text_input("직접 입력한 음식 (쉼표로 구분)")

intake = 0
if st.button("📊 칼로리 계산 및 저장"):
    intake += sum(f["calories"] for f in foods if f["name"] in selected_meals)
    today = datetime.date.today().isoformat()
    if direct_meal:
        direct_items = [name.strip() for name in direct_meal.split(",") if name.strip()]
        for item in direct_items:
            match = next((f for f in foods if f["name"] == item), None)
            if match:
                intake += match["calories"]
                selected_meals.append(item)
            else:
                st.warning(f"'{item}'은(는) 데이터에 없습니다. [음식 추가하기]로 등록해주세요.")
    log = load_log()
    log[today] = {"meals": selected_meals, "intake": intake}
    save_log(log)
    st.success(f"오늘 총 섭취 칼로리: {intake} kcal 저장 완료!")

# -------------------- 주간 섭취 기록 --------------------
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
