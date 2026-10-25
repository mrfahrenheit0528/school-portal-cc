# CSEC Student & Faculty Portal

A cloud-based student and faculty portal developed for the **Computer Science Department** to centralize announcements, academic resources, and downloadable department documents.

The application combines a Flask web application with Microsoft Azure services for database management, private file storage, deployment, and infrastructure provisioning.

---

## Project Explanation

The CSEC Student & Faculty Portal was developed to provide students and faculty with a centralized platform for accessing department information and resources.

Users can view categorized announcements and download department files, while an administrative dashboard provides tools for managing announcements and uploaded documents.

---

## Key Features

### Dynamic Announcements
- Displays announcements stored in Azure SQL Database
- Supports **Notice**, **Event**, and **Urgent** categories
- Allows announcements to be created, edited, and deleted through the admin dashboard

### Department File Repository
- Stores documents in private Azure Blob Storage
- Lists available files dynamically
- Securely streams files through the Flask application for download
- Allows administrators to upload and remove documents

### Administrative Dashboard
- Create and manage announcements
- Upload department resources
- Delete existing files
- Manage portal content from a centralized interface

### Interactive Interface
- Responsive desktop and mobile layout
- Hash-based page navigation
- Animated page transitions
- Scroll-reveal and staggered card animations

### Azure Cloud Infrastructure
- Azure App Service for application hosting
- Azure SQL Database for announcement data
- Azure Blob Storage for department files
- Infrastructure provisioning with Azure Bicep
- CPU-based automatic scaling
- HTTPS-only web application configuration

---

## Methodology

The project was designed using a cloud-based three-layer approach:

1. **Presentation Layer** — Flask templates, CSS, and JavaScript provide the student and faculty portal interface.
2. **Application Layer** — Flask handles announcement management, document operations, and communication with Azure services.
3. **Cloud Data Layer** — Azure SQL stores announcement data while Azure Blob Storage manages downloadable files.

Azure Bicep was used to define and provision the required cloud infrastructure consistently.

---

## Results

The completed system provides a centralized portal capable of:

- Publishing department announcements
- Categorizing notices by importance and type
- Uploading and managing department documents
- Providing files to students through private cloud storage
- Managing portal content through an administrative dashboard
- Deploying the complete application on Microsoft Azure
- Automatically scaling application resources according to CPU usage

The project demonstrates the integration of a Python web application with cloud-based database, storage, deployment, and infrastructure services.

---

## Tech Stack

**Backend:** Python, Flask  
**Database:** Azure SQL Database  
**Storage:** Azure Blob Storage  
**Frontend:** HTML5, CSS3, JavaScript, Jinja2  
**Cloud Platform:** Microsoft Azure  
**Hosting:** Azure App Service  
**Infrastructure as Code:** Azure Bicep  
**Database Connectivity:** pyodbc  

---

## Cloud Architecture

```text
                    ┌───────────────────┐
                    │      Users        │
                    │ Students / Faculty│
                    └─────────┬─────────┘
                              │ HTTPS
                              ▼
                    ┌───────────────────┐
                    │ Azure App Service │
                    │   Flask Web App   │
                    └─────────┬─────────┘
                              │
                  ┌───────────┴───────────┐
                  │                       │
                  ▼                       ▼
        ┌─────────────────┐     ┌──────────────────┐
        │    Azure SQL    │     │ Azure Blob       │
        │    Database     │     │ Storage          │
        │                 │     │ Private Container│
        │ Announcements   │     │ Documents        │
        └─────────────────┘     └──────────────────┘
```

The Azure resources are provisioned using the Bicep template located in:

```text
deployment/main.bicep
```

---

## Project Structure

```text
school-portal-cc/
├── deployment/
│   ├── main.bicep
│   └── README.md
├── diagram/
│   └── architecture.png
├── report/
│   └── cost-estimate.md
├── static/
│   ├── ccs.png
│   ├── script.js
│   └── style.css
├── templates/
│   ├── admin.html
│   ├── base.html
│   └── index.html
├── app.py
├── CHANGELOG.md
├── requirements.txt
└── README.md
```

---

## Deployment

The project uses **Azure Bicep** to provision the required infrastructure.

The deployment includes:

- Azure App Service
- Azure App Service Plan
- Azure SQL Server and Database
- Azure Blob Storage
- Private Blob container
- Autoscaling configuration

Detailed deployment instructions are available in:

```text
deployment/README.md
```

---

## Health Check

The application includes a `/health` endpoint for checking connectivity with Azure SQL Database and Blob Storage.

```text
/health
```

---

## Security Considerations

- Application credentials are supplied through Azure environment variables.
- Blob Storage public access is disabled.
- The web application is configured for HTTPS-only traffic.
- SQL administrator credentials are provided as secure deployment parameters.

> The administrative interface is intended for controlled environments. Authentication and authorization should be added before using the management dashboard in a public production deployment.

---

## Developer

- **Guiller Angelo Hermoso** 
- **Rona Mae Quite**
- **Mary Joyce Moico**

Developed as a cloud-based academic portal project for the Computer Science Department.
