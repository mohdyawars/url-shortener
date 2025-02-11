from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
import os

load_dotenv()

MONGO_DB_URI = os.environ.get("MONGO_DB_URI")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

# MongoDB Setup
client = AsyncIOMotorClient(MONGO_DB_URI)
db = client.test
collection = db.urls

# Redis Setup
redis_client = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)
