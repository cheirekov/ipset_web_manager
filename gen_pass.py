from werkzeug.security import generate_password_hash

password = input("Enter password to hash: ")
hash = generate_password_hash(password)
print(f"Hashed password: {hash}")

