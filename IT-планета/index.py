from flask import Flask, request, make_response, jsonify
from peewee import *
import sqlite3
import json
from Functions import *

app = Flask(__name__)


@app.route('/registration', methods = ['POST'])
def post_registration():
    checkAuthorization = check_Authorization(request.headers)
    if checkAuthorization == True:
        return make_response("403 Request from authorization account", 403)

    content = request.get_json()
    check_content = valid_RegistrationData(content)
    if check_content == False:
        return make_response("400 Error", 400)

    email_count = check_DbEmail(content['email'])
    if email_count[0] == 0 :
        with sqlite3.connect('wonderland.db') as db:
            cursor = db.cursor()
            cursor.execute("""INSERT INTO Account (firstName, lastName, email, password) 
                                VALUES(?, ?, ?, ?);""", (content['firstName'] , content['lastName'], content['email'], content['password']))
            
            cursor.execute("""SELECT id, firstName, lastName, email 
                                FROM Account 
                                WHERE id = (SELECT MAX(id) FROM Account);""")
            response = cursor.fetchone()
            answer = ResponseForAccount(response)
            return answer, 201
    else:
        return make_response("409 email already exists", 409)

@app.route('/accounts/<accountId>', methods = ['GET'])
def get_account(accountId):
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error with login or password", 401)
    
    if int(accountId) and int(accountId) > 0:
        response = select_AccountId(int(accountId))
        if response == None:
            return make_response("404 Account with this accountId not found", 404)
        answer = ResponseForAccount(response)
        return answer
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
    _from = request.args.get('from', type=int)
    size = request.args.get('size', type=int)

    if firstName != None:
        firstName = '%' + firstName + '%'
    if lastName != None:
        lastName = '%' + lastName + '%'
    if email != None:
        email = '%' + email + '%'
    if size == None:
        size = 10
    if _from == None:
        _from = 0
 
    if size <= 0:
        return make_response("400 Error", 400)
    if _from < 0:
        return make_response("400 Error", 400)

    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT id, firstName, lastName, email 
                          FROM Account 
                          WHERE (firstName LIKE ? or ? IS NULL) 
                            and (lastName LIKE ? or ? IS NULL)
                            and (email LIKE ? or ? IS NULL)
                          LIMIT ? OFFSET ?;""", (firstName, firstName, lastName, lastName, email, email, size, _from))
        response = cursor.fetchall()
        
    answer = []
    for i in response:
        ans = ResponseForAccount(i)
        answer.append(ans)

    return answer
    
@app.route('/accounts/<accountId>', methods = ['PUT'])
def put_account(accountId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if accountId == ' ' or int(accountId) <= 0:
        return make_response("400 id error", 400)

    content = request.get_json()
    check_content = valid_RegistrationData(content)
    if check_content == False:
        return make_response("400 Error", 400)
    check_id = valid_id(int(accountId), request.headers)
    if check_id == False:
        return make_response("403 Error", 403)

    email_count = check_DbEmail(content['email'])
    if email_count[0] > 1:
        return make_response("409 Error", 409)

    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""UPDATE Account
                        SET (firstName, lastName, email, password) = (?, ?, ?, ?) 
                        WHERE id = ?;""", (content['firstName'], content['lastName'], content['email'], content['password'], int(accountId)))
        
    response = select_AccountId(int(accountId))
    answer = ResponseForAccount(response)
    return answer

@app.route('/accounts/<accountId>', methods = ['DELETE'])
def delete_account(accountId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if accountId == None or int(accountId) <= 0:
        return make_response("400 id error", 400)
    else:
        check_id = valid_id(int(accountId), request.headers)
        if check_id == False:
            return make_response("403 Error", 403)

    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(chipperId) as count 
                          FROM Animal
                          WHERE chipperId = ?""", (int(accountId),))
        response = cursor.fetchone()
        if response[0] != 0:
            return make_response("400 Error", 400)

        cursor.execute("""DELETE FROM Account
                          WHERE id = ?""", (int(accountId),))
        return "Request completed successfully"
        
@app.route('/locations/<pointId>', methods = ['GET'])
def get_location(pointId):
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error", 401)

    if int(pointId) == None or int(pointId) <= 0:
        return make_response('400 Error', 400)
    
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM Location
                          WHERE id = ?""", (int(pointId),))
        response = cursor.fetchone()
        if response == None:
            return make_response("404 Error", 404)
        answer = ResponseForLocation(response)
        return answer
    
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
    
    with sqlite3.connect('wonderland.db') as db:
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
            response = cursor.fetchone()
            answer = ResponseForLocation(response)
            return answer, 201
        else:
            return make_response("409 Error", 409)

