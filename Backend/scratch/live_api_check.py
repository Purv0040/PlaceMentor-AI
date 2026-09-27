import sys
import os
import asyncio
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, os.path.abspath("Backend"))

from app.main import app
from app.core.database import db_manager

async def test_api():
    print("=== STARTING LIVE API INTEGRATION TEST AGAINST ATLAS ===")
    await db_manager.connect_to_mongo()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        print(f"GET /health: {res.status_code}, data={res.json()}")
        
        res_v1 = await client.get("/api/v1/health")
        print(f"GET /api/v1/health: {res_v1.status_code}, data={res_v1.json()}")
        
        # 2. Check migrated users directly from Atlas DB to get a test user email
        db = db_manager.get_database()
        user_docs = await db["users"].find({}).to_list(10)
        print(f"Total migrated users on Atlas: {len(user_docs)}")
        
        from bson import ObjectId
        for user_doc in user_docs:
            u_id_str = str(user_doc["_id"])
            u_id_oid = user_doc["_id"]
            prof = await db["student_profiles"].find_one({"$or": [{"user_id": u_id_str}, {"user_id": u_id_oid}]})
            if prof:
                print(f"Found profile for user ID {u_id_str[:8]}...: onboarding_completed={prof.get('onboarding_completed')}, step={prof.get('current_step')}")
    
    await db_manager.close_mongo_connection()
    print("=== LIVE API TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_api())
