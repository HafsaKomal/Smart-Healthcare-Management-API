from extensions import mongo  # now no circular import

def create_patient(data):
    patients_collection = mongo.db.patients
    patients_collection.insert_one(data)
    return True

def get_patient_by_id(patient_id):
    patients_collection = mongo.db.patients
    return patients_collection.find_one({"patient_id": patient_id})

def get_all_patients():
    patients_collection = mongo.db.patients
    return list(patients_collection.find())
