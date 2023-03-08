from flask import Flask, request, make_response, jsonify
from json import dumps
from peewee import *
import sqlite3
import base64
from datetime import datetime
from collections import Counter


app = Flask(__name__)

def find_duplicates(list):
    for i in range(len(list)):
        for j in range(len(list)):
            if list[i] == list[j] and i != j:
                return True
    
    return False
def valid_RegistrationData(content):
    if content['firstName'] == '' or content['firstName'] == None:
        return False
    elif content['lastName'] == '' or content['lastName'] == None:
        return False
    elif content['email'] == '' or content['email'] == None:
        return False
    elif content['password'] == '' or content['password'] == None:
        return False
    else:
        checkEmail = valid_email(content['email'])
        if checkEmail == False:
            return False
        return True
def valid_email(str):
    isOk = 0
    for i in str:
        if i == '@':
            isOk += 1 

    if isOk == 1:
        return True
    else:
        return False
def takeBase64(str):
    b = ""
    isOk = 0
    for i in str:
        if i == ' ':
            isOk = 1
            continue
        if isOk == 1:
            b = b + i
    
    return b
def take_email(str):
    email = ""
    for i in str:
        if i != ":":
            email += i
        else:
            break

    checkEmail = valid_email(email)
    if checkEmail == True:
        return email
    else:
        return ""
def take_password(str):
    pas = ""
    isOk = False
    for i in str:
        if i == ':':
            isOk = True
            continue
        if isOk == True:
            pas += i
    return pas
def check_Authorization(req):
    if 'Authorization' in req:
        a = req['Authorization']
        b = takeBase64(a)
        decode = base64.b64decode(b)
        decode_str = decode.decode('ascii')
        decode_e = take_email(decode_str)
        decode_p = take_password(decode_str)
        with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
            cursor = db.cursor()
            cursor.execute("""SELECT count(email) as count, count(password) as count 
                              FROM Account 
                              WHERE email = ? and password = ?;""", (decode_e, decode_p))
            email_password = cursor.fetchone()
            if email_password[0] == 0 or email_password[1] == 0:
                return False
            else:
                return True
def valid_id(accountId, req):
    a = req['Authorization']
    b = takeBase64(a)
    decode = base64.b64decode(b)
    decode_str = decode.decode('ascii')
    decode_e = take_email(decode_str)
    decode_p = take_password(decode_str)
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT id
                            FROM Account 
                            WHERE email = ? and password = ?;""", (decode_e, decode_p))
        database_id = cursor.fetchone()
        if database_id[0] != accountId:
            return False
        else:
            return True
def valid_longLat(content):
    P_latitude = content['latitude']
    P_longitude = content['longitude']

    if float(P_latitude) == None or float(P_latitude) < -90 or float(P_latitude) > 90:
        return False
    if float(P_longitude) == None or float(P_longitude) < -180 or float(P_longitude) > 180:
        return False
    return True
def valid_IDAnimalType(typeId):
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(id) as count 
                          FROM AnimalType
                          WHERE id = ?;""", (typeId,))
        check_id = cursor.fetchone()
        return check_id
def select_AnimalType(typeId):
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT id, type 
                            FROM AnimalType
                            WHERE id = ?;""", (typeId,))
        content = cursor.fetchone()
        return content
def valid_AnimalType(animalType):
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
            cursor = db.cursor()
            cursor.execute("""SELECT count(type) as count 
                            FROM AnimalType
                            WHERE type = ?;""", (animalType,))
            check_type = cursor.fetchone()
            return check_type
def check_DbEmail(email):
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(email) as count 
                            FROM Account 
                            WHERE email = ?;""", (email,))
        email_count = cursor.fetchone()
        return email_count
def select_AccountId(accountId):
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
            cursor = db.cursor()
            cursor.execute("""SELECT id, firstName, lastName, email 
                              FROM Account 
                              WHERE id = ?;""", (accountId,))
            response = cursor.fetchone()
            return response
def datetime_valid(dt_str):
    try:
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except:
        return False
    return True
def TakeArrayFromStr(str):
    a = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    c = []
    isOk = False
    q = 0
    for i in str:
        for j in a:
            if i == '-':
                return None
            if i == j:
                q = q * 10 + int(i)
                isOk = True
            if (i == ',' or i == ']') and isOk == False:
                return None
            
            if (i == ',' or i == ']') and isOk == True:
                c.append(q)
                isOk = False
                q = 0
                break

    return c
