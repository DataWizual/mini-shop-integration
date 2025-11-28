#!/usr/bin/env python3
import os
import socket
import time

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", 5432))
timeout = int(os.environ.get("WAIT_DB_TIMEOUT", 120))

start = time.time()
while True:
    try:
        with socket.create_connection((host, port), timeout=3):
            print(f"✅ Database {host}:{port} is available.")
            break
    except Exception as e:
        if time.time() - start > timeout:
            raise TimeoutError(f"❌ Timeout waiting for {host}:{port}") from e
        print(f"Waiting for DB {host}:{port}... ({e})")
        time.sleep(3)
