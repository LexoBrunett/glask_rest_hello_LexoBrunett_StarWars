import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Vehicle, Favorite 
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

#AUTENTICACION
current_logged_user_id = 1

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():

    users = User.query.all()

    user_list = [
        {
            'id': user.id,
            'email': user.email
        }
        for user in users
    ]

    return jsonify(user_list), 200

@app.route('/planet', methods=['GET'])
def get_planets():
    allPlanets = Planet.query.all()
    result = [element.serialize() for element in allPlanets]
    return jsonify(result), 200

@app.route('/planet', methods=['POST'])
def post_planet():

    # obtener los datos de la petición que están en formato JSON a un tipo de datos entendibles por pyton (a un diccionario). En principio, en esta petición, deberían enviarnos 3 campos: el nombre, la descripción del planeta y la población
    data = request.get_json()

    # creamos un nuevo objeto de tipo Planet
    planet = Planet(name=data['name'], description=data['description'], population=data['population'])

    # añadimos el planeta a la base de datos
    db.session.add(planet)
    db.session.commit()

    response_body = {"msg": "Planet inserted successfully"}
    return jsonify(response_body), 200

#CHARACTER

@app.route('/character', methods=['GET'])
def get_characters():
    allCharacters = Character.query.all()
    result = [element.serialize() for element in allCharacters]
    return jsonify(result), 200

@app.route('/character', methods=['POST'])
def post_character():

    data = request.get_json()

    character = Character(name=data['name'], description=data['description'], eye_color=data['eye_color'])

    db.session.add(character)
    db.session.commit()

    response_body = {"msg": "Character added succesfully!"}
    return jsonify(response_body), 200


#VEHICLES

@app.route('/vehicle', methods=['GET'])
def get_vehicles():
    allVehicles = Vehicle.query.all()
    result = [element.serialize() for element in allVehicles]
    return jsonify(result), 200

@app.route('/character', methods=['POST'])
def post_vehicle():

    data = request.get_json()

    vehicle = Vehicle(name=data['name'], description=data['description'], model=data['model'])

    db.session.add(vehicle)
    db.session.commit()

    response_body = {"msg": "Vehicle added succesfully!"}
    return jsonify(response_body), 200

#FAVORITE PLANET
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
 
    user = User.query.get(current_logged_user_id)

    new_favorite = Favorite(user_id=current_logged_user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    response_body = {
        "msg": "Planeta agregado correctamente", 
        "favorite": new_favorite.serialize()
    }

    return jsonify(response_body), 200

#FAVORITE CHARACTER
@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
 
    user = User.query.get(current_logged_user_id)

    new_favorite = Favorite(user_id=current_logged_user_id, character_id = character_id)
    db.session.add(new_favorite)
    db.session.commit()

    response_body = {
        "msg": "Personaje agregado correctamente", 
        "favorite": new_favorite.serialize()
    }

    return jsonify(response_body), 200


#DELETE FAV PLANET
@app.route('/favorite/planet/<int:favorite_id>', methods=['DELETE'])
def delete_favorite_planet(favorite_id):
 
    favorite = Favorite.query(favorite_id)

    if favorite is None:
        return jsonify({'msg' : 'No favorite found'}), 404
    
    db.session.delete(favorite)
    db.session.commit()

    response_body = {
        "msg" : "Planeta favorito eliminado correctamente"
    }
    return jsonify(response_body), 200

#DELETE FAV CHARACTER
@app.route('/favorite/character/<int:favorite_id>', methods=['DELETE'])
def delete_favorite_character(favorite_id):
    
    favorite = Favorite.query.get(favorite_id)

    if favorite is None:
        return jsonify({'msg' : 'No favorite found'}), 404
    
    db.session.delete(favorite)
    db.session.commit()

    response_body = {
        "msg" : "Personaje favorito eliminado correctamente"
    }
    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
