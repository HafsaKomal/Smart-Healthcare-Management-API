from sqlalchemy import create_engine, Column, String, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base class for our models
Base = declarative_base()

# MySQL connection string (update with your actual MySQL credentials)
#DATABASE_URI = 'mysql+pymysql://root:Pakistan0911@localhost:3306/healthcare_db'
DATABASE_URI = 'mysql+mysqlconnector://root:Pakistan0911@localhost:3306/healthcare_db'

# Create the engine and session
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# PrescriptionBilling model to represent the billing table
class PrescriptionBilling(Base):
    __tablename__ = 'prescription_billing'
    # Specify length for the VARCHAR column (e.g., 255 characters)
    prescription_id = Column(String(255), primary_key=True)  # Specify length here
    drug_name = Column(String(255))  # Specify length here
    cost = Column(DECIMAL(10, 2))
# Create table if it doesn't exist already
Base.metadata.create_all(engine)
