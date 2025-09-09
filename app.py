from flask import Flask
from extensions import mongo  # import PyMongo instance

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/healthcare_db"

# Initialize mongo AFTER app creation
mongo.init_app(app)

from routes import register_routes
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
