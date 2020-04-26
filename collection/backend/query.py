Queries = {
    'CHECK_USER_TABLE': '''SELECT 1 FROM users''',
    'CHECK_DATA_TABLE': '''SELECT 1 FROM data''',
    'ADD_DATA_COLUMN': '''ALTER TABLE data ADD COLUMN %s TEXT''',
    'DATA_COLUMN_NAMES': '''PRAGMA table_info('data')''',
    'FETCH_USER':"SELECT * FROM users WHERE user_id = '{user_id}'",
    "FETCH_ALL_USERS": "SELECT user_id, user_type, market FROM users WHERE user_id != '{current_user}'",
    'UPDATE_USER_MARKETS':"UPDATE users SET market = '{markets}' WHERE user_id = '{user_id}'",
    'UPDATE_USER_PASSWORD': "UPDATE users SET password = '{password}' WHERE user_id = '{user_id}'",
    'DELETE_USER':"DELETE FROM users WHERE user_id='{user_id}'",
    'CREATE_NEW_USER':"INSERT INTO users (user_id, user_type, password, market) VALUES ('{user_id}', '{user_type}', '{password}', '{market}')",
    'UPDATE_MY_PASSWORD':"UPDATE users SET password = '{password_new}' WHERE password = '{password_old}' AND user_id = '{user_id}' ",
    'FETCH_DATA':'SELECT * FROM data {filters} ORDER BY 3 ASC, 4 ASC, 5 ASC, 6 ASC',
    'INSERT_DATA_ROW': "INSERT INTO data ({cols}) VALUES ({vals})",
    'CREATE_SUPER_USER': "INSERT INTO users (user_id, password, user_type, market) VALUES ('admin', 'admin', 'super', ''),('external', 'external', 'external', 'AMH')",
    'CREATE_USER_TABLE' : '''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id text NOT NULL,
        password text NOT NULL,
        user_type VARCHAR(10) NOT NULL,
        market text
    )''',
    'CREATE_DATA_TABLE': '''CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        market__market TEXT
    )'''
}