@app.route('/locations/<pointId>', methods = ['PUT'])
def put_location(pointId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if pointId == ' ' or int(pointId) <= 0:
        return make_response("400 Error", 400)

    content = request.get_json()
    checkContent = valid_longLat(content)
    if checkContent == False:
        return make_response("400 Error", 400)
    
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(id) as count 
                          FROM Location
                          WHERE id = ?;""", (int(pointId),))
        check_id = cursor.fetchone()
        if check_id[0] != 0:
            cursor.execute("""SELECT count(latitude) as count, count(longitude) as count 
                            FROM Location
                            WHERE latitude = ? and longitude = ?;""", (content['latitude'], content['longitude']))
            count = cursor.fetchone()
            if count[0] == 0 and count[1] == 0:
                cursor.execute("""UPDATE Location
                                  SET (latitude, longitude) = (?, ?)
                                  WHERE id = ?;""", (content['latitude'], content['longitude'], int(pointId)))
                cursor.execute("""SELECT * FROM Location
                                WHERE id = ?;""", (int(pointId),))
                response = cursor.fetchone()
                answer = ResponseForLocation(response)
                return answer
            else:
                return make_response("409 Error", 409)
        else:
            return make_response("404 Error", 404)

@app.route('/locations/<pointId>', methods = ['DELETE'])
def delete_location(pointId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if pointId == None or int(pointId) <= 0:
        return make_response("400 id error", 400)
    
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(id) as count 
                          FROM Location
                          WHERE id = ?;""", (int(pointId),))
        check_id = cursor.fetchone()
        if check_id[0] == 0:
            return make_response("404 Error", 404)
        
        cursor.execute("""SELECT count(chippingLocationId) as count 
                          FROM Animal
                          WHERE chippingLocationId = ?;""", (int(pointId),))
        response = cursor.fetchone()
        if response[0] != 0:
            return make_response("400 Error", 400)
        
        cursor.execute("""SELECT visitedLocations 
                          FROM Animal;""")
        response = cursor.fetchall()
        for i in response:
            for j in i:
                if j != "[]" and j != None:
                    array = TakeArrayFromStr(j)
                    checkArray = findIdinArray(array, int(pointId))
                    if checkArray == True:
                        return ("400 Error", 400)

        cursor.execute("""DELETE FROM Location
                        WHERE id = ?""", (int(pointId),))
        return "Request completed successfully"
        
@app.route('/animals/types/<typeId>', methods = ['GET'])
def get_animalsType(typeId):
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error", 401)

    if int(typeId) == None or int(typeId) <= 0:
        return make_response("400 Error", 400)
    
    check_id = valid_IDAnimalType(int(typeId))
    if check_id[0] == 0:
        return make_response("404 Error", 404)
    else:
        response = select_AnimalType(int(typeId))
        answer = ResponseForAnimalTypes(response)
        return answer

@app.route('/animals/types', methods = ['POST'])
def post_animalsType():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)
    
    content = request.get_json()
    if  content['type'] == None or content['type'] == '':
        return make_response("400 Error", 400)
    check = validPassword(content['type'])
    if check == False:
        return make_response("400 Error", 400)

    check_type = valid_AnimalType(content['type'])
    if check_type[0] > 0:
        return make_response("409 Error", 409)

    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO AnimalType (type)
                        VALUES (?);""", (content['type'],))
        cursor.execute("""SELECT id, type
                          FROM AnimalType
                          WHERE type = ?;""", (content['type'],))
        response = cursor.fetchone()
        answer = ResponseForAnimalTypes(response)
        return answer, 201

@app.route('/animals/types/<typeId>', methods = ['PUT'])
def put_animalsType(typeId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    content = request.get_json()
    if typeId == ' ' or int(typeId) <= 0:
        return make_response("400 Error", 400)
    
    content = request.get_json()
    if  content['type'] == None or content['type'] == '':
        return make_response("400 Error", 400)
    check = validPassword(str(content['type']))
    if check == False:
        return make_response("400 Error", 400)

    check_type = valid_AnimalType(str(content['type']))
    if check_type[0] > 0:
        return make_response("409 Error", 409)
    check_typeId = valid_IDAnimalType(int(typeId))
    if check_typeId[0] == 0:
        return make_response("404 Error", 404)

    
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""UPDATE AnimalType
                          SET (type) = (?)
                          WHERE id = ?;""", (str(content['type']), int(typeId)))
        cursor.execute("""SELECT *
                          FROM AnimalType
                          WHERE id = ?;""", (int(typeId),))
        response = cursor.fetchone()
        answer = ResponseForAnimalTypes(response)
        return answer

