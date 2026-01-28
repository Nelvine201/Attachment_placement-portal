import sqlite3

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

try:
    # This manually adds the column that Django is missing
    cursor.execute(
        "ALTER TABLE portal_employer ADD COLUMN user_id integer REFERENCES auth_user(id);"
    )
    conn.commit()
    print("Success! The user_id column has been added.")
except sqlite3.OperationalError as e:
    print(f"Note: {e}")

conn.close()
