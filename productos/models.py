from django.db import models


class CategoriaProducto(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "categorias_productos"
        verbose_name = "Categoría de producto"
        verbose_name_plural = "Categorías de productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)

    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        db_column="id_categoria",
        related_name="productos"
    )

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)

    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    stock = models.IntegerField(default=0)

    imagen = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    ficha_tecnica = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "productos"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    @property
    def estatus(self):
        if self.stock > 0:
            return "Existencia"
        return "Agotado"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"