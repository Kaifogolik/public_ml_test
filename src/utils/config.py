from dataclasses import dataclass
import os
from typing import Optional

import yaml


CONFIG_PATH = os.getenv("CONFIG_PATH", os.path.join("configs", "config.yaml"))


@dataclass
class Settings:
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket: str = "ml-models-bucket"
    s3_region: str = "us-east-1"

    model_local_path: str = "models/model.joblib"
    model_s3_key: str = "model.joblib"

    data_path: str = "src/input/dataset.parquet"
    target_column: str = "target"
    upload_to_s3: bool = False

    @staticmethod
    def from_sources() -> "Settings":
        # 1) YAML файл как базовый источник
        base = {}
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f) or {}
            # поддержка вложенной структуры из README
            aws = content.get("aws", {})
            s3 = content.get("s3", {})
            paths = content.get("paths", {})
            training = content.get("training", {})
            base = {
                "aws_access_key_id": aws.get("access_key_id", ""),
                "aws_secret_access_key": aws.get("secret_access_key", ""),
                "s3_bucket": s3.get("bucket", "ml-models-bucket"),
                "s3_region": aws.get("region", "us-east-1"),
                "model_local_path": paths.get("model_local", "models/model.joblib"),
                "model_s3_key": s3.get("model_key", "model.joblib"),
                "data_path": paths.get("data", "src/input/dataset.parquet"),
                "target_column": training.get("target_column", "target"),
                "upload_to_s3": bool(training.get("upload_to_s3", False)),
            }
        # 2) ENV перекрывают YAML
        env = {
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", base.get("aws_access_key_id", "")),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", base.get("aws_secret_access_key", "")),
            "s3_bucket": os.getenv("S3_BUCKET", base.get("s3_bucket", "ml-models-bucket")),
            "s3_region": os.getenv("AWS_DEFAULT_REGION", base.get("s3_region", "us-east-1")),
            "model_local_path": os.getenv("MODEL_LOCAL_PATH", base.get("model_local_path", "models/model.joblib")),
            "model_s3_key": os.getenv("MODEL_S3_KEY", base.get("model_s3_key", "model.joblib")),
            "data_path": os.getenv("DATA_PATH", base.get("data_path", "src/input/dataset.parquet")),
            "target_column": os.getenv("TARGET_COLUMN", base.get("target_column", "target")),
            "upload_to_s3": os.getenv("UPLOAD_TO_S3", str(base.get("upload_to_s3", False))).lower() in {"1","true","yes"},
        }
        return Settings(**env)


settings = Settings.from_sources()