@app.route('/animals/types/<typeId>', methods = ['DELETE'])
def delete_animalsType(typeId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if typeId == None or int(typeId) <= 0:
        return make_response("400 Error", 400)
    
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        check_id = valid_IDAnimalType(int(typeId))
        if check_id[0] == 0:
            return make_response("404 Error", 404)
        
        cursor.execute("""SELECT animalTypes 
                          FROM Animal;""")
        response = cursor.fetchall()
        for i in response:
            for j in i:
                if j != "[]" and j != None:
                    array = TakeArrayFromStr(j)
                    checkArray = findIdinArray(array, int(typeId))
                    if checkArray == True:
                        return ("400 Error", 400)

        cursor.execute("""DELETE FROM AnimalType
                        WHERE id = ?""", (int(typeId),))
        return "Request completed successfully"

@app.route('/animals/<animalId>', methods = ['GET'])
def get_animal(animalId):
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error", 401)

    if int(animalId) == None or int(animalId) <= 0:
        return make_response("400 Error", 400)

    response = animalIdNotFound(int(animalId))
    if response == False:
        return make_response("404 Error", 404)
    else:
        answer = ResponseForAnimals(response) 
        return answer
        
@app.route('/animals/search', methods = ['GET'])
def search_animal():
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error", 401)
    
    startDateTime = request.args.get('startDateTime')
    endDateTime = request.args.get('endDateTime')
    chipperId = request.args.get('chipperId', type=int)
    chippingLocationId = request.args.get('chippingLocationId', type=int)
    lifeStatus = request.args.get('lifeStatus')
    gender = request.args.get('gender')
    _from = request.args.get('from', type=int)
    size = request.args.get('size', type=int)

    if size == None:
        size = 10
    if _from == None:
        _from = 0
    if size <= 0 or _from < 0:
        return make_response("400 Error", 400)

    if startDateTime != None:
        check_startDateTime = datetime_valid(startDateTime)
        if check_startDateTime == False:
            return make_response("400 sss Error", 400)
    if endDateTime != None:
        check_endDateTime = datetime_valid(endDateTime)
        if check_endDateTime == False:
            return make_response("400 Error", 400) 
    
    if chipperId != None and chipperId <= 0:
        return make_response("400 Error", 400)
    if chippingLocationId != None and chippingLocationId <= 0:
        return make_response("400 Error", 400)

    if lifeStatus != None and lifeStatus != 'ALIVE' and lifeStatus != 'DEAD':
        return make_response("400 Error", 400)  
    if gender != None and gender !=  'FEMALE' and gender != 'OTHER' and gender !=  'MALE':
        return make_response("400 Error", 400)

    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT * 
                          FROM Animal 
                          WHERE chippingDateTime >= COALESCE(NULLIF(?, ''), chippingDateTime) and chippingDateTime <= COALESCE(NULLIF(?, ''), chippingDateTime) 
                                and (chipperId LIKE ? or ? IS NULL) and (chippingLocationId LIKE ? or ? IS NULL)
                                and (lifeStatus LIKE ? or ? IS NULL) and (gender LIKE ? or ? IS NULL)
                          ORDER BY id
                          LIMIT ? OFFSET ?;""", (startDateTime, endDateTime, chipperId, chipperId, chippingLocationId, chippingLocationId, lifeStatus, lifeStatus, gender, gender,size, _from))
        response = cursor.fetchall()
        answer = []
        for i in response:
            qwe = ResponseForAnimals(i)
            answer.append(qwe)

        return answer

@app.route('/animals', methods = ['POST'])
def post_animal():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
     return make_response("401 Error! Not authorized request", 401)
    
    content = request.get_json()
    if len(content['animalTypes']) == 0:
        return make_response("400 Error", 400)

    jarray = json.dumps(content['animalTypes'])
    if content['animalTypes'] == None:
        return make_response("400 Error", 400)
    duplicates = find_duplicates(content['animalTypes'])
    if duplicates == 1:
        return make_response("409 Error", 409)
    if duplicates == 2:
        return make_response("400 Error", 400)
    
    weight = content['weight']
    length = content['length']
    height = content['height']
    gender = content['gender']
    chipperId = content['chipperId']
    chippingLocationId = content['chippingLocationId']
    check_AnimalData = valid_AnimalData(content)
    if check_AnimalData == False:
        return make_response("400 Error", 400)

    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        for i in content['animalTypes']:
            cursor.execute("""SELECT count(id) as count
                            FROM AnimalType
                            WHERE id = ?;""", (i,))
            content = cursor.fetchone()
            if content[0] == 0:
                return make_response("404 AnimalType Error", 404)
        
        check_chipperId = check_idFromDB(chipperId)
        if check_chipperId == False:
            return make_response("404 chipperId Error", 404)
        check_chippingLocationId = check_locationFromDB(chippingLocationId)
        if check_chippingLocationId == False:
            return make_response("404 chippingLocationId Error", 404)
        
        cursor.execute("""INSERT INTO Animal (animalTypes, weight, length, height, gender, chipperId, chippingLocationId)
                        VALUES (?, ?, ?, ?, ?, ?, ?);""", (jarray, weight
                                                        , length,height, gender
                                                        , chipperId, chippingLocationId))

        cursor.execute("""SELECT *
                            FROM Animal
                            WHERE animalTypes = ? and weight = ? and length = ?
                                  and height = ? and gender = ? and chipperId = ? and chippingLocationId = ?;""", (jarray, weight, length, height, gender, chipperId, chippingLocationId))
        response = cursor.fetchone()
        answer = ResponseForAnimals(response)
        return answer, 201
    
@app.route('/animals/<animalId>', methods = ['PUT'])
def put_animal(animalId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
     return make_response("401 Error! Not authorized request", 401)
    
    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)
    

    check_animalId = animalIdNotFound(int(animalId))
    if check_animalId == False:
        return make_response("404 Error", 404)

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
    
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT lifeStatus
                        FROM Animal
                        WHERE id = ?;""", (int(animalId),))
        response = cursor.fetchone()
        if response[0] == 'DEAD':
            return make_response("400 Error", 400)
        
        cursor.execute("""SELECT visitedLocations
                        FROM Animal
                        WHERE id = ?;""", (int(animalId),))
        response = cursor.fetchone()
        if response[0] != "[]" and response[0] != None:
            Array_VisitedLocations = TakeArrayFromStr(response[0])
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
                          WHERE id = ?;""", (weight, length, height, gender, lifeStatus, chipperId, chippingLocationId, int(animalId)))
        
        cursor.execute("""SELECT *
                          FROM Animal
                          WHERE id = ?;""", (int(animalId),))
        response = cursor.fetchone()
        answer = ResponseForAnimals(response)
        return answer
        
@app.route('/animals/<animalId>', methods = ['DELETE'])
def delete_animal(animalId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
     return make_response("401 Error! Not authorized request", 401)

    if animalId == None or int(animalId) <= 0:
        return make_response("400 Error", 400)
    
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        response = animalIdNotFound(int(animalId))
        if response == False:
            return make_response("404 Error", 404)
        cursor.execute("""SELECT visitedLocations
                          FROM Animal
                          WHERE id = ?""", (int(animalId),))
        response = cursor.fetchone()
        if response[0] != None:
            return make_response("400 sss Error", 400)

        cursor.execute("""DELETE FROM Animal
                        WHERE id = ?;""", (int(animalId),))
        return "Request completed successfully"

@app.route('/animals/<animalId>/types/<typeId>' ,methods = ['POST'])
def post_ATypes(animalId, typeId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
     return make_response("401 Error! Not authorized request", 401)
    
    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)
    if typeId == ' ' or int(typeId) <= 0:
        return make_response("400 Error", 400)
    
    response = animalIdNotFound(int(animalId))
    if response == False:
        return make_response("404 Error", 404)
    check_id = valid_IDAnimalType(int(typeId))
    if check_id[0] == 0:
        return make_response("404 Error", 404)

    AnimalTypeArray = TakeArrayFromStr(response[1])
    for i in AnimalTypeArray:
        if i == int(typeId):
            return make_response("409 Error", 409)
        
    AnimalTypeArray.append(int(typeId))
    answer = ResponseForAnimals(response)
    answer['animalTypes'] = AnimalTypeArray
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""UPDATE Animal
                          SET (animalTypes) = (?)
                          WHERE id = (?);""", (str(AnimalTypeArray), int(animalId)))
    return answer, 201
    
