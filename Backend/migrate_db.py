"""
One-time migration script: Copy all collections from source MongoDB → target MongoDB.

Usage:
    python migrate_db.py

Edit SOURCE_URI, TARGET_URI, and DB_NAME below before running.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — Edit these before running!
# ─────────────────────────────────────────────────────────────────────────────
SOURCE_URI = "mongodb://localhost:27017"         # Your CURRENT connection
TARGET_URI = "mongodb+srv://ddsavaliya2006_db_user:IgmE8d7t8tdUly4w@placementor.sda9o3c.mongodb.net/"  # Your NEW connection
DB_NAME    = "placementor"                       # Database name to migrate
# ─────────────────────────────────────────────────────────────────────────────


COLLECTIONS = [
    "users",
    "student_profiles",
]


async def migrate():
    print(f"Connecting to SOURCE: {SOURCE_URI}")
    source_client = AsyncIOMotorClient(SOURCE_URI, serverSelectionTimeoutMS=10000)
    source_db = source_client[DB_NAME]

    print(f"Connecting to TARGET: {TARGET_URI}")
    target_client = AsyncIOMotorClient(TARGET_URI, serverSelectionTimeoutMS=10000)
    target_db = target_client[DB_NAME]

    # Verify connections
    await source_client.admin.command("ping")
    print("✅ Source connection OK")
    await target_client.admin.command("ping")
    print("✅ Target connection OK")

    for collection_name in COLLECTIONS:
        print(f"\n📦 Migrating collection: {collection_name} ...")
        source_collection = source_db[collection_name]
        target_collection = target_db[collection_name]

        docs = await source_collection.find({}).to_list(length=None)
        count = len(docs)

        if count == 0:
            print(f"   ⚠️  No documents found in '{collection_name}', skipping.")
            continue

        # Insert into target (ignore duplicates)
        result = await target_collection.insert_many(docs, ordered=False)
        print(f"   ✅ Migrated {len(result.inserted_ids)}/{count} documents from '{collection_name}'")

    # Re-create required indexes on target
    print("\n🔧 Creating indexes on target ...")
    await target_db["users"].create_index("email", unique=True, background=True)
    print("   ✅ Index created: users.email (unique)")
    await target_db["student_profiles"].create_index("user_id", unique=True, background=True)
    print("   ✅ Index created: student_profiles.user_id (unique)")

    source_client.close()
    target_client.close()
    print("\n🎉 Migration complete!")


if __name__ == "__main__":
    asyncio.run(migrate())
