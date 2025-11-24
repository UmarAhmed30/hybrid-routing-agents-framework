import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="sys-ml-user",
    password="Admin@123",
    database="model-registry"
)

cursor = conn.cursor()

# 1. Create a table to test inserts
cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 2. Insert a row
cursor.execute("""
    INSERT INTO test_users (name)
    VALUES (%s)
""", ("sahil-test",))
conn.commit()

# 3. Fetch some rows back
cursor.execute("SELECT id, name, created_at FROM test_users ORDER BY id DESC LIMIT 5")
rows = cursor.fetchall()

print("Latest rows:")
for r in rows:
    print(r)

cursor.close()
conn.close()