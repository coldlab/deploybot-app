from fastapi import FastAPI
import os
import psycopg2

app = FastAPI()

def get_db_connection():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    db_connection_name = os.getenv('DB_CONNECTION_NAME')

    host = f"/cloudsql/{db_connection_name}"
    
    return psycopg2.connect(
        host=host,
        user=db_user,
        password=db_password,
        database=db_name
    )

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Cloud Run!"}


@app.get('/health')
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(result)
        cursor.close()
        conn.close()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}