import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import config
from src.recommend import load_data, recommend

TEST_USERS = [
    ["egg", "onion", "rice", "garlic", "salt", "butter"],
    ["chicken", "garlic", "onion", "salt", "black pepper"],
    ["flour", "sugar", "butter", "eggs", "vanilla extract"],
    ["tomato", "garlic", "olive oil", "basil", "salt"],
    ["salt", "sugar", "butter"],
]

def check_missing_ingredients(df, rarity_map, top_n=5):
    print("Missing Ingredient 분포 체크 (top5 평균)")
    for i, user in enumerate(TEST_USERS):
        top = recommend(user, df, rarity_map, version="v2", top_n=top_n)
        avg_missing = top["ingredients_normalized"].apply(
            lambda lst: len(set(lst) - set(user))
        ).mean()
        print(f"유저 {i+1} {user[:3]}... -> 평균 missing: {avg_missing:.1f}")


def check_common_ingredient_bias(df, rarity_map, top_n=5):
    print("Common 재료 편향 체크 (V2 vs V3 비교)")
    overall = df["common_ingredient_ratio"].mean()
    print(f"전체 레시피 평균 common_ratio: {overall:.3f}")
    for version in ["v2", "v3"]:
        print(f"\n[{version}]")
        for i, user in enumerate(TEST_USERS):
            pw = 0.3 if version == "v2" else 0.5
            top = recommend(user, df, rarity_map, version=version, top_n=top_n, penalty_weight=pw)
            avg_common = top["common_ingredient_ratio"].mean()
            avg_count = top["ingredient_count"].mean()
            flag = "편향 의심" if avg_common > overall + 0.2 else "양호"
            print(f"유저 {i+1} -> common_ratio: {avg_common:.3f}, 평균재료수: {avg_count:.1f} ({flag})")


def check_penalty_sensitivity(df, rarity_map, user, weights=(0.1, 0.3, 0.5, 0.7)):
    print(f"penalty_weight 민감도 분석 (유저: {user[:3]}...)")
    for pw in weights:
        top3 = recommend(user, df, rarity_map, version="v2", top_n=3, penalty_weight=pw)
        print(f"penalty_weight={pw}: {top3['Title'].tolist()}")


if __name__ == "__main__":
    df, rarity_map = load_data()
    check_missing_ingredients(df, rarity_map)
    check_common_ingredient_bias(df, rarity_map)
    check_penalty_sensitivity(df, rarity_map, TEST_USERS[0])