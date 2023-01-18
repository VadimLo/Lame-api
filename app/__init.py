# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
#
#
# class Config(object):
#     SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost:5432/pdb'
#
#
# app = Flask(__name__)
# print(Config.SQLALCHEMY_DATABASE_URI)
# app.config.from_object(Config)
# db = SQLAlchemy(app)
#
# with app.app_context():
#     db.create_all()
#
