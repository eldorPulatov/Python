from peewee import *
#
# db = PostgresqlDatabase('animals', user='postgres', password='123',
#                         host='localhost', port=5432)

db = PostgresqlDatabase('animals', user='qwerty', password='123',
                        host='database', port=5432)

class BaseModel(Model):
    id = PrimaryKeyField()

    class Meta:
        database = db
        order_by = "id"


class Account(BaseModel):
    firstName = CharField()
    lastName = CharField()
    email = CharField()
    password = CharField()
    role = CharField(default='USER')

    class Meta:
        db_table = "Account"


class Location(BaseModel):
    latitude = DoubleField()
    longitude = DoubleField()

    class Meta:
        db_table = "Location"


class Area(BaseModel):
    name = CharField()
    areaPoints = TextField()

    class Meta:
        db_table = "Area"


class AnimalType(BaseModel):
    type = CharField()

    class Meta:
        db_table = "AnimalType"

class Animal(BaseModel):
    animalTypes = TextField()
    weight = FloatField()
    length = FloatField()
    height = FloatField()
    gender = CharField()
    lifeStatus = CharField(default='ALIVE')
    chippingDateTime = TextField(default=None)
    chipperId = ForeignKeyField(Account, to_field=Account.id, backref='chipperIdFromAccounts')
    chippingLocationId = ForeignKeyField(Location, to_field=Location.id, backref='chipFromLocation')
    visitedLocations = TextField(null=True, default=None)
    deathDateTime = TextField(null=True, default=None)

    class Meta:
        db_table = "Animal"

class VisitedLocation(Model):
    id = IntegerField()
    dateTimeOfVisitLocationPoint = TextField()
    locationPointId = IntegerField()

    class Meta:
        database = db
        order_by = "id"
        db_table = "VisitedLocation"
