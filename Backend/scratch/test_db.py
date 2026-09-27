import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv("Backend/.env")

local_client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
local_db = local_client["placementor_ai"]
users_count = local_db["users"].count_documents({})
profiles_count = local_db["student_profiles"].count_documents({})

print(f"LOCAL_USERS: {users_count}")
print(f"LOCAL_PROFILES: {profiles_count}")

atlas_uri = os.getenv("MONGODB_URL") or os.getenv("MONGODB_URI")
print(f"ATLAS_URI_CONFIGURED: {bool(atlas_uri)}")
if atlas_uri:
    print(f"IS_SRV: {atlas_uri.startswith('mongodb+srv://')}")
    print(f"IS_LOCAL: {'localhost' in atlas_uri}")
    
    # Try connecting to Atlas
    try:
        atlas_client = MongoClient(atlas_uri, serverSelectionTimeoutMS=5000)
        atlas_client.admin.command("ping")
        print("ATLAS_PING: SUCCESS")
        atlas_db = atlas_client["placementor"]
        print(f"ATLAS_USERS_COUNT: {atlas_db['users'].count_documents({})}")
        print(f"ATLAS_PROFILES_COUNT: {atlas_db['student_profiles'].count_documents({})}")
    except Exception as e:
        print(f"ATLAS_PING_ERROR_TYPE: {type(e).__name__}")
        print(f"ATLAS_PING_ERROR: {str(e)[:200]}")
