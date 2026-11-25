from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import LoginAdministradorForm
from .permisos import es_administrador


class IniciarSesionView(LoginView):
    """
    Vista basada en clase (POO) para el inicio de sesión de administradores.
    """

    template_name = "gestion/autenticacion/iniciar_sesion.html"
    authentication_form = LoginAdministradorForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        usuario = getattr(request, "user", None)
        if usuario and usuario.is_authenticated and not es_administrador(usuario):
            self.redirect_authenticated_user = False
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        usuario = form.get_user()
        nombre = usuario.get_full_name() or usuario.get_username()
        messages.success(
            self.request,
            f"Bienvenido al sistema administrativo, {nombre}.",
        )
        return respuesta

    def form_invalid(self, form):
        messages.error(
            self.request,
            "No fue posible iniciar sesión. Revisa los datos ingresados.",
        )
        return super().form_invalid(form)


class CerrarSesionView(LogoutView):
    """
    Vista basada en clase (POO) para cerrar la sesión administrativa
    de forma segura mediante solicitud POST.
    """

    next_page = reverse_lazy("autenticacion:iniciar_sesion")
    http_method_names = ["post", "options"]

    def post(self, request, *args, **kwargs):
        messages.info(
            request,
            "Has cerrado tu sesión administrativa correctamente.",
        )
        return super().post(request, *args, **kwargs)
