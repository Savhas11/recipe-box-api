from app import create_app

app = create_app("testing")

with app.test_client() as client:
    # 1. Register a new user
    register_response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123",
        },
    )
    print("REGISTER status:", register_response.status_code)
    print("REGISTER body:", register_response.get_json())

    # 2. Log in as that user
    login_response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpassword123",
        },
    )
    print("LOGIN status:", login_response.status_code)
    print("LOGIN body:", login_response.get_json())