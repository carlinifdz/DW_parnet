from django.db import models


class Sugerencia(models.Model):
    id_sugerencia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(max_length=150)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "sugerencias"
        verbose_name = "Sugerencia"
        verbose_name_plural = "Sugerencias"
        ordering = ["-fecha_registro", "-id_sugerencia"]

    def __str__(self):
        return f"Sugerencia de {self.nombre}"