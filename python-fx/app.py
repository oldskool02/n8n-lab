import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify
from datetime import datetime
import os

DB_PATH = "/app/data/fx_state.db"

app = Flask(__name__)

# -----------------------------
# Database helpers
# -----------------------------
def get_secret(env_var, file_var):
    import os
    if file_var in os.environ:
        try:
            with open(os.environ[file_var], "r") as f:
                return f.read().strip()
        except Exception:
            pass
    return os.getenv(env_var)

def get_db():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=get_secret("DB_PASSWORD", "DB_PASSWORD_FILE")
    )

def init_db():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fx_state (
            pair TEXT PRIMARY KEY,
            previous_rate NUMERIC,
            current_rate NUMERIC,
            last_updated TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# -----------------------------
# API endpoint
# -----------------------------

@app.route("/fx", methods=["POST"])
def fx_update():

    data = request.get_json(force=True)

    pair = data.get("pair")
    current_rate = data.get("current_rate")

    if not pair or len(pair) < 6:
        return jsonify({"error": "Invalid currency pair"}), 400

    if current_rate is None:
        return jsonify({"error": "Missing current_rate"}), 400

    # Normalize precision immediately
    current_rate = round(float(current_rate), 4)
    timestamp = data.get(
        "timestamp",
        datetime.utcnow().isoformat()
    )

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT previous_rate, current_rate FROM fx_state WHERE pair = %s",
        (pair,)
    )
    row = cur.fetchone()

    previous_rate = None
    change = 0.0
    percent_change = 0.0
    direction = "→"

    if row is None:
        cur.execute("""
            INSERT INTO fx_state (pair, previous_rate, current_rate, last_updated)
            VALUES (%s, NULL, %s, %s)
        """, (pair, current_rate, timestamp))
    else:
        previous_rate = round(row["current_rate"], 4)
        change = round(current_rate - previous_rate, 6)

        if previous_rate != 0:
            percent_change = round((change / previous_rate * 100), 4)

        direction = "→"

        if change > 0:
            direction = "↑"
        elif change < 0:
            direction = "↓"

        cur.execute("""
            UPDATE fx_state
            SET previous_rate = %s
                current_rate = %s,
                last_updated = %s
            WHERE pair = %s
        """, (previous_rate, current_rate, timestamp, pair))

    conn.commit()
    conn.close()

    return jsonify({
        "pair": pair,
        "previous_rate": previous_rate,
        "current_rate": current_rate,
        "change": change,
        "percent_change": percent_change,
        "direction": direction,
        "timestamp": timestamp
    })


# -----------------------------
# Startup
# -----------------------------

# Run init regardless of server
os.makedirs("/app/data", exist_ok=True)
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
