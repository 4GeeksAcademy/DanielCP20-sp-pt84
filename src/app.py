"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, FavoriteItem
#from models import Person

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

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    all_users_serialize = [
        {
            "id": user.id,
            "email": user.email,
            "user_name": user.user_name
        }
        for user in all_users
    ]
    # Alternativa a:
    #for user in all_users:
    #    all_users_serialize.append(user.serialize())
    
    return jsonify ({'msg': 'get users ok', 'data': all_users_serialize}), 200

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_favorites_by_user(user_id):
    favorites_user = FavoriteItem.query.filter_by(user_id=user_id).all()
    favorites_user_serialize = []
    for favorite in favorites_user:
        if favorite.planet is not None:
            favorites_user_serialize.append(favorite.planet.serialize())
        if favorite.people is not None:
            favorites_user_serialize.append(favorite.people.serialize())

    return jsonify ({'Favoritos': favorites_user_serialize}), 200



@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    all_people_serialize = []
    for person in all_people:
        all_people_serialize.append(person.serialize())

    return jsonify ({'msg': 'get all people ok', 'data': all_people_serialize}), 200

@app.route('/people', methods=['POST'])
def add_person():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify({'msg': 'Debes enviar imformación del personaje'}), 400
    
    if 'name' not in body:
        return jsonify({'msg': 'El campo NAME del personaje es obligatorio'}), 400
    
    if People.query.filter_by(name=body['name']).first():
        return jsonify({'msg': 'Ese personaje ya esta creado'}), 400
    
    new_person = People(
        name = body['name'],
        gender = body.get('gender'),
        height = body.get('height'),
        mass = body.get('mass'),
        planet_id = body.get('planet_id'),
        url = body.get('url')
    )

    db.session.add(new_person)
    db.session.commit()

    return jsonify({'msg': 'Personaje añadido', 'data': new_person.serialize()})

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    person_to_update = People.query.get(people_id)
    if person_to_update is None:
        return jsonify({'msg': f'El personaje {people_id} no existe'}),404

    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información del personaje'}), 400
    
    if 'name' in body:
        person_to_update.name = body['name']
    if 'gender' in body:
        person_to_update.gender = body['gender']
    if 'height' in body:
        person_to_update.height = body['height']
    if 'mass' in body:
        person_to_update.mass = body['mass']
    if 'planet_id' in body:
        person_to_update.planet_id = body['planet_id']
    if 'url' in body:
        person_to_update.url = body['url']

    db.session.commit()
    return jsonify({'msg': 'Personaje actualizado', 'data': person_to_update.serialize()}), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def remove_person(people_id):
    person_to_remove = People.query.get(people_id)
    if person_to_remove is None:
        return jsonify({'msg': f'El personaje {people_id} no existe'}),404
    
    db.session.delete(person_to_remove)
    db.session.commit()
    return jsonify({'msg': 'Personaje Borrado'}), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify ({'mg': f'El personaje con ID {people_id} no existe'}), 404
    
    return jsonify ({'mg': 'get person ok', 'data': person.serialize()}), 200

