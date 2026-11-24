from django.db import models

class Noticia(models.Model):

    id_noticia = models.AutoField(primary_key=True)

    titulo = models.CharField(max_length=200)

    resumen = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    contenido = models.TextField()

    imagen = models.ImageField(
        upload_to="noticias/",
        max_length=255,
        blank=True,
        null=True
    )

    fecha_publicacion = models.DateTimeField(
        auto_now_add=True
    )

    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "noticias"

        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"

        ordering = [
            "-fecha_publicacion",
            "-id_noticia"
        ]

    def __str__(self):
        return self.titulo

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)

    nombre = models.CharField(
        max_length=150
    )

    logo = models.ImageField(
        upload_to="clientes/",
        max_length=255
    )

    sitio_web = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    activo = models.BooleanField(
        default=True
    )

    class Meta:
        managed = False
        db_table = "clientes"

        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

        ordering = ["nombre", "id_cliente"]

    def __str__(self):
        return self.nombre


class Slider(models.Model):
    id_slider = models.AutoField(primary_key=True)

    titulo = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    descripcion = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    imagen = models.ImageField(
        upload_to="slider/",
        max_length=255
)

    enlace = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "slider"

        verbose_name = "Imagen del slider"
        verbose_name_plural = "Imágenes del slider"

        ordering = ["orden", "id_slider"]

    def __str__(self):
        return self.titulo or f"Slider {self.id_slider}"


class Visita(models.Model):
    id_visita = models.BigAutoField(primary_key=True)
    pagina = models.CharField(max_length=255)
    fecha_visita = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "visitas"
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        ordering = ["-fecha_visita"]

    def __str__(self):
        return f"{self.pagina} - {self.fecha_visita}"


class UsuarioConectado(models.Model):
    id_sesion = models.CharField(
        max_length=64,
        primary_key=True
    )

    ultima_actividad = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "usuarios_conectados"
        verbose_name = "Usuario conectado"
        verbose_name_plural = "Usuarios conectados"

    def __str__(self):
        return self.id_sesion