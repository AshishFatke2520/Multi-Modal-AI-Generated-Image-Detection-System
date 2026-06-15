import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

from dotenv import load_dotenv
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

async def test_connection():
    print(f"Testing connection to: {MONGODB_URL}")
    client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    try:
        await client.admin.command('ping')
        print("Success! Connected to MongoDB.")
    except Exception as e:
        print(f"Failed to connect: {e}")

asyncio.run(test_connection())