def valid_AnimalData(content):
    weight = content['weight']
    length = content['length']
    height = content['height']
    gender = content['gender']
    chipperId = content['chipperId']
    chippingLocationId = content['chippingLocationId']

    if weight == '' or float(weight) <= 0:
        return False
    if length == '' or float(length) <= 0:
        return False
    if height == '' or float(height) <= 0:
        return False
    if gender != '' and gender!=  'FEMALE' and gender != 'OTHER' and gender != 'MALE':
        return False
    if chipperId == '' or int(chipperId) <= 0:
        return False
    if chippingLocationId == '' or int(chippingLocationId) <= 0:
        return False
    
    return True
def check_idFromDB(chipperId):
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(chipperId) as count
                                FROM Animal
                                WHERE chipperId = ?;""", (chipperId,))
        content = cursor.fetchone()
        if content[0] == 0:
            return False
        else:
            return True
def check_locationFromDB(chippingLocationId):
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(id) as count
                                FROM Location
                                WHERE id = ?;""", (chippingLocationId,))
        content = cursor.fetchone()
        if content[0] == 0:
            return False
        else:
            return True
def select_Animal(chipperId):
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT *
                            FROM Animal
                            WHERE chipperId = ?;""", (chipperId,))
        content = cursor.fetchone()
        return content
def animalIdNotFound(animalId):
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT *
                          FROM Animal
                          WHERE id = ?;""", (animalId,))
        content = cursor.fetchone()
        if content != None:
            return content
        else:
            return False

@app.route('/registration', methods = ['POST'])
def post_registration():
    checkAuthorization = check_Authorization(request.headers)
    if checkAuthorization == False:
        return make_response("403 Request from authorization account", 403)

    content = request.get_json()
    check_content = valid_RegistrationData(content)
    if check_content == False:
        return make_response("400 Error", 400)

    email_count = check_DbEmail(content['email'])
    if email_count[0] == 0 :
        with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
            cursor = db.cursor()
            cursor.execute("""INSERT INTO Account (firstName, lastName, email, password) 
                                VALUES(?, ?, ?, ?);""", (content['firstName'] , content['lastName'], content['email'], content['password']))
            
            cursor.execute("""SELECT id, firstName, lastName, email 
                                FROM Account 
                                WHERE id = (SELECT MAX(id) FROM Account);""")
            records = cursor.fetchone()
            return jsonify(records)
    else:
        return make_response("409 email already exists", 409)

@app.route('/accounts/<int:accountId>', methods = ['GET'])
def get_account(accountId):
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error with login or password", 401)

    if accountId and accountId > 0:
        response = select_AccountId(accountId)
        if response == None:
            return make_response("404 Account with this accountId not found", 404)
        return jsonify(response)
    else:
        return make_response("400 Error", 400)
    
@app.route('/accounts/search', methods = ['GET'])
def get_account_search():
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error with login or password", 401)

    firstName = request.args.get('firstName')
    lastName = request.args.get('lastName')
    email = request.args.get('email')
    _from = request.args.get('from', type=int) or 0
    size = request.args.get('size', type=int) or 10

    if size <= 0:
        return make_response("400 Error", 400)
    if _from < 0:
        return make_response("400 Error", 400)

    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT id, firstName, lastName, email 
                          FROM Account 
                          WHERE firstName = COALESCE(NULLIF(?, ''), firstName) and lastName = COALESCE(NULLIF(?, ''), lastName) and email = COALESCE(NULLIF(?, ''), email)
                          LIMIT ? OFFSET ?;""", (firstName, lastName, email, size, _from))
        account = cursor.fetchall()
        return jsonify(account)
    
@app.route('/accounts/', methods = ['PUT'])
def update_account():
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error", 401)
    
    accountId = request.args.get('accountId', type=int)
    if accountId == None or accountId <= 0:
        return make_response("400 id error", 400)
    else:
        check_id = valid_id(accountId, request.headers)
        if check_id == False:
            return make_response("403 Error", 403)

    content = request.get_json()
    check_content = valid_RegistrationData(content)
    if check_content == False:
        return make_response("400 Error", 400)

    email_count = check_DbEmail(content['email'])
    if email_count[0] == 0 :
        with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
            cursor = db.cursor()
            cursor.execute("""UPDATE Account
                            SET (firstName, lastName, email, password) = (?, ?, ?, ?) 
                            WHERE id = ?;""", (content['firstName'], content['lastName'], content['email'], content['password'], accountId))
            
        records = select_AccountId(accountId)
        return jsonify(records)
    else:
        return make_response("409 Error", 409)

@app.route('/accounts/', methods = ['DELETE'])
def delete_account():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)
    
    accountId = request.args.get('accountId', type=int)
    if accountId == None or accountId <= 0:
        return make_response("400 id error", 400)
    else:
        check_id = valid_id(accountId, request.headers)
        if check_id == False:
            return make_response("403 Error", 403)

    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""DELETE FROM Account
                          WHERE id = ?""", (accountId,))
        return "Request completed successfully"
        
