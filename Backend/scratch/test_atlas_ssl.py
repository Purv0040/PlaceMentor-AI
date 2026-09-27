import sys
import os
sys.path.insert(0, os.path.abspath("Backend"))
import certifi
from pymongo import MongoClient
from app.core.config import settings

atlas_uri = settings.get_mongo_uri()
print("Testing with certifi...")

try:
    client = MongoClient(atlas_uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("Atlas Ping with certifi: SUCCESS!")
except Exception as e:
    print(f"Atlas Ping with certifi failed: {type(e).__name__} - {e}")
    try:
        print("Testing with tlsAllowInvalidCertificates=True...")
        client = MongoClient(atlas_uri, tls=True, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("Atlas Ping with tlsAllowInvalidCertificates=True: SUCCESS!")
    except Exception as e2:
        print(f"Atlas Ping with tlsAllowInvalidCertificates failed: {type(e2).__name__} - {e2}")
