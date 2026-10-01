from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# PostgreSQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg://postgres:Bariloe20%40@localhost:5432/User'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)


@app.route('/')
def index():
    return "Database connected successfully!"


if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)