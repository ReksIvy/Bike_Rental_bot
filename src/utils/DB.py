import psycopg2
from src.utils.globals import g_state, CONN
from src.utils.logger import log
import os

def get_available_bikes():
    """
    Retrieves all currently available bikes
    """
    with CONN.cursor() as cursor:
        try:
            cursor.execute("select * from available_bikes")
            bike_rows = cursor.fetchall()
            CONN.commit()
            return bike_rows
        except Exception as e:
            log("log/DB.log", e, 40)

async def send_order(data: dict):
    """
    Sends order and client details to the database

    :params data: Normally - context.user_data dictionary, but can be any dict containing valid data about user and order
    """
    with CONN.cursor() as cursor:
        try:
            if not g_state['exists']:
                # If the user is new, we need to add them first
                with open(data['path'], 'rb') as f:
                    passport_data = f.read()
                cursor.callproc('insert_client', [
                    psycopg2.Binary(passport_data),
                    data['pass_num'],
                    data['telegram'],
                    data['pn'],
                    data['fullname'],
                    data['whatsapp']
                ])
                CONN.commit()
            cursor.callproc('insert_order', [
                data['pass_num'],
                data['rent_start'],
                data['rent_end'],
                data['helmets'],
                data['price'],
                data['b_id'],
                data['helmets_kids'],
                data['address'],
                None,
                "Pending",
                1500
            ])
            response = cursor.fetchone()[0]
            CONN.commit()
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
    with CONN.cursor() as cursor:
        try:
            cursor.execute("select * from check_user_exists(%s)", (username, ))
            result = cursor.fetchone()

            if result:
                CONN.commit()
                g_state['exists'] = True
                pass_num, fullname, thai_pn, whatsapp = result
                return pass_num, fullname, thai_pn, whatsapp
            return None, None, None, None
        except Exception as e:
            log("log/DB.log", e, 40)