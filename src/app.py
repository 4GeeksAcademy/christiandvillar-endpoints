import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Person, Favorite  # Asegúrate de importar Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors as JSON
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generate sitemap
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Rutas para Person
@app.route('/person', methods=['POST'])
def create_person():
    data = request.get_json()
    person = Person(
        name=data.get("name"),
        height=data.get("height"),
        mass=data.get("mass"),
        hair_color=data.get("hair_color"),
        skin_color=data.get("skin_color"),
        eye_color=data.get("eye_color"),
        birth_year=data.get("birth_year"),
        gender=data.get("gender"),
        homeworld_id=data.get("homeworld_id")
    )
    db.session.add(person)
    db.session.commit()
    return jsonify(person.serialize()), 201

@app.route('/person/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    data = request.get_json()
    person = Person.query.get(person_id)
    if not person:
        raise APIException("Person not found", 404)

    person.name = data.get("name", person.name)
    person.height = data.get("height", person.height)
    person.mass = data.get("mass", person.mass)
    person.hair_color = data.get("hair_color", person.hair_color)
    person.skin_color = data.get("skin_color", person.skin_color)
    person.eye_color = data.get("eye_color", person.eye_color)
    person.birth_year = data.get("birth_year", person.birth_year)
    person.gender = data.get("gender", person.gender)
    person.homeworld_id = data.get("homeworld_id", person.homeworld_id)
    
    db.session.commit()
    return jsonify(person.serialize()), 200

@app.route('/person/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    person = Person.query.get(person_id)
    if not person:
        raise APIException("Person not found", 404)
    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": "Person deleted successfully"}), 200

# Rutas para Planet
@app.route('/planet', methods=['POST'])
def create_planet():
    data = request.get_json()
    planet = Planet(
        name=data.get("name"),
        diameter=data.get("diameter"),
        rotation_period=data.get("rotation_period"),
        orbital_period=data.get("orbital_period"),
        gravity=data.get("gravity"),
        population=data.get("population")
    )
    db.session.add(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 201

@app.route('/planet/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    data = request.get_json()
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException("Planet not found", 404)

    planet.name = data.get("name", planet.name)
    planet.diameter = data.get("diameter", planet.diameter)
    planet.rotation_period = data.get("rotation_period", planet.rotation_period)
    planet.orbital_period = data.get("orbital_period", planet.orbital_period)
    planet.gravity = data.get("gravity", planet.gravity)
    planet.population = data.get("population", planet.population)
    
    db.session.commit()
    return jsonify(planet.serialize()), 200

@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException("Planet not found", 404)
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planet deleted successfully"}), 200

# Rutas para Favorites
@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.get_json()
    user_id = data.get("user_id")
    person_id = data.get("person_id")
    planet_id = data.get("planet_id")
    starship_id = data.get("starship_id")
    
    if not user_id:
        raise APIException("User ID is required", 400)

    favorite = Favorite(user_id=user_id, person_id=person_id, planet_id=planet_id, starship_id=starship_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    favorite = Favorite.query.get(favorite_id)
    if not favorite:
        raise APIException("Favorite not found", 404)
    
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted successfully"}), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        raise APIException("User not found", 404)
    
    favorites = [favorite.serialize() for favorite in user.favorites]
    return jsonify(favorites), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)