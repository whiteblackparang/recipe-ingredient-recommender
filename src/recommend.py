import ast
import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import config

def load_data():
    df = pd.read_csv(config.FEATURES_CSV_PATH)
    df["ingredients_normalized"] = df["ingredients_normalized"].apply(ast.literal_eval)
    stats = pd.read_csv(config.INGREDIENT_STATS_PATH)
    rarity_map = dict(zip(stats["ingredient"], stats["rarity"]))
    return df, rarity_map

# 첫번째
def score_v1(user_ingredients: set, recipe_ingredients: list) -> tuple:
    recipe_set = set(recipe_ingredients)
    matched = user_ingredients & recipe_set
    match_rate = len(matched) / len(recipe_set) if recipe_set else 0
    missing_count = len(recipe_set - user_ingredients)
    return match_rate, missing_count

# 두번째
def score_v2(user_ingredients, recipe_ingredients, rarity_map, penalty_weight=0.3):
    recipe_set = set(recipe_ingredients)
    matched = user_ingredients & recipe_set
    missing = recipe_set - user_ingredients

    total_rarity = sum(rarity_map.get(i, 0) for i in recipe_set)
    matched_rarity = sum(rarity_map.get(i, 0) for i in matched)
    weighted_coverage = matched_rarity / total_rarity if total_rarity > 0 else 0

    missing_ratio = len(missing) / len(recipe_set) if recipe_set else 0
    return weighted_coverage - penalty_weight * missing_ratio

# 세번째 
def score_v3(user_ingredients, recipe_ingredients, rarity_map, penalty_weight=0.5):
    recipe_set = set(recipe_ingredients)
    matched = user_ingredients & recipe_set
    missing_count = len(recipe_set - user_ingredients)

    matched_rarity_sum = sum(rarity_map.get(i, 0) for i in matched)
    return matched_rarity_sum - penalty_weight * missing_count

def recommend(user_ingredients, df, rarity_map, version="v2", top_n=5, penalty_weight=0.3):
    user_set = set(user_ingredients)
    result = df.copy()

    if version == "v1":
        scores = result["ingredients_normalized"].apply(lambda lst: score_v1(user_set, lst))
        result["match_rate"], result["missing_count"] = zip(*scores)
        result = result.sort_values(["match_rate", "missing_count"], ascending=[False, True])
    elif version == "v2":
        result["score"] = result["ingredients_normalized"].apply(
            lambda lst: score_v2(user_set, lst, rarity_map, penalty_weight)
        )
        result = result.sort_values("score", ascending=False)
    elif version == "v3":
        result["score"] = result["ingredients_normalized"].apply(
            lambda lst: score_v3(user_set, lst, rarity_map, penalty_weight)
        )
        result = result.sort_values("score", ascending=False)
    else:
        raise ValueError(f"알 수 없는 버전: {version}")

    return result.head(top_n)


if __name__ == "__main__":
    df, rarity_map = load_data()

    user_have = ["egg", "onion", "rice", "garlic", "salt", "butter"]

    print("첫번째 (단순 매칭률)")
    top_v1 = recommend(user_have, df, rarity_map, version="v1", top_n=5)
    print(top_v1[["Title", "match_rate", "missing_count"]])

    print()
    print("두번째 (rarity 가중치)")
    top_v2 = recommend(user_have, df, rarity_map, version="v2", top_n=5)
    print(top_v2[["Title", "score"]])
    
    print()
    print("Version 3 (절대량 기준)")
    print(recommend(user_have, df, rarity_map, version="v3", top_n=5, penalty_weight=0.5)[["Title", "score"]])