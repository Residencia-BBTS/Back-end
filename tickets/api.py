from ninja import Router
from datetime import datetime, timedelta, timezone
from .models import Tickets
from .schema import TicketSchema, DashboardResponse
from django.db.models import Count

router = Router()

@router.get("/", response=list[TicketSchema])
def get_tickets(request, order: str = "recent", status: str = None, severity: str = None, providerName: str = None, days: int = None):    
    tickets = Tickets.objects.all()

    if days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        tickets = tickets.filter(createdTime__range=(start_date, end_date))

    if order == "recent":
        tickets = tickets.order_by("-createdTime")
    elif order == "oldest":
        tickets = tickets.order_by("createdTime")

    if status:
        tickets = tickets.filter(status=status)

    if severity:
        tickets = tickets.filter(severity=severity)

    if providerName:
        tickets = tickets.filter(providerName=providerName)

    return tickets

@router.post("/new_incidents")
def new_incidents(request, tickets: list[dict]):
    for ticket in tickets:
        try:
            ticket_data = {
                "uuid": ticket["object"]["name"],
                "createdTime": datetime.fromisoformat(ticket["object"]["properties"]["firstActivityTimeUtc"][:-1]).replace(tzinfo=timezone.utc),
                "lastModifiedTime": datetime.fromisoformat(ticket["object"]["properties"]["lastModifiedTimeUtc"][:-1]).replace(tzinfo=timezone.utc),
                "status": ticket["object"]["properties"].get("status", "Unknown"),
                "severity": ticket["object"]["properties"].get("severity", "Low"),
                "assignedTo": ticket["object"]["properties"]["owner"].get("assignedTo", "Unassigned"),
                "title": ticket["object"]["properties"].get("title", "No Title"),
                "description": ticket["object"]["properties"].get("description", "No Description"),
                "incidentURL": ticket["object"]["properties"].get("incidentUrl", "URL not Found"),
                "providerName": ticket["object"]["properties"].get("providerName", "No provider"),
            }

            ticket_schema = TicketSchema(**ticket_data)

            ticket_obj, created = Tickets.objects.get_or_create(
                uuid=ticket_schema.uuid,
                defaults={
                    'createdTime': ticket_schema.createdTime,
                    'lastModifiedTime': ticket_schema.lastModifiedTime,
                    'status': ticket_schema.status,
                    'severity': ticket_schema.severity,
                    'assignedTo': ticket_schema.assignedTo,
                    'title': ticket_schema.title,
                    'description': ticket_schema.description,
                    'incidentURL': ticket_schema.incidentURL,
                    'providerName': ticket_schema.providerName,
                }
            )

            if not created:
                ticket_obj.lastModifiedTime = ticket_schema.lastModifiedTime
                ticket_obj.status = ticket_schema.status
                ticket_obj.severity = ticket_schema.severity
                ticket_obj.assignedTo = ticket_schema.assignedTo
                ticket_obj.title = ticket_schema.title
                ticket_obj.description = ticket_schema.description
                ticket_obj.save(update_fields=["lastModifiedTime", "status", "severity", "assignedTo", "title", "description", "incidentURL", "providerName"])

            print("Objeto criado ou atualizado:", ticket_obj)

        except Exception as e:
            print(f"Erro ao processar o ticket {ticket_schema.uuid}: {e}")

    return {"message": "Tickets processed successfully"}


@router.get("/dashboard", response=DashboardResponse)
def get_dashboard(request, days: int=7):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    ticket_counts = (
        Tickets.objects.filter(createdTime__range=(start_date, end_date)).values("status").annotate(count=Count("uuid"))
    )
    total_count = Tickets.objects.filter(createdTime__range=(start_date, end_date)).count()

    new_count = in_progress_count = resolved_count = 0

    for ticket in ticket_counts:
        if ticket["status"] == "New":
            new_count = ticket["count"]
        elif ticket["status"] == "In Progress":
            in_progress_count = ticket["count"]
        elif ticket["status"] == "Resolved":
            resolved_count = ticket["count"]
        
    return {"new": new_count, "in_progress": in_progress_count, "resolved": resolved_count, "total": total_count}
