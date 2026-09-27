from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017")
db = client["placementor_ai"]

print("--- USERS ---")
for u in db["users"].find({}):
    print(f"User _id: {repr(u['_id'])}, type: {type(u['_id'])}")

print("\n--- STUDENT PROFILES ---")
for p in db["student_profiles"].find({}):
    uid = p.get("user_id")
    print(f"Profile _id: {repr(p['_id'])}, user_id: {repr(uid)}, user_id type: {type(uid)}")
    
    # Check if matching user exists in local users
    match_oid = db["users"].find_one({"_id": ObjectId(uid) if isinstance(uid, str) else uid})
    match_str = db["users"].find_one({"_id": str(uid)}) if isinstance(uid, (str, ObjectId)) else None
    print(f"  Match with ObjectId({uid}): {bool(match_oid)}")
    print(f"  Match with str({uid}): {bool(match_str)}")
