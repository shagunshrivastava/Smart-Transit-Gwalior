from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORS(app)

DATABASE = "transport.db"

# ──────────────────────────────────────────────
# DB HELPERS
# ──────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Routes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        destination TEXT,
        distance REAL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Fares(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id INTEGER UNIQUE,
        fare REAL,
        FOREIGN KEY(route_id) REFERENCES Routes(id) ON DELETE CASCADE
    )""")

    conn.commit()
    conn.close()


def seed_data():
    conn = get_db()
    cur = conn.cursor()

    # ── Seed default admin user ──
    cur.execute("SELECT COUNT(*) FROM Users WHERE role='admin'")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO Users(username,password,role) VALUES(?,?,?)",
            ("admin", "admin123", "admin")
        )

    # ── Seed Gwalior routes ──
    cur.execute("SELECT COUNT(*) FROM Routes")
    if cur.fetchone()[0] == 0:
        routes = [
            ("Gwalior Railway Station", "Bus Stand (ISBT)",        4,   15),
            ("Gwalior Railway Station", "Gwalior Fort",             3,   12),
            ("Gwalior Railway Station", "City Centre",              5,   20),
            ("Gwalior Railway Station", "Lashkar",                  6,   22),
            ("Gwalior Railway Station", "Jiwaji University",        8,   28),
            ("Gwalior Railway Station", "Morar",                    9,   30),
            ("Gwalior Railway Station", "Gwalior Airport",         18,   60),
            ("Bus Stand (ISBT)",        "City Centre",              3,   12),
            ("Bus Stand (ISBT)",        "DD Nagar",                 5,   18),
            ("Bus Stand (ISBT)",        "Gandhi Nagar",             6,   20),
            ("Bus Stand (ISBT)",        "Kampoo Bus Stand",         4,   15),
            ("Bus Stand (ISBT)",        "Phool Bagh",               7,   25),
            ("Bus Stand (ISBT)",        "Thatipur",                10,   35),
            ("City Centre",             "DB Mall",                  2,   10),
            ("City Centre",             "Padav",                    4,   15),
            ("City Centre",             "Baija Taal",               3,   12),
            ("City Centre",             "Jai Vilas Palace",         2,   10),
            ("City Centre",             "Gwalior Fort",             5,   18),
            ("City Centre",             "GRMC Gwalior",             3,   12),
            ("City Centre",             "Jayarogya Hospital (JAH)", 4,   15),
            ("City Centre",             "Sun Temple",               6,   22),
            ("Lashkar",                 "DD Mall",                  3,   12),
            ("Lashkar",                 "Patel Nagar",              4,   15),
            ("Lashkar",                 "Birla Nagar",              5,   18),
            ("Lashkar",                 "Keshar Towers",            3,   12),
            ("Morar",                   "ITM University Gwalior",   6,   22),
            ("Morar",                   "MITS Gwalior",             7,   25),
            ("Thatipur",                "Cancer Hospital & Research Institute", 5, 18),
            ("Tansen Tomb",             "Gwalior Fort",             2,   10),
            ("Govindpuri",              "Gwalior Railway Station",  7,   25),
        ]

        for (src, dst, dist, fare) in routes:
            cur.execute(
                "INSERT INTO Routes(source,destination,distance) VALUES(?,?,?)",
                (src, dst, dist)
            )
            route_id = cur.lastrowid
            cur.execute(
                "INSERT INTO Fares(route_id,fare) VALUES(?,?)",
                (route_id, fare)
            )

    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────

@app.route('/')
def home():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/selection.html')
def passenger_page():
    return send_from_directory(BASE_DIR, 'selection.html')

@app.route('/admin.html')
def admin_page():
    return send_from_directory(BASE_DIR, 'admin.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory(BASE_DIR, 'style.css')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(BASE_DIR, filename)


# ── LOGIN ──────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    role     = (data.get("role")     or "passenger").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    conn = get_db()
    cur  = conn.cursor()

    if role == "admin":
        cur.execute(
            "SELECT * FROM Users WHERE username=? AND password=? AND role='admin'",
            (username, password)
        )
        user = cur.fetchone()
        conn.close()
        if user:
            return jsonify({"success": True, "role": "admin", "username": username})
        return jsonify({"error": "Invalid admin credentials."}), 401

    else:  # passenger
        cur.execute(
            "SELECT * FROM Users WHERE username=? AND password=? AND role='passenger'",
            (username, password)
        )
        user = cur.fetchone()
        conn.close()
        if user:
            return jsonify({"success": True, "role": "passenger", "username": username})
        return jsonify({"error": "Invalid credentials. If you are a new user, please sign up."}), 401


# ── SIGNUP ─────────────────────────────────────
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    
    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Users(username, password, role) VALUES(?, ?, 'passenger')",
            (username, password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Username already exists."}), 400
    conn.close()
    return jsonify({"success": True, "role": "passenger", "username": username})


# ── LOCATIONS ──────────────────────────────────
@app.route('/api/locations', methods=['GET'])
def get_locations():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT DISTINCT source AS name FROM Routes UNION SELECT DISTINCT destination FROM Routes ORDER BY name")
    locs = [r["name"] for r in cur.fetchall()]
    conn.close()
    return jsonify(locs)


# ── ALL ROUTES (plain) ──────────────────────────
@app.route('/api/routes', methods=['GET'])
def get_routes():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM Routes ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ── ROUTES WITH FARES ──────────────────────────
@app.route('/api/routes/withFares', methods=['GET'])
def get_routes_with_fares():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT Routes.id, Routes.source, Routes.destination, Routes.distance,
               COALESCE(Fares.fare, 0) AS fare, Fares.id AS fare_id
        FROM Routes
        LEFT JOIN Fares ON Routes.id = Fares.route_id
        ORDER BY Routes.id
    """)
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ── CALCULATE FARE ─────────────────────────────
@app.route('/api/calculateFare', methods=['GET', 'POST'])
def calculate_fare():
    if request.method == 'POST':
        data         = request.json or {}
        source       = data.get("source", "")
        destination  = data.get("destination", "")
        vehicle_type = data.get("vehicle_type", "City Bus")
    else:
        source       = request.args.get("source", "")
        destination  = request.args.get("destination", "")
        vehicle_type = request.args.get("vehicle_type", "City Bus")

    if not source or not destination:
        return jsonify({"error": "Source and destination are required."}), 400

    if source == destination:
        return jsonify({"error": "Source and destination cannot be the same."}), 400

    # Determine multiplier based on vehicle type
    multiplier = 1.0
    if vehicle_type == "AC Bus":
        multiplier = 1.5
    elif vehicle_type == "Cab":
        multiplier = 3.0

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT Routes.source, Routes.destination, Routes.distance,
               Fares.fare
        FROM Routes
        JOIN Fares ON Routes.id = Fares.route_id
    """)
    edges = cur.fetchall()
    conn.close()

    # Build adjacency list for an undirected graph
    graph = {}
    for edge in edges:
        u = edge["source"]
        v = edge["destination"]
        dist = edge["distance"]
        fare = edge["fare"] * multiplier
        
        if u not in graph: graph[u] = []
        if v not in graph: graph[v] = []
        
        graph[u].append((v, dist, fare))
        graph[v].append((u, dist, fare))

    import heapq
    # Priority queue stores: (total_distance, total_fare, current_node, path)
    # path is a list of dicts: [{"stop": source, "leg_fare": 0.0}]
    pq = [(0.0, 0.0, source, [{"stop": source, "leg_fare": 0.0}])]
    visited = set()

    while pq:
        curr_dist, curr_fare, u, path = heapq.heappop(pq)

        if u == destination:
            return jsonify({
                "source":      source,
                "destination": destination,
                "distance":    round(curr_dist, 2),
                "fare":        round(curr_fare, 2),
                "route":       path
            })

        if u in visited:
            continue
        visited.add(u)

        for v, dist, fare in graph.get(u, []):
            if v not in visited:
                new_path = list(path)
                new_path.append({"stop": v, "leg_fare": round(fare, 2)})
                heapq.heappush(pq, (curr_dist + dist, curr_fare + fare, v, new_path))

    return jsonify({"error": "Route not found between selected stops."}), 404

# ── BOOK TRIP ──────────────────────────────
@app.route('/api/book', methods=['POST'])
def book_trip():
    import random
    data = request.json or {}
    
    drivers = ["Rajesh Kumar", "Amit Singh", "Suresh Sharma", "Vijay Yadav", "Deepak Gupta"]
    vehicles = ["MP 07 BG 4512", "MP 07 AH 9821", "MP 07 RT 3345", "MP 07 BK 1109"]
    
    booking_id = f"TRP-{random.randint(10000, 99999)}"
    otp = random.randint(1000, 9999)
    driver = random.choice(drivers)
    vehicle = random.choice(vehicles)
    
    return jsonify({
        "success": True,
        "booking_id": booking_id,
        "otp": otp,
        "driver_name": driver,
        "vehicle_no": vehicle,
        "trip_details": data
    })


# ── ADD ROUTE ──────────────────────────────────
@app.route('/api/addRoute', methods=['POST'])
def add_route():
    data        = request.json or {}
    source      = (data.get("source")      or "").strip()
    destination = (data.get("destination") or "").strip()
    distance    = data.get("distance")
    fare        = data.get("fare")

    if not source or not destination or distance is None or fare is None:
        return jsonify({"error": "All fields (source, destination, distance, fare) are required."}), 400

    try:
        distance = float(distance)
        fare     = float(fare)
    except (TypeError, ValueError):
        return jsonify({"error": "Distance and fare must be numbers."}), 400

    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO Routes(source,destination,distance) VALUES(?,?,?)",
        (source, destination, distance)
    )
    route_id = cur.lastrowid
    cur.execute(
        "INSERT INTO Fares(route_id,fare) VALUES(?,?)",
        (route_id, fare)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Route added successfully.", "id": route_id})


# ── UPDATE FARE ────────────────────────────────
@app.route('/api/updateFare', methods=['POST'])
def update_fare():
    data     = request.json or {}
    route_id = data.get("route_id")
    fare     = data.get("fare")

    if route_id is None or fare is None:
        return jsonify({"error": "route_id and fare are required."}), 400

    try:
        fare = float(fare)
    except (TypeError, ValueError):
        return jsonify({"error": "Fare must be a number."}), 400

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT id FROM Routes WHERE id=?", (route_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Route not found."}), 404

    cur.execute(
        "UPDATE Fares SET fare=? WHERE route_id=?",
        (fare, route_id)
    )
    if cur.rowcount == 0:
        cur.execute("INSERT INTO Fares(route_id,fare) VALUES(?,?)", (route_id, fare))

    conn.commit()
    conn.close()
    return jsonify({"message": "Fare updated successfully."})


# ── DELETE ROUTE ───────────────────────────────
@app.route('/api/deleteRoute/<int:id>', methods=['DELETE'])
def delete_route(id):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM Fares  WHERE route_id=?", (id,))
    cur.execute("DELETE FROM Routes WHERE id=?",       (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Route deleted successfully."})


# ──────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    seed_data()
    app.run(debug=True)