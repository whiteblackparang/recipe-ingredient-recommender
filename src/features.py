import ast
import math
import os
import sys
from collections import Counter

import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import config


def load_cleaned():
    df = pd.read_csv(config.CLEANED_CSV_PATH)
    df["ingredients_normalized"] = df["ingredients_normalized"].apply(ast.literal_eval)
    return df


def build_ingredient_stats(df: pd.DataFrame) -> pd.DataFrame:
    n_recipes = len(df)
    all_ingredients = [ing for lst in df["ingredients_normalized"] for ing in lst]
    freq = Counter(all_ingredients)

    stats = pd.DataFrame({
        "ingredient": list(freq.keys()),
        "frequency": list(freq.values()),
    })
    stats["frequency_ratio"] = stats["frequency"] / n_recipes
    stats["rarity"] = stats["frequency_ratio"].apply(lambda r: math.log(1 / r))
    stats["is_common"] = stats["frequency_ratio"] >= config.COMMON_INGREDIENT_THRESHOLD

    return stats.sort_values("frequency", ascending=False).reset_index(drop=True)


def add_recipe_features(df: pd.DataFrame, ingredient_stats: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rarity_map = dict(zip(ingredient_stats["ingredient"], ingredient_stats["rarity"]))
    common_set = set(ingredient_stats[ingredient_stats["is_common"]]["ingredient"])

    def avg_rarity(lst):
        if not lst:
            return 0.0
        return sum(rarity_map.get(i, 0.0) for i in lst) / len(lst)

    def common_ratio(lst):
        if not lst:
            return 0.0
        return sum(1 for i in lst if i in common_set) / len(lst)

    df["ingredient_rarity_avg"] = df["ingredients_normalized"].apply(avg_rarity)
    df["common_ingredient_ratio"] = df["ingredients_normalized"].apply(common_ratio)

    return df


if __name__ == "__main__":
    df = load_cleaned()

    ingredient_stats = build_ingredient_stats(df)
    print(f"고유 재료 수: {len(ingredient_stats)}")
    print(f"Common 재료 수: {ingredient_stats['is_common'].sum()}")
    print(ingredient_stats.head(10))

    df_with_features = add_recipe_features(df, ingredient_stats)
    print(df_with_features[["Title", "ingredient_count", "ingredient_rarity_avg", "common_ingredient_ratio"]].head(5))

    os.makedirs("outputs", exist_ok=True)
    ingredient_stats.to_csv(config.INGREDIENT_STATS_PATH, index=False)
    df_with_features.to_csv(config.FEATURES_CSV_PATH, index=False)
    print(f"완료: {config.INGREDIENT_STATS_PATH}, {config.FEATURES_CSV_PATH}")