@app.route('/animals/<animalId>/types' ,methods = ['PUT'])
def put_Atypes(animalId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
     return make_response("401 Error! Not authorized request", 401)
    
    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)
    content = request.get_json()
    oldTypeId = content['oldTypeId']
    newTypeId = content['newTypeId']

    if oldTypeId == None or newTypeId == None:
        return make_response("400 Error", 400)

    if oldTypeId == ' ' or int(oldTypeId) <= 0:
        return make_response("400 Error", 400)
    if newTypeId == ' ' or int(newTypeId) <= 0:
        return make_response("400 Error", 400)
    
    response = animalIdNotFound(int(animalId))
    if response == False:
        return make_response("404 Error", 404)
    check_id = valid_IDAnimalType(int(oldTypeId))
    if check_id[0] == 0:
        return make_response("404 Error", 404)
    check_id = valid_IDAnimalType(int(newTypeId))
    if check_id[0] == 0:
        return make_response("404 Error", 404)

    isOk_oldTypeId = False
    isOk_newTypeId = False
    AnimalTypeArray = TakeArrayFromStr(response[1])

    for i in AnimalTypeArray:
        if i == int(oldTypeId):
            isOk_oldTypeId = True
        if i == int(newTypeId):
            isOk_newTypeId = True
    
    if isOk_oldTypeId == False:
        return make_response("404 s Error", 404)
    if isOk_newTypeId == True:
        return make_response("409 Error", 409)
    
    for i in range(0, len(AnimalTypeArray)):
        if AnimalTypeArray[i] == int(oldTypeId):
            AnimalTypeArray[i] = int(newTypeId)
            break
    
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""UPDATE Animal
                          SET (animalTypes) = (?)
                          WHERE id = (?);""", (str(AnimalTypeArray), int(animalId)))

    answer = ResponseForAnimals(response)
    answer['animalTypes'] = AnimalTypeArray
    return answer
    
@app.route('/animals/<animalId>/types/<typeId>' ,methods = ['DELETE'])
def delete_Atypes(animalId, typeId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
     return make_response("401 Error! Not authorized request", 401)
    
    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)
    if typeId == ' ' or int(typeId) <= 0:
        return make_response("400 Error", 400)
    
    response = animalIdNotFound(int(animalId))
    if response == False:
        return make_response("404 Error", 404)
    check_id = valid_IDAnimalType(int(typeId))
    if check_id[0] == 0:
        return make_response("404 Error", 404)
    
    array = TakeArrayFromStr(response[1])
    isOk = False
    for i in range(0, len(array)):
        if array[i] == int(typeId):
            isOk = True
 
    if isOk == False:
        return make_response("404 QWER Error", 404)
    
    if isOk == True and len(array) == 1:
        return make_response("400 Error", 400)
    
    array.remove(int(typeId))

    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""UPDATE Animal
                          SET (animalTypes) = (?)
                          WHERE id = (?);""", (str(array), int(animalId)))
        
        answer = ResponseForAnimals(response)
        answer['animalTypes'] = array
        return answer

