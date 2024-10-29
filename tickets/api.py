import requests
from ninja import Router
from datetime import datetime
from .models import Tickets
from .schema import TicketSchema
from apscheduler.schedulers.background import BackgroundScheduler

router = Router()

def fetch_tickets():
    url = "http://127.0.0.1:8000/api/tickets/"
    response = requests.get(url)
    return response.json()

def save():
    tickets = fetch_tickets()

    for ticket in tickets:
        uuid = ticket["object"]["name"]
        created_time = datetime.fromisoformat(ticket["object"]["properties"]["firstActivityTimeUtc"][:-1]).date()
        last_modified_time = datetime.fromisoformat(ticket["object"]["properties"]["lastModifiedTimeUtc"][:-1]).date()

        # Tenta atualizar ou criar um novo ticket
        ticket_obj, created = Tickets.objects.get_or_create(
            uuid=uuid,
            defaults={
                'createdTime': created_time,
                'lastModifiedTime': last_modified_time,
                'status': ticket["object"]["properties"].get("status", "Unknown"),
                'severity': ticket["object"]["properties"].get("severity", "Low"),
                'assignedTo': ticket["object"]["properties"]["owner"].get("assignedTo", "Unassigned"),
                'title': ticket["object"]["properties"].get("title", "No Title"),
                'description': ticket["object"]["properties"].get("description", "No Description"),
            }
        )

        if not created:
            ticket_obj.lastModifiedTime = last_modified_time
            ticket_obj.status = ticket["object"]["properties"].get("status", ticket_obj.status)
            ticket_obj.severity = ticket["object"]["properties"].get("severity", ticket_obj.severity)
            ticket_obj.assignedTo = ticket["object"]["properties"]["owner"].get("assignedTo", ticket_obj.assignedTo)
            ticket_obj.title = ticket["object"]["properties"].get("title", ticket_obj.title)
            ticket_obj.description = ticket["object"]["properties"].get("description", ticket_obj.description)
            ticket_obj.save(update_fields=["lastModifiedTime", "status", "severity", "assignedTo", "title", "description"])
        print("Objeto criado")

def initialize_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(save, 'interval', seconds=300)
    scheduler.start()

save()

@router.get("/", response=list[TicketSchema])
def get_tickets(request, order: str = "recent", status: str = None, severity: str = None):
    tickets = Tickets.objects.all()

    if order == "recent":
        tickets = tickets.order_by("-createdTime")
    elif order == "oldest":
        tickets = tickets.order_by("createdTime")

    if status:
        tickets = tickets.filter(status=status)

    if severity:
        tickets = tickets.filter(severity=severity)

    return tickets
