from Functions import *
from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/registration', methods=['POST'])
def post_registration():
    checkAuthorization = check_Authorization(request.headers)
    if checkAuthorization:
        return make_response("403 Request from authorization account", 403)

    content = request.get_json()
    check_content = valid_RegistrationData(content)
    if not check_content:
        return make_response("400 Error", 400)

    email_count = check_db_email(content['email'])
    if email_count == 0:
        with db:
            Account.create(**content)
            query = (Account.select(Account.id, Account.firstName, Account.lastName, Account.email, Account.role)
                     .order_by(Account.id.desc())
                     .limit(1)
                     .dicts()
                     .first())
            return query, 201
    else:
        return make_response("409 Error", 409)


@app.route('/accounts/<accountId>', methods=['GET'])
def get_account(accountId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if int(accountId) and int(accountId) > 0:
        role = take_roleand_id(request.headers)
        if role['role'] in ['USER', 'CHIPPER']:
            if role['id'] != int(accountId):
                return make_response("403 Error", 403)
        else:
        response = select_account_id(int(accountId))
        if not response:
            return make_response("404 Account with this accountId not found", 404)
        return response
    else:
        return make_response("400 Error", 400)


@app.route('/accounts/search', methods=['GET'])
def get_account_search():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    firstName = request.args.get('firstName')
    lastName = request.args.get('lastName')
    email = request.args.get('email')
    _from = request.args.get('from', type=int)
    size = request.args.get('size', type=int)

    if size is None:
        size = 10
    if _from is None:
        _from = 0

    if size <= 0:
        return make_response("400 Error", 400)
    if _from < 0:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] != "ADMIN":
        return make_response("403 Error", 403)

    with db:
        query = (Account
                 .select(Account.id, Account.firstName, Account.lastName, Account.email, Account.role)
                 .where((Account.firstName ** f"%{firstName}%") | (firstName is None),
                        (Account.lastName ** f"%{lastName}%") | (lastName is None),
                        (Account.email ** f"%{email}%") | (email is None))
                 .limit(size)
                 .offset(_from)
                 .dicts())

        listQuery = list(query)
        return listQuery


@app.route('/accounts', methods=['POST'])
def post_account():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    content = request.get_json()
    check_content = valid_RegistrationData(content)
    if not check_content:
        return make_response("400 Error", 400)
    if content['role'] not in ["ADMIN", "CHIPPER", "USER"]:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] != "ADMIN":
        return make_response("403 Error", 403)

    email_count = check_db_email(content['email'])
    if email_count > 1:
        return make_response("409 Error", 409)

    with db:
        Account.create(**content)
        query = (Account.select(Account.id, Account.firstName, Account.lastName, Account.email, Account.role)
                 .where(Account.email == content['email'])
                 .dicts()
                 .first())
        return query, 201


@app.route('/accounts/<accountId>', methods=['PUT'])
def put_account(accountId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if accountId == ' ' or int(accountId) <= 0:
        return make_response("400 id error", 400)

    content = request.get_json()
    check_content = valid_RegistrationData(content)
    if not check_content:
        return make_response("400 Error", 400)
    if content['role'] not in ["ADMIN", "CHIPPER", "USER"]:
        return make_response("400 Error", 400)

    roleAndId_dict = take_role_and_id(request.headers)
    if roleAndId_dict['role'] in ['CHIPPER', 'USER']:
        check_id = valid_id(int(accountId))
        if check_id is None:
            return make_response("403 Error такого id не сущ.", 403)
        if roleAndId_dict['id'] != int(accountId):
            return make_response("403 Error Обновление не своего аккаунта", 403)
    else:
        check_id = valid_id(int(accountId))
        if check_id is None:
            return make_response("404 Error такого id не сущ.", 404)

    email_count = check_db_email(content['email'])
    if email_count > 1:
        return make_response("409 Error", 409)

    with db:
        query = Account.update(**content)
        query.execute()
        response = select_account_id(int(accountId))
        return response


@app.route('/accounts/<accountId>', methods=['DELETE'])
def delete_account(accountId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if accountId is None or int(accountId) <= 0:
        return make_response("400 id error", 400)

    roleAndId_dict = take_role_and_id(request.headers)
    if roleAndId_dict['role'] in ['CHIPPER', 'USER']:
        check_id = valid_id(int(accountId))
        if check_id is None:
            return make_response("403 Error такого id не сущ.", 403)
        if roleAndId_dict['id'] != int(accountId):
            return make_response("403 Error Обновление не своего аккаунта", 403)
    else:
        check_id = valid_id(int(accountId))
        if check_id is None:
            return make_response("404 Error такого id не сущ.", 404)

    with db:
        query = (Animal.select(fn.COUNT(Animal.chipperId).alias('chipperId_count'))
                 .where(Animal.chipperId == int(accountId))
                 .dicts()
                 .first())
        if query['chipperId_count'] != 0:
            return make_response("400 Error acc сввязан с животным", 400)

        Account.delete().where(Account.id == int(accountId)).execute()

        return "Request completed successfully"


@app.route('/locations/<pointId>', methods=['GET'])
def get_location(pointId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if int(pointId) is None or int(pointId) <= 0:
        return make_response('400 Error', 400)

    response = select_location(int(pointId))
    if response is None:
        return make_response("404 Error", 404)
    else:
        return response


@app.route('/locations', methods=['POST'])
def post_location():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    content = request.get_json()
    checkContent = valid_longLat(content)
    if not checkContent:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ['ADMIN', 'CHIPPER']:
        return make_response("403 Error", 403)

    with db:
        query = (Location.select(fn.COUNT(Location.latitude).alias('count_lat'),
                                 fn.COUNT(Location.longitude).alias('count_lon'))
                 .where(Location.latitude == content['latitude'],
                        Location.longitude == content['longitude'])
                 .dicts()
                 .first())
        if query['count_lat'] == 0 and query['count_lon'] == 0:
            Location.create(**content)
            query = (Location.select()
                     .where(Location.latitude == content['latitude'],
                            Location.longitude == content['longitude'])
                     .dicts()
                     .first())
            return query, 201
        else:
            return make_response("409 Error", 409)


@app.route('/locations/<pointId>', methods=['PUT'])
def put_location(pointId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if pointId == ' ' or int(pointId) <= 0:
        return make_response("400 Error", 400)

    content = request.get_json()
    checkContent = valid_longLat(content)
    if not checkContent:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ['ADMIN', 'CHIPPER']:
        return make_response("403 Error", 403)
    # Если точка используется как точка чипирования или как посещенная точка, то её изменять нельзя !
    with db:
        query = (Location.select(fn.COUNT(Location.id).alias('count_id'))
                 .where(Location.id == int(pointId))
                 .dicts()
                 .first())
        if query['count_id'] != 0:
            query = (Location.select(fn.COUNT(Location.latitude).alias('count_lat'),
                                     fn.COUNT(Location.longitude).alias('count_lon'))
                     .where(Location.latitude == content['latitude'],
                            Location.longitude == content['longitude'])
                     .dicts()
                     .first())
            if query['latitude'] == 0 and query['longitude'] == 0:
                query = Location.update(**content).where(Location.id == int(pointId))
                query.execute()
                response = select_location(int(pointId))
                return response
            else:
                return make_response("409 Error", 409)
        else:
            return make_response("404 Error", 404)


@app.route('/locations/<pointId>', methods=['DELETE'])
def delete_location(pointId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if pointId is None or int(pointId) <= 0:
        return make_response("400 id error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] != ['ADMIN']:
        return make_response("403 Error", 403)

    with db:
        check_id = select_location(int(pointId))
        if check_id is None:
            return make_response("404 Error", 404)

        query = (Animal.select(fn.COUNT(Animal.chippingLocationId).alias('chippingLocationId_count'))
                 .where(Animal.chippingLocationId == int(pointId))
                 .dicts()
                 .first())
        if query['chippingLocationId_count'] != 0:
            return make_response("400 Error точка сввязана с животным", 400)

        Location.delete().where(Location.id == int(pointId)).execute()
        return "Request completed successfully"


@app.route('/areas/<areaId>', methods=['GET'])
def get_area(areaId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if areaId is None or int(areaId) <= 0:
        return make_response("400 Error", 400)

    with db:
        query = Area.select().where(Area.id == int(areaId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)
        query['areaPoints'] = json.loads(query['areaPoints'])
        return query


@app.route('/areas', methods=['POST'])
def post_area():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    content = request.get_json()
    if content['name'] is None or content['name'] == ' ':
        return make_response("400 Error", 400)

    checkAreaPoints = check_area_points(content['areaPoints'])
    if not checkAreaPoints:
        return make_response("400 Error", 400)

    if len(content['areaPoints']) != 3:
        return make_response("400 Error", 400)

    checkPointsOnLine = are_points_on_line(content['areaPoints'])
    if not checkPointsOnLine:
        return make_response("400 Error точки лежат на 1 плоскости", 400)

    checkBorders = check_polygon(content['areaPoints'])
    if not checkBorders:
        return make_response("400 Границы пересекаются между собой", 400)

    checkNewZone = check_new_zone_and_old_zone(content['areaPoints'])
    if not checkNewZone:
        return make_response("400  Границы новой зоны пересекают границы уже существующей зоны.", 400)

    check = is_new_zone_within_existing_zone(content['areaPoints'])
    if not check:
        return make_response("400  Граница новой зоны находятся внутри границ существующей зоны.", 400)

    check = is_existing_zone_within_new_zone(content['areaPoints'])
    if not check:
        return make_response("400 Границы существующей зоны находятся внутри границ новой зоны.")

    checkDuplicates = has_duplicates(content['areaPoints'])
    if checkDuplicates:
        return make_response("400 Новая зона имеет дубликаты точек.", 400)

    check = new_zone_does_not_contain_zone_viewpoints(content['areaPoints'])
    if check:
        return make_response("400 Новая зона состоит из части точек существующей зоны", 400)

    role = take_role_and_id(request.headers)
    if role['role'] != ['ADMIN']:
        return make_response("403 Error", 403)

    zone = zone_exists(content['areaPoints'])
    if zone:
        return make_response("400 Такая зона существует", 409)

    with db:
        query = Area.select().where(Area.name == content['name']).dicts().first()
        if query is not None:
            return make_response("409 Зона с таким name уже существует", 409)

        content['areaPoints'] = json.dumps(content['areaPoints'])
        Area.create(**content)

        query = Area.select().where(Area.name == content['name']).dicts().first()
        query['areaPoints'] = json.loads(content['areaPoints'])
        return query, 201


@app.route('/areas/<areaId>', methods=['PUT'])
def put_area(areaId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if areaId == ' ' or int(areaId) <= 0:
        return make_response("400 Error", 400)

    content = request.get_json()
    if content['name'] is None or content['name'] == ' ':
        return make_response("400 Error", 400)

    checkAreaPoints = check_area_points(content['areaPoints'])
    if not checkAreaPoints:
        return make_response("400 Error", 400)

    if len(content['areaPoints']) != 3:
        return make_response("400 Error", 400)

    checkPointsOnLine = are_points_on_line(content['areaPoints'])
    if not checkPointsOnLine:
        return make_response("400 Error точки лежат на 1 плоскости", 400)

    checkBorders = check_polygon(content['areaPoints'])
    if not checkBorders:
        return make_response("400 Границы пересекаются между собой", 400)

    checkNewZone = check_new_zone_and_old_zone(content['areaPoints'])
    if not checkNewZone:
        return make_response("400  Границы новой зоны пересекают границы уже существующей зоны.", 400)

    check = is_new_zone_within_existing_zone(content['areaPoints'])
    if not check:
        return make_response("400  Граница новой зоны находятся внутри границ существующей зоны.", 400)

    check = is_existing_zone_within_new_zone(content['areaPoints'])
    if not check:
        return make_response("400 Границы существующей зоны находятся внутри границ новой зоны.")

    checkDuplicates = has_duplicates(content['areaPoints'])
    if checkDuplicates:
        return make_response("400 Новая зона имеет дубликаты точек.", 400)

    check = new_zone_does_not_contain_zone_viewpoints(content['areaPoints'])
    if check:
        return make_response("400 Новая зона состоит из части точек существующей зоны", 400)

    role = take_role_and_id(request.headers)
    if role['role'] != ['ADMIN']:
        return make_response("403 Error", 403)

    zone = zone_exists(content['areaPoints'])
    if zone:
        return make_response("400 Такая зона существует", 409)

    with db:
        query = Area.select().where(Area.name == content['name']).dicts().first()
        if query is None:
            return make_response("409 Зона с таким name уже существует", 409)

        content['areaPoints'] = json.dumps(content['areaPoints'])
        query = Area.update(**content).where(Location.id == int(areaId))
        query.execute()

        query = Area.select().where(Area.name == content['name']).dicts().first()
        query['areaPoints'] = json.loads(content['areaPoints'])
        return query


@app.route('/areas/<areaId>', methods=['DELETE'])
def delete_area(areaId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if areaId == ' ' or int(areaId) <= 0:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] != "ADMIN":
        return make_response("403 Error", 403)

    with db:
        query = Area.select().where(Area.id == int(areaId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)

        Area.delete().where(Area.id == int(areaId)).execute()
        return "Request completed successfully"


@app.route('/animals/types/<typeId>', methods=['GET'])
def get_animals_type(typeId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if int(typeId) is None or int(typeId) <= 0:
        return make_response("400 Error", 400)

    with db:
        query = AnimalType.select().where(AnimalType.id == int(typeId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)

        return query


@app.route('/animals/types', methods=['POST'])
def post_animals_type():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    content = request.get_json()
    if content['type'] is None or content['type'] == '':
        return make_response("400 Error", 400)
    check = validData(content['type'])
    if not check:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ['ADMIN', 'CHIPPER']:
        return make_response("403 Error", 403)

    with db:
        query = AnimalType.select().where(AnimalType.type == content['type']).dicts().first()
        if query is not None:
            return make_response("409 Error", 409)

        AnimalType.create(**content)
        response = AnimalType.select().where(AnimalType.type == content['type']).dicts().first()
        return response, 201


@app.route('/animals/types/<typeId>', methods=['PUT'])
def put_animals_type(typeId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if typeId == ' ' or int(typeId) <= 0:
        return make_response("400 Error", 400)

    content = request.get_json()
    if content['type'] is None or content['type'] == '':
        return make_response("400 Error", 400)
    check = validData(content['type'])
    if not check:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ['ADMIN', 'CHIPPER']:
        return make_response("403 Error", 403)

    with db:
        query = AnimalType.select().where(AnimalType.id == int(typeId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)

        query = AnimalType.select().where(AnimalType.type == content['type']).dicts().first()
        if query is not None:
            return make_response("409 Error", 409)

        query = AnimalType.update(**content).where(AnimalType.id == int(typeId))
        query.execute()
        response = AnimalType.select().where(AnimalType.type == content['type']).dicts().first()
        return response


@app.route('/animals/types/<typeId>', methods=['DELETE'])
def delete_animals_type(typeId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if typeId is None or int(typeId) <= 0:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] != 'ADMIN':
        return make_response("403 Error", 403)

    with db:
        query = AnimalType.select().where(AnimalType.id == int(typeId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)

        query = Animal.select(Animal.animalTypes).dicts()
        list_query = list(query)

        # Преобразуем строку ['animalTypes'] из массива list_query в list[int]
        for i in range(0, len(list_query)):
            list_query[i]['animalTypes'] = json.loads(list_query[i]['animalTypes'])

        # Проверка typeId в массиве animalTypes
        for i in range(0, len(list_query)):
            if int(typeId) in list_query[i]['animalTypes']:
                return make_response("400 Есть животное с таким типом", 400)

        AnimalType.delete().where(AnimalType.id == int(typeId)).execute()
        return "Request completed successfully"


@app.route('/animals/<animalId>', methods=['GET'])
def get_animal(animalId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if int(animalId) is None or int(animalId) <= 0:
        return make_response("400 Error", 400)

    with db:
        query = Animal.select().where(Animal.id == int(animalId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)

        query['animalTypes'] = json.loads(query['animalTypes'])
        return query


@app.route('/animals/search', methods=['GET'])
def search_animal():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    startDateTime = request.args.get('startDateTime')
    endDateTime = request.args.get('endDateTime')
    chipperId = request.args.get('chipperId', type=int)
    chippingLocationId = request.args.get('chippingLocationId', type=int)
    lifeStatus = request.args.get('lifeStatus')
    gender = request.args.get('gender')
    _from = request.args.get('from', type=int)
    size = request.args.get('size', type=int)

    if size is None:
        size = 10
    if _from is None:
        _from = 0
    if size <= 0 or _from < 0:
        return make_response("400 Error", 400)

    if startDateTime is not None:
        check_startDateTime = datetime_valid(startDateTime)
        if not check_startDateTime:
            return make_response("400 sss Error", 400)
    if endDateTime is not None:
        check_endDateTime = datetime_valid(endDateTime)
        if not check_endDateTime:
            return make_response("400 Error", 400)

    if chipperId is not None and chipperId <= 0:
        return make_response("400 Error", 400)
    if chippingLocationId is not None and chippingLocationId <= 0:
        return make_response("400 Error", 400)

    if lifeStatus is not None and lifeStatus not in ['ALIVE', 'DEAD']:
        return make_response("400 Error", 400)
    if gender is not None and gender not in ['FEMALE', 'OTHER', 'MALE']:
        return make_response("400 Error", 400)

    with db:
        query = (Animal.select()
                 .where((Animal.chippingDateTime >= startDateTime) | (startDateTime is None),
                        (Animal.chippingDateTime <= endDateTime) | (endDateTime is None),
                        (Animal.chipperId == chipperId) | (chipperId is None),
                        (Animal.chippingLocationId_id == chippingLocationId) | (chippingLocationId == None),
                        (Animal.lifeStatus == lifeStatus) | (lifeStatus == None),
                        (Animal.gender == gender) | (gender == None))
                 .limit(size)
                 .offset(_from)
                 .dicts())
        list_Query = list(query)

        # преобразуем каждую строку ['animalTypes'] в list[int].
        # Если сущ. ['visitedLocations'] то и это преобразуем
        for i in range(0, len(list_Query)):
            list_Query[i]['animalTypes'] = json.loads(list_Query[i]['animalTypes'])
            if list_Query[i]['visitedLocations'] is not None:
                list_Query[i]['visitedLocations'] = json.loads(list_Query[i]['visitedLocations'])

        return list_Query


@app.route('/animals', methods=['POST'])
def post_animal():
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    content = request.get_json()
    check_AnimalData = valid_animal_data(content)
    if not check_AnimalData:
        return make_response("400 Error", 400)

    if len(content['animalTypes']) == 0:
        return make_response("400 Error", 400)

    if content['animalTypes'] is None:
        return make_response("400 Error", 400)

    check_animalTypes = valid_animalTypes(content['animalTypes'])
    if not check_animalTypes:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ["ADMIN", "CHIPPER"]:
        return make_response("403 Error", 403)

    check_id_fromDB = check_animal_types_from_db(content['animalTypes'])
    if not check_id_fromDB:
        return make_response("404 Тип животного не найден", 404)

    check_chipperId = check_id_from_db(content['chipperId'])
    if not check_chipperId:
        return make_response("404 chipperId Error", 404)

    check_chippingLocationId = check_location_from_db(content['chippingLocationId'])
    if not check_chippingLocationId:
        return make_response("404 chippingLocationId Error", 404)

    with db:
        content['animalTypes'] = json.dumps(content['animalTypes'])
        Animal.create(**content)
        query = (Animal.select()
                 .order_by(Animal.id.desc())
                 .limit(1)
                 .dicts()
                 .first())
        query['animalTypes'] = json.loads(query['animalTypes'])
        return query, 201


@app.route('/animals/<animalId>', methods=['PUT'])
def put_animal(animalId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)

    content = request.get_json()
    check_AnimalData = valid_animal_data(content)
    if not check_AnimalData:
        return make_response("400 Error", 400)

    if content['lifeStatus'] not in ['ALIVE', 'DEAD']:
        return make_response("400 Error", 400)

    if len(content['animalTypes']) == 0:
        return make_response("400 Error", 400)

    if content['animalTypes'] is None:
        return make_response("400 Error", 400)

    check_animalTypes = valid_animalTypes(content['animalTypes'])
    if not check_animalTypes:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ["ADMIN", "CHIPPER"]:
        return make_response("403 Error", 403)

    check_id_fromDB = check_animal_types_from_db(content['animalTypes'])
    if not check_id_fromDB:
        return make_response("404 Тип животного не найден", 404)

    check_chipperId = check_id_from_db(content['chipperId'])
    if not check_chipperId:
        return make_response("404 chipperId Error", 404)

    check_chippingLocationId = check_location_from_db(content['chippingLocationId'])
    if not check_chippingLocationId:
        return make_response("404 chippingLocationId Error", 404)

    with db:
        query = Animal.select(Animal.lifeStatus).where(Animal.id == int(animalId)).dicts().first()
        if query['lifeStatus'] == 'DEAD' and content['lifeStatus'] == 'ALIVE':
            return make_response("400 Error", 400)

        query = Animal.select(Animal.visitedLocations).where(Animal.id == int(animalId)).dicts().first()
        if query['visitedLocations'] is not None:
            list_visitedLocations = json.loads(query['visitedLocations'])
            if content['chippingLocationId'] == list_visitedLocations[0]:
                return make_response("400 Error", 400)

        content['animalTypes'] = json.dumps(content['animalTypes'])
        Animal.update(**content).where(Animal.id == int(animalId)).execute()

        query = response_for_animals(int(animalId))
        return query


@app.route('/animals/<animalId>', methods=['DELETE'])
def delete_animal(animalId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId is None or int(animalId) <= 0:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] != "ADMIN":
        return make_response("403 Error", 403)

    with db:
        query = Animal.select().where(Animal.id == int(animalId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)

        query = Animal.select(Animal.visitedLocations).where(Animal.id == int(animalId)).dicts().first()
        if query is None:
            return make_response("400 Error животное покинуло точку", 400)

        Animal.delete().where(Animal.id == int(animalId)).execute()
        return "Request completed successfully"


@app.route('/animals/<animalId>/types/<typeId>', methods=['POST'])
def post_animal_types(animalId, typeId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)
    if typeId == ' ' or int(typeId) <= 0:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ["ADMIN", "CHIPPER"]:
        return make_response("403 Error", 403)

    with db:
        query = Animal.select().where(Animal.id == int(animalId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)

        query = AnimalType.select().where(AnimalType.id == int(typeId)).dicts().first()
        if query is None:
            return make_response("404 Error тип животного не найден", 404)

        # Добавляем новый тип животного
        query = Animal.select(Animal.animalTypes).where(Animal.id == int(animalId)).dicts().first()

        list_animalTypes = json.loads(query['animalTypes'])
        list_animalTypes.append(int(typeId))
        query['animalTypes'] = json.dumps(list_animalTypes)
        Animal.update(**query).execute()

        query = response_for_animals(int(animalId))
        return query, 201


@app.route('/animals/<animalId>/types', methods=['PUT'])
def put_animal_types(animalId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)

    content = request.get_json()
    if content['oldTypeId'] is None or content['oldTypeId'] <= 0:
        return make_response("400 Error", 400)
    if content['newTypeId'] is None or content['newTypeId'] <= 0:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ["ADMIN", "CHIPPER"]:
        return make_response("403 Error", 403)

    with db:
        query = Animal.select().where(Animal.id == int(animalId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)

        check = AnimalType.select().where(AnimalType.id == content['oldTypeId']).dicts().first()
        if check is None:
            return make_response("404 Error Тип животного с oldTypeId не найден", 404)

        check = AnimalType.select().where(AnimalType.id == content['newTypeId']).dicts().first()
        if check is None:
            return make_response("404 Error Тип животного с newTypeId не найден", 404)

        list_animalTypes = json.loads(query['animalTypes'])
        check_oldTypeId = find_id(list_animalTypes, content['oldTypeId'])
        if not check_oldTypeId:
            return make_response("404 Типа животного с oldTypeId нет у животного с animalId", 404)

        check_newTypeId = find_id(list_animalTypes, content['newTypeId'])
        if check_newTypeId:
            return make_response("409 Тип животного с newTypeId уже есть у животного с animalId", 409)

        if check_oldTypeId is True and check_newTypeId is True:
            return make_response("409 Животное с animalId уже имеет типы с oldTypeId и newTypeId", 409)

        list_animalTypes = replace_id(list_animalTypes, content['oldTypeId'], content['newTypeId'])
        list_animalTypes = json.dumps(list_animalTypes)
        Animal.update(animalTypes=list_animalTypes).where(Animal.id == int(animalId)).execute()

        query = response_for_animals(int(animalId))
        return query


@app.route('/animals/<animalId>/types/<typeId>', methods=['DELETE'])
def delete_animal_types(animalId, typeId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)
    if typeId == ' ' or int(typeId) <= 0:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ["ADMIN", "CHIPPER"]:
        return make_response("403 Error", 403)

    with db:
        query = Animal.select().where(Animal.id == int(animalId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)

        check = AnimalType.select().where(AnimalType.id == int(typeId)).dicts().first()
        if check is None:
            return make_response("404 Тип животного с typeId не найден", 404)

        list_animalTypes = json.loads(query['animalTypes'])
        check_typeId = find_id(list_animalTypes, int(typeId))
        if not check_typeId:
            return make_response("404 У животного с animalId нет типа с typeId", 404)

        if len(list_animalTypes) == 1 and list_animalTypes[0] == int(typeId):
            return make_response("400 У животного только один тип и это тип с typeId ", 400)

        list_animalTypes.remove(int(typeId))
        list_animalTypes = json.dumps(list_animalTypes)
        Animal.update(animalTypes=list_animalTypes).where(Animal.id == int(animalId)).execute()

        query = response_for_animals(int(animalId))
        return query


@app.route('/animals/<animalId>/locations', methods=['GET'])
def get_animal_locations(animalId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)

    startDateTime = request.args.get('startDateTime')
    endDateTime = request.args.get('endDateTime')
    _from = request.args.get('form', type=int)
    size = request.args.get('size', type=int)

    if size is None:
        size = 10
    if _from is None:
        _from = 0
    if size <= 0 or _from < 0:
        return make_response("400 Error", 400)

    if startDateTime is not None:
        check_startDateTime = datetime_valid(startDateTime)
        if not check_startDateTime:
            return make_response("400 sss Error", 400)
    if endDateTime is not None:
        check_endDateTime = datetime_valid(endDateTime)
        if not check_endDateTime:
            return make_response("400 Error", 400)

    with db:
        query = Animal.select().where(Animal.id == int(animalId)).dicts().first()
        if query is None:
            return make_response("404 Error", 404)

        query = (VisitedLocation.select()
                 .where(VisitedLocation.id == int(animalId),
                        (VisitedLocation.dateTimeOfVisitLocationPoint >= startDateTime) | (startDateTime is None),
                        (VisitedLocation.dateTimeOfVisitLocationPoint <= endDateTime) | (endDateTime is None))
                 .limit(size)
                 .offset(_from)
                 .dicts())
        list_Query = list(query)
        return list_Query


@app.route('/animals/<animalId>/locations/<pointId>', methods=['POST'])
def post_animal_locations(animalId, pointId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 valid Error", 400)
    if pointId == ' ' or int(pointId) <= 0:
        return make_response("400 valid Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ["ADMIN", "CHIPPER"]:
        return make_response("403 Error", 403)

    with db:
        query = Location.select().where(Location.id == int(pointId)).dicts().first()
        if query is None:
            return make_response("404 Точка локации с pointId не найдена", 404)

        query = Animal.select().where(Animal.id == int(animalId)).dicts().first()
        if query is None:
            return make_response("404 Животное с animalId не найдено", 404)

        if query['lifeStatus'] == "DEAD":
            return make_response("400 Dead animal", 400)

        # if query['visitedLocations'] is None:
        #     return make_response("400 Животное находится в точке чипирования и никуда не перемещалось", 400)

        if query['chippingLocationId'] == int(pointId):
            return make_response("400 попытка добавить точку локации, равную точке чипирования.", 400)

        list_visitedLocations = json.loads(query['visitedLocations']) if query['visitedLocations'] is not None else []
        if len(list_visitedLocations) != 0 and list_visitedLocations[-1] == int(pointId):
            return make_response("400 Попытка добавить точку локации, в которой уже находится животное", 400)

        # Добавляем запись в таблицу VisitedLcoation
        content = {
            "id": int(animalId),
            "locationPointId": int(pointId)
        }
        VisitedLocation.create(**content)

        # Добавляем запись в таблицу Animal для столбца visitedLcoations
        list_visitedLocations.append(int(pointId))
        list_visitedLocations = json.dumps(list_visitedLocations)
        Animal.update(visitedLocations=list_visitedLocations).where(Animal.id == int(animalId)).execute()

        query = (VisitedLocation.select().where(VisitedLocation.id == int(animalId),
                                                VisitedLocation.locationPointId == int(pointId))
                 .dicts()
                 .first())

        return query, 201


@app.route('/animals/<animalId>/locations', methods=['PUT'])
def put_animal_locations(animalId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 valid Error", 400)

    content = request.get_json()
    visitedLocationPointId = content['visitedLocationPointId']
    locationPointId = content['locationPointId']
    if visitedLocationPointId is None or visitedLocationPointId <= 0:
        return make_response("400 Error", 400)
    if locationPointId is None or locationPointId <= 0:
        return make_response("400 Error", 400)
    if visitedLocationPointId == locationPointId:
        return make_response("400 Обновление точки на такую же точку", 400)

    role = take_role_and_id(request.headers)
    if role['role'] not in ["ADMIN", "CHIPPER"]:
        return make_response("403 Error", 403)

    with db:
        query = Location.select().where(Location.id == locationPointId).dicts().first()
        if query is None:
            return make_response("404 Точка локации с locationPointId не найдена", 404)

        query = (VisitedLocation.select()
                 .where(VisitedLocation.locationPointId == visitedLocationPointId,
                        VisitedLocation.id == int(animalId)).dicts().first())
        if query is None:
            return make_response("404 У животного нет объекта с информацией"
                                 " о посещенной точке локации с visitedLocationPointId.", 404)

        query = Animal.select().where(Animal.id == int(animalId)).dicts().first()
        if query is None:
            return make_response("404 Животное с animalId не найдено", 404)

        list_visitedLocations = json.loads(query['visitedLocations'])
        if list_visitedLocations[0] == visitedLocationPointId and locationPointId == query['chippingLocationId']:
            return make_response("400 Обновление первой посещенной точки на точку чипирования", 400)

        check_locations = match_next_or_previous(list_visitedLocations,
                                                 visitedLocationPointId, locationPointId)
        if not check_locations:
            return make_response("400 точка совпадает со след. или с предыдущей")

        # Обновляем visitedLocationPointId на locationPointId
        list_visitedLocations = [locationPointId if x == visitedLocationPointId else x for x in list_visitedLocations]
        list_visitedLocations = json.dumps(list_visitedLocations)
        Animal.update(visitedLocations=list_visitedLocations).where(Animal.id == int(animalId)).execute()

        (VisitedLocation.update(locationPointId=locationPointId)
         .where(VisitedLocation.id == int(animalId),
                VisitedLocation.locationPointId == visitedLocationPointId).execute())

        query = (VisitedLocation.select().where(VisitedLocation.id == int(animalId),
                                                VisitedLocation.locationPointId == locationPointId)
                 .dicts()
                 .first())

        return query


@app.route('/animals/<animalId>/locations/<visitedPointId>', methods=['DELETE'])
def delete_animal_locations(animalId, visitedPointId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if animalId == ' ' or int(animalId) <= 0:
        return make_response("400 Error", 400)
    if visitedPointId == ' ' or int(visitedPointId) <= 0:
        return make_response("400 Error", 400)

    role = take_role_and_id(request.headers)
    if role['role'] != "ADMIN":
        return make_response("403 Error", 403)

    with db:
        query = (VisitedLocation.select()
                 .where(VisitedLocation.locationPointId == int(visitedPointId),
                        VisitedLocation.id == int(animalId)).dicts().first())
        if query is None:
            return make_response("404 У животного нет объекта с информацией"
                                 " о посещенной точке локации с visitedLocationPointId.", 404)

        query = Animal.select().where(Animal.id == int(animalId)).dicts().first()
        if query is None:
            return make_response("404 Животное с animalId не найдено", 404)

        list_visitedLocations = json.loads(query['visitedLocations'])
        list_visitedLocations.remove(int(visitedPointId))
        if list_visitedLocations[0] == query['chippingLocationId']:
            list_visitedLocations.remove(query['chippingLocationId'])

        if list_visitedLocations is not None:
            list_visitedLocations = json.dumps(list_visitedLocations)
            Animal.update(visitedLocations=list_visitedLocations).where(Animal.id == int(animalId)).execute()
        else:
            Animal.update(visitedLocations=None).where(Animal.id == int(animalId)).execute()

        VisitedLocation.delete() \
            .where(VisitedLocation.id == int(animalId),
                   VisitedLocation.locationPointId == visitedPointId).execute()
        return "Request completed successfully"


@app.route('/areas/<areaId>/analytics', methods=['GET'])
def animal_analytics(areaId):
    if 'Authorization' in request.headers:
        check = check_Authorization(request.headers)
        if not check:
            return make_response("401 Error", 401)
    else:
        return make_response("401 Error! Not authorized request", 401)

    if areaId == ' ' or int(areaId) <= 0:
        return make_response("400 valid Error", 400)

    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    # if startDate >= endDate:
    #     return make_response("400 valid Error", 400)

    # check_date = valid_date(startDate)
    # if not check_date:
    #     return make_response("400 valid Error", 400)
    # check_date = valid_date(endDate)
    # if not check_date:
    #     return make_response("400 valid Error", 400)

    with db:
        query = Area.select().where(Area.id == int(areaId)).dicts().first()
        if query is None:
            return make_response("404 Зона с areaId не найдена", 404)

        list_areaPoints = json.loads(query['areaPoints'])

        list_location_id = find_location_id(list_areaPoints)

        asd = animal_count_on_zone(list_location_id, startDate, endDate)
        return str(asd)









if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
