from flask import Blueprint, request, jsonify
from models.patient import create_patient, get_patient_by_id, get_all_patients

patient_bp = Blueprint('patients', __name__, url_prefix='/api/patients')

@patient_bp.route('/', methods=['GET'])
def list_patients():
    patients = get_all_patients()
    return jsonify(patients)

@patient_bp.route('/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = get_patient_by_id(patient_id)
    if patient:
        return jsonify(patient)
    return jsonify({"msg": "Patient not found"}), 404

@patient_bp.route('/', methods=['POST'])
def add_patient():
    data = request.json
    create_patient(data)
    return jsonify({"msg": "Patient created"}), 201
