"use strict";


document.addEventListener("DOMContentLoaded", function () {

    inicializarContadores();

});


/* =========================================
   INICIALIZAR CONTADORES
   ========================================= */

function inicializarContadores() {

    const contenedor = document.getElementById(
        "contadores-parnet"
    );

    if (!contenedor) {
        return;
    }

    const url = contenedor.dataset.apiUrl;

    const csrf = contenedor.querySelector(
        'input[name="csrfmiddlewaretoken"]'
    );

    if (!url || !csrf) {
        return;
    }

    const token = csrf.value;

    let actualizando = false;


    async function consultarEstadisticas() {

        // No actualizar si la pestana esta oculta

        if (document.hidden || actualizando) {
            return;
        }

        actualizando = true;

        try {

            const respuesta = await fetch(url, {

                method: "POST",

                credentials: "same-origin",

                cache: "no-store",

                headers: {

                    "X-CSRFToken": token,

                    "Accept": "application/json"

                }

            });

            if (!respuesta.ok) {

                throw new Error(
                    `Error HTTP: ${respuesta.status}`
                );

            }

            const datos = await respuesta.json();

            actualizarUsuarios(
                datos.usuarios_conectados
            );

            actualizarVisitas(
                datos.total_visitas
            );

        } catch (error) {

            console.warn(
                "No fue posible actualizar los contadores:",
                error
            );

        } finally {

            actualizando = false;

        }

    }


    // Primera consulta

    consultarEstadisticas();


    // Actualizar cada 30 segundos

    setInterval(
        consultarEstadisticas,
        30000
    );


    // Actualizar al regresar a la pestana

    document.addEventListener(
        "visibilitychange",
        function () {

            if (!document.hidden) {

                consultarEstadisticas();

            }

        }
    );

}


/* =========================================
   ACTUALIZAR USUARIOS CONECTADOS
   ========================================= */

function actualizarUsuarios(total) {

    const elemento = document.getElementById(
        "usuarios-conectados"
    );

    if (!elemento) {
        return;
    }

    if (!Number.isSafeInteger(total) || total < 0) {
        return;
    }

    elemento.textContent = total;

}


/* =========================================
   ACTUALIZAR CONTADOR DIGITAL DE VISITAS
   ========================================= */

function actualizarVisitas(total) {

    const contador = document.getElementById(
        "contador-visitas"
    );

    if (!contador) {
        return;
    }

    if (!Number.isSafeInteger(total) || total < 0) {
        return;
    }

    const digitos = String(total).padStart(
        5,
        "0"
    );

    const fragmento = document.createDocumentFragment();

    for (const digito of digitos) {

        const elemento = document.createElement(
            "span"
        );

        elemento.className = "contador-digito";

        elemento.setAttribute(
            "aria-hidden",
            "true"
        );

        elemento.textContent = digito;

        fragmento.appendChild(elemento);

    }

    contador.replaceChildren(fragmento);

    contador.setAttribute(
        "aria-label",
        `${total} visitas`
    );

}