from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from src.config import MONGO_URL, MONGO_DB_NAME

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]
deals_collection = db["deals"]

# Function to update riskScore and next_step in a deal
async def update_deal_by_id(deal_id: str, update_data: dict):
    result = await deals_collection.update_one(
        {"_id": ObjectId(deal_id)},
        {"$set": update_data}
    )
    return result.modified_count
