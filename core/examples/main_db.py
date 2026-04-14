from generator.db_generator import DBGenerator

entity_name = "User"
fields = [
    "name string",
    "email string unique",
    "password string secret"
]

generator = DBGenerator(entity_name, fields)
print(generator.generate())
