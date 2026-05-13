@description('The location for all resources.')
param location string = resourceGroup().location

@description('The primary prefix for all resource names to ensure uniqueness.')
param projectPrefix string = 'csec3portal'

@description('The administrator username for the SQL Server.')
param sqlAdministratorLogin string

@description('The administrator password for the SQL Server. Must meet Azure complexity requirements.')
@secure()
param sqlAdministratorLoginPassword string

var storageAccountName = '${projectPrefix}store${uniqueString(resourceGroup().id)}'
var appServicePlanName = '${projectPrefix}-asp'
var webAppName = '${projectPrefix}-webapp-${uniqueString(resourceGroup().id)}'
var sqlServerName = '${projectPrefix}-sqlserver-${uniqueString(resourceGroup().id)}'
var sqlDatabaseName = '${projectPrefix}-sqldb'
var autoscaleName = '${projectPrefix}-autoscale'

// ==========================================
// 1. Storage Account (Optimization: Fault Tolerance via ZRS)
// ==========================================
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: substring(storageAccountName, 0, min(length(storageAccountName), 24))
  location: location
  sku: {
    name: 'Standard_ZRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false // Explicitly disabled to comply with strict tenant policies
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource container 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'downloads'
  properties: {
    publicAccess: 'None' // Container is now strictly private
  }
}

// ==========================================
// 2. Azure SQL Database (Baseline Data Resource)
// ==========================================
resource sqlServer 'Microsoft.Sql/servers@2023-05-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdministratorLogin
    administratorLoginPassword: sqlAdministratorLoginPassword
    version: '12.0'
  }
}

resource sqlFirewall 'Microsoft.Sql/servers/firewallRules@2023-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAllWindowsAzureIps'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-05-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
    capacity: 5
  }
}

// ==========================================
// 3. App Service Plan & Web App (Baseline Compute Resource)
// ==========================================
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'S1'
    tier: 'Standard'
    capacity: 2
  }
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2022-09-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: true
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'SQL_SERVER'
          value: sqlServer.properties.fullyQualifiedDomainName
        }
        {
          name: 'SQL_DATABASE'
          value: sqlDatabaseName
        }
        {
          name: 'SQL_USERNAME'
          value: sqlAdministratorLogin
        }
        {
          name: 'SQL_PASSWORD'
          value: sqlAdministratorLoginPassword
        }
        {
          name: 'STORAGE_CONNECTION_STRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${listKeys(storageAccount.id, storageAccount.apiVersion).keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
        }
        {
          name: 'STORAGE_CONTAINER_NAME'
          value: 'downloads'
        }
      ]
    }
    httpsOnly: true
  }
}

// ==========================================
// 4. Autoscale Settings (Optimization: Scalability)
// ==========================================
resource autoscaleSettings 'Microsoft.Insights/autoscalesettings@2022-10-01' = {
  name: autoscaleName
  location: location
  properties: {
    enabled: true
    targetResourceUri: appServicePlan.id
    profiles: [
      {
        name: 'DefaultProfile'
        capacity: {
          minimum: '2'
          maximum: '5'
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
              threshold: 70
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
              threshold: 30
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
  }
}

output webAppUrl string = webApp.properties.defaultHostName
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output storageAccountNameOut string = storageAccount.name
