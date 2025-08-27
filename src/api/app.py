from typing import List, Dict, Any
import os

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ..utils.config import settings
from ..utils.s3_utils import download_file_from_s3

app = FastAPI(title="ML API", version="0.1.0")

_artifact = None
_feature_names: List[str] = []


@app.on_event("startup")
def _load_model_on_startup() -> None:
    global _artifact, _feature_names
    path = settings.model_local_path
    if not os.path.exists(path):
        try:
            path = download_file_from_s3()
        except Exception as exc:
            raise RuntimeError(f"Cannot load model from disk or S3: {exc}") from exc
    _artifact = joblib.load(path)
    _feature_names = list(_artifact.get("feature_names", []))


class PredictRequest(BaseModel):
    items: List[Dict[str, Any]]


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/predict")
async def predict(req: PredictRequest) -> Dict[str, Any]:
    if _artifact is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    model = _artifact["model"]
    X = pd.DataFrame(req.items)

    if _feature_names:
        for col in _feature_names:
            if col not in X.columns:
                X[col] = 0
        X = X[_feature_names]

    preds = model.predict(X)
    result: Dict[str, Any] = {"preds": preds.tolist()}
    try:
        proba = model.predict_proba(X).tolist()
        result["proba"] = proba
    except Exception:
        pass
    return result
