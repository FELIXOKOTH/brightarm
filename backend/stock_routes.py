from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import sqlite3

stock_bp = Blueprint('stock', __name__)

def get_db():
    conn = sqlite3.connect('starson_pos.db')
    conn.row_factory = sqlite3.Row
    return conn

@stock_bp.route('/stock', methods=['GET'])
def get_stock():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM stock')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)

@stock_bp.route('/stock', methods=['POST'])
def add_stock():
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO stock (name, quantity, threshold, last_updated) VALUES (?, ?, ?, ?)',
                 (data['name'], data['quantity'], data['threshold'], datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Stock item added successfully'})

@stock_bp.route('/stock/<int:stock_id>', methods=['PUT'])
def update_stock(stock_id):
    data = request.json
    conn = get_db()
    conn.execute('UPDATE stock SET name = ?, quantity = ?, threshold = ?, last_updated = ? WHERE id = ?',
                 (data['name'], data['quantity'], data['threshold'], datetime.now(), stock_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Stock item updated'})

@stock_bp.route('/stock/low', methods=['GET'])
def low_stock():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM stock WHERE quantity <= threshold')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)

@stock_bp.route('/report', methods=['GET'])
def report():
    start = request.args.get('start_date')
    end = request.args.get('end_date')
    conn = get_db()
    cursor = conn.execute('''
        SELECT item_name, SUM(quantity) as total_quantity, SUM(total_price) as total_earned
        FROM sales
        WHERE date BETWEEN ? AND ?
        GROUP BY item_name
    ''', (start, end))
    report = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(report)

@stock_bp.route('/stock/take', methods=['POST'])
def stock_take():
    # for demo, just logs a timestamp
    conn = get_db()
    conn.execute('INSERT INTO stock_audit (taken_on) VALUES (?)', (datetime.now(),))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Stock take recorded'})
