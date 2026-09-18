import ast
import re
import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import config

PAREN_PATTERN = re.compile(r"\([^)]*\)")

FRACTION_CHARS = "½⅓⅔¼¾⅛⅜⅝⅞"
FRACTION_PATTERN = re.compile("[" + FRACTION_CHARS + "]")

UNIT_PATTERN = re.compile(
    r"\b(\d+([./]\d+)?|"
    r"teaspoons?|tsp\.?|tablespoons?|tbsp\.?|cups?|oz\.?|lb\.?|lbs?\.?|g|kg|ml|l|"
    r"cloves?|pinch(es)?|piece s?|inch|\"|"
    r"large|small|medium|fresh|freshly|chopped|sliced|minced|divided|"
    r"room temperature|thinly|finely|good.quality|sturdy|"
    r"ground|kosher|unsalted|plus|to taste|torn into|cut into|"
    r"optional|for serving|stems removed|about|total|packed|lightly|of)\b",
    flags=re.IGNORECASE,
)
PUNCT_PATTERN = re.compile(r"[^\w\s]")


def parse_ingredient_list(raw: str) -> list:
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list):
            return parsed
    except (ValueError, SyntaxError):
        pass
    return []


def normalize_ingredient(text: str) -> str:
    text = text.lower()
    text = PAREN_PATTERN.sub("", text)
    text = text.split(",")[0]
    text = FRACTION_PATTERN.sub("", text)
    text = UNIT_PATTERN.sub("", text)
    text = PUNCT_PATTERN.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    col = config.COLUMNS

    df = df.dropna(subset=[col["title"]])
    df["has_image"] = df[col["image_name"]] != config.MISSING_IMAGE_PLACEHOLDER
    df["ingredients_list"] = df[col["ingredients_raw"]].apply(parse_ingredient_list)
    df["ingredients_normalized"] = df["ingredients_list"].apply(
        lambda lst: [n for n in (normalize_ingredient(i) for i in lst) if n]
    )
    df["ingredient_count"] = df["ingredients_normalized"].apply(len)
    df = df[df["ingredient_count"] > 0].reset_index(drop=True)

    return df


if __name__ == "__main__":
    from src.data import load_raw

    raw = load_raw()
    cleaned = clean_dataframe(raw)

    print(f"원본: {raw.shape[0]}행 -> 전처리 후: {cleaned.shape[0]}행")
    print(cleaned[["Title", "ingredients_normalized", "ingredient_count", "has_image"]].head(5))

    os.makedirs("outputs", exist_ok=True)
    cleaned.to_csv(config.CLEANED_CSV_PATH, index=False)
    print(f"완료: {config.CLEANED_CSV_PATH}")