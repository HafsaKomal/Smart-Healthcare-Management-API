# resources/report_resource.py
from flask import Blueprint, jsonify
from extensions import mongo  # This is your PyMongo instance from app.py
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from models.billing import PrescriptionBilling, session  # SQLAlchemy Session
from models.patient import get_all_patients  # MongoDB function to get patient data
# resources/report_resource.py

# Create Blueprint
report_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@report_bp.route('/top-doctors', methods=['GET'])
def top_doctors():
    """
    Endpoint: /api/reports/top-doctors
    Returns top 5 doctors by patient load
    """
    pipeline = [
        {"$unwind": "$appointments"},
        {"$group": {
            "_id": "$appointments.doctor_id",
            "patient_count": {"$sum": 1}
        }},
        {"$sort": {"patient_count": -1}},
        {"$limit": 5}
    ]
    
    top_doctors = list(mongo.db.patients.aggregate(pipeline))
    return jsonify(top_doctors)

@report_bp.route('/disease-trends', methods=['GET'])
def calculate_disease_treatment_duration():
    pipeline = [
        # Step 1: Unwind the medical_conditions array to process each disease
        {
            "$unwind": {
                "path": "$medical_conditions",
                "preserveNullAndEmptyArrays": True
            }
        },
        # Step 2: Extract relevant fields (appointments.date, discharge_date)
        {
            "$addFields": {
                # Use the first appointment date (if any), otherwise null
                "date_of_admission": {"$arrayElemAt": ["$appointments.date", 0]},  # Extract first appointment date
                "discharge_date": "$discharge_date",  # Top-level field for discharge date
            }
        },
        # Step 3: Convert string dates to ISODate
        {
            "$addFields": {
                "date_of_admission_iso": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$date_of_admission"}, "string"]},
                        "then": {
                            "$dateFromString": {
                                "dateString": "$date_of_admission",
                                "format": "%Y-%m-%d",  # Matches the string format 'YYYY-MM-DD'
                                "onError": None  # Gracefully handle conversion failure
                            }
                        },
                        "else": "$date_of_admission"  # If already ISODate, keep it
                    }
                },
                "discharge_date_iso": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$discharge_date"}, "string"]},
                        "then": {
                            "$dateFromString": {
                                "dateString": "$discharge_date",
                                "format": "%Y-%m-%d",  # Matches the string format 'YYYY-MM-DD'
                                "onError": None  # Gracefully handle conversion failure
                            }
                        },
                        "else": "$discharge_date"  # If already ISODate, keep it
                    }
                }
            }
        },
        # Step 4: Filter for valid ISODate conversions
        {
            "$match": {
                "date_of_admission_iso": {"$exists": True, "$ne": None, "$type": "date"},
                "discharge_date_iso": {"$exists": True, "$ne": None, "$type": "date"}
            }
        },
        # Step 5: Calculate treatment duration in days (with debugging)
        {
            "$addFields": {
                "treatment_duration": {
                    "$cond": {
                        "if": {
                            "$and": [
                                {"$ne": ["$date_of_admission_iso", None]},  # Ensure both dates exist
                                {"$ne": ["$discharge_date_iso", None]}
                            ]
                        },
                        "then": {
                            "$divide": [
                                {"$subtract": ["$discharge_date_iso", "$date_of_admission_iso"]},  # Subtract dates in milliseconds
                                1000 * 60 * 60 * 24  # Convert milliseconds to days
                            ]
                        },
                        "else": 0  # If dates are missing, set duration to 0
                    }
                }
            }
        },
        # Step 6: Group by medical condition and calculate total duration and count
        {
            "$group": {
                "_id": "$medical_conditions",  # Group by disease
                "total_duration": {"$sum": "$treatment_duration"},  # Sum of all treatment durations
                "count": {"$sum": 1},  # Count the number of occurrences of the disease
            }
        },
        # Step 7: Calculate average treatment duration for each disease
        {
            "$project": {
                "disease_name": "$_id",  # Set disease name as the _id field
                "average_duration": {
                    "$cond": {
                        "if": {"$eq": ["$count", 0]},  # Handle divide by zero
                        "then": 0,
                        "else": {"$divide": ["$total_duration", "$count"]}  # Calculate the average treatment duration
                    }
                }
            }
        },
        # Step 8: Sort diseases by average treatment duration in descending order
        {
            "$sort": {"average_duration": -1}  # Sort by average duration (highest to lowest)
        },
        {
            "$limit": 5  # Limit the results to top 5 diseases
        }
    ]

    # Execute the aggregation pipeline
    disease_avg_durations = list(mongo.db.patients.aggregate(pipeline))  # Execute the aggregation
    return disease_avg_durations