@app.route('/favorite/<int:user_id>/people/<int:people_id>', methods=['POST'])
def add_favorite_person(user_id, people_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify ({'mg': f'El usuario con ID {user_id} no existe'}), 404
    
    person = People.query.get(people_id)
    if person is None:
        return jsonify ({'mg': f'El personaje con ID {people_id} no existe'}), 404
    
    if FavoriteItem.query.filter_by(user_id=user_id, people_id=people_id).first():
        return jsonify({'msg': f'Al usuario {user_id} ya le gusta el personaje {people_id}'}), 200
    
    new_favorito = FavoriteItem()
    new_favorito.user_id = user_id
    new_favorito.people_id = people_id

    db.session.add(new_favorito)
    db.session.commit()

    return jsonify({'msg': 'Person favorite add', 'data': new_favorito.serialize()}), 200

@app.route('/favorite/<int:user_id>/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_person(user_id, people_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify ({'mg': f'El usuario con ID {user_id} no existe'}), 404
    
    person = People.query.get(people_id)
    if person is None:
        return jsonify ({'mg': f'El personaje con ID {people_id} no existe'}), 404
    
    favorite_to_remove = FavoriteItem.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite_to_remove:
        db.session.delete(favorite_to_remove)
        db.session.commit()
        return jsonify({'msg': 'Favorito eliminado'}), 200
    else:
        return jsonify({'msg': f'Al usuario {user_id} no le gusta el personaje {people_id}'}), 400



@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planet.query.all()
    all_planets_serialize = []
    for planet in all_planets:
        all_planets_serialize.append(planet.serialize())

    return jsonify ({'msg': 'get all planets ok', 'data': all_planets_serialize}), 200

@app.route('/planet', methods=['POST'])
def add_planet():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify({'msg': 'Debes enviar información del planeta'}), 400
    
    if 'name' not in body:
        return jsonify({'msg': 'El campo NAME del planeta es obligatorio'}), 400
    
    if Planet.query.filter_by(name=body['name']).first():
        return jsonify({'msg': 'Ese planeta ya esta creado'}), 400
    
    new_planet = Planet(
        name = body['name'],
        diameter = body.get('diameter'),
        climate = body.get('climate'),
        population = body.get('population'),
        terrain = body.get('terrain'),
        url = body.get('url')
    )
    
    db.session.add(new_planet)
    db.session.commit()

    return jsonify({'msg': 'Planeta añadido', 'data': new_planet.serialize()}), 200

@app.route('/planet/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet_to_update = Planet.query.get(planet_id)
    if planet_to_update is None:
        return jsonify({'msg': f'El planeta {planet_id} no existe'}),404

    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información del planeta'}), 400
    
    if 'name' in body:
        planet_to_update.name = body['name']
    if 'diameter' in body:
        planet_to_update.diameter = body['diameter']
    if 'climate' in body:
        planet_to_update.climate = body['climate']
    if 'population' in body:
        planet_to_update.population = body['population']
    if 'terrain' in body:
        planet_to_update.terrain = body['terrain']
    if 'url' in body:
        planet_to_update.url = body['url']

    db.session.commit()
    return jsonify({'msg': 'Planeta actualizado', 'data': planet_to_update.serialize()}), 200

@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def remove_planet(planet_id):
    planet_to_remove = Planet.query.get(planet_id)
    if planet_to_remove is None:
        return jsonify({'msg': f'El planeta {planet_id} no existe'}),404
    
    db.session.delete(planet_to_remove)
    db.session.commit()
    return jsonify({'msg': 'Planeta Borrado'}), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify ({'mg': f'El planeta con ID {planet_id} no existe'}), 404

    return jsonify ({'mg': 'get planet ok', 'data': planet.serialize()}), 200

@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify ({'mg': f'El usuario con ID {user_id} no existe'}), 404
    
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify ({'mg': f'El planeta con ID {planet_id} no existe'}), 404
    
    if FavoriteItem.query.filter_by(user_id=user_id, planet_id=planet_id).first():
        return jsonify({'msg': f'Al usuario {user_id} ya le gusta el planeta {planet_id}'}), 400
    
    new_favorito = FavoriteItem()
    new_favorito.user_id = user_id
    new_favorito.planet_id = planet_id

    db.session.add(new_favorito)
    db.session.commit()

    return jsonify({'msg': 'Planet favorite add', 'data': new_favorito.serialize()}), 200

@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify ({'mg': f'El usuario con ID {user_id} no existe'}), 404
    
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify ({'mg': f'El planeta con ID {planet_id} no existe'}), 404
    
    favorite_to_remove = FavoriteItem.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite_to_remove:
        db.session.delete(favorite_to_remove)
        db.session.commit()
        return jsonify({'msg': 'Favorito eliminado'}), 200
    else:
        return jsonify({'msg': f'Al usuario {user_id} no le gusta el planeta {planet_id}'}), 400



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
