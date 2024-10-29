from ninja import Schema
from datetime import date
from uuid import UUID

class TicketSchema(Schema):
    uuid: UUID
    createdTime: date
    lastModifiedTime: date
    status: str
    severity: str
    assignedTo: str
    title: str
    description: str