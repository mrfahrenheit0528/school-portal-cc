# **Changelog: SchoolPortal**

All notable changes to this project will be documented in this file.

## **[2026-05-13, 5:00AM] - Unreleased**

### **Added**

* **[HERMOSO]** - Drafted the final README.md deployment instructions and prerequisites  
* **[HERMOSO]** - Set up base Flask app structure (app.py) with mock data for announcements and downloads
* **[HERMOSO]** - Created base HTML templates (base.html, index.html, announcements.html, downloads.html) and requirements.txt

## **[2026-05-13, 12:00PM] - Fixed Bicep validation error**

### **Added**

* **[HERMOSO]** - Wrote main.bicep template defining the baseline App Service, Azure SQL Database, and Autoscale rules
* **[HERMOSO]** - Added Zone-Redundant Storage (ZRS) configuration to main.bicep to fulfill the fault tolerance optimization
* **[HERMOSO]** - Successfully provisioned the complete baseline infrastructure to Azure via Bicep
* **[QUITE]** - Designed and styled the CS Department Portal UI with external CSS and JavaScript files
* **[QUITE]** - Created static/ folder with style.css, script.js, and ccs.png logo
* **[QUITE]** - Updated templates/index.html with linked stylesheet and navigation script


### **Fixed**

* **[HERMOSO]** - Fixed Azure CLI Windows permission issue by overriding the local configuration directory path
* **[HERMOSO]** - Fixed policy block error: Pivoted deployment region from southeastasia to eastasia to comply with student subscription policy restrictions
* **[HERMOSO]** - Fixed Bicep validation error: Shortened the Storage Account name prefix to ensure the 24-character maximum length limit was not exceeded
* **[HERMOSO]** - Resolved Azure SQL password complexity policy requirements to allow successful deployment


## **[2026-05-13, 2:40PM] - Deployment**

### **Added**

* **[HERMOSO]** - Deployed the baseline Python Flask application to the App Service using Azure CLI ```az webapp up```
---
---
# **Sample lang tong sa baba, copy paste na lang kayo**
|

|

|

|

|

|

|

|

|

---

## ****[2026-05-13]** - Cost Report and Diagram Finalization**

### **Added**

* **[Groupmate 1 Name]** - Added pricing screenshots and cost optimization strategy (using basic tier SQL) to the cost report  
* **[Groupmate 2 Name]** - Created presentation slides for the architecture walkthrough and cost review  
* **[Your Name]** - Added Zone-Redundant Storage (ZRS) configuration to main.bicep to fulfill the fault tolerance optimization

### **Changed**

* **[Groupmate 2 Name]** - Updated architecture diagram to explicitly highlight the Autoscale and ZRS optimizations with red boundary lines

### **Fixed**

* **[Groupmate 1 Name]** - Fixed broken href links in the downloads.html template