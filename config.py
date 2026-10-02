from decouple import config

class Config:
    SQLALCHEMY_DATABASE_URI = config("SQLALCHEMY_DATABASE_URI")
    passwords = config("passwords")
    my_email = config("my_email")
    host = config("host")
    port = config("port", cast=int)
    SQLALCHEMY_TRACK_MODIFICATIONS = config("SQLALCHEMY_TRACK_MODIFICATIONS", cast=bool)
    secret_key = config("secret_key")