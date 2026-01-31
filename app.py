#!/usr/bin/env python3
"""Simple Flask backend for tracking utility bills."""

import os
import sqlite3
from datetime import date
from flask import Flask, jsonify, request, g, send_from_directory, render_template, redirect

# Configuration
DATABASE = os.environ.get("DATABASE_PATH", "bills.db")
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path="")


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


def parse_float(value, default=0):
    """Convert form value to float, handling empty strings."""
    if value == "" or value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


# Jinja2 Template Filters

@app.template_filter('format_currency')
def format_currency(value):
    """Format number as currency."""
    if value is None or value == '':
        return "$0.00"
    try:
        return f"${float(value):.2f}"
    except (ValueError, TypeError):
        return "$0.00"


@app.template_filter('format_date')
def format_date(date_str):
    """Format date string as 'Jan 28, 2026'."""
    if not date_str:
        return ""
    try:
        from datetime import datetime
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return date_str


@app.template_filter('total_cost')
def calculate_total_cost(bill):
    """Calculate total cost from all cost fields."""
    return (
        (bill.get('gas_cost') or 0) +
        (bill.get('electricity_delivery_cost') or 0) +
        (bill.get('electricity_generation_cost') or 0) +
        (bill.get('other_cost') or 0)
    )


@app.template_filter('total_kwh')
def calculate_total_kwh(bill):
    """Calculate total electricity kWh."""
    return (
        (bill.get('electricity_on_peak_kwh') or 0) +
        (bill.get('electricity_off_peak_kwh') or 0) +
        (bill.get('electricity_super_off_peak_kwh') or 0)
    )


# Health Check

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


# API Routes (used by HTMX)

@app.route("/api/bills/<int:bill_id>", methods=["DELETE"])
def delete_bill(bill_id):
    """Delete a bill."""
    db = get_db()

    cursor = db.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
    if cursor.fetchone() is None:
        return jsonify({"error": "Bill not found"}), 404

    db.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
    db.commit()

    # Return empty response for HTMX
    if request.headers.get('HX-Request'):
        return '', 200
    return jsonify({"message": "Bill deleted successfully"})


# Template Routes

@app.route("/")
def bills_list():
    """Render bills list page."""
    db = get_db()
    cursor = db.execute("SELECT * FROM bills ORDER BY date DESC")
    bills = [row_to_dict(row) for row in cursor.fetchall()]
    return render_template('bills_list.html', bills=bills)


@app.route("/add")
def add_bill():
    """Render create bill form."""
    return render_template('bill_form.html',
                         is_editing=False,
                         default_date=date.today().isoformat())


@app.route("/edit/<int:bill_id>")
def edit_bill(bill_id):
    """Render edit bill form."""
    db = get_db()
    cursor = db.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
    bill = row_to_dict(cursor.fetchone())
    if bill is None:
        return "Bill not found", 404
    return render_template('bill_form.html',
                         is_editing=True,
                         bill=bill)


