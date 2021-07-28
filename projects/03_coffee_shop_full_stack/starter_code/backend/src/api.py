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
