import sqlite3


# Функция сохранения сообщения в бд
def save_message(chat_id, message_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    # Вставляем chat_id, если его еще нет
    cursor.execute('''
    INSERT OR IGNORE INTO chats (chat_id) VALUES (?)
    ''', (chat_id,))

    # Вставляем message_id и связываем его с chat_id
    cursor.execute('''
    INSERT INTO messages (message_id, chat_id) VALUES (?, ?)
    ''', (message_id, chat_id))

    conn.commit()
    conn.close()


# Функция для получения всех сообщений кроме последнего с последующей очисткой БД.
def get_message_ids(chat_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    # Получаем все message_id для данного chat_id
    cursor.execute('''
    SELECT message_id FROM messages WHERE chat_id = ?
    ''', (chat_id,))

    data = cursor.fetchall()[:-1]
    message_ids = [row[0] for row in data]

    for message_id in message_ids:
        cursor.execute('''
        DELETE FROM messages WHERE message_id = ?
        ''', (message_id,))

    conn.commit()
    conn.close()
    return message_ids


# Функа для записи или обновления выбранного ЗЗ
def add_or_update_user_zodiac(user_id, zodiac_sign):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    # Check if the user already exists in the database
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Update the zodiac sign if the user already exists
        cursor.execute('''
        UPDATE users SET zodiac_sign = ? WHERE user_id = ?
        ''', (zodiac_sign, user_id))
    else:
        # Insert a new record if the user does not exist
        cursor.execute('''
        INSERT INTO users (user_id, zodiac_sign) VALUES (?, ?)
        ''', (user_id, zodiac_sign))

    conn.commit()
    conn.close()


def add_or_update_horoscope(sign_name, horoscope_dict):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    # Проверяем, существует ли уже запись с данным знаком зодиака
    cursor.execute('SELECT sign_name FROM horoscopes WHERE sign_name = ?', (sign_name,))
    existing_horoscope = cursor.fetchone()

    if existing_horoscope:
        # Обновляем словарь гороскопа, если запись уже существует
        cursor.execute('''
        UPDATE horoscopes SET horoscope_dict = ? WHERE sign_name = ?
        ''', (horoscope_dict, sign_name))
    else:
        # Вставляем новую запись, если запись не существует
        cursor.execute('''
        INSERT INTO horoscopes (sign_name, horoscope_dict) VALUES (?, ?)
        ''', (sign_name, horoscope_dict))

    conn.commit()
    conn.close()


def get_horoscope(zodiac_sign):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT horoscope_dict FROM horoscopes WHERE sign_name = ?
    ''', (zodiac_sign,))

    horoscope = cursor.fetchone()

    conn.close()

    return horoscope[0] if horoscope else "Horoscope not found for the given zodiac sign."
