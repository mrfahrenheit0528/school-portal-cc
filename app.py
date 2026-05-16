import os
import io
import pyodbc
from flask import Flask, render_template, send_file, abort, jsonify, request, redirect, url_for
from azure.storage.blob import BlobServiceClient
from werkzeug.utils import secure_filename

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
                content NVARCHAR(MAX) NOT NULL,
                category NVARCHAR(20) NOT NULL DEFAULT 'notice'
            )
        ''')
        
        # Add category column if table already exists but column is missing
        cursor.execute('''
            IF NOT EXISTS (
                SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Announcements' AND COLUMN_NAME = 'category'
            )
            ALTER TABLE Announcements ADD category NVARCHAR(20) NOT NULL DEFAULT 'notice'
        ''')
        
        # Seed initial data if table is empty
        cursor.execute('SELECT COUNT(*) FROM Announcements')
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Announcements (title, date_posted, content, category) VALUES ('Final Project Deadlines', '2026-05-15', 'All CSEC 3 final projects must be deployed on Azure and submitted via GitHub.', 'urgent')")
            cursor.execute("INSERT INTO Announcements (title, date_posted, content, category) VALUES ('Department Town Hall', '2026-05-20', 'Join the faculty for the end-of-semester department meeting.', 'event')")
            
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
    # 1. Fetch Announcements from Azure SQL
    announcements_list = []
    if SQL_SERVER:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, date_posted, content, category FROM Announcements ORDER BY date_posted DESC")
            for row in cursor.fetchall():
                announcements_list.append({
                    "id": row[0],
                    "title": row[1],
                    "date": row[2].strftime('%B %d, %Y') if row[2] else '',
                    "content": row[3],
                    "category": row[4] if len(row) > 4 else 'notice'
                })
            conn.close()
        except Exception as e:
            print(f"Database Read Error: {e}")

    # 2. Fetch Files from Azure Blob Storage
    files_list = []
    if STORAGE_CONNECTION_STRING:
        try:
            blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(STORAGE_CONTAINER_NAME)
            
            blob_list = container_client.list_blobs()
            for blob in blob_list:
                size_kb = blob.size / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
                files_list.append({"name": blob.name, "size": size_str})
        except Exception as e:
            print(f"Storage Read Error: {e}")

    # Render index with live data
    return render_template('index.html', announcements=announcements_list, files=files_list)



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

@app.route('/health')
def health():
    """Diagnostic endpoint to verify Azure resource connectivity."""
    status = {"db": "not configured", "storage": "not configured", "blob_count": 0}
    
    if SQL_SERVER:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Announcements")
            count = cursor.fetchone()[0]
            conn.close()
            status["db"] = f"connected ({count} announcements)"
        except Exception as e:
            status["db"] = f"error: {e}"
    
    if STORAGE_CONNECTION_STRING:
        try:
            blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(STORAGE_CONTAINER_NAME)
            blobs = list(container_client.list_blobs())
            status["storage"] = f"connected ({len(blobs)} files)"
            status["blob_count"] = len(blobs)
            status["blob_names"] = [b.name for b in blobs]
        except Exception as e:
            status["storage"] = f"error: {e}"
    
    return jsonify(status)

# --- Admin Routes ---
@app.route('/admin')
def admin():
    """Renders the admin dashboard and fetches existing content for management."""
    announcements_list = []
    if SQL_SERVER:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, date_posted, content, category FROM Announcements ORDER BY date_posted DESC")
            for row in cursor.fetchall():
                announcements_list.append({
                    "id": row[0],
                    "title": row[1],
                    "date": row[2].strftime('%Y-%m-%d') if row[2] else '',
                    "content": row[3],
                    "category": row[4] if len(row) > 4 else 'notice'
                })
            conn.close()
        except Exception as e:
            print(f"Database Read Error: {e}")

    files_list = []
    if STORAGE_CONNECTION_STRING:
        try:
            blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(STORAGE_CONTAINER_NAME)
            blob_list = container_client.list_blobs()
            for blob in blob_list:
                files_list.append({"name": blob.name})
        except Exception as e:
            print(f"Storage Read Error: {e}")

    return render_template('admin.html', announcements=announcements_list, files=files_list)

@app.route('/admin/edit_announcement/<int:id>', methods=['POST'])
def edit_announcement(id):
    """Updates an existing announcement in Azure SQL."""
    title = request.form.get('title')
    date_posted = request.form.get('date_posted')
    content = request.form.get('content')
    category = request.form.get('category', 'notice')
    
    if SQL_SERVER and title and date_posted and content:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Announcements SET title = ?, date_posted = ?, content = ?, category = ? WHERE id = ?",
                (title, date_posted, content, category, id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database Update Error: {e}")
            
    return redirect(url_for('admin'))

@app.route('/admin/delete_announcement/<int:id>', methods=['POST'])
def delete_announcement(id):
    """Removes an announcement from Azure SQL."""
    if SQL_SERVER:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Announcements WHERE id = ?", (id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database Delete Error: {e}")
            
    return redirect(url_for('admin'))

@app.route('/admin/delete_file/<filename>', methods=['POST'])
def delete_file(filename):
    """Permanently deletes a file from Azure Blob Storage."""
    if STORAGE_CONNECTION_STRING:
        try:
            blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
            blob_client = blob_service_client.get_blob_client(container=STORAGE_CONTAINER_NAME, blob=filename)
            blob_client.delete_blob()
        except Exception as e:
            print(f"File Delete Error: {e}")
            
    return redirect(url_for('admin'))

@app.route('/admin/post_announcement', methods=['POST'])
def post_announcement():
    """Handles the form submission to insert a new announcement into Azure SQL."""
    title = request.form.get('title')
    date_posted = request.form.get('date_posted')
    content = request.form.get('content')
    category = request.form.get('category', 'notice')
    
    if SQL_SERVER and title and date_posted and content:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Parameterized query to prevent SQL injection
            cursor.execute(
                "INSERT INTO Announcements (title, date_posted, content, category) VALUES (?, ?, ?, ?)",
                (title, date_posted, content, category)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database Insert Error: {e}")
            
    return redirect(url_for('admin'))

@app.route('/admin/upload_file', methods=['POST'])
def upload_file():
    """Handles file uploads and pushes them securely to the Azure Blob Storage container."""
    if 'file' not in request.files:
        return redirect(request.url)
        
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('admin'))
        
    if file and STORAGE_CONNECTION_STRING:
        try:
            # Secure the filename before saving
            filename = secure_filename(file.filename)
            
            blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
            blob_client = blob_service_client.get_blob_client(container=STORAGE_CONTAINER_NAME, blob=filename)
            
            # Upload the file stream directly to Azure
            blob_client.upload_blob(file.stream, overwrite=True)
        except Exception as e:
            print(f"File Upload Error: {e}")
            
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)