@app.route("/history")
def history():
    """Render electricity usage history page."""
    db = get_db()
    show_all = request.args.get('all', '').lower() == 'true'

    # Get last 13 months or all entries, then reverse to show chronologically
    if show_all:
        cursor = db.execute("""
            SELECT date, electricity_on_peak_kwh, electricity_off_peak_kwh,
                   electricity_super_off_peak_kwh, gas_cost, electricity_delivery_cost,
                   electricity_generation_cost, other_cost
            FROM bills
            ORDER BY date DESC
        """)
    else:
        cursor = db.execute("""
            SELECT date, electricity_on_peak_kwh, electricity_off_peak_kwh,
                   electricity_super_off_peak_kwh, gas_cost, electricity_delivery_cost,
                   electricity_generation_cost, other_cost
            FROM bills
            ORDER BY date DESC
            LIMIT 13
        """)
    bills = [row_to_dict(row) for row in cursor.fetchall()]
    # Reverse to show chronologically (oldest to newest)
    bills.reverse()

    # Prepare data for charts
    dates = [bill['date'] for bill in bills]
    on_peak = [bill['electricity_on_peak_kwh'] or 0 for bill in bills]
    off_peak = [bill['electricity_off_peak_kwh'] or 0 for bill in bills]
    super_off_peak = [bill['electricity_super_off_peak_kwh'] or 0 for bill in bills]

    gas_cost = [bill['gas_cost'] or 0 for bill in bills]
    el_delivery_cost = [bill['electricity_delivery_cost'] or 0 for bill in bills]
    el_generation_cost = [bill['electricity_generation_cost'] or 0 for bill in bills]
    other_cost = [bill['other_cost'] or 0 for bill in bills]

    return render_template('history.html',
                         bills=bills,
                         dates=dates,
                         on_peak=on_peak,
                         off_peak=off_peak,
                         super_off_peak=super_off_peak,
                         gas_cost=gas_cost,
                         el_delivery_cost=el_delivery_cost,
                         el_generation_cost=el_generation_cost,
                         other_cost=other_cost,
                         show_all=show_all)


# Form Submission Routes

@app.route("/bills/create", methods=["POST"])
def create_bill_form():
    """Handle form submission for creating a bill."""
    bill_date = request.form.get('date')

    if not bill_date:
        return render_template('bill_form.html',
                             error="Date is required",
                             form=request.form,
                             is_editing=False,
                             default_date=date.today().isoformat())

    db = get_db()
    try:
        db.execute("""
            INSERT INTO bills (
                date, gas_cost, electricity_delivery_cost, electricity_generation_cost,
                other_cost, gas_therms, electricity_on_peak_kwh, electricity_off_peak_kwh,
                electricity_super_off_peak_kwh
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bill_date,
            parse_float(request.form.get('gas_cost')),
            parse_float(request.form.get('electricity_delivery_cost')),
            parse_float(request.form.get('electricity_generation_cost')),
            parse_float(request.form.get('other_cost')),
            parse_float(request.form.get('gas_therms')),
            parse_float(request.form.get('electricity_on_peak_kwh')),
            parse_float(request.form.get('electricity_off_peak_kwh')),
            parse_float(request.form.get('electricity_super_off_peak_kwh')),
        ))
        db.commit()
        return redirect('/')
    except sqlite3.IntegrityError:
        return render_template('bill_form.html',
                             error="A bill with this date already exists",
                             form=request.form,
                             is_editing=False,
                             default_date=bill_date)


@app.route("/bills/update/<int:bill_id>", methods=["POST"])
def update_bill_form(bill_id):
    """Handle form submission for updating a bill."""
    bill_date = request.form.get('date')

    if not bill_date:
        db = get_db()
        cursor = db.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        bill = row_to_dict(cursor.fetchone())
        return render_template('bill_form.html',
                             error="Date is required",
                             form=request.form,
                             is_editing=True,
                             bill=bill)

    db = get_db()
    cursor = db.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
    if cursor.fetchone() is None:
        return "Bill not found", 404

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
            bill_date,
            parse_float(request.form.get('gas_cost')),
            parse_float(request.form.get('electricity_delivery_cost')),
            parse_float(request.form.get('electricity_generation_cost')),
            parse_float(request.form.get('other_cost')),
            parse_float(request.form.get('gas_therms')),
            parse_float(request.form.get('electricity_on_peak_kwh')),
            parse_float(request.form.get('electricity_off_peak_kwh')),
            parse_float(request.form.get('electricity_super_off_peak_kwh')),
            bill_id,
        ))
        db.commit()
        return redirect('/')
    except sqlite3.IntegrityError:
        cursor = db.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        bill = row_to_dict(cursor.fetchone())
        return render_template('bill_form.html',
                             error="A bill with this date already exists",
                             form=request.form,
                             is_editing=True,
                             bill=bill)


# Initialize database on import (for gunicorn)
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
