import os
from typing import Tuple

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.ensemble import HistGradientBoostingClassifier

from ..utils.config import settings
from ..utils.s3_utils import upload_file_to_s3


def _load_data(path: str) -> pd.DataFrame:
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path)


def train() -> Tuple[str, dict]:
    df = _load_data(settings.data_path)
    target_col = os.getenv("TARGET_COLUMN", "target")
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in data. Available: {list(df.columns)[:20]} ...")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    stratify = y if y.nunique() <= 20 else None
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=stratify)

    model = HistGradientBoostingClassifier(random_state=42)
    model.fit(X_tr, y_tr)

    y_pred = model.predict(X_te)
    metrics = {"report": classification_report(y_te, y_pred, output_dict=False)}
    try:
        y_proba = model.predict_proba(X_te)[:, 1]
        metrics["roc_auc"] = float(roc_auc_score(y_te, y_proba))
    except Exception:
        pass

    os.makedirs(os.path.dirname(settings.model_local_path), exist_ok=True)
    artifact = {"model": model, "feature_names": list(X.columns)}
    joblib.dump(artifact, settings.model_local_path)

    if os.getenv("UPLOAD_TO_S3", "false").lower() in {"1", "true", "yes"}:
        uri = upload_file_to_s3(settings.model_local_path)
        metrics["model_uri"] = uri
        print("Uploaded model to:", uri)

    print(metrics.get("report", ""))
    if "roc_auc" in metrics:
        print("roc_auc:", metrics["roc_auc"]) 

    return settings.model_local_path, metrics


def main():
    train()


if __name__ == "__main__":
    main()
