/* =========================================
   PARNET INGENIERIA
   Interacciones de formularios de comunicación
   ========================================= */

document.addEventListener("DOMContentLoaded", function () {
    const areasTexto = document.querySelectorAll("textarea[data-contador-max]");

    areasTexto.forEach(function (textarea) {
        const maximo = parseInt(textarea.getAttribute("data-contador-max"), 10) || 2000;
        const contenedor = textarea.parentElement.querySelector(".contador-caracteres");

        if (!contenedor) {
            return;
        }

        const actualizarContador = function () {
            const actual = textarea.value.length;
            contenedor.textContent = actual + " / " + maximo + " caracteres";
        };

        textarea.addEventListener("input", actualizarContador);
        actualizarContador();
    });

    const formularios = document.querySelectorAll(".formulario-comunicacion");

    formularios.forEach(function (formulario) {
        formulario.addEventListener("submit", function () {
            const boton = formulario.querySelector("button[type='submit']");
            if (boton && !boton.disabled) {
                boton.dataset.textoOriginal = boton.innerHTML;
                boton.disabled = true;
            }
        });
    });
});
