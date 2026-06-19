import psycopg2

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5433,
        database="alemeno",
        user="postgres",
        password="postgres"
    )

    print("Connected successfully!")
    conn.close()

except Exception as e:
    print("Error:", e)