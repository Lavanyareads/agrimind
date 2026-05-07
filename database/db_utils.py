import os
from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Initialize MongoDB Client
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.get_database('agrimind') # Explicitly use 'agrimind' database
except Exception as e:
    print(f"Database connection error: {e}")
    db = None

# --- USER OPERATIONS ---
def create_user(username, email, password, farm_name):
    """Creates a new user with a hashed password."""
    if db is None: return False, "Database connection error"
    
    users_collection = db['users']
    
    # Check if username or email already exists
    if users_collection.find_one({"$or": [{"username": username}, {"email": email}]}):
        return False, "Username or Email already exists"
        
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    user_doc = {
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "farm_name": farm_name,
        "created_at": datetime.now()
    }
    
    users_collection.insert_one(user_doc)
    return True, "User created successfully"

def authenticate_user(username, password):
    """Authenticates a user and returns the user document if successful."""
    if db is None: return False, None
    
    users_collection = db['users']
    user = users_collection.find_one({"username": username})
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        return True, user
    return False, None

# --- LIVESTOCK OPERATIONS ---
def add_livestock(user_id, species, breed, state, weight, age, milk_yield):
    if db is None: return False
    livestock_collection = db['livestock']
    
    doc = {
        "user_id": user_id,
        "species": species,
        "breed": breed,
        "state": state,
        "weight_kg": weight,
        "age_years": age,
        "milk_yield_liters": milk_yield,
        "created_at": datetime.now()
    }
    result = livestock_collection.insert_one(doc)
    return str(result.inserted_id)

def get_livestock_by_user(user_id):
    if db is None: return []
    return list(db['livestock'].find({"user_id": user_id}))

# --- MIGRATION (Optional Helper) ---
def migrate_excel_to_db(df, user_id):
    """Helper to bulk insert from the provided excel dataset if needed."""
    if db is None: return
    # This can be expanded later
    pass