# 3️⃣ Monthly appointment cancellations vs completions
@report_bp.route('/monthly-appointments-trend', methods=['GET'])
def get_monthly_appointments_trend():
    pipeline = [
        # Step 1: Unwind the appointments array to work with individual appointments
        {
            "$unwind": "$appointments"
        },
        # Step 2: Match the completed and canceled appointments
        {
            "$match": {
                "$or": [
                    {"appointments.status": "completed"},
                    {"appointments.status": "canceled"}
                ]
            }
        },
        # Step 3: Convert `appointments.date` string to ISODate if it's in string format
        {
            "$addFields": {
                "appointments.date": {
                    "$cond": {
                        "if": { "$eq": [{"$type": "$appointments.date"}, "string"] },
                        "then": { "$dateFromString": { "dateString": "$appointments.date" } },
                        "else": "$appointments.date"
                    }
                }
            }
        },
        # Step 4: Extract year and month from the ISODate
        {
            "$addFields": {
                "year": { "$year": "$appointments.date" },
                "month": { "$month": "$appointments.date" }
            }
        },
        # Step 5: Group by year and month to calculate monthly statistics
        {
            "$group": {
                "_id": { "year": "$year", "month": "$month" },
                "completed": {
                    "$sum": {
                        "$cond": [{"$eq": ["$appointments.status", "completed"]}, 1, 0]
                    }
                },
                "canceled": {
                    "$sum": {
                        "$cond": [{"$eq": ["$appointments.status", "canceled"]}, 1, 0]
                    }
                }
            }
        },
        # Step 6: Sort by year and month
        {
            "$sort": { "_id.year": 1, "_id.month": 1 }
        }
    ]
    
    # Execute the aggregation pipeline
    result = list(mongo.db.patients.aggregate(pipeline))  # Execute the aggregation
    return result
@report_bp.route('/average-prescription-cost', methods=['GET'])
def average_prescription_cost():
    """
    Calculate the average prescription cost per disease
    by joining MongoDB patient data with MySQL billing data.
    """
    patients = get_all_patients()  # Fetch all patients from MongoDB
    disease_costs = {}

    # Loop through all patients and their prescriptions
    for patient in patients:
        # Loop through prescriptions for each patient
        for prescription in patient.get("prescriptions", []):
            drug_name = prescription["drug"]
            disease_list = patient.get("diseases", [])
            
            # Query the billing table for the prescription cost
            billing_record = session.query(PrescriptionBilling).filter_by(drug_name=drug_name).first()
            
            if billing_record:
                cost = billing_record.cost  # Prescription cost from SQL

                # Assign cost to each disease
                for disease in disease_list:
                    if disease not in disease_costs:
                        disease_costs[disease] = {"total_cost": 0, "count": 0}
                    disease_costs[disease]["total_cost"] += cost
                    disease_costs[disease]["count"] += 1

    # Calculate average cost per disease
    average_costs = {}
    for disease, data in disease_costs.items():
        average_costs[disease] = data["total_cost"] / data["count"] if data["count"] > 0 else 0

    return jsonify(average_costs)