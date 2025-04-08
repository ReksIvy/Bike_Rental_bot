import pyodbc
from utils.globals import g_state, CONN_STR
from utils.logger import log
import os

conn = pyodbc.connect(CONN_STR)

def get_available_bikes():
    """
    Retrieves all currently available bikes
    """
    with conn.cursor() as cursor:
        try:
            bike_rows = cursor.execute("select * from available_bikes").fetchall()
            return bike_rows
        except Exception as e:
            log("log/DB.log", e, 40)

async def send_order(data: dict):
    """
    Sends order and client details to the database

    :params data: Normally - context.user_data dictionary, but can be any dict containing valid data about user and order
    """
    with conn.cursor() as cursor:
        try:
            if not g_state['exists']:
                # If the user is new, we need to add them first
                cursor.execute(f"exec InsertClient @c_passport = \"{data['path']}\"," +
                            f"@c_passport_num = \"{data['pass_num']}\", @c_telegram = \"{data['telegram']}\", @c_thai_pn = \"{data['pn']}\"," +
                            f"@c_fullname = \"{data['fullname']}\", @c_whatsapp = \"{data['whatsapp']}\"")
            response = cursor.execute(f"exec InsertOrder @c_passport_num = \"{data['pass_num']}\", @o_id = 1, @o_delivery_date = \"{data['rent_start']}\"," +
                        f"@o_rent_end = \"{data['rent_end']}\", @o_helmets = {data['helmets']}, @o_price_total = {data['price']}, " +
                        f"@b_id = \"{data['b_id']}\", @o_helmets_kids = {data['helmets_kids']}, @o_address = \"{data['address']}\"").fetchall()[0][0]
            # Delete the passport photo from local storage
            if 'path' in data and os.path.exists(data['path']):
                os.remove(data['path'])
            return response
        except Exception as e:
            log("log/DB.log", e, 40)

async def is_new_user(username: str):
    """
    Determines whether the user is new and fetches all personal info

    :params username: User's telegram username
    """
    with conn.cursor() as cursor:
        try:
            users = cursor.execute('select c_telegram from Clients').fetchall()
            t_link = f'https://t.me/{username}'
            for row in users:
                if row[0] == f'https://t.me/{username}':
                    user_data = cursor.execute('select c_passport_num, c_fullname, c_thai_pn, c_whatsapp from Clients where c_telegram = ?', (t_link,)).fetchone()
                    if user_data:
                        g_state['exists'] = True
                        pass_num, fullname, thai_pn, whatsapp = user_data
                        return pass_num, fullname, thai_pn, whatsapp
            return None, None, None, None
        except Exception as e:
            log("log/DB.log", e, 40)