from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from flask import Flask, jsonify
app = Flask(__name__)




db = SQLAlchemy()

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    restaurant_pizzas = relationship("RestaurantPizza", back_populates="restaurant", cascade='all, delete')

    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        return f'<Restaurant {self.id}>'

class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)  

    restaurant_pizzas = relationship("RestaurantPizza", back_populates="pizza", cascade='all, delete')

    serialize_rules = ('-restaurant_pizzas.pizza',)

    def __repr__(self):
        return f'<Pizza {self.id}>'

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    ingredients = db.column(db.String)

    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id', ondelete='CASCADE'))

    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")

    serialize_rules = ('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas', 'pizza.id', 'pizza.name', 'pizza.ingredients', 'restaurant.id', 'restaurant.name', 'restaurant.address', 'price')

    # __table_args__ = (
    #     CheckConstraint('price >= 1 AND price <= 30', name='check_price_range'),
    # )

    @validates('price')
    def validate_price(self, key, price):
        if not 1 <= price <= 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f'<RestaurantPizza {self.id}>'
    
    