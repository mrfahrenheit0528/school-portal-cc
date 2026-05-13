import os
import io
import pyodbc
from flask import Flask, render_template, send_file, abort
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

# --- Environment Variables (Injected by Azure App Service) ---
SQL_SERVER = os.environ.get('SQL_SERVER')
SQL_DATABASE = os.environ.get('SQL_DATABASE')
SQL_USERNAME = os.environ.get('SQL_USERNAME')
SQL_PASSWORD = os.environ.get('SQL_PASSWORD')
STORAGE_CONNECTION_STRING = os.environ.get('STORAGE_CONNECTION_STRING')
STORAGE_CONTAINER_NAME = os.environ.get('STORAGE_CONTAINER_NAME')

# --- Database Helper ---
def get_db_connection():
    # ODBC Driver 18 is pre-installed on Azure App Service Linux environments
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
    return pyodbc.connect(conn_str)

def init_db():
    """Creates the Announcements table and inserts initial data if it does not exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Announcements' AND xtype='U')
            CREATE TABLE Announcements (
                id INT IDENTITY(1,1) PRIMARY KEY,
                title NVARCHAR(255) NOT NULL,
                date_posted DATE NOT NULL,
                content NVARCHAR(MAX) NOT NULL
            )
        ''')
        
        # Seed initial data if table is empty
        cursor.execute('SELECT COUNT(*) FROM Announcements')
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Announcements (title, date_posted, content) VALUES ('Final Project Deadlines', '2026-05-15', 'All CSEC 3 final projects must be deployed on Azure and submitted via GitHub.')")
            cursor.execute("INSERT INTO Announcements (title, date_posted, content) VALUES ('Department Town Hall', '2026-05-20', 'Join the faculty for the end-of-semester department meeting.')")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Initialization Error: {e}")

# Run initialization when the app starts on Azure
if SQL_SERVER:
    init_db()

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/announcements')
def announcements():
    announcements_list = []
    if SQL_SERVER:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, date_posted, content FROM Announcements ORDER BY date_posted DESC")
            for row in cursor.fetchall():
                announcements_list.append({
                    "id": row[0],
                    "title": row[1],
                    "date": row[2].strftime('%Y-%m-%d') if row[2] else '',
                    "content": row[3]
                })
            conn.close()
        except Exception as e:
            print(f"Database Read Error: {e}")
            announcements_list = [{"title": "System Alert", "date": "", "content": "Unable to connect to the Azure SQL database."}]
    
    return render_template('announcements.html', announcements=announcements_list)

@app.route('/downloads')
def downloads():
    files_list = []
    if STORAGE_CONNECTION_STRING:
        try:
            blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(STORAGE_CONTAINER_NAME)
            
            # List all blobs in the private container
            blob_list = container_client.list_blobs()
            for blob in blob_list:
                size_kb = blob.size / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
                files_list.append({"name": blob.name, "size": size_str})
                
        except Exception as e:
            print(f"Storage Read Error: {e}")
            
    return render_template('downloads.html', files=files_list)

@app.route('/download/<filename>')
def download_file(filename):
    """Securely streams a file from the private Azure Blob Storage container to the user."""
    if not STORAGE_CONNECTION_STRING:
        abort(404)
    try:
        blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=STORAGE_CONTAINER_NAME, blob=filename)
        
        # Download the blob into memory
        download_stream = blob_client.download_blob()
        file_stream = io.BytesIO(download_stream.readall())
        file_stream.seek(0)
        
        return send_file(file_stream, as_attachment=True, download_name=filename)
    except Exception as e:
        print(f"File Download Error: {e}")
        abort(404)

if __name__ == '__main__':
    app.run(debug=True, port=5001)