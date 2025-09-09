from flask_restful import Resource, reqparse
from models.doctor import Doctor

class DoctorResource(Resource):
    def get(self, doctor_id):
        doctor = Doctor.objects(doctor_id=doctor_id).first()
        if doctor:
            return doctor.to_json(), 200
        return {'message': 'Doctor not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('specialty', required=True)
        data = parser.parse_args()

        doctor = Doctor(**data)
        doctor.save()
        return doctor.to_json(), 201
