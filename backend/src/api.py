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
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

#MAKE CREATION FIRST! TOKEN MIGHT EXPIRE!

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        'success':'true',
        'drinks': formatted_drinks
    
    
    })



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(self):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]
   
    return jsonify({
        'success':'true',
        'drinks': formatted_drinks
    
    
    })

# start creating
'''
@TODO implement endpoint 
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(self):
    
    try:
        data = request.get_json()
        drink = Drink(recipe = json.dumps(data['recipe']), title = data['title'])
    #print(drink)
        Drink.insert(drink)
    except:
        abort(500)
    return jsonify({
        'success':True,
        'drinks': [drink.long()]
    })
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH']) #key error title/recipe from request
@requires_auth('patch:drinks')
def update_drink(self, id):
    data = request.get_json()
    drink = Drink.query.filter(Drink.id == id).first()
    try:
        title = data['title']
    except:
        abort(400)
    if drink is None:
        abort(404)
    try:
        drink.title = title
        Drink.update(drink)
    except:
        abort(500)
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })




'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(self, id):
    drink = Drink.query.filter(Drink.id == id).first()
    if drink is None:
        abort(404)    
    try:
        Drink.delete(drink)
    except:
        abort(500)

    return jsonify({
        'success': True,
        'delete': id
    })


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

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
      "success": False,
      "error": 401,
      "message": "Unauthorized"
    }), 401
@app.errorhandler(400)
def unauthorized(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "Bad request."
    }), 400
@app.errorhandler(500)
def server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "Unexpected error."
    }), 500