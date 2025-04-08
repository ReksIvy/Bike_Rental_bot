import json

USER_LANG_FILE = "user_languages.json"

def load_user_languages():
    try:
        with open(USER_LANG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_languages():
    with open(USER_LANG_FILE, "w") as file:
        json.dump(user_languages, file)

def load_translations():
    with open("translations.json", 'r', encoding='utf-8') as file:
        return json.load(file)

user_languages = load_user_languages()

translations = load_translations()