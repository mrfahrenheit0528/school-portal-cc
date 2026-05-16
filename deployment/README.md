# Deployment Guide: CSEC Student & Faculty Portal

This guide provides step-by-step instructions for deploying the CSEC Portal to Microsoft Azure. The deployment uses Infrastructure-as-Code (Bicep) to ensure a consistent and secure environment.

## Prerequisites
- **Azure Subscription**: A valid account with permission to create resources.
- **Azure CLI**: [Installed and authenticated](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) (`az login`).
- **Python 3.10+**: For local testing and development.

---

## Step 1: Infrastructure Deployment (Bicep)
The system uses a Bicep template to provision the App Service, SQL Server, and Storage Account automatically.

1. Open your terminal in the project root.
2. Create a resource group:
   ```bash
   az group create --name rg-csec3-final --location eastasia
   ```
3. Deploy the infrastructure (replace placeholders for SQL credentials):
   ```bash
   az deployment group create \
     --resource-group rg-csec3-final \
     --template-file ./deployment/main.bicep \
     --parameters sqlAdministratorLogin='YOUR_ADMIN_USER' \
     --parameters sqlAdministratorLoginPassword='YOUR_SECURE_PASSWORD'
   ```
   > !IMPORTANT
   > Ensure your password meets Azure complexity requirements (uppercase, lowercase, number, symbol).

---

## Step 2: Configure Azure Storage
The application expects a private container named `downloads` to store documents.

1. The Bicep template creates this container automatically.
2. You can upload initial documents via the Azure Portal or the Admin Dashboard at `/admin` after deployment.

---

## Step 3: Application Deployment
Once the infrastructure is ready, deploy the Flask application code.

1. Run the deployment command:
   ```bash
   az webapp up --name csec3portal-webapp-sfajbuykzajcu --resource-group rg-csec3-final --plan csec3portal-asp
   ```
2. Azure will automatically detect the Python environment, install dependencies from `requirements.txt`, and start the web server.

---

## Step 4: Verification
1. Navigate to your Web App URL (provided by the `az webapp up` output).
2. Visit the `/health` endpoint to verify database and storage connectivity:
   `https://<your-app-name>.azurewebsites.net/health`
3. If successful, you should see a JSON response confirming "connected" status for both services.

---

## Security Notes
- **No Hardcoded Passwords**: All credentials (SQL Connection String, Storage Keys) are injected as **Environment Variables** in the Azure App Service.
- **HTTPS Only**: The Web App is configured to redirect all traffic to HTTPS.
- **Private Storage**: Blob storage public access is explicitly disabled.

---
