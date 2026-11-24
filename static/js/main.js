"use strict";

document.addEventListener("DOMContentLoaded", function () {

    inicializarMenuMovil();

    console.log("ParNet Ingeniería iniciado correctamente.");

});


/* =========================================
   Navegacion movil
   ========================================= */

function inicializarMenuMovil() {

    const menu = document.getElementById("menuParnet");

    if (!menu || typeof bootstrap === "undefined") {
        return;
    }

    const enlaces = menu.querySelectorAll(".nav-link");

    enlaces.forEach(function (enlace) {

        enlace.addEventListener("click", function () {

            const esMovil = window.matchMedia(
                "(max-width: 991.98px)"
            ).matches;

            if (esMovil && menu.classList.contains("show")) {

                const instancia = bootstrap.Collapse
                    .getOrCreateInstance(menu, {
                        toggle: false
                    });

                instancia.hide();

            }

        });

    });

}