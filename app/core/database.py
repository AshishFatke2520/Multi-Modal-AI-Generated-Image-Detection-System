from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        connection_string = settings.MONGODB_URL or settings.MONGO_URI
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[settings.DATABASE_NAME]
        print("Connected to MongoDB")

    def close(self):
        if self.client:
            self.client.close()
            print("Closed MongoDB Connection")

db = Database()
