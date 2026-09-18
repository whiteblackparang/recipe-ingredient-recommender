import ast
import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import config


def load_features():
    df = pd.read_csv(config.FEATURES_CSV_PATH)
    df["ingredients_normalized"] = df["ingredients_normalized"].apply(ast.literal_eval)
    df = df.reset_index().rename(columns={"index": "recipe_id"})
    return df


def build_recipe_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df[[
        "recipe_id", "Title", "ingredient_count", "ingredient_rarity_avg",
        "common_ingredient_ratio", "has_image", "Image_Name",
    ]].copy()


def build_ingredient_long(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        for ing in row["ingredients_normalized"]:
            rows.append({
                "recipe_id": row["recipe_id"],
                "Title": row["Title"],
                "ingredient": ing,
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = load_features()

    summary = build_recipe_summary(df)
    long_df = build_ingredient_long(df)

    os.makedirs("outputs/tableau", exist_ok=True)
    summary.to_csv("outputs/tableau/recipe_summary.csv", index=False)
    long_df.to_csv("outputs/tableau/ingredient_long.csv", index=False)

    print(f"recipe_summary: {summary.shape[0]}행 -> outputs/tableau/recipe_summary.csv")
    print(f"ingredient_long: {long_df.shape[0]}행 -> outputs/tableau/ingredient_long.csv")
    print("ingredient_stats.csv는 outputs/ingredient_stats.csv에 이미 있음 (ingredient 컬럼으로 join 가능)")