@app.route('/animals/<animalId>/locations' ,methods = ['GET'])
def get_Alocations(animalId):
    check = check_Authorization(request.headers)
    if check == False:
        return make_response("401 Error with login or password", 401)
    
    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)
    
    startDateTime = request.args.get('startDateTime')
    endDateTime = request.args.get('endDateTime')
    _from = request.args.get('form', type=int)
    size = request.args.get('size', type=int)

    if size == None:
        size = 10
    if _from == None:
        _from = 0
    if size <= 0 or _from < 0:
        return make_response("400 Error", 400)

    if startDateTime != None:
        check_startDateTime = datetime_valid(startDateTime)
        if check_startDateTime == False:
            return make_response("400 sss Error", 400)
    if endDateTime != None:
        check_endDateTime = datetime_valid(endDateTime)
        if check_endDateTime == False:
            return make_response("400 Error", 400) 
    
    response = animalIdNotFound(int(animalId))
    if response == False:
        return make_response("404 Error", 404)
    
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT * 
                          FROM VisitedLocation 
                          WHERE id = ? and dateTimeOfVisitLocationPoint >= COALESCE(NULLIF(?, ''), dateTimeOfVisitLocationPoint) and dateTimeOfVisitLocationPoint <= COALESCE(NULLIF(?, ''), dateTimeOfVisitLocationPoint)
                          LIMIT ? OFFSET ?;""", (int(animalId), startDateTime, endDateTime, size, _from))
        response = cursor.fetchall()
        answer = []
        for i in response:
            qwe = ResponseForVisitedLocation(i)
            answer.append(qwe)

        return answer
        
@app.route('/animals/<animalId>/locations/<pointId>' ,methods = ['POST'])
def post_Alocations(animalId, pointId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)
    
    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 valid Error", 400)
    if pointId == ' ' or int(pointId) <= 0:
        return make_response("400 valid Error", 400)

    response = animalIdNotFound(int(animalId))
    if response == False:
        return make_response("404 Error", 404)

    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM Location
                          WHERE id = ?;""", (int(pointId),))
        response = cursor.fetchone()
        if response == None:
            return make_response("404 Error", 404)
        
        cursor.execute("""SELECT lifeStatus
                          FROM Animal 
                          WHERE id = ?;""", (int(animalId),))
        response = cursor.fetchone()
        if response[0] == 'DEAD':
            return make_response("400 DEAD Error", 400)

        response = TakeChippingLocationId(int(animalId))
        if response[0] == int(pointId):
            return make_response("400 chippinglocation Error", 400)

        response = TakeLocationPointId(int(animalId))
        for i in reversed(response):
            for j in i:
                if j == int(pointId):
                    return make_response("400 locationpointid Error", 400)
                else:
                    break
            break
        
        cursor.execute("""INSERT INTO VisitedLocation (id, locationPointId)
                          VALUES (?, ?) ;""", (int(animalId), int(pointId)))
        
        cursor.execute("""SELECT visitedLocations
                          FROM Animal
                          WHERE id = ?;""", (int(animalId),))
        response = cursor.fetchone()
        if response[0] == None:
            ArrayForAnimalVL = [int(pointId)]
            jarray = json.dumps(ArrayForAnimalVL)
            cursor.execute("""UPDATE Animal
                              SET (visitedLocations) = (?)
                              WHERE id = (?) ;""", (jarray, int(animalId)))
        else:
            ArrayForAnimalVL = TakeArrayFromStr(response[0])
            ArrayForAnimalVL.append(int(pointId))
            jarray = json.dumps(ArrayForAnimalVL)
            cursor.execute("""UPDATE Animal
                              SET (visitedLocations) = (?)
                              WHERE id = (?) ;""", (jarray, int(animalId)))

        cursor.execute("""SELECT * FROM VisitedLocation
                          WHERE id = ? and locationPointId = ?;""", (int(animalId),int(pointId)))
        response = cursor.fetchone()
        answer = ResponseForVisitedLocation(response)
        return answer, 201
        
