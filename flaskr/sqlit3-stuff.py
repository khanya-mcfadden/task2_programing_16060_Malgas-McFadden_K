import sqlite3

connection = sqlite3.connect('users.db')
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS contact (
    contact_id INTEGER PRIMARY KEY,
    userid INTEGER,
    is_error BOOLEAN DEFAULT 0,
    error_message TEXT,
    feedback_message TEXT,
    email TEXT,
    what_error TEXT,
    is_contacted BOOLEAN DEFAULT 0,
    FOREIGN KEY (userid) REFERENCES users(id)
)
""")
connection.commit()
cursor.close()
