from ninja import Router
import uuid
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from .models import Tickets
from .schema import TicketSchema

router = Router()
incidents_cache = []

# função de gerar uuid
def random_uuid():
    return str(uuid.uuid4())

# função de gerar uma data aleatória
def random_date():
    now = datetime.utcnow()
    random_past_time = now - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return random_past_time.isoformat() + "Z"

# função de gerar um incidente aleatório
def generate_random_incident(incident_number):
    incident = {}
    incident["object"] = {
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

# função de adicionar os incidentes aleatórios à uma lista
def generate_incidents(n):
    for i in range(1,n+1):
        incidents_cache.append(generate_random_incident(i))
    return incidents_cache

def save(incidents):
    for incident in incidents:
        uuid = incident["object"]["object"]["name"]  
        created_time = datetime.fromisoformat(incident["object"]["object"]["properties"]["firstActivityTimeUtc"][:-1]).date()
        last_modified_time = datetime.fromisoformat(incident["object"]["object"]["properties"]["lastModifiedTimeUtc"][:-1]).date()

        # tentando atualizar ou criar um novo ticket
        ticket, created = Tickets.objects.get_or_create(
            uuid=uuid,
            defaults={
                'createdTime': created_time,
                'lastModifiedTime': last_modified_time,
                'status': incident["object"]["object"]["properties"].get("status", "Unknown"),
                'severity': incident["object"]["object"]["properties"].get("severity", "Low"),
                'assignedTo': incident["object"]["object"]["properties"]["owner"].get("assignedTo", "Unassigned"),
                'title': incident["object"]["object"]["properties"].get("title", "No Title"),
                'description': incident["object"]["object"]["properties"].get("description", "No Description"),
            }
        )

        if not created:
            ticket.lastModifiedTime = last_modified_time
            ticket.status = incident["object"]["object"]["properties"].get("status", ticket.status)
            ticket.severity = incident["object"]["object"]["properties"].get("severity", ticket.severity)
            ticket.assignedTo = incident["object"]["object"]["properties"]["owner"].get("assignedTo", ticket.assignedTo)
            ticket.title = incident["object"]["object"]["properties"].get("title", ticket.title)
            ticket.description = incident["object"]["object"]["properties"].get("description", ticket.description)
            ticket.save()  

save(generate_incidents(4))

def update_incidents():
    incidents_cache.append(generate_random_incident(random.randint(2, 9999)))
    save(incidents_cache)

def initialize_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_incidents, 'interval', seconds=600)
    scheduler.start()

@router.get("/", response=list[TicketSchema])     
def get_tickets(request, order: str="recent", status: str=None, severity: str=None):
    tickets = Tickets.objects.all()

    if order == "recent":
        tickets = tickets.order_by("-createdTime")
    elif order == "oldest":
        tickets = tickets.order_by("createdTime")

    if status == "New":
        tickets = tickets.filter(status="New")
    elif status == "In Progress":
        tickets = tickets.filter(status="In Progress")
    elif status == "Resolved":
        tickets = tickets.filter(status="Resolved")

    if severity == "High":
        tickets = tickets.filter(severity="High")
    elif severity == "Medium":
        tickets = tickets.filter(severity="Medium")
    elif severity == "Low":
        tickets = tickets.filter(severity="Low")

    return tickets