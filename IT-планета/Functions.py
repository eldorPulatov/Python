from peewee import *
import sqlite3
import base64
from datetime import datetime
import re
import json


def find_duplicates(list):
    for i in range(len(list)):
        if list[i] <= 0:
            return 2
        for j in range(len(list)):
            if list[i] == list[j] and i != j:
                return 1
    
    return 3


def validPassword(str):
    symbols = "?/\!$%<>\t\n "
    for i in str:
        for j in symbols:
            if i == j:
                return False  
    return True

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
        check = validPassword(content['firstName'])
        if check == False:
            return False
        
        check = validPassword(content['lastName'])
        if check == False:
            return False
        
        check = validPassword(content['password'])
        if check == False:
            return False

        check = validPassword(content['email'])
        if check == False:
            return False

        check = check_email(content['email'])
        if check == False:
            return False
        
        return True
    
def check_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
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

    check = check_email(email)
    if check == False:
        return ""
    else:
        return email

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
        with sqlite3.connect('wonderland.db') as db:
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
    with sqlite3.connect('wonderland.db') as db:
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

    if P_latitude == None or float(P_latitude) < -90 or float(P_latitude) > 90:
        return False
    if P_longitude == None or float(P_longitude) < -180 or float(P_longitude) > 180:
        return False
    return True

def valid_IDAnimalType(typeId):
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(id) as count 
                          FROM AnimalType
                          WHERE id = ?;""", (typeId,))
        check_id = cursor.fetchone()
        return check_id
    
def select_AnimalType(typeId):
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT *
                            FROM AnimalType
                            WHERE id = ?;""", (typeId,))
        content = cursor.fetchone()
        return content
    
def valid_AnimalType(animalType):
    with sqlite3.connect('wonderland.db') as db:
            cursor = db.cursor()
            cursor.execute("""SELECT count(type) as count 
                            FROM AnimalType
                            WHERE type = ?;""", (animalType,))
            check_type = cursor.fetchone()
            return check_type
    
def check_DbEmail(email):
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(email) as count 
                            FROM Account 
                            WHERE email = ?;""", (email,))
        email_count = cursor.fetchone()
        return email_count
    
def select_AccountId(accountId):
    with sqlite3.connect('wonderland.db') as db:
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
            if (i == ',' or i == ']' or i == '}') and isOk == False:
                return None
            
            if (i == ',' or i == ']' or i == '}') and isOk == True:
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

    if weight == '' or weight == None or float(weight) <= 0:
        return False
    if length == '' or length == None or float(length) <= 0:
        return False
    if height == '' or height == None or float(height) <= 0:
        return False
    if gender != '' and gender!=  'FEMALE' and gender != 'OTHER' and gender != 'MALE':
        return False
    if chipperId == '' or chipperId == None or int(chipperId) <= 0:
        return False
    if chippingLocationId == '' or chippingLocationId == None or int(chippingLocationId) <= 0:
        return False
    
    return True

def check_idFromDB(chipperId):
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(id) as count
                                FROM Account
                                WHERE id = ?;""", (chipperId,))
        content = cursor.fetchone()
        if content[0] == 0:
            return False
        else:
            return True
        
def check_locationFromDB(chippingLocationId):
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT count(id) as count
                                FROM Location
                                WHERE id = ?;""", (chippingLocationId,))
        content = cursor.fetchone()
        if content[0] == 0:
            return False
        else:
            return True
    
def animalIdNotFound(animalId):
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT *
                          FROM Animal
                          WHERE id = ?;""", (animalId,))
        content = cursor.fetchone()
        if content != None:
            return content
        else:
            return False
        
def JSON_response(params, response):
    for i, j in zip(params, response):
        params[i] = j

    return dict(params)

def arraysForAnimals(answer):
    if answer['animalTypes'] != None and answer['animalTypes'] != "[]":
        array = TakeArrayFromStr(answer['animalTypes'])
        answer['animalTypes'] = array
    else:
        answer['animalTypes'] = []
    if answer['visitedLocations'] != None and answer['visitedLocations'] != "[]":
        array = TakeArrayFromStr(answer['visitedLocations'])
        answer['visitedLocations'] = array
    else:
        answer['visitedLocations'] = []

def ResponseForAnimals(response):
    params = {
        "id" : "1",
        "animalTypes":"asd",
        "weight":"51",
        "length":"34",
        "height":"42",
        "gender" : "MALE",
        "lifeStatus":"DEAD",
        "chippingDateTime":[],
        "chipperId":"34",
        "chippingLocationId":"42",
        "visitedLocations":[],
        "deathDateTime":[],
    }
    answer = JSON_response(params, response)
    arraysForAnimals(answer)
    return answer

def ResponseForAccount(response):
    params = {
        "id" : "1",
        "firstName":"asd",
        "lastName":"qwe",
        "email":"asd@asd.rs"
    }
    answer = JSON_response(params, response)
    return answer

def ResponseForLocation(response):
    params = {
        "id" : "1",
        "latitude":"asd",
        "longitude":"qwe",
    }
    answer = JSON_response(params, response)
    return answer

def ResponseForAnimalTypes(response):
    params = {
        "id" : "1",
        "type":str("asd"),
    }
    answer = JSON_response(params, response)
    return answer

def ResponseForVisitedLocation(response):
    params = {
        "id" : "1",
        "dateTimeOfVisitLocationPoint":"asd",
        "locationPointId":"4"
    }
    answer = JSON_response(params, response)
    return answer

def TakeChippingLocationId (animalId):
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT chippingLocationId
                          FROM Animal
                          WHERE id = ?;""", (animalId,))
        chippingLoctaionId = cursor.fetchone()
        return chippingLoctaionId

def TakeLocationPointId (animalId):
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT locationPointId
                          FROM VisitedLocation 
                          WHERE id = ?;""", (animalId,))
        response = cursor.fetchall()
        return response
    
def VLarrayToAnimal(animalId, pointId):
    with sqlite3.connect('wonderland.db') as db:
        cursor = db.cursor()
        cursor.execute("""SELECT visitedLocations
                          FROM Animal
                          WHERE id = ?;""", (animalId,))
        response = cursor.fetchone()
        if response[0] == None:
            ArrayForAnimalVL = [int(pointId)]
            jarray = json.dumps(ArrayForAnimalVL)
            cursor.execute("""UPDATE Animal
                              SET (visitedLocations) = (?)
                              WHERE id = (?) ;""", (jarray, animalId))
        else:
            ArrayForAnimalVL = TakeArrayFromStr(response[0])
            ArrayForAnimalVL.append(pointId)
            jarray = json.dumps(ArrayForAnimalVL)
            cursor.execute("""UPDATE Animal
                              SET (visitedLocations) = (?)
                              WHERE id = (?) ;""", (jarray, animalId))

def findIdinArray(array, id):
    for i in array:
        if i == id:
            return True
    
    return False