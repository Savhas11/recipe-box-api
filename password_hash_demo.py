from werkzeug.security import generate_password_hash, check_password_hash

password = "SunsetTrail!"  # sample password

# 1) Make a hash
password_hash = generate_password_hash(password)
print("Password hash:", password_hash)

# 2) Check with the correct password
is_correct = check_password_hash(password_hash, "SunsetTrail!")
print("Correct password check:", is_correct)

# 3) Check with a wrong password
is_wrong = check_password_hash(password_hash, "SunriseTrail!")
print("Wrong password check:", is_wrong)