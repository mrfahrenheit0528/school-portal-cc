# **CSEC 3 Final Project: Cloud Web Application Deployment**

**Scenario A: School Portal**

This repository contains the Infrastructure as Code (IaC) deployment scripts and application code for our Final Project in Cloud Computing. We utilized Azure Bicep to declaratively provision our cloud resources to ensure idempotency and repeatable deployments.

# Infrastructure Deployment Guide

This directory contains the Infrastructure as Code (IaC) configuration required to provision the Azure environment for the CSEC 3 School Portal.

## Prerequisites
1. Ensure the Azure CLI is installed on your Windows machine.
2. Authenticate to Azure by running `az login`.
3. Create a resource group if you haven't already:
   ```cmd
   az group create --name rg-csec3-final --location eastasia