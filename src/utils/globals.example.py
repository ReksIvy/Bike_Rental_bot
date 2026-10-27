# Template for globals.py (gitignored): copy it to globals.py and fill in TOKEN and ADMIN_CHAT.
import pathlib
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

GREETINGS, BIKE_SELECTION, LANGUAGE, PERSONAL_INFORMATION, ORDER_COMPLETE = range(5)

g_state = {
    "editing": False, # If the user is editing their order data
    "exists": False, # If the user exists in DB
    "message_id": any, # Required to edit some messages
    "chat_id": any # Current chat_id
}

CONN = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
TOKEN = "" # Bot token from @BotFather
PATH = pathlib.Path().resolve() # Bot path
ADMIN_CHAT = 0 # Chat to which the order details are sent after user forms an order