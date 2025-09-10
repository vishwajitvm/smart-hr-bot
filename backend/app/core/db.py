# app/core/db.py
import os
from pymongo import MongoClient
from cryptography.fernet import Fernet
from app.core.config import settings

# Setup encryption
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

# MongoDB client
client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

# Collections
users_collection = db["users"]
chatlogs_collection = db["chat_logs"]
tokens_collection = db["tokens"]
keka_tokens_collection = db["keka_tokens"]
candidates_collection = db["candidates"]
jobs_collection = db["jobs"]
candidate_scores_collection = db["candidate_scores"]

# Encryption helpers
def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

# Generic token save
def save_token(user_id: str, provider: str, access_token: str, refresh_token: str = None):
    data = {
        "user_id": user_id,
        "provider": provider,
        "access_token": encrypt_token(access_token)
    }
    if refresh_token:
        data["refresh_token"] = encrypt_token(refresh_token)

    tokens_collection.update_one(
        {"user_id": user_id, "provider": provider},
        {"$set": data},
        upsert=True
    )

def get_token(user_id: str, provider: str):
    token = tokens_collection.find_one({"user_id": user_id, "provider": provider})
    if token and "access_token" in token:
        token["access_token"] = decrypt_token(token["access_token"])
    if token and "refresh_token" in token:
        token["refresh_token"] = decrypt_token(token["refresh_token"])
    return token

def delete_token(user_id: str, provider: str):
    return tokens_collection.delete_one({"user_id": user_id, "provider": provider})
