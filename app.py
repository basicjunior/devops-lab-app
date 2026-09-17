import os
import time
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

def get_db_connection():
    # Retry loop — Postgres container may not be ready the instant Flask starts
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "db"),
                database=os.environ.get("DB_NAME", "visits_db"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASSWORD", "postgres"),
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            time.sleep(2)
    raise Exception("Could not connect to database")

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS visits (id SERIAL PRIMARY KEY, count INTEGER NOT NULL);")
    cur.execute("SELECT COUNT(*) FROM visits;")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO visits (count) VALUES (0);")
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE visits SET count = count + 1 WHERE id = 1 RETURNING count;")
    new_count = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Hello from your Dockerized app with Kube", "visits": new_count})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
