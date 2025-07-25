
from flask import Flask, render_template, request, jsonify
import csv
import io
import os

app = Flask(__name__)

products = [
    {"id": "001", "name": "Milk", "price": 50.0},
    {"id": "002", "name": "Bread", "price": 30.0},
    {"id": "003", "name": "Eggs", "price": 15.0},
    {"id": "004", "name": "Soda", "price": 10.0}
]

transactions = []
transaction_id_counter = 1

ADMIN_USER = os.environ.get('ADMIN_USER', "admin")
ADMIN_PASS = os.environ.get('ADMIN_PASS', "StarSon2025")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('username') == ADMIN_USER and data.get('password') == ADMIN_PASS:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/products')
def get_products():
    return jsonify(products)

@app.route('/generate_receipt', methods=['POST'])
def generate_receipt():
    global transaction_id_counter
    data = request.get_json()
    cart_items = data.get('items', [])
    payment_method = data.get('paymentMethod', 'Cash')
    total = sum(item['price'] * item['qty'] for item in cart_items)

    new_transaction = {
        'id': transaction_id_counter,
        'items': cart_items,
        'total': total,
        'payment_method': payment_method
    }
    transactions.append(new_transaction)
    transaction_id_counter += 1

    return jsonify({
        'receipt_id': new_transaction['id'],
        'total': total,
        'payment_method': payment_method,
        'items': cart_items,
        'qr_img': f'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=StarSon_Receipt_{new_transaction["id"]}'
    })

@app.route('/export_inventory')
def export_inventory():
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(['Product ID', 'Name', 'Price'])
    for product in products:
        writer.writerow([product['id'], product['name'], product['price']])
    return csv_buffer.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=inventory.csv'
    }

if __name__ == '__main__':
    app.run(debug=True)
