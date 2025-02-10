import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

def reset_password(username, new_password, cursor, connection):
    hashed_password = hash_password(new_password)
    query = "UPDATE users SET password = %s WHERE username = %s"
    cursor.execute(query, (hashed_password, username))
    connection.commit()