@app.route('/locations/', methods = ['GET'])
def get_location():
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error", 401)

    pointId = request.args.get('pointId', type=int)
    if pointId == None or pointId <= 0:
        return make_response('400 Error', 400)
    
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM Location
                          WHERE id = ?""", (pointId,))
        content = cursor.fetchone()
        if content == None:
            return make_response("404 Error", 404)
        return jsonify(content)
    
@app.route('/locations', methods = ['POST'])
def post_location():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)
    
    content = request.get_json()
    checkContent = valid_longLat(content)
    if checkContent == False:
        return make_response("400 Error", 400)
    
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(latitude) as count, count(longitude) as count 
                          FROM Location
                          WHERE latitude = ? and longitude = ?;""", (content['latitude'], content['longitude']))
        count = cursor.fetchone()
        if count[0] == 0 and count[1] == 0:
            cursor.execute("""INSERT INTO Location(latitude, longitude)
                              VALUES (?, ?);""", (content['latitude'], content['longitude']))
            cursor.execute("""SELECT * FROM Location
                              WHERE latitude = ? and longitude = ?;""", (content['latitude'], content['longitude']))
            resp = cursor.fetchone()
            return jsonify(resp)
        else:
            return make_response("409 Error", 409)

@app.route('/locations/', methods = ['PUT'])
def put_location():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)
    
    pointId = request.args.get('pointId', type=int)
    content = request.get_json()
    checkContent = valid_longLat(content)
    if checkContent == False:
        return make_response("400 Error", 400)
    
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(id) as count 
                          FROM Location
                          WHERE id = ?;""", (pointId,))
        check_id = cursor.fetchone()
        if check_id[0] != 0:
            cursor.execute("""SELECT count(latitude) as count, count(longitude) as count 
                            FROM Location
                            WHERE latitude = ? and longitude = ?;""", (content['latitude'], content['longitude']))
            count = cursor.fetchone()
            if count[0] == 0 and count[1] == 0:
                cursor.execute("""UPDATE Location
                                  SET (latitude, longitude) = (?, ?)
                                  WHERE id = ?;""", (content['latitude'], content['longitude'], pointId))
                cursor.execute("""SELECT * FROM Location
                                WHERE id = ?;""", (pointId,))
                resp = cursor.fetchone()
                return jsonify(resp)
            else:
                return make_response("409 Error", 409)
        else:
            return make_response("404 Error", 404)

@app.route('/locations/', methods = ['DELETE'])
def delete_location():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)
    
    pointId = request.args.get('pointId', type=int)
    if pointId == None or pointId <= 0:
        return make_response("400 id error", 400)
    
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(id) as count 
                          FROM Location
                          WHERE id = ?;""", (pointId,))
        check_id = cursor.fetchone()
        if check_id[0] != 0:
            cursor.execute("""DELETE FROM Location
                            WHERE id = ?""", (pointId,))
            return "Request completed successfully"
        else:
            return make_response("404 Error", 404)

@app.route('/animals/types/', methods = ['GET'])
def get_animalsType():
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error", 401)
    
    typeId = request.args.get('typeId', type=int)
    if typeId == None or typeId <= 0:
        return make_response("400 Error", 400)
    
    check_id = valid_IDAnimalType(typeId)
    if check_id[0] == 0:
        return make_response("404 Error", 404)
    else:
        content = select_AnimalType(typeId)
        return jsonify(content)

@app.route('/animals/types', methods = ['POST'])
def post_animalsType():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)
    
    content = request.get_json()
    if content['type'] and content['type'] != ' ':
        check_type = valid_AnimalType(content['type'])
        if check_type[0] > 0:
            return make_response("409 Error", 409)
    else:
        return make_response("400 Error", 400)
    
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO AnimalType (type)
                        VALUES (?);""", (content['type'],))
        cursor.execute("""SELECT id, type
                          FROM AnimalType
                          WHERE type = ?;""", (content['type'],))
        content = cursor.fetchone()
        return jsonify(content), 201

@app.route('/animals/types/', methods = ['PUT'])
def put_animalsType():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)
    
    typeId = request.args.get('typeId', type=int)
    content = request.get_json()
    if typeId == None or typeId <= 0:
        return make_response("400 Error", 400)
    if content['type'] and content['type'] != ' ':
        check_type = valid_AnimalType(content['type'])
        if check_type[0] > 0:
            return make_response("409 Error", 409)
        check_typeId = valid_IDAnimalType(typeId)
        if check_typeId[0] == 0:
            return make_response("404 Error", 404)
    else:
        return make_response("400 Error", 400)
    
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""UPDATE AnimalType
                          SET (type) = (?)
                          WHERE id = ?;""", (content['type'], typeId))
        content = select_AnimalType(typeId)
        return jsonify(content)

@app.route('/animals/types/', methods = ['DELETE'])
def delete_animalsType():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)
    
    typeId = request.args.get('typeId', type=int)
    if typeId == None or typeId <= 0:
        return make_response("400 Error", 400)
    
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        check_id = valid_IDAnimalType(typeId)
        if check_id[0] != 0:
            cursor.execute("""DELETE FROM AnimalType
                            WHERE id = ?""", (typeId,))
            return "Request completed successfully"
        else:
            return make_response("404 Error", 404)

@app.route('/animals/', methods = ['GET'])
def get_animal():
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error", 401)
    
    animalId = request.args.get('animalId', type=int)
    if animalId == None or animalId <= 0:
        return make_response("400 Error", 400)

    content = animalIdNotFound(animalId)
    if content == False:
        return make_response("404 Error", 404)
    else:
        return jsonify(content)
        
@app.route('/animals/search', methods = ['GET'])
def search_animal():
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error", 401)
    
    startDateTime = request.args.get('startDateTime', type=str)
    endDateTime = request.args.get('endDateTime', type=str)
    chipperId = request.args.get('chipperId', type=int)
    chippingLocationId = request.args.get('chippingLocationId', type=int)
    lifeStatus = request.args.get('lifeStatus', type=str)
    gender = request.args.get('gender', type=str)
    _from = request.args.get('from', type=int) or 0
    size = request.args.get('size', type=int) or 10

    if startDateTime != '':
        check_startDateTime = datetime_valid(startDateTime)
        if check_startDateTime == False:
            return make_response("400 Error", 400)
    if endDateTime != '':
        check_endDateTime = datetime_valid(endDateTime)
        if check_endDateTime == False:
            return make_response("400 Error", 400) 
    
    if size <= 0 or chipperId <= 0 or chippingLocationId <= 0 or _from < 0:
        return make_response("400 Error", 400)
    if lifeStatus != '' and lifeStatus != 'ALIVE' and lifeStatus != 'DEAD':
        return make_response("400 Error", 400)  
    if gender != '' and gender !=  'FEMALE' and gender != 'OTHER' and gender !=  'MALE':
        return make_response("400 Error", 400)

    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT * 
                          FROM Animal 
                          WHERE chippingDateTime >= COALESCE(NULLIF(?, ''), chippingDateTime) and chippingDateTime <= COALESCE(NULLIF(?, ''), chippingDateTime) 
                                and chipperId = COALESCE(NULLIF(?, ''), chipperId) and chippingLocationId = COALESCE(NULLIF(?, ''), chippingLocationId)
                                and lifeStatus = COALESCE(NULLIF(?, ''), lifeStatus) and gender = COALESCE(NULLIF(?, ''), gender)
                          ORDER BY id
                          LIMIT ? OFFSET ?;""", (startDateTime, endDateTime, chipperId, chippingLocationId, lifeStatus, gender, size, _from))
        response = cursor.fetchall()
        return jsonify(response)

@app.route('/animals', methods = ['POST'])
def post_animal():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
     return make_response("401 Error! Not authorized request", 401)
    
    content = request.get_json()
    array = TakeArrayFromStr(content['animalTypes'])
    if array == None:
        return make_response("400 Error", 400)
    duplicates = find_duplicates(array)
    if duplicates == True:
        return make_response("409 Error", 409)
    
    weight = content['weight']
    length = content['length']
    height = content['height']
    gender = content['gender']
    chipperId = content['chipperId']
    chippingLocationId = content['chippingLocationId']
    check_AnimalData = valid_AnimalData(content)
    if check_AnimalData == False:
        return make_response("400 Error", 400)

    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        for i in array:
            cursor.execute("""SELECT count(id) as count
                            FROM AnimalType
                            WHERE id = ?;""", (i,))
            content = cursor.fetchone()
            if content[0] == 0:
                return make_response("404 Error", 404)
        
        check_chipperId = check_idFromDB(chipperId)
        if check_chipperId == False:
            return make_response("404 Error", 404)
        check_chippingLocationId = check_locationFromDB(chippingLocationId)
        if check_chippingLocationId == False:
            return make_response("404 Error", 404)
        
        cursor.execute("""INSERT INTO Animal (animalTypes, weight, length, height, gender, chipperId, chippingLocationId)
                        VALUES (?, ?, ?, ?, ?, ?, ?);""", (str(array), weight
                                                        , length,height, gender
                                                        , chipperId, chippingLocationId))

        content = select_Animal(chipperId)
        return jsonify(content), 201
    
@app.route('/animals', methods = ['PUT'])
def put_animal():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
     return make_response("401 Error! Not authorized request", 401)
    
    animalId = request.args.get('animalId', type=int)
    if animalId == None or animalId <= 0:
        return make_response("400 Error", 400)
    
    content = request.get_json()
    weight = content['weight']
    length = content['length']
    height = content['height']
    gender = content['gender']
    lifeStatus = content["lifeStatus"]
    chipperId = content['chipperId']
    chippingLocationId = content['chippingLocationId']
    check_AnimalData = valid_AnimalData(content)
    if check_AnimalData == False:
        return make_response("400 DD Error", 400)
    if lifeStatus != "ALIVE" and lifeStatus != "DEAD":
        return make_response("400 l Error", 400)
    
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT lifeStatus
                        FROM Animal
                        WHERE id = ?;""", (animalId,))
        content = cursor.fetchone()
        if content[0] == 'DEAD':
            return make_response("400 Error", 400)
        
        cursor.execute("""SELECT visitedLocations
                        FROM Animal
                        WHERE id = ?;""", (animalId,))
        content = cursor.fetchone()
        Array_VisitedLocations = TakeArrayFromStr(content[0])
        if chippingLocationId == Array_VisitedLocations[0]:
            return make_response("400 Error", 400)
        
        check_chipperId = check_idFromDB(chipperId)
        if check_chipperId == False:
            return make_response("404 Error", 404)
        check_chippingLocationId = check_locationFromDB(chippingLocationId)
        if check_chippingLocationId == False:
            return make_response("404 Error", 404)
        
        cursor.execute("""UPDATE Animal
                          SET (weight, length, height, gender, lifeStatus, chipperId, chippingLocationId) = (?, ?, ?, ?, ?, ?, ?)
                          WHERE id = ?;""", (weight, length, height, gender, lifeStatus, chipperId, chippingLocationId, animalId))
        
        content = select_Animal(chipperId)
        return jsonify(content)
        
@app.route('/animals/', methods = ['DELETE'])
def delete_animal():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
     return make_response("401 Error! Not authorized request", 401)
    
    animalId = request.args.get('animalId', type=int)
    if animalId == None or animalId <= 0:
        return make_response("400 Error", 400)
    
    with sqlite3.connect('D:\\work\\junk\\Конкурс Simbir\\wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(id) as count 
                          FROM VisitedLocation
                          WHERE id = ?""", (animalId,))
        content = cursor.fetchall()
        if content[0] == 1:
            return make_response("400 Error", 400)

    content = animalIdNotFound(animalId)
    if content == False:
        return make_response("404 Error", 404)
    else:
        return jsonify(content)  
##############################
@app.route('/animals/{animalId}/types/' ,methods = ['POST'])
def post_ATypes():
    typeId = request.args.get('typeId', type=int)
    animalId = request.args.get('animalId')
    if int(animalId) <= 0 and int(animalId) != '':
        return make_response("400 Error", 400)        
        
    return f"{animalId} asdasd = {typeId}"
    

    



if __name__ == '__main__':
    app.run(debug = True)