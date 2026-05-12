# **CSEC 3 Final Project: Cloud Web Application Deployment**

**Scenario A: School Portal**

This repository contains the Infrastructure as Code (IaC) deployment scripts and application code for our Final Project in Cloud Computing. We utilized Azure Bicep to declaratively provision our cloud resources to ensure idempotency and repeatable deployments.

## **Cloud Optimizations Implemented**

1. **Scalability:** We implemented an Autoscale Profile on the Azure App Service Plan. It is configured to automatically scale out (add an instance) if the average CPU percentage exceeds 70% over a 5-minute window, and scale in when the CPU drops below 30%.  
2. **Fault Tolerance:** We utilized Zone-Redundant Storage (ZRS) for our Azure Blob Storage account, ensuring our department files remain highly available even if an entire Azure data center experiences an outage.

## **Prerequisites**

Before running the deployment script, ensure you have the following installed on your local machine:

* [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)  
* [Visual Studio Code](https://code.visualstudio.com/)  
* The **Bicep** extension for VS Code

## **Deployment Instructions**

### **Step 1: Authenticate with Azure**

Open your terminal and run the following command to log into your Azure account:

az login

*This will open a browser window asking for your Azure credentials. Once logged in, return to the terminal.*

### **Step 2: Create the Resource Group**

All resources must reside in a Resource Group. We are deploying to the southeastasia region. Run this command to create it:

az group create \--name rg-csec3-schoolportal \--location southeastasia

### **Step 3: Execute the Bicep Deployment**

Run the following command to deploy the infrastructure defined in main.bicep.

az deployment group create \--resource-group rg-csec3-schoolportal \--template-file main.bicep

**Security Note:** The script will pause and prompt you to enter a value for sqlAdminPassword. This is the password for the Azure SQL Database. By prompting for it dynamically at runtime using the @secure() decorator in Bicep, we ensure no hardcoded passwords exist in our repository, adhering to security best practices.

### **Step 4: Clean Up Resources**

To prevent unwanted charges on your Azure account, delete the entire resource group once testing and grading are complete:

az group delete \--name rg-csec3-schoolportal \--yes \--no-wait  
