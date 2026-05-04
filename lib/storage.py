import json
import os
from datetime import timedelta

from google.cloud import storage
from google.oauth2 import service_account

_client: storage.Client | None = None


def _get_client() -> storage.Client:
    global _client
    if _client is not None:
        return _client

    creds_json = os.getenv("GCS_CREDENTIALS_JSON")
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if creds_json:
        info = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(info)
        _client = storage.Client(
            project=info.get("project_id"),
            credentials=credentials,
        )
    elif creds_path:
        _client = storage.Client.from_service_account_json(creds_path)
    else:
        raise RuntimeError(
            "GCS non configuré : définissez GOOGLE_APPLICATION_CREDENTIALS ou GCS_CREDENTIALS_JSON"
        )
    return _client


def _bucket_name() -> str:
    return os.getenv("GCS_BUCKET", "ramery-agrement")


def upload_datasheet(file_bytes: bytes, agrement_id: str) -> str:
    """Upload PDF vers GCS. Retourne le blob_name stocké en base."""
    client = _get_client()
    blob_name = f"datasheets/{agrement_id}.pdf"
    blob = client.bucket(_bucket_name()).blob(blob_name)
    blob.upload_from_string(file_bytes, content_type="application/pdf")
    return blob_name


def get_download_url(blob_name: str, expiry_minutes: int = 60) -> str:
    """Génère une URL signée valide pendant `expiry_minutes` minutes."""
    client = _get_client()
    blob = client.bucket(_bucket_name()).blob(blob_name)
    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiry_minutes),
        method="GET",
    )


def delete_datasheet(blob_name: str) -> None:
    """Supprime le blob GCS si il existe."""
    client = _get_client()
    blob = client.bucket(_bucket_name()).blob(blob_name)
    if blob.exists():
        blob.delete()
