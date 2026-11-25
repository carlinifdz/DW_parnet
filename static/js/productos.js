"use strict";


document.addEventListener("DOMContentLoaded", function () {

    inicializarFiltroProductos();

});


/* =========================================
   FILTRO POR CATEGORIA DE PRODUCTOS
   ========================================= */

function inicializarFiltroProductos() {

    const formulario = document.getElementById(
        "formulario-buscador-productos"
    );

    const selectorCategoria = document.getElementById(
        "filtro-categoria-producto"
    );

    if (!formulario || !selectorCategoria) {
        return;
    }

    selectorCategoria.addEventListener("change", function () {

        formulario.submit();

    });

}
