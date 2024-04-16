from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in Restaurant.query.all()]
    return make_response(restaurants, 200)

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return make_response(restaurant.to_dict(), 200)
    else:
        return make_response({'error': 'Restaurant not found'}, 404)
    
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)  # Empty response with status code 204
    else:
        return make_response(jsonify({'error': 'Restaurant not found'}), 404)

restaurant_pizzas = []

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_data = [{'id': pizza.id, 'name': pizza.name, 'ingredients': pizza.ingredients} for pizza in pizzas]
    return jsonify(pizzas_data), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizzas():
    data = request.json
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')
    price = data.get('price')

    # Validation logic (ensure required fields are provided)
    if price is None or not 1<=price<=30:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        # Create the restaurant_pizzas entry
        restaurant_pizza = RestaurantPizza(
            pizza_id=pizza_id,
            restaurant_id=restaurant_id,
            price=price
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        # Retrieve related objects
        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        # Construct serialized response
        response_data = {
            "id": restaurant_pizza.id,
            "pizza": pizza.to_dict(),
            "pizza_id": pizza_id,
            "price": price,
            "restaurant": restaurant.to_dict(),
            "restaurant_id": restaurant_id
        }

        return make_response(jsonify(response_data), 201)
    except Exception as e:
        # Rollback the transaction if an error occurs
        db.session.rollback()
        return jsonify({"error": "Failed to create restaurant_pizzas"}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
