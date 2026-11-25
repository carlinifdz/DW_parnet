"use strict";


document.addEventListener("DOMContentLoaded", function () {

    inicializarConfirmacionesEliminar();

});


/* =========================================
   CONFIRMACION DE ACCIONES DESTRUCTIVAS
   ========================================= */

function inicializarConfirmacionesEliminar() {

    const formularios = document.querySelectorAll(
        "form[data-confirmar-eliminacion]"
    );

    formularios.forEach(function (formulario) {

        formulario.addEventListener("submit", function (evento) {

            const mensaje = formulario.dataset.confirmarEliminacion
                || "¿Confirmas que deseas eliminar este registro?";

            if (!window.confirm(mensaje)) {
                evento.preventDefault();
            }

        });

    });

}
