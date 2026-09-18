"""9단계: Streamlit 데모 (데이터 대시보드 + 이미지 카드형).

실행: streamlit run app/app.py  (프로젝트 루트에서)
"""
import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.recommend import load_data, recommend

st.set_page_config(page_title="Food Recipe Recommendation", layout="wide")

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]


@st.cache_data
def get_data():
    return load_data()


def find_image_path(image_name: str):
    """Image_Name에 맞는 실제 파일 경로를 찾는다. 없으면 None."""
    for ext in IMAGE_EXTENSIONS:
        path = os.path.join(config.IMAGE_DIR, image_name + ext)
        if os.path.exists(path):
            return path
    return None


def render_metrics(results, user_ingredients):
    """상단 요약 지표."""
    col1, col2, col3, col4 = st.columns(4)

    avg_missing = results["ingredients_normalized"].apply(
        lambda lst: len(set(lst) - set(user_ingredients))
    ).mean()
    avg_rarity = results["ingredient_rarity_avg"].mean()
    avg_common_ratio = results["common_ingredient_ratio"].mean()

    col1.metric("추천 레시피 수", len(results))
    col2.metric("평균 부족 재료", f"{avg_missing:.1f}개")
    col3.metric("평균 재료 rarity", f"{avg_rarity:.2f}")
    col4.metric("평균 common 비율", f"{avg_common_ratio:.0%}")


def render_score_chart(results, version):
    """추천된 레시피들의 점수 비교 차트."""
    score_col = "score" if version != "v1" else "match_rate"
    chart_data = results.set_index("Title")[[score_col]]
    st.bar_chart(chart_data)


def render_recipe_cards(results, user_ingredients, version):
    """이미지 카드 그리드."""
    score_col = "score" if version != "v1" else "match_rate"
    cols = st.columns(3)

    for i, (_, row) in enumerate(results.iterrows()):
        recipe_set = set(row["ingredients_normalized"])
        matched = recipe_set & set(user_ingredients)
        missing = recipe_set - set(user_ingredients)

        with cols[i % 3]:
            with st.container(border=True):
                image_path = find_image_path(row["Image_Name"]) if row["has_image"] else None
                if image_path:
                    st.image(image_path, use_container_width=True)
                else:
                    st.caption("이미지 없음")

                st.markdown(f"**{row['Title']}**")
                st.caption(f"재료 {row['ingredient_count']}개 | 점수 {row[score_col]:.3f}")

                st.markdown(f"가진 재료: {', '.join(sorted(matched)) if matched else '없음'}")
                st.markdown(f"부족한 재료: {', '.join(sorted(missing)) if missing else '없음'}")


def main():
    st.title("냉장고 재료로 레시피 추천")
    st.caption("가진 재료를 입력하면 매칭 스코어 상위 레시피를 추천합니다 (V3 로직 기준)")

    df, rarity_map = get_data()

    with st.sidebar:
        st.header("설정")
        version = st.selectbox("추천 버전", ["v3", "v2", "v1"], index=0)
        top_n = st.slider("추천 개수", 3, 12, 6)
        penalty_weight = st.slider("Missing 재료 페널티", 0.0, 1.5, 0.5, step=0.1)

    ingredients_input = st.text_input(
        "가진 재료를 콤마(,)로 구분해서 입력하세요",
        placeholder="예: egg, onion, rice, garlic, salt, butter",
    )

    if st.button("추천받기") and ingredients_input.strip():
        user_ingredients = [i.strip().lower() for i in ingredients_input.split(",") if i.strip()]

        results = recommend(
            user_ingredients, df, rarity_map,
            version=version, top_n=top_n, penalty_weight=penalty_weight,
        )

        st.divider()
        render_metrics(results, user_ingredients)

        st.divider()
        render_score_chart(results, version)

        st.divider()
        render_recipe_cards(results, user_ingredients, version)


if __name__ == "__main__":
    main()