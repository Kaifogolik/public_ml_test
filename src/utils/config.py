from dataclasses import dataclass
import os


@dataclass
class Settings:
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    s3_bucket: str = os.getenv("S3_BUCKET", "ml-models-bucket")
    s3_region: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    model_local_path: str = os.getenv("MODEL_LOCAL_PATH", "models/model.joblib")
    model_s3_key: str = os.getenv("MODEL_S3_KEY", "model.joblib")

    data_path: str = os.getenv("DATA_PATH", "src/input/dataset.parquet")


settings = Settings()