@app.route('/animals/<animalId>/locations' ,methods = ['PUT'])
def put_Alocations(animalId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)
    check_animalId = animalIdNotFound(int(animalId))
    if check_animalId == False:
        return make_response("404 Error", 404)


    content = request.get_json()
    visitedLocationPointId = content['visitedLocationPointId']
    locationPointId = content['locationPointId']

    if visitedLocationPointId == None or int(visitedLocationPointId) <= 0:
        return make_response("400 Error", 400)
    if locationPointId == None or int(locationPointId) <= 0:
        return make_response("400 Error", 400)
    if int(visitedLocationPointId) == int(locationPointId):
        return make_response("400 Error", 400)

    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        response = TakeLocationPointId(int(animalId))
        chippingLoctaionId = TakeChippingLocationId(int(animalId))
        for i in response:
            for j in i:
                if j == int(visitedLocationPointId) and chippingLoctaionId[0] == int(locationPointId):
                    return make_response("400 1 point to chippinglocation Error", 404)
                else:
                    break
            break
        
        response_len = len(response)
        for i in range(0, response_len):
            if response[i][0] == int(visitedLocationPointId):
                if i <= response_len-1 and i != 0 and response[i-1][0] == int(locationPointId):
                    return make_response("400 Error", 400)
            if response[i][0] == int(visitedLocationPointId):
                if i < response_len-1 and response[i+1][0] == int(locationPointId):
                    return make_response("400 Error", 400)
        
        cursor.execute("""SELECT count(locationPointId) as count
                          FROM VisitedLocation
                          WHERE id = ? and locationPointId = ?;""", (int(animalId), int(visitedLocationPointId)))
        response = cursor.fetchone()
        if response[0] == None:
            return make_response("404 visitedLocationPoint not FOUND Error", 404)
        

        cursor.execute("""SELECT count(id) as count
                          FROM Location
                          WHERE id = ?;""", (int(locationPointId),))
        response = cursor.fetchone()
        if response[0] == 0:
            return make_response("404 Error", 404)
        
        cursor.execute("""UPDATE VisitedLocation
                          SET (locationPointId) = (?)
                          WHERE locationPointId = ?;""", (int(locationPointId), int(visitedLocationPointId)))
        
        cursor.execute("""SELECT visitedLocations
                          FROM Animal
                          WHERE id = ?;""", (int(animalId),))
        response = cursor.fetchone()
        ArrayFromAnimalVL = TakeArrayFromStr(response[0])
        for i in range(0, len(ArrayFromAnimalVL)):
            if ArrayFromAnimalVL[i] == int(visitedLocationPointId):
                ArrayFromAnimalVL[i] = int(locationPointId)
        
        jarray = json.dumps(ArrayFromAnimalVL)
        cursor.execute("""UPDATE Animal
                            SET (visitedLocations) = (?)
                            WHERE id = (?) ;""", (jarray, int(animalId)))

        cursor.execute("""SELECT * FROM VisitedLocation
                          WHERE id = ? and locationPointId = ?;""", (int(animalId),int(locationPointId)))
        response = cursor.fetchone()
        answer = ResponseForVisitedLocation(response)
        return answer

@app.route('/animals/<animalId>/locations/<visitedPointId>' ,methods = ['DELETE'])
def delete_Alocations(animalId, visitedPointId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if check == False:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)
    if visitedPointId == ' ' or int(visitedPointId) <= 0:
        return make_response("400 Error", 400)
    
    response = animalIdNotFound(int(animalId))
    if response == False:
        return make_response("404 Error", 404)
    
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT locationPointId
                          FROM VisitedLocation 
                          WHERE id = ?;""", (int(animalId),))
        response = cursor.fetchall()
        isOk = False
        response_len = len(response)
        for i in range(0, response_len):
            if response[i][0] == int(visitedPointId):
                isOk = True

        if isOk == False:
            return make_response("404 Error", 404)

        cursor.execute("""SELECT chippingLocationId
                            FROM Animal
                            WHERE id = ?;""", (int(animalId),))
        chippingLocationId = cursor.fetchone()
        DeleteTheSecond = False

        for i in range(0, response_len):
            if response[i][0] == int(visitedPointId):
                if response[i+1][0] == chippingLocationId[0]:
                    DeleteTheSecond = True
            else:
                break
        
        cursor.execute("""SELECT visitedLocations
                          FROM Animal
                          WHERE id = ?;""", (int(animalId),))
        response = cursor.fetchone()
        ArrayFromAnimalVL = TakeArrayFromStr(response[0])
        cursor.execute("""DELETE FROM VisitedLocation
                          WHERE id = ? and locationPointId = ?;""", (int(animalId), int(visitedPointId)))
        if DeleteTheSecond == True:
            cursor.execute("""DELETE FROM VisitedLocation
                              WHERE id = ? and locationPointId = ?;""", (int(animalId), chippingLocationId[0]))
            ArrayFromAnimalVL.remove(chippingLocationId[0])
        
        ArrayFromAnimalVL.remove(int(visitedPointId))
        jarray = json.dumps(ArrayFromAnimalVL)
        cursor.execute("""UPDATE Animal
                            SET (visitedLocations) = (?)
                            WHERE id = (?) ;""", (jarray, int(animalId)))

        return "Request complete succesfuly"

if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0", port=8080)