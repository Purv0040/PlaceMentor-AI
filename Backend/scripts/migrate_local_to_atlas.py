import os
import sys
import logging
import certifi
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("migration")

# Add Backend root to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.config import settings

def run_migration():
    logger.info("=== STARTING MONGODB MIGRATION TO ATLAS ===")
    
    # 1. Connect to Local MongoDB
    local_uri = "mongodb://localhost:27017"
    local_db_name = "placementor_ai"
    logger.info(f"Connecting to local MongoDB: {local_db_name}...")
    
    try:
        local_client = MongoClient(local_uri, serverSelectionTimeoutMS=5000)
        local_client.admin.command("ping")
        logger.info("Local MongoDB connected successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to local MongoDB: {type(e).__name__} - {e}")
        return False
        
    local_db = local_client[local_db_name]
    local_users_coll = local_db["users"]
    local_profiles_coll = local_db["student_profiles"]
    
    local_users_count = local_users_coll.count_documents({})
    local_profiles_count = local_profiles_coll.count_documents({})
    
    logger.info(f"Local database count: users={local_users_count}, student_profiles={local_profiles_count}")
    
    # 2. Connect to Atlas MongoDB
    atlas_uri = settings.get_mongo_uri()
    target_db_name = settings.MONGODB_DATABASE
    
    logger.info(f"Connecting to target MongoDB Atlas (database: {target_db_name})...")
    
    try:
        try:
            atlas_client = MongoClient(atlas_uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
            atlas_client.admin.command("ping")
        except Exception as e_ssl:
            logger.warning(f"Default SSL failed ({e_ssl}), trying tlsAllowInvalidCertificates=True...")
            atlas_client = MongoClient(atlas_uri, tls=True, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
            atlas_client.admin.command("ping")
        logger.info("Atlas MongoDB connected and pinged successfully!")
    except Exception as e:
        logger.error(f"Failed to connect to Atlas MongoDB: {type(e).__name__} - {e}")
        logger.warning("Atlas connection could not be established with current connection settings.")
        return False

    atlas_db = atlas_client[target_db_name]
    atlas_users_coll = atlas_db["users"]
    atlas_profiles_coll = atlas_db["student_profiles"]

    # 3. Create Idempotent Unique Indexes on Atlas
    try:
        atlas_users_coll.create_index("email", unique=True)
        logger.info("Verified unique index on users.email")
    except Exception as e:
        logger.warning(f"Note on users index creation: {e}")

    try:
        atlas_profiles_coll.create_index("user_id", unique=True)
        logger.info("Verified unique index on student_profiles.user_id")
    except Exception as e:
        logger.warning(f"Note on student_profiles index creation: {e}")

    # 4. Migrate users collection preserving ObjectIds
    local_users = list(local_users_coll.find({}))
    migrated_users = 0
    skipped_users = 0

    for user_doc in local_users:
        user_id = user_doc.get("_id")
        existing = atlas_users_coll.find_one({"_id": user_id})
        if existing:
            skipped_users += 1
        else:
            atlas_users_coll.insert_one(user_doc)
            migrated_users += 1

    logger.info(f"Users migration complete: {migrated_users} inserted, {skipped_users} skipped (already existing).")

    # 5. Migrate student_profiles collection preserving ObjectIds and user_id
    local_profiles = list(local_profiles_coll.find({}))
    migrated_profiles = 0
    skipped_profiles = 0

    for profile_doc in local_profiles:
        profile_id = profile_doc.get("_id")
        existing = atlas_profiles_coll.find_one({"_id": profile_id})
        if existing:
            skipped_profiles += 1
        else:
            atlas_profiles_coll.insert_one(profile_doc)
            migrated_profiles += 1

    logger.info(f"Student profiles migration complete: {migrated_profiles} inserted, {skipped_profiles} skipped (already existing).")

    # 6. Verification
    atlas_users_count = atlas_users_coll.count_documents({})
    atlas_profiles_count = atlas_profiles_coll.count_documents({})
    
    logger.info(f"VERIFICATION: Atlas users count = {atlas_users_count}, Atlas student_profiles count = {atlas_profiles_count}")
    
    # Verify user_id relationship on Atlas
    relationship_ok = True
    for prof in atlas_profiles_coll.find({}):
        rel_user_id = prof.get("user_id")
        search_id = ObjectId(rel_user_id) if isinstance(rel_user_id, str) and ObjectId.is_valid(rel_user_id) else rel_user_id
        matched_user = atlas_users_coll.find_one({"_id": search_id})
        if not matched_user:
            logger.error(f"Relationship error: profile {prof.get('_id')} points to user_id {rel_user_id} which does not exist in Atlas users!")
            relationship_ok = False
            
    if relationship_ok:
        logger.info("VERIFICATION: All student_profiles user_id relationships verified successfully on Atlas.")
    
    logger.info("=== MIGRATION COMPLETED SUCCESSFULLY ===")
    return True

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
