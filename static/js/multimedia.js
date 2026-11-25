/* =========================================
   PARNET INGENIERIA
   Control del reproductor multimedia
   ========================================= */

document.addEventListener("DOMContentLoaded", function () {
    const reproductor = document.getElementById("reproductor-parnet");

    if (!reproductor) {
        return;
    }

    reproductor.addEventListener("error", function () {
        reproductor.setAttribute(
            "aria-label",
            "No fue posible cargar el recurso de video institucional."
        );
    });
});
