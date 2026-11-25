from django.db import models


class ReporteInventarioVista(models.Model):
    """
    Modelo ORM asociado a la vista SQL `vw_inventario` de MySQL.
    """

    id_producto = models.IntegerField(primary_key=True)
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=100)
    marca = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    modelo = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    stock = models.IntegerField()
    activo = models.BooleanField(default=True)
    estatus = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = "vw_inventario"
        verbose_name = "Registro de inventario"
        verbose_name_plural = "Registros de inventario"
        ordering = ["nombre", "id_producto"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.estatus})"


class DashboardServiciosVista(models.Model):
    """
    Modelo ORM asociado a la vista SQL `vw_dashboard_servicios` de MySQL.
    """

    id_area = models.IntegerField(primary_key=True)
    servicio = models.CharField(max_length=100)
    total = models.IntegerField()

    class Meta:
        managed = False
        db_table = "vw_dashboard_servicios"
        verbose_name = "Indicador de servicio"
        verbose_name_plural = "Indicadores de servicios"
        ordering = ["-total", "servicio"]

    def __str__(self):
        return f"{self.servicio}: {self.total}"


class DashboardProductosVista(models.Model):
    """
    Modelo ORM asociado a la vista SQL `vw_dashboard_productos` de MySQL.
    """

    id_categoria = models.IntegerField(primary_key=True)
    categoria = models.CharField(max_length=100)
    total = models.IntegerField()

    class Meta:
        managed = False
        db_table = "vw_dashboard_productos"
        verbose_name = "Indicador de categoría"
        verbose_name_plural = "Indicadores de categorías"
        ordering = ["-total", "categoria"]

    def __str__(self):
        return f"{self.categoria}: {self.total}"
