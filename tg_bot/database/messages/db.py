import sqlite3


def init_db():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    # Создаем таблицу для чатов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chats (
        chat_id INTEGER PRIMARY KEY
    )
    ''')

    # Создаем таблицу для сообщений
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY,
        chat_id INTEGER,
        FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
    )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            zodiac_sign TEXT
        )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS horoscopes (
            sign_name TEXT PRIMARY KEY,
            horoscope_dict TEXT
        )
        ''')

    conn.commit()
    conn.close()
