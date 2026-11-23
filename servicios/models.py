from django.db import models


class AreaServicio(models.Model):
    id_area = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "areas_servicios"
        verbose_name = "Área de servicio"
        verbose_name_plural = "Áreas de servicios"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class SolicitudServicio(models.Model):

    class Estatus(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        EN_PROCESO = "En proceso", "En proceso"
        ATENDIDA = "Atendida", "Atendida"
        CANCELADA = "Cancelada", "Cancelada"

    id_solicitud = models.AutoField(primary_key=True)

    area = models.ForeignKey(
        AreaServicio,
        on_delete=models.PROTECT,
        db_column="id_area",
        related_name="solicitudes"
    )

    nombre = models.CharField(max_length=150)
    empresa = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    correo = models.EmailField(max_length=150)

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    detalle = models.TextField()

    estatus = models.CharField(
        max_length=10,
        choices=Estatus.choices,
        default=Estatus.PENDIENTE
    )

    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "solicitudes_servicios"
        verbose_name = "Solicitud de servicio"
        verbose_name_plural = "Solicitudes de servicios"
        ordering = ["-fecha_solicitud", "-id_solicitud"]

    def __str__(self):
        return f"{self.nombre} - {self.area.nombre}"