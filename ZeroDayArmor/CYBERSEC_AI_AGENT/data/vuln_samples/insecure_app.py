# INTENTIONALLY VULNERABLE — For testing only
import sqlite3, subprocess, os, hashlib

# CWE-89: SQL Injection
def get_user(username: str):
    conn = sqlite3.connect("users.db")
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return conn.execute(query).fetchall()

# CWE-78: Command Injection
def ping_host(host: str):
    result = subprocess.check_output(f"ping -c 4 {host}", shell=True)
    return result.decode()

# CWE-798: Hardcoded Credentials
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DB_PASSWORD = "SuperSecret123!"

# CWE-916: Weak Password Hash (MD5)
def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

# CWE-22: Path Traversal
def read_file(filename: str) -> str:
    with open(f"/var/app/files/{filename}") as f:
        return f.read()
