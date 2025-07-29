from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database file path
DATABASE_FILE = 'database.json'

def load_database():
    """Load database from JSON file"""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "customers": [],
        "orders": [],
        "products": [],
        "settings": {}
    }

def save_database(data):
    """Save database to JSON file"""
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    """Serve the main website"""
    return render_template('index.html')

@app.route('/api/customers', methods=['GET', 'POST'])
def handle_customers():
    """Handle customer data"""
    db = load_database()
    
    if request.method == 'GET':
        return jsonify(db['customers'])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new customer
        customer = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data.get('address', ''),
            'city': data.get('city', ''),
            'postal_code': data.get('postal_code', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Check if customer already exists
        for existing_customer in db['customers']:
            if existing_customer['email'] == customer['email']:
                return jsonify({'error': 'Customer with this email already exists'}), 400
        
        db['customers'].append(customer)
        save_database(db)
        
        return jsonify({
            'message': 'Customer created successfully',
            'customer': customer
        }), 201

@app.route('/api/customers/<customer_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_customer_by_id(customer_id):
    """Handle individual customer operations"""
    db = load_database()
    
    # Find customer
    customer = None
    customer_index = None
    for i, c in enumerate(db['customers']):
        if c['id'] == customer_id:
            customer = c
            customer_index = i
            break
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    if request.method == 'GET':
        return jsonify(customer)
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        # Update customer data
        for key in ['name', 'email', 'phone', 'address', 'city', 'postal_code']:
            if key in data:
                customer[key] = data[key]
        
        customer['updated_at'] = datetime.now().isoformat()
        db['customers'][customer_index] = customer
        save_database(db)
        
        return jsonify({
            'message': 'Customer updated successfully',
            'customer': customer
        })
    
    elif request.method == 'DELETE':
        db['customers'].pop(customer_index)
        save_database(db)
        return jsonify({'message': 'Customer deleted successfully'})

@app.route('/api/orders', methods=['GET', 'POST'])
def handle_orders():
    """Handle order data"""
    db = load_database()
    
    if request.method == 'GET':
        return jsonify(db['orders'])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_id', 'items', 'total_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new order
        order = {
            'id': str(uuid.uuid4()),
            'customer_id': data['customer_id'],
            'items': data['items'],  # Array of {product_id, quantity, price}
            'total_amount': data['total_amount'],
            'status': data.get('status', 'pending'),
            'notes': data.get('notes', ''),
            'delivery_address': data.get('delivery_address', ''),
            'delivery_date': data.get('delivery_date', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        db['orders'].append(order)
        save_database(db)
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order
        }), 201

@app.route('/api/orders/<order_id>', methods=['GET', 'PUT'])
def handle_order_by_id(order_id):
    """Handle individual order operations"""
    db = load_database()
    
    # Find order
    order = None
    order_index = None
    for i, o in enumerate(db['orders']):
        if o['id'] == order_id:
            order = o
            order_index = i
            break
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if request.method == 'GET':
        return jsonify(order)
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        # Update order status or other fields
        for key in ['status', 'notes', 'delivery_address', 'delivery_date']:
            if key in data:
                order[key] = data[key]
        
        order['updated_at'] = datetime.now().isoformat()
        db['orders'][order_index] = order
        save_database(db)
        
        return jsonify({
            'message': 'Order updated successfully',
            'order': order
        })

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    db = load_database()
    return jsonify(db['products'])

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    """Handle contact form submissions"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'phone', 'subject', 'message']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Save contact message (you could also email this)
    contact_message = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'subject': data['subject'],
        'message': data['message'],
        'created_at': datetime.now().isoformat(),
        'status': 'new'
    }
    
    # Load database and add contact message
    db = load_database()
    if 'contacts' not in db:
        db['contacts'] = []
    
    db['contacts'].append(contact_message)
    save_database(db)
    
    return jsonify({
        'message': 'Contact message sent successfully',
        'contact': contact_message
    }), 201

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get basic statistics"""
    db = load_database()
    
    stats = {
        'total_customers': len(db['customers']),
        'total_orders': len(db['orders']),
        'total_products': len(db['products']),
        'pending_orders': len([o for o in db['orders'] if o.get('status') == 'pending']),
        'completed_orders': len([o for o in db['orders'] if o.get('status') == 'completed'])
    }
    
    return jsonify(stats)

@app.route('/admin')
def admin_dashboard():
    """Simple admin dashboard"""
    db = load_database()
    return render_template('admin.html', 
                         customers=db['customers'], 
                         orders=db['orders'],
                         contacts=db.get('contacts', []))

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists(DATABASE_FILE):
        initial_data = {
            "customers": [],
            "orders": [],
            "products": [
                {
                    "id": 1,
                    "name": "Custom Birthday Cake",
                    "price": 150000,
                    "category": "cake",
                    "description": "Kue ulang tahun custom dengan berbagai rasa dan desain sesuai keinginan Anda",
                    "image": "birthday-cake.jpg"
                },
                {
                    "id": 2,
                    "name": "Premium Cookies",
                    "price": 25000,
                    "category": "cookies",
                    "description": "Koleksi cookies premium dengan berbagai varian rasa",
                    "image": "cookies.jpg"
                },
                {
                    "id": 3,
                    "name": "Artisan Bread",
                    "price": 35000,
                    "category": "bread",
                    "description": "Roti artisan segar dengan berbagai varian",
                    "image": "bread.jpg"
                }
            ],
            "contacts": [],
            "settings": {
                "company_name": "PT Y&V Bites",
                "phone": "+62 812-3456-7890",
                "email": "info@ynvbites.com",
                "address": "Jl. Raya Bogor No. 123, Bogor, Jawa Barat 16111"
            }
        }
        save_database(initial_data)
    
    app.run(debug=True, host='0.0.0.0', port=5000)