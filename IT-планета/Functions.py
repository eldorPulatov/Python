import base64
from datetime import datetime
import json
import re
from Models import *
from shapely.geometry import Polygon, LineString, Point
from shapely.validation import explain_validity

# with db:
#     params = {
#         "firstName": "adminFirstName",
#         "lastName": "adminLastName",
#         "email": "admin@simbirsoft.com",
#         "password": "qwerty123",
#         "role": "ADMIN"
#     }
#     Account.create(**params)
#     params = {
#         "firstName": "chipperFirstName",
#         "lastName": "chipperLastName",
#         "email": "chipper@simbirsoft.com",
#         "password": "qwerty123",
#         "role": "CHIPPER"
#     }
#     Account.create(**params)
#     params = {
#         "firstName": "userFirstName",
#         "lastName": "userLastName",
#         "email": "user@simbirsoft.com",
#         "password": "qwerty123",
#         "role": "USER"
#     }
#     Account.create(**params)


def valid_animalTypes(animalTypes: list) -> bool:
    """
    Функция проверки на наличие эл. со значением NULL или <= 0
    :param animalTypes:
    :return True or False, если есть такой элемент:
    """
    for animal in animalTypes:
        if animal is None or animal <= 0:
            return False

    return True


def validData(string: str) -> bool:
    """
    Функция проверки на лишние символы
    :param string:
    :return True(если данные валидны) or False:
    """
    symbols = "?/\!$%<>\t\n "
    for i in string:
        for j in symbols:
            if i == j:
                return False
    return True


def valid_RegistrationData(Body: dict) -> bool:
    """
    Функция проверки валидности данных из запроса
    :param Body:
    :return True(если все данные валидны) or False:
    """

    if Body['firstName'] == '' or Body['firstName'] is None:
        return False
    elif Body['lastName'] == '' or Body['lastName'] is None:
        return False
    elif Body['email'] == '' or Body['email'] is None:
        return False
    elif Body['password'] == '' or Body['password'] is None:
        return False
    else:
        check = validData(Body['firstName'])
        if not check:
            return False

        check = validData(Body['lastName'])
        if not check:
            return False

        check = validData(Body['password'])
        if not check:
            return False

        check = validData(Body['email'])
        if not check:
            return False

        check = check_email(Body['email'])
        if not check:
            return False

        return True


