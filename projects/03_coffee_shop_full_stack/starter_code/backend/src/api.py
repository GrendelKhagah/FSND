import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

###############################################################################
#####                   Routes                                            #####
###############################################################################
# loging route: https://docmon.us.auth0.com/authorize?audience=CoffeeShare&response_type=token&client_id=VsohXIsBviOmycBwOOtWRrwID4D9yKBE&redirect_uri=http://localhost:8080/login-results
# tocket: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBjSnByXzljSmdudS16aW5PdHh2WSJ9.eyJpc3MiOiJodHRwczovL2RvY21vbi51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTQxMTkxNDE2NzQ0Nzk3MTkyOTMiLCJhdWQiOiJDb2ZmZWVTaGFyZSIsImlhdCI6MTYyNzg2NzkzMiwiZXhwIjoxNjI3ODc1MTMyLCJhenAiOiJWc29oWElzQnZpT215Y0J3T090V1Jyd0lENEQ5eUtCRSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOltdfQ.L-6RwV3WUYgYIwLLJk4YttP_KtZtWXW1TowIDQWfNLI91tbHSLjSuPI2EJALFBLiZG8ilHX8qwNlvMDQMXj6PVp-5IuX-hhN5zKek2e6BKRyhbZQJC_JSODNw69CH6jjarL_8WgSBER7QL5M_Q6R63eRIdpDtLJajzoQaKj6L1Tw7xaKwsrfX4HAUDo9lglbQ6e1pgHBWiC-9LVHAMYWSRGKRW9Wp017hJsNVZnz0CJ8H5kTnfdIkblNqe96zslaZ9DGMDhm6qBgcBKp5KBf7CuWFI7DLtDvTx1ekUmK2zklJ9h-UafqvYrDHmToxvCGbwEvJwztYbPdFcnEbL58Vw

#token 2 : eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBjSnByXzljSmdudS16aW5PdHh2WSJ9.eyJpc3MiOiJodHRwczovL2RvY21vbi51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTQ0MTA4MTUzMjM5Nzc1MjgzNDQiLCJhdWQiOiJDb2ZmZWVTaGFyZSIsImlhdCI6MTYyNzg2OTEzNiwiZXhwIjoxNjI3ODc2MzM2LCJhenAiOiJWc29oWElzQnZpT215Y0J3T090V1Jyd0lENEQ5eUtCRSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOltdfQ.UPqOZCfgT_eY2IZL3CoKtAdip5qYo9IgKWJPglqiML2gTi-kWZAFznpyVli-M9HW42p2h65ZffB9CIwhg3tresnOrq6-AWcHH-opYCxEsQP2ciyalJyIv49e2Xf0GY4k83CiC5NZG8ki-eqNTSifY6zv3BZddD2gDIxXjHqTq1AVcE1uDMGn3HAUSa23YS78YpkV3LB45A2c1sfOIToaeu9s5bAWL78wiliJkF1cMRu1ZP6SysId6eRSJL-2Q2X433QDwuEyx9K57x6DfksXAx2VAPTHrsXYcnLRmXouTewWxfQPvJ6yBJGfS8MhH-Xv_JBsQfln-XlCVrdjAsl-kg
@app.route('/')
@app.route('/drinks')
def index():
    drinks = Drink.query.order_by(Drink.id.desc())  #new Drinks Show in front
    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in drinks]
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    drinks = Drink.query.order_by(Drink.id.desc())
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    request = request.get_json()
    try:
        request_recipe = request['recipe']
        if isinstance(request_recipe, dict):
            request_recipe = [request_recipe]
        drink = Drink()
        drink.title = request['title']
        drink.recipe = json.dumps(request_recipe)
        drink.insert()

    except BaseException:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
        }), 201



@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    request = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink: # can use not drink because .one_or_none()
        abort(404)

    try:
        request_title = request.get('title')
        request_recipe = request.get('recipe')

        if request_title:
            drink.title = req_title

        if request_recipe:
            drink.recipe = json.dumps(request['recipe'])

        drink.update()
    except BaseException:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()
    ]}), 200


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    try:
        drink.delete()
    except BaseException:
        abort(400)

    return jsonify({
        'success': True,
        'delete': id
    }), 200


###############################################################################
#####                    Error handlers                                   #####
###############################################################################


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not Found"
    }), 404


@app.errorhandler(403)
def AuthError(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Authentication Error"
    }), 403

@app.errorhandler(400)
def badRequest(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400
