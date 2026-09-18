CSV_PATH = "data/Food_Ingredients_and_Recipe_Dataset_with_Image_Name_Mapping.csv"
IMAGE_DIR = "data/Food Images"

COLUMNS = {
    "index": "Unnamed: 0",
    "title": "Title",
    "ingredients_raw": "Ingredients",
    "instructions": "Instructions",
    "image_name": "Image_Name",
    "ingredients_cleaned": "Cleaned_Ingredients",
}

MISSING_IMAGE_PLACEHOLDER = "#NAME?"

CLEANED_CSV_PATH = "outputs/recipes_cleaned.csv"
FEATURES_CSV_PATH = "outputs/recipes_with_features.csv"
INGREDIENT_STATS_PATH = "outputs/ingredient_stats.csv"
COMMON_INGREDIENT_THRESHOLD = 0.05