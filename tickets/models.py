from django.db import models
import uuid

class Tickets(models.Model):
   uuid = models.UUIDField(
      primary_key=True,
      default=uuid.uuid4,  
      editable=False,
      db_index=True,
      unique=True
   )

   createdTime = models.DateField(
      verbose_name="Data de Criação",
      null=False,  
      blank=False
   )

   lastModifiedTime = models.DateField(
      verbose_name="Última Modificação",
      null=False,
      blank=False
   )

   status = models.CharField(
      max_length=20,
      verbose_name="Status",
      help_text="Status atual do ticket (e.g., aberto, fechado)."
   )

   severity = models.CharField(
      max_length=20,
      verbose_name="Gravidade",
      help_text="Nível de gravidade do ticket (e.g., baixo, médio, alto)."
   )

   assignedTo = models.CharField(
      max_length=80,
      verbose_name="Atribuído a",
      help_text="Nome da pessoa ou equipe responsável pelo ticket."
   )

   title = models.CharField(
      max_length=80,
      verbose_name="Título",
      help_text="Título breve do ticket."
   )

   description = models.CharField(
      max_length=255,  
      verbose_name="Descrição",
      help_text="Descrição detalhada do ticket."
   )

   def __str__(self):
      return f"{self.title} - {self.status} - {self.severity}"

