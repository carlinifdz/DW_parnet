from pathlib import Path
from uuid import uuid4

from django import forms
from django.core.files.storage import default_storage

from core.models import Cliente, Noticia, Slider
from productos.models import CategoriaProducto, Producto
from servicios.models import SolicitudServicio


class ProductoForm(forms.ModelForm):
    """
    Formulario administrativo para el registro y edición de productos,
    permitiendo tanto ruta de imagen como subida opcional de archivo.
    """

    archivo_imagen = forms.ImageField(
        label="Subir archivo de imagen (opcional)",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "campo-parnet",
                "accept": "image/*",
            }
        ),
    )

    class Meta:
        model = Producto
        fields = [
            "categoria",
            "codigo",
            "nombre",
            "descripcion",
            "marca",
            "modelo",
            "precio",
            "stock",
            "imagen",
            "ficha_tecnica",
            "activo",
        ]
        labels = {
            "categoria": "Categoría",
            "codigo": "Código del producto",
            "nombre": "Nombre del producto",
            "descripcion": "Descripción",
            "marca": "Marca",
            "modelo": "Modelo",
            "precio": "Precio unitario (MXN)",
            "stock": "Existencias (Stock)",
            "imagen": "Ruta de imagen (ej. productos/equipo.jpg)",
            "ficha_tecnica": "Especificaciones de ficha técnica",
            "activo": "Producto activo en catálogo",
        }
        widgets = {
            "categoria": forms.Select(attrs={"class": "campo-parnet"}),
            "codigo": forms.TextInput(
                attrs={
                    "class": "campo-parnet",
                    "placeholder": "Ej. PROD-006",
                }
            ),
            "nombre": forms.TextInput(
                attrs={
                    "class": "campo-parnet",
                    "placeholder": "Nombre comercial o técnico",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={"class": "campo-parnet", "rows": 3}
            ),
            "marca": forms.TextInput(attrs={"class": "campo-parnet"}),
            "modelo": forms.TextInput(attrs={"class": "campo-parnet"}),
            "precio": forms.NumberInput(
                attrs={
                    "class": "campo-parnet",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "stock": forms.NumberInput(
                attrs={"class": "campo-parnet", "min": "0"}
            ),
            "imagen": forms.TextInput(
                attrs={
                    "class": "campo-parnet",
                    "placeholder": "productos/imagen.jpg",
                }
            ),
            "ficha_tecnica": forms.Textarea(
                attrs={"class": "campo-parnet", "rows": 4}
            ),
            "activo": forms.CheckboxInput(
                attrs={"class": "checkbox-parnet"}
            ),
        }

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is not None and precio < 0:
            raise forms.ValidationError(
                "El precio del producto no puede ser negativo."
            )
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is not None and stock < 0:
            raise forms.ValidationError(
                "El stock del producto no puede ser negativo."
            )
        return stock

    def save(self, commit=True):
        instancia = super().save(commit=False)
        archivo = self.cleaned_data.get("archivo_imagen")

        if archivo:
            ext = Path(archivo.name).suffix.lower() or ".jpg"
            nombre_seguro = f"productos/prod_{uuid4().hex[:10]}{ext}"
            ruta_guardada = default_storage.save(
                nombre_seguro,
                archivo
            )
            instancia.imagen = ruta_guardada.replace("\\", "/")

        if commit:
            instancia.save()
        return instancia


class CategoriaProductoForm(forms.ModelForm):
    """
    Formulario administrativo para crear y editar categorías de productos.
    """

    class Meta:
        model = CategoriaProducto
        fields = [
            "nombre",
            "descripcion",
            "activo",
        ]
        labels = {
            "nombre": "Nombre de la categoría",
            "descripcion": "Descripción",
            "activo": "Categoría activa",
        }
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "campo-parnet",
                    "placeholder": "Ej. Redes industriales",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={"class": "campo-parnet", "rows": 3}
            ),
            "activo": forms.CheckboxInput(
                attrs={"class": "checkbox-parnet"}
            ),
        }


class SolicitudServicioEstatusForm(forms.ModelForm):
    """
    Formulario administrativo para actualizar el estatus de una solicitud de servicio.
    """

    class Meta:
        model = SolicitudServicio
        fields = ["estatus"]
        labels = {
            "estatus": "Estatus de atención",
        }
        widgets = {
            "estatus": forms.Select(attrs={"class": "campo-parnet"}),
        }


class NoticiaForm(forms.ModelForm):
    """
    Formulario administrativo para crear y actualizar noticias.
    """

    class Meta:
        model = Noticia
        fields = [
            "titulo",
            "resumen",
            "contenido",
            "imagen",
            "activo",
        ]
        labels = {
            "titulo": "Título de la noticia",
            "resumen": "Resumen breve",
            "contenido": "Contenido completo",
            "imagen": "Imagen de la noticia",
            "activo": "Noticia publicada / activa",
        }
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "campo-parnet"}),
            "resumen": forms.TextInput(attrs={"class": "campo-parnet"}),
            "contenido": forms.Textarea(
                attrs={"class": "campo-parnet", "rows": 5}
            ),
            "imagen": forms.ClearableFileInput(
                attrs={"class": "campo-parnet"}
            ),
            "activo": forms.CheckboxInput(
                attrs={"class": "checkbox-parnet"}
            ),
        }


class ClienteForm(forms.ModelForm):
    """
    Formulario administrativo para crear y actualizar clientes.
    """

    class Meta:
        model = Cliente
        fields = [
            "nombre",
            "logo",
            "sitio_web",
            "descripcion",
            "activo",
        ]
        labels = {
            "nombre": "Nombre de la empresa / cliente",
            "logo": "Logotipo",
            "sitio_web": "Sitio web (URL)",
            "descripcion": "Descripción",
            "activo": "Cliente activo",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "campo-parnet"}),
            "logo": forms.ClearableFileInput(
                attrs={"class": "campo-parnet"}
            ),
            "sitio_web": forms.URLInput(
                attrs={
                    "class": "campo-parnet",
                    "placeholder": "https://ejemplo.com",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={"class": "campo-parnet", "rows": 3}
            ),
            "activo": forms.CheckboxInput(
                attrs={"class": "checkbox-parnet"}
            ),
        }


class SliderForm(forms.ModelForm):
    """
    Formulario administrativo para crear y actualizar imágenes del slider.
    """

    class Meta:
        model = Slider
        fields = [
            "titulo",
            "descripcion",
            "imagen",
            "enlace",
            "orden",
            "activo",
        ]
        labels = {
            "titulo": "Título del banner",
            "descripcion": "Descripción corta",
            "imagen": "Imagen del slider",
            "enlace": "Enlace de destino",
            "orden": "Orden de aparición",
            "activo": "Banner activo",
        }
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "campo-parnet"}),
            "descripcion": forms.TextInput(
                attrs={"class": "campo-parnet"}
            ),
            "imagen": forms.ClearableFileInput(
                attrs={"class": "campo-parnet"}
            ),
            "enlace": forms.TextInput(
                attrs={
                    "class": "campo-parnet",
                    "placeholder": "/servicios/",
                }
            ),
            "orden": forms.NumberInput(
                attrs={"class": "campo-parnet", "min": "0"}
            ),
            "activo": forms.CheckboxInput(
                attrs={"class": "checkbox-parnet"}
            ),
        }
