@description('Location for all resources.')
param location string = resourceGroup().location

@description('A unique suffix to ensure resource names are globally unique.')
param appNameSuffix string = uniqueString(resourceGroup().id)

@description('The administrator username for the SQL Server.')
param sqlAdminLogin string = 'adminuser'

@description('The administrator password for the SQL Server. Must be at least 8 characters.')
@secure() // This ensures the password is never logged or displayed in Azure Portal
param sqlAdminPassword string

// ---------------------------------------------------------------------------
// 1. STORAGE ACCOUNT (Optimization 1: Fault Tolerance via ZRS)
// ---------------------------------------------------------------------------
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stportal${appNameSuffix}' // Shortened prefix to stay under 24 character limit
  location: location
  sku: {
    name: 'Standard_ZRS' // Cloud Optimization: Zone-Redundant Storage
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
  }
}

// ---------------------------------------------------------------------------
// 2. AZURE SQL DATABASE (Private Backend)
// ---------------------------------------------------------------------------
resource sqlServer 'Microsoft.Sql/servers@2023-05-01-preview' = {
  name: 'sql-schoolportal-${appNameSuffix}'
  location: location
  properties: {
    administratorLogin: sqlAdminLogin
    administratorLoginPassword: sqlAdminPassword
    version: '12.0'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-05-01-preview' = {
  parent: sqlServer
  name: 'db-announcements'
  location: location
  sku: {
    name: 'Basic' // Using the cheapest tier to protect your student credits
  }
}

// Allow Azure services (like our App Service) to access the SQL server
resource sqlFirewallRule 'Microsoft.Sql/servers/firewallRules@2023-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAllWindowsAzureIps'
  properties: {
    endIpAddress: '0.0.0.0'
    startIpAddress: '0.0.0.0'
  }
}

// ---------------------------------------------------------------------------
// 3. APP SERVICE (Compute Baseline)
// ---------------------------------------------------------------------------
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'asp-schoolportal-${appNameSuffix}'
  location: location
  sku: {
    name: 'S1' // Standard tier required to enable Autoscaling
    capacity: 2 // Rubric requirement: 2+ instances for baseline
  }
  properties: {
    reserved: true // Required for Linux App Services
  }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: 'app-schoolportal-${appNameSuffix}'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11' // Setting up the environment for your Flask App
      alwaysOn: true
    }
  }
}

// ---------------------------------------------------------------------------
// 4. AUTOSCALE RULES (Optimization 2: Scalability)
// ---------------------------------------------------------------------------
resource autoscaleSetting 'Microsoft.Insights/autoscalesettings@2022-10-01' = {
  name: 'autoscale-schoolportal-${appNameSuffix}'
  location: location
  properties: {
    profiles: [
      {
        name: 'DefaultAutoscaleProfile'
        capacity: {
          minimum: '2'
          maximum: '4' // Automatically scale up to 4 instances if under heavy load
          default: '2'
        }
        rules: [
          {
            metricTrigger: {
              metricName: 'CpuPercentage'
              metricResourceUri: appServicePlan.id
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT5M'
              timeAggregation: 'Average'
              operator: 'GreaterThan'
              threshold: 70 // Trigger if CPU exceeds 70%
            }
            scaleAction: {
              direction: 'Increase'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT5M'
            }
          }
          {
            metricTrigger: {
              metricName: 'CpuPercentage'
              metricResourceUri: appServicePlan.id
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT5M'
              timeAggregation: 'Average'
              operator: 'LessThan'
              threshold: 30 // Scale back down if CPU drops below 30%
            }
            scaleAction: {
              direction: 'Decrease'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT5M'
            }
          }
        ]
      }
    ]
    targetResourceUri: appServicePlan.id
  }
}
