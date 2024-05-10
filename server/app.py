#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):

    def get(self):
        campers = [camper.to_dict(only=('id','name','age')) for camper in Camper.query.all()]
        
        return make_response(campers, 200)

    def post(self):
        json = request.get_json()

        try:
            new_camper = Camper(name = json.get('name'), age = json.get('age'))
            
        except ValueError as e:
            return {'errors': ["validation errors"]}, 400  

        if new_camper:     
            db.session.add(new_camper)
            db.session.commit()
            return make_response(new_camper.to_dict(only=('id','name','age')),201)

        
class CampersByID(Resource):

    def get(self,id):
        camper = Camper.query.filter_by(id = id).first()

        if camper:
            return make_response(camper.to_dict(),200)

        return {'error':"Camper not found"}, 404
    
    def patch(self,id):
        json = request.get_json()
        camper = Camper.query.filter_by(id=id).first()
        
        if camper:
            try:
                setattr(camper,'name', json['name'])
                setattr(camper,'age',json['age'])
            except ValueError as e:
                return {"errors":["validation errors"]},400

            db.session.add(camper)
            db.session.commit()

            return make_response(camper.to_dict(only=('id','name','age')),202)
        else:
            return {"error": "Camper not found"},404


class Activities(Resource):

    def get(self):
        activities = [activity.to_dict(only=('id','name','difficulty')) for activity in Activity.query.all()]

        return make_response(activities,200)

class ActivitiesByID(Resource):

    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()

        if activity:
            db.session.delete(activity)
            db.session.commit()

            return {'message':""},204
        
        return {"error": "Activity not found"},404

class Signups(Resource):
    
    def post(self):
        json = request.get_json()

        try:
            new_signup = Signup(time = json.get('time'), activity_id=json.get('activity_id'), camper_id=json.get('camper_id'))
            db.session.add(new_signup)
            db.session.commit()
            return make_response(new_signup.to_dict(),201)

        except ValueError as e:
            return {'errors': ["validation errors"]}, 400

            
            

api.add_resource(Campers,'/campers')
api.add_resource(CampersByID,'/campers/<int:id>')
api.add_resource(Activities,'/activities')
api.add_resource(ActivitiesByID,'/activities/<int:id>')
api.add_resource(Signups,'/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
