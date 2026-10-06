import os
import json
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Determine path to serviceAccountKey.json
# Check relative to this file's parent (backend directory), or root, or via env variable
current_file_dir = Path(__file__).resolve().parent  # backend/firebase
backend_dir = current_file_dir.parent               # backend
project_root = backend_dir.parent                  # workspace root

def get_firebase_credentials():
    """
    Resolve credentials for Firebase Admin SDK:
    1. FIREBASE_CREDENTIALS_PATH environment variable if set.
    2. FIREBASE_CREDENTIALS_JSON environment variable (for Render / cloud deployments).
    3. serviceAccountKey.json in backend/ directory.
    4. serviceAccountKey.json in project root directory.
    """
    env_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if env_path and Path(env_path).exists():
        return credentials.Certificate(env_path)

    env_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if env_json:
        try:
            cert_dict = json.loads(env_json)
            return credentials.Certificate(cert_dict)
        except Exception as e:
            print(f"Warning: Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")

    backend_key = backend_dir / "serviceAccountKey.json"
    if backend_key.exists():
        return credentials.Certificate(str(backend_key))

    root_key = project_root / "serviceAccountKey.json"
    if root_key.exists():
        return credentials.Certificate(str(root_key))

    raise FileNotFoundError(
        "Firebase credentials not found! Place 'serviceAccountKey.json' in 'backend/' "
        "or define 'FIREBASE_CREDENTIALS_PATH' / 'FIREBASE_CREDENTIALS_JSON'."
    )

def initialize_firebase():
    """Initialize Firebase Admin SDK only once."""
    if not firebase_admin._apps:
        cred = get_firebase_credentials()
        firebase_admin.initialize_app(cred, {
            "projectId": "garmentmanager-ae69f"
        })
        print("[Firebase] Admin SDK initialized successfully for project: garmentmanager-ae69f")

initialize_firebase()

# Expose Firestore client and Auth
db = firestore.client()
