import os
import pyodbc
from flask import Flask, render_template, send_file
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import io

# Load environment variables for local development
load_dotenv()

app = Flask(__name__)

# Fetch connection strings from environment variables
SQL_CONN_STR = os.getenv('SQL_CONNECTION_STRING')
BLOB_CONN_STR = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER_NAME = 'department-files'

def get_db_connection():
    """Establish a connection to Azure SQL Database."""
    conn = pyodbc.connect(SQL_CONN_STR)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/announcements')
def announcements():
    announcements_data = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT title, date, content FROM Announcements ORDER BY date DESC")
        
        # Convert pyodbc rows to dictionaries for the template
        for row in cursor.fetchall():
            announcements_data.append({
                "title": row.title,
                "date": row.date.strftime('%Y-%m-%d'),
                "content": row.content
            })
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        # Fallback empty list if connection fails
        pass 

    return render_template('announcements.html', announcements=announcements_data)

@app.route('/downloads')
def downloads():
    files_data = []
    try:
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            # Convert size from bytes to KB
            size_kb = round(blob.size / 1024, 2)
            files_data.append({
                "name": blob.name,
                "size": f"{size_kb} KB"
            })
    except Exception as e:
        print(f"Blob storage error: {e}")

    return render_template('downloads.html', files=files_data)

@app.route('/download/<filename>')
def download_file(filename):
    """Securely downloads a file from private blob storage and streams it to the user."""
    try:
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
        
        # Download blob into memory
        download_stream = blob_client.download_blob()
        file_bytes = download_stream.readall()
        
        return send_file(
            io.BytesIO(file_bytes),
            download_name=filename,
            as_attachment=True
        )
    except Exception as e:
        return f"Error downloading file: {e}", 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)