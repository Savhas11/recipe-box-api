from app import create_app
from app.extensions import db, migrate

if __name__ == "__main__":
    app = create_app("development")
    with app.app_context():
        print("App loaded with DB:", app.config["SQLALCHEMY_DATABASE_URI"])

        # this line will act like "flask db init" the first time
        migrate.init_app(app, db)