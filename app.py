from flask import Flask, render_template

app = Flask(__name__)

# Mock Data: To be replaced by Azure SQL Database 
mock_announcements = [
    {
        "id": 1, 
        "title": "Final Project Deadlines", 
        "date": "2026-05-15", 
        "content": "All CSEC 3 final projects must be deployed on Azure and submitted via GitHub."
    },
    {
        "id": 2, 
        "title": "Department Town Hall", 
        "date": "2026-05-20", 
        "content": "Join the faculty for the end-of-semester department meeting."
    }
]

# Mock Data: To be replaced by Azure Blob Storage 
mock_files = [
    {"name": "CSEC3_Syllabus.pdf", "size": "1.2 MB"},
    {"name": "Project_Rubric.docx", "size": "45 KB"},
    {"name": "Department_Clearance.pdf", "size": "210 KB"}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/announcements')
def announcements():
    # TODO: Connect to Azure SQL using pyodbc or SQLAlchemy here
    # Fetch rows from the Announcements table instead of using mock_announcements
    return render_template('announcements.html', announcements=mock_announcements)

@app.route('/downloads')
def downloads():
    # TODO: Connect to Azure Blob Storage using azure-storage-blob here
    # Fetch list of blobs from the department container instead of using mock_files
    return render_template('downloads.html', files=mock_files)

if __name__ == '__main__':
    app.run(debug=True, port=5001)