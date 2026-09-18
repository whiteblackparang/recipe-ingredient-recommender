import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import config


def load_raw():
    df = pd.read_csv(config.CSV_PATH)
    return df


def inspect(df: pd.DataFrame):
    report = {}
    report["shape"] = df.shape
    report["columns"] = df.columns.tolist()
    report["missing"] = df.isna().sum().to_dict()

    img_col = config.COLUMNS["image_name"]
    report["duplicate_image_names"] = int(df[img_col].duplicated().sum())
    report["missing_image_placeholder_count"] = int(
        (df[img_col] == config.MISSING_IMAGE_PLACEHOLDER).sum()
    )

    if os.path.isdir(config.IMAGE_DIR):
        actual_files = set(os.listdir(config.IMAGE_DIR))
        report["image_dir_file_count"] = len(actual_files)
        expected_names = set(
            df[df[img_col] != config.MISSING_IMAGE_PLACEHOLDER][img_col].astype(str)
        )
        missing_files = [
            n for n in list(expected_names)[:500]
            if not any(f.startswith(n) for f in actual_files)
        ]
        report["sample_missing_file_count_in_first_500_check"] = len(missing_files)
    else:
        report["image_dir_file_count"] = "IMAGE_DIR 경로를 config.py에서 확인할 것 (아직 못 찾음)"

    return report


if __name__ == "__main__":
    df = load_raw()
    report = inspect(df)
    for k, v in report.items():
        print(f"{k}: {v}")