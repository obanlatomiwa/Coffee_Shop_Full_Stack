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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH

!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN (DONE)
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure (DONE)
'''


@app.route('/drinks')
def get_drinks_representation():
    drinks = Drink.query.all()
    drinks_short = [drink.short() for drink in drinks]
    return jsonify({'success': True, 'drinks': drinks_short}), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure (DONE)
'''
@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(permission):
    drinks = Drink.query.all()
    drinks_long = [drink.long() for drink in drinks]
    return jsonify({'success': True, 'drinks': drinks_long}), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure (DONE)
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def add_new_drink(permission):
    title = request.json.get('title')
    recipe = request.json.get('recipe')
    if not recipe or not title:
        abort(400)
    recipe_string = str(recipe).replace("\'", "\"")
    new_drink = Drink(title=title, recipe=recipe_string)
    new_drink.insert()
    drink = [new_drink.long()]
    return jsonify({'success': True, 'drinks': drink}), 200



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure (DONE)
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def modify_drink(permission, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink:
        abort(404)
    title = request.json.get('title')
    if title:
        drink.title = title
    recipe = request.json.get('recipe')
    if recipe:
        recipe_string = str(recipe).replace("\'", "\"")
        drink.recipe = recipe_string
    drink.update()
    return jsonify({'success': True, 'drinks': [drink.long()]}), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure (DONE)
'''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(permission, drink_id):
    drink_to_delete = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not drink_to_delete:
        abort(404)
    drink_to_delete.delete()
    return jsonify({'success': True, 'delete': drink_id}), 200



## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404 
                    (DONE)

'''

'''
@TODO implement error handler for 404 
    error handler should conform to general task above  (DONE)
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        'error': 404,
        'message': "resource not found"
    }), 404


# FOR ERROR 400
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False,
                    'error': 400,
                    'message': 'bad request'
                    }), 400

# FOR ERROR 500
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'success': False,
                    'error': 500,
                    'message': 'internal server error'
                    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above  (DONE)
'''
@app.errorhandler(AuthError)
def authorization_failed(error):
    return jsonify({
        "success": False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code
