from ninja import Router
import uuid
import random
import json
from datetime import datetime, timedelta
import os

router = Router()
incidents = []

def random_uuid():
    return str(uuid.uuid4())

def random_date():
    now = datetime.utcnow()
    random_past_time = now - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return random_past_time.isoformat() + "Z"

def generate_random_incident(incident_number):
    incident = {
        "eventUniqueId": random_uuid(),
        "objectSchemaType": "Incident",
        "objectEventType": "Create",
        "workspaceInfo": {
            "SubscriptionId": "556ac391-e8b4-4a9e-8f05-024974300f27",
            "ResourceGroupName": "rg-siem",
            "WorkspaceName": "sentinelhml"
        },
        "workspaceId": "8d300aff-d535-4430-9eef-3046965c48cf",
        "object": {
            "id": f"/subscriptions/556ac391-e8b4-4a9e-8f05-024974300f27/resourceGroups/rg-siem/providers/Microsoft.OperationalInsights/workspaces/sentinelhml/providers/Microsoft.SecurityInsights/Incidents/{random_uuid()}",
            "name": random_uuid(),
            "etag": f"\"{random_uuid()}\"",
            "type": "Microsoft.SecurityInsights/Incidents",
            "properties": {
                "title": f"Incidente Teste - {random.choice(["Porto Digital", "BBTS", "Banco do Brasil"])}",
                "description": f"{random.choice(["Sistema caiu", "Erro de conexão", "Falha no login"])}",
                "severity": f"{random.choice(["High", "Medium", "Low"])}",
                "status": f"{random.choice(["New", "In Progress", "Resolved"])}",
                "owner": {
                    "objectId": random_uuid(),
                    "email": "ext-teste@bbts.com.br",
                    "assignedTo": f"{random.choice(["Lohhan Guilherme", "Arthur Coelho", "Lucas Kauã"])}",
                    "userPrincipalName": "ext-teste@bbts.com.br",
                },
                "labels": [],
                "firstActivityTimeUtc": random_date(),
                "lastActivityTimeUtc": random_date(),
                "lastModifiedTimeUtc": random_date(),
                "createdTimeUtc": random_date(),
                "incidentNumber": str(incident_number),
                "additionalData": {
                    "alertsCount": 0,
                    "bookmarksCount": 0,
                    "commentsCount": 0,
                    "alertProductNames": [],
                    "tactics": [],
                    "techniques": []
                },
                "relatedAnalyticRuleIds": [],
                "incidentUrl": "https://portal.azure.com/#asset/Microsoft_Azure_Security_Insights/Incident/subscriptions/556ac391-e8b4-4a9e-8f05-024974300f27/resourceGroups/rg-siem/providers/Microsoft.OperationalInsights/workspaces/sentinelhml/providers/Microsoft.SecurityInsights/Incidents/22d80f17-3e6d-49a7-8cc4-ad88fc708c95",
                "providerName": "Azure Sentinel",
                "providerIncidentId": str(incident_number),
                "alerts": [],
                "bookmarks": [],
                "relatedEntities": [],
                "comments": []
            }
        }
    }
    return incident

def generate_incidents(n):
    for i in range(1,n+1):
        incidents.append(generate_random_incident(i))
    return incidents

def save(incidents):
    filename = "incidents.json"
    with open (filename, "w") as file:
        json.dump(incidents, file)

save(generate_incidents(10))
my_incidents_path = os.path.join("..", "incidents.json")
        
@router.get("/")     
def all_tickets(request):
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Diretório atual do arquivo
    incidents_path = os.path.join(current_dir, "../incidents.json")  # Caminho completo

    with open(incidents_path, "r") as file:
        all_incidents = json.load(file)
        return all_incidents