from ninja import Schema
from datetime import datetime
from uuid import UUID

class TicketSchema(Schema):
    uuid: UUID
    createdTime: datetime
    lastModifiedTime: datetime
    status: str
    severity: str
    assignedTo: str
    title: str
    description: str
    incidentURL: str
    providerName: str

class DashboardResponse(Schema):
    new: int
    in_progress: int
    resolved: int
    total: int