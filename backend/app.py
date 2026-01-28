#!/usr/bin/env python3
"""Simple Flask backend for tracking utility bills."""

import os
import sqlite3
from flask import Flask, jsonify, request, g, send_from_directory
from flask_cors import CORS

# Configuration
DATABASE = os.environ.get("DATABASE_PATH", "bills.db")
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path="")
CORS(app)


def get_db():
    """Get database connection for current request."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Close database connection at end of request."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database with the bills table."""
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                gas_cost REAL DEFAULT 0,
                electricity_delivery_cost REAL DEFAULT 0,
                electricity_generation_cost REAL DEFAULT 0,
                other_cost REAL DEFAULT 0,
                gas_therms REAL DEFAULT 0,
                electricity_on_peak_kwh REAL DEFAULT 0,
                electricity_off_peak_kwh REAL DEFAULT 0,
                electricity_super_off_peak_kwh REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()


def row_to_dict(row):
    """Convert a sqlite3.Row to a dictionary."""
    if row is None:
        return None
    return dict(row)


# API Routes

@app.route("/api/bills", methods=["GET"])
def get_bills():
    """Get all bills, ordered by date descending."""
    db = get_db()
    cursor = db.execute("SELECT * FROM bills ORDER BY date DESC")
    bills = [row_to_dict(row) for row in cursor.fetchall()]
    return jsonify(bills)


@app.route("/api/bills/<int:bill_id>", methods=["GET"])
def get_bill(bill_id):
    """Get a single bill by ID."""
    db = get_db()
    cursor = db.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
    bill = row_to_dict(cursor.fetchone())
    if bill is None:
        return jsonify({"error": "Bill not found"}), 404
    return jsonify(bill)


@app.route("/api/bills", methods=["POST"])
def create_bill():
    """Create a new bill."""
    data = request.get_json()

    if not data or "date" not in data:
        return jsonify({"error": "Date is required"}), 400

    db = get_db()
    try:
        cursor = db.execute("""
            INSERT INTO bills (
                date, gas_cost, electricity_delivery_cost, electricity_generation_cost,
                other_cost, gas_therms, electricity_on_peak_kwh, electricity_off_peak_kwh,
                electricity_super_off_peak_kwh
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["date"],
            data.get("gas_cost", 0),
            data.get("electricity_delivery_cost", 0),
            data.get("electricity_generation_cost", 0),
            data.get("other_cost", 0),
            data.get("gas_therms", 0),
            data.get("electricity_on_peak_kwh", 0),
            data.get("electricity_off_peak_kwh", 0),
            data.get("electricity_super_off_peak_kwh", 0),
        ))
        db.commit()

        # Return the created bill
        cursor = db.execute("SELECT * FROM bills WHERE id = ?", (cursor.lastrowid,))
        return jsonify(row_to_dict(cursor.fetchone())), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "A bill with this date already exists"}), 400


@app.route("/api/bills/<int:bill_id>", methods=["PUT"])
def update_bill(bill_id):
    """Update an existing bill."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    db = get_db()

    # Check if bill exists
    cursor = db.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
    if cursor.fetchone() is None:
        return jsonify({"error": "Bill not found"}), 404

    try:
        db.execute("""
            UPDATE bills SET
                date = ?,
                gas_cost = ?,
                electricity_delivery_cost = ?,
                electricity_generation_cost = ?,
                other_cost = ?,
                gas_therms = ?,
                electricity_on_peak_kwh = ?,
                electricity_off_peak_kwh = ?,
                electricity_super_off_peak_kwh = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data.get("date"),
            data.get("gas_cost", 0),
            data.get("electricity_delivery_cost", 0),
            data.get("electricity_generation_cost", 0),
            data.get("other_cost", 0),
            data.get("gas_therms", 0),
            data.get("electricity_on_peak_kwh", 0),
            data.get("electricity_off_peak_kwh", 0),
            data.get("electricity_super_off_peak_kwh", 0),
            bill_id,
        ))
        db.commit()

        # Return the updated bill
        cursor = db.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        return jsonify(row_to_dict(cursor.fetchone()))
    except sqlite3.IntegrityError:
        return jsonify({"error": "A bill with this date already exists"}), 400


@app.route("/api/bills/<int:bill_id>", methods=["DELETE"])
def delete_bill(bill_id):
    """Delete a bill."""
    db = get_db()

    cursor = db.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
    if cursor.fetchone() is None:
        return jsonify({"error": "Bill not found"}), 404

    db.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
    db.commit()

    return jsonify({"message": "Bill deleted successfully"})


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


# Static file serving for production

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path):
    """Serve static files and handle SPA routing."""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


# Initialize database on import (for gunicorn)
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