def check_email(email: str) -> bool:
    """
    Функция проверки валидности email-а
    :param email:
    :return True or False, если емаил невалидный:
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False


def takeBase64(string: str) -> str:
    """
    Функция принимает строку из header-а {Authorization} запроса и записывает кодировку в отдельную переменную
    :param string:
    :return base64:
    """
    base64 = ""
    isOk = 0
    for i in string:
        if i == ' ':
            isOk = 1
            continue
        if isOk == 1:
            base64 = base64 + i

    return base64


def take_email(string: str) -> str:
    """
    Функция отделения email-а от запроса {Authorization} формата login:password.
    :param string:
    :return email or "", если данные не валидны:
    """
    email = ""
    for i in string:
        if i != ":":
            email += i
        else:
            break

    check = check_email(email)
    if not check:
        return ""
    else:
        return email


def take_password(string: str) -> str:
    """
    Функция отделения password-а от запроса {Authorization} формата login:password.
    :param string:
    :return password:
    """
    password = ""
    isOk = False
    for i in string:
        if i == ':':
            isOk = True
            continue
        if isOk is True:
            password += i
    return password


def check_Authorization(request) -> bool:
    """
    Функция проверки авторизации 
    декодит и проверяет, есть ли такие данные в БД
    :param request: 
    :return True or False, если нет данных в БД:
    """
    if 'Authorization' in request:
        a = request['Authorization']
        b = takeBase64(a)
        decode = base64.b64decode(b)
        decode_str = decode.decode('ascii')
        decode_e = take_email(decode_str)
        decode_p = take_password(decode_str)
        with db:
            query = (Account
                     .select(fn.count(Account.email).alias('email_count'),
                             fn.count(Account.password).alias('password_count'))
                     .where(Account.email == decode_e, Account.password == decode_p))
            result = query.dicts().first()
            if result['email_count'] == 0 or result['password_count'] == 0:
                return False
            else:
                return True


def take_role_and_id(request) -> dict:
    """
    Функция берет role и id из запроса
    :param request:
    :return result['role', 'id']:
    """
    if 'Authorization' in request:
        a = request['Authorization']
        b = takeBase64(a)
        decode = base64.b64decode(b)
        decode_str = decode.decode('ascii')
        decode_e = take_email(decode_str)
        decode_p = take_password(decode_str)
        with db:
            query = (Account.select(Account.id, Account.role)
                     .where(Account.email == decode_e, Account.password == decode_p)
                     .dicts()
                     .first())
            return query


def valid_id(accountId: id) -> dict:
    """
    Функция проверяет id в БД
    :param accountId:
    :return dict с id или None:
    """
    with db:
        query = (Account.select(Account.id)
                 .where(Account.id == accountId)
                 .dicts()
                 .first())
        return query


def valid_longLat(content: dict) -> bool:
    """
    Функция проверки валидности долготы и широоты
    :param content:
    :return True or False, если один из точек не валдиный:
    """
    P_latitude = content['latitude']
    P_longitude = content['longitude']

    if P_latitude is None or float(P_latitude) < -90 or float(P_latitude) > 90:
        return False
    if P_longitude is None or float(P_longitude) < -180 or float(P_longitude) > 180:
        return False
    return True


def check_area_points(areaPoints: list[dict]) -> bool:
    """
    Функция проверяет валидность всех точек
    :param areaPoints:
    :return True or False, если один из точек не валидный:
    """
    for i in areaPoints:
        check = valid_longLat(i)
        if not check:
            return False

    return True


def are_points_on_line(areaPoints: list[dict]) -> bool:
    """
    Функция проверки точек. Лежат ли они на 1 плоскости.
    :param areaPoints:
    :return True or False, если точки лежат на 1 плоскости:
    """
    x1, y1 = areaPoints[0]["longitude"], areaPoints[0]["latitude"]
    x2, y2 = areaPoints[1]["longitude"], areaPoints[1]["latitude"]
    for i in range(2, len(areaPoints)):
        x3, y3 = areaPoints[i]["longitude"], areaPoints[i]["latitude"]
        if (y3 - y1) * (x2 - x1) != (y2 - y1) * (x3 - x1):
            return False
    return True


def check_polygon(areaPoints: list[dict]) -> bool:
    """
    Функция провреки границ пересекающихся между собой
    :param areaPoints:
    :return True or False, если границы пересекаются:
    """
    polygon = Polygon([(point['longitude'], point['latitude']) for point in areaPoints])
    if not polygon.is_valid:
        invalid_reason = explain_validity(polygon)
        if 'Self-intersection' in invalid_reason:
            return False
    return True


def check_new_zone_and_old_zone(areaPoints: list[dict]) -> bool:
    """
    Функция проверки пересечения границ новой зоны с существующими зонами
    :param areaPoints:
    :return True or False, если они пересекаются:
    """
    new_zone = Polygon([(point['longitude'], point['latitude']) for point in areaPoints])

    with db:
        query = Area.select().dicts()
        query = list(query)

        # преобразуем каждую строку ['areaPoints'] в list[dict]
        for i in range(0, len(query)):
            query[i]['areaPoints'] = json.loads(query[i]['areaPoints'])

        # проверяем, пересекаются ли границы
        for i in range(0, len(query)):
            existing_zone = Polygon([(point['longitude'], point['latitude']) for point in query[i]['areaPoints']])
            if existing_zone.intersects(LineString(new_zone.exterior.coords)):
                return False

    return True


def is_new_zone_within_existing_zone(new_zone_points: list[dict]) -> bool:
    """
    Находится ли новая зона внутри границ сущ. зоны
    :param new_zone_points:
    :return True or False, если она находится:
    """
    with db:
        query = Area.select().dicts()
        query = list(query)

        # преобразуем каждую строку ['areaPoints'] в list[dict]
        for i in range(0, len(query)):
            query[i]['areaPoints'] = json.loads(query[i]['areaPoints'])

        for i in range(0, len(query)):
            existing_zone_polygon = Polygon(
                [(point['longitude'], point['latitude']) for point in query[i]['areaPoints']])
            # Проверяем, что все точки новой зоны находятся внутри границ существующей зоны
            for point in new_zone_points:
                if not existing_zone_polygon.contains(Point(point['longitude'], point['latitude'])):
                    return False

    return True


def is_existing_zone_within_new_zone(new_zone_points: list[dict]) -> bool:
    """
    Находится ли сущ зона внутри границ новой зоны
    :param new_zone_points:
    :return True or False, если она находится:
    """

    new_zone_polygon = Polygon([(point['longitude'], point['latitude']) for point in new_zone_points])
    with db:
        query = Area.select().dicts()
        query = list(query)

        # преобразуем каждую строку ['areaPoints'] в list[dict]
        for i in range(0, len(query)):
            query[i]['areaPoints'] = json.loads(query[i]['areaPoints'])

        # Проверяем, что все точки существующей зоны находятся внутри границ новой зоны
        for i in range(0, len(query)):
            for point in query[i]['areaPoints']:
                if not Point(point['longitude'], point['latitude']).within(new_zone_polygon):
                    return True

    return False


def new_zone_does_not_contain_zone_viewpoints(new_zone_points: list[dict]) -> bool:
    """
    Функция поверки, что новая зона не содержит точки существующей зоны
    :param new_zone_points:
    :return True, если содержит or False:
    """
    new_zone_polygon = Polygon([(point['longitude'], point['latitude']) for point in new_zone_points])
    with db:
        query = Area.select().dicts()
        query = list(query)

        # преобразуем каждую строку ['areaPoints'] в list[dict]
        for i in range(0, len(query)):
            query[i]['areaPoints'] = json.loads(query[i]['areaPoints'])

        # Проверяем, что новая зона не содержит точки существующей зоны
        for i in range(0, len(query)):
            for point in query[i]:
                if new_zone_polygon.contains(Point(point['longitude'], point['latitude'])):
                    return False

    return True


def has_duplicates(new_zone_points: list[dict]) -> bool:
    """
    Функция проверки дубликатов точек
    :param new_zone_points:
    :return True, если есть дубликаты or False:
    """
    # Преобразуем список точек в список кортежей с координатами
    points = [(point['longitude'], point['latitude']) for point in new_zone_points]

    return len(points) != len(set(points))


def zone_exists(new_zone_points: list[dict]) -> bool:
    """
    Функция проверяет, есть ли такая зона в БД
    :param new_zone_points:
    :return True or False, если такой зоны нет:
    """
    new_zone_polygon = Polygon([(point['longitude'], point['latitude']) for point in new_zone_points])
    with db:
        query = Area.select().dicts()
        query = list(query)

        # Преобразуем каждую строку ['areaPoints'] в list[dict]
        for i in range(len(query)):
            query[i]['areaPoints'] = json.loads(query[i]['areaPoints'])

        # Проверяем, есть ли в базе зона, равная новой зоне
        for zone in query:
            zone_polygon = Polygon([(point['longitude'], point['latitude']) for point in zone['areaPoints']])
            if zone_polygon.equals(new_zone_polygon):
                return True

    return False


def select_location(pointId: int) -> dict:
    """
    Функция выборки данных, где совподают id в БД
    :param pointId:
    :return dict:
    """
    with db:
        query = (Location.select()
                 .where(Location.id == pointId)
                 .dicts()
                 .first())
        return query


def check_db_email(email: str) -> int:
    """
    Функция проверки email-а в БД
    :param email:
    :return кол-во email-ов в БД:
    """
    with db:
        count = (Account.select(fn.COUNT(Account.email).alias('count'))
                 .where(Account.email == email)
                 .scalar())

    return count


def select_account_id(accountId: int) -> dict:
    """
    Функция выборки данных, где совподают id в БД
    :param accountId:
    :return dict:
    """
    with db:
        query = (Account.select(Account.id, Account.firstName, Account.lastName, Account.email, Account.role)
                 .where(Account.id == accountId)
                 .dicts()
                 .first())
        return query


def datetime_valid(dt_str):
    try:
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except:
        return False
    return True


def valid_animal_data(content: dict) -> bool:
    """
    Функция проверки валидности данных для таблицы Animal
    :param content:
    :return True or False, если они не валидны:
    """
    weight = content['weight']
    length = content['length']
    height = content['height']
    gender = content['gender']
    chipperId = content['chipperId']
    chippingLocationId = content['chippingLocationId']

    if not (weight and float(weight) > 0):
        return False
    if not (length and float(length) > 0):
        return False
    if not (height and float(height) > 0):
        return False
    if gender not in ['', 'FEMALE', 'OTHER', 'MALE']:
        return False
    if not (chipperId and int(chipperId) > 0):
        return False
    if not (chippingLocationId and int(chippingLocationId) > 0):
        return False

    return True


def check_animal_types_from_db(animalTypes: list) -> bool:
    """
    Функция для проверки элемента массива(id) из таблицы AnimalType
    :param animalTypes:
    :return True or False, если такого id не существует:
    """
    with db:
        for i in animalTypes:
            query = AnimalType.select().where(AnimalType.id == i).dicts().first()
            if query is None:
                return False

    return True


def check_id_from_db(chipperId: int) -> bool:
    """
    Функция проверки id из таблицы Account
    :param chipperId:
    :return True or False, если id не существует:
    """
    with db:
        query = Account.select().where(Account.id == chipperId).dicts().first()
        if query is None:
            return False

    return True


def check_location_from_db(chippingLocationId: int) -> bool:
    """
    Функция проверки id из таблицы Location
    :param chippingLocationId:
    :return True or False, если id не существует:
    """
    with db:
        query = Location.select().where(Location.id == chippingLocationId).dicts().first()
        if query is None:
            return False

    return True


def response_for_animals(animalId: int) -> dict:
    """
    Функция для выборки данных из таблицы Animal
    :param animalId:
    :return dict:
    """
    with db:
        query = Animal.select().where(Animal.id == animalId).dicts().first()
        query['animalTypes'] = json.loads(query['animalTypes'])
        if query['visitedLocations'] is not None:
            query['visitedLocations'] = json.loads(query['visitedLocations'])

        return query


def find_id(array: list, id: int) -> bool:
    """
    Функция для проверки на наличие TypeId у животного
    :param array:
    :param id:
    :return True or False, если нет такого id:
    """
    for item in array:
        if item == id:
            return True

    return False


def replace_id(array: list, oldId: int, newId: int) -> list:
    """
    Заменяет все вхождения значения oldTypeId на newTypeId в массиве list.
    :param array:
    :param oldId:
    :param newId:
    :return array с новыми значениями:
    """
    for i in range(len(array)):
        if array[i] == oldId:
            array[i] = newId

    return array


def match_next_or_previous(visitedLocations: list, visitedLocationPointId: int, locationPointId: int) -> bool:
    """
    Функция проверки точки локации на точку, совпадающую со следующей и/или с предыдущей точками
    :param visitedLocations:
    :param visitedLocationPointId:
    :param locationPointId:
    :return True or False, если точка совпадает со следующией и/или с предыдущей:
    """
    visitedLocations_len = len(visitedLocations)
    for i in range(visitedLocations_len):
        if visitedLocations[i] == visitedLocationPointId:
            if i > 0 and visitedLocations[i - 1] == locationPointId:
                # Совпадает с предыдущей
                return False
            if i < visitedLocations_len - 1 and visitedLocations[i + 1] == locationPointId:
                # Совпадает со следующей
                return False

    return True


def valid_date(date):
    """
    Функция проверки формата ISO-8601 (pattern "yyyy-MM-dd")
    :param date:
    :return True or False, если другого формата:
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def find_location_id(areaPoints: list) -> list:
    """
    Функция выборки id из таблицы Location
    :param areaPoints:
    :return location_id:
    """
    location_id = []
    with db:
        for i in range(len(areaPoints)):
            query = (Location.select()
                     .where(Location.longitude == areaPoints[i]['latitude'],
                            Location.latitude == areaPoints[i]['longitude'])
                     .dicts()
                     .first())

            location_id.append(query['id'])

        return location_id


def animal_count_on_zone(location_id: list, startDate: str, endDate: str) -> int:
    """
    Функция для подсчета кол-ва животных находящихся в зоне в указанный интервал времени
    :param location_id:
    :param startDate:
    :param endDate:
    :return count:
    """
    count = 0
    with db:
        for i in range(len(location_id)):
            query = (
                VisitedLocation.select(VisitedLocation.locationPointId, fn.COUNT(VisitedLocation.id).alias('id_count'))
                .where(VisitedLocation.locationPointId == location_id[i])
                .group_by(VisitedLocation.locationPointId)
                .dicts()
                .first())

            count += query['id_count']

    return count
