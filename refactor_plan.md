# BE105 Refactor Plan

## Target layout (plan only, not implemented yet)

(we'll fill this later)

## Acceptance list (public contract)

- POST /login with correct username & password → 200 OK, JSON with JWT token
- POST /login with wrong password → 401 Unauthorized, JSON {"error": "invalid credentials"}
- GET /recipes with a valid token → 200 OK, JSON list of recipes
- GET /recipes/<id> with a valid token and an existing id → 200 OK, JSON for that recipe
- GET /recipes/<id> with a valid token and a non‑existing id → 404 Not Found, JSON {"error": "recipe not found"}
- PATCH /recipes/<id> with no JSON body → 400 Bad Request, JSON {"error": "JSON body required"}
- PATCH /recipes/<id> with valid JSON → 201 Created, JSON for the updated recipe

## Responsibility count in app.py

- Database access (queries, connections)
- Config / environment loading
- Auth and JWT handling
- Password hashing and checking
- Auth routes (login, register)
- Recipe routes (list, get one, update, delete, etc.)
- Permission checks (ownership/admin)
- Decorators for auth/permissions
- HTTP layer wiring (Flask app, request/response)

**Total distinct responsibilities:** 

## Target layout (plan only, not implemented yet)

app/
  __init__.py        # create Flask app, register feature modules
  auth.py           # auth routes, JWT helpers, password hashing
  recipes.py        # recipe routes and helpers
  database.py       # DB connection and query helpers
  config.py         # configuration values (secrets, DB paths, etc.)