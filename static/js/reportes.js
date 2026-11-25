"use strict";


document.addEventListener("DOMContentLoaded", function () {

    inicializarGraficasReportes();

});


/* =========================================
   RENDERIZADO DE GRAFICAS EN CANVAS
   ========================================= */

function inicializarGraficasReportes() {

    const lienzos = document.querySelectorAll(
        "canvas[data-grafica-reporte]"
    );

    if (!lienzos.length) {
        return;
    }

    lienzos.forEach(function (canvas) {

        dibujarGraficaBarras(canvas);

    });

}


function dibujarGraficaBarras(canvas) {

    const contexto = canvas.getContext("2d");

    if (!contexto) {
        return;
    }

    let etiquetas = [];
    let valores = [];

    try {
        etiquetas = JSON.parse(
            canvas.dataset.etiquetas || "[]"
        );
        valores = JSON.parse(
            canvas.dataset.valores || "[]"
        );
    } catch (error) {
        return;
    }

    if (!etiquetas.length || !valores.length) {
        return;
    }

    const ancho = canvas.width || 620;
    const alto = canvas.height || 230;

    contexto.clearRect(0, 0, ancho, alto);

    const margenIzq = 42;
    const margenDer = 20;
    const margenSup = 22;
    const margenInf = 48;

    const anchoUtil = ancho - margenIzq - margenDer;
    const altoUtil = alto - margenSup - margenInf;

    const maximo = Math.max(...valores, 1);

    // Lineas guia horizontales
    contexto.strokeStyle = "rgba(150, 196, 223, 0.35)";
    contexto.lineWidth = 1;
    contexto.fillStyle = "#d4e8f5";
    contexto.font = "11px Arial, sans-serif";

    const pasos = 4;
    for (let i = 0; i <= pasos; i++) {
        const y = margenSup + (altoUtil / pasos) * i;
        const valorEscala = Math.round(
            maximo - (maximo / pasos) * i
        );

        contexto.beginPath();
        contexto.moveTo(margenIzq, y);
        contexto.lineTo(ancho - margenDer, y);
        contexto.stroke();

        contexto.fillText(
            String(valorEscala),
            10,
            y + 4
        );
    }

    // Dibujar barras
    const totalBarras = Math.min(etiquetas.length, 10);
    const pasoBarra = anchoUtil / totalBarras;
    const anchoBarra = Math.max(14, Math.min(44, pasoBarra * 0.6));

    for (let i = 0; i < totalBarras; i++) {
        const valor = Number(valores[i]) || 0;
        const alturaBarra = (valor / maximo) * altoUtil;

        const x = margenIzq + i * pasoBarra + (pasoBarra - anchoBarra) / 2;
        const y = margenSup + altoUtil - alturaBarra;

        const gradiente = contexto.createLinearGradient(0, y, 0, margenSup + altoUtil);
        gradiente.addColorStop(0, "#ffee00");
        gradiente.addColorStop(1, "#4298c5");

        contexto.fillStyle = gradiente;
        contexto.fillRect(x, y, anchoBarra, Math.max(2, alturaBarra));

        contexto.strokeStyle = "#ffffff";
        contexto.strokeRect(x, y, anchoBarra, Math.max(2, alturaBarra));

        // Valor numerico encima de la barra
        contexto.fillStyle = "#ffff00";
        contexto.font = "bold 11px Arial, sans-serif";
        contexto.textAlign = "center";
        contexto.fillText(
            String(valor),
            x + anchoBarra / 2,
            Math.max(14, y - 5)
        );

        // Etiqueta inferior recortada
        const nombreCorto = String(etiquetas[i]).slice(0, 11);
        contexto.fillStyle = "#ffffff";
        contexto.font = "10px Arial, sans-serif";
        contexto.fillText(
            nombreCorto,
            x + anchoBarra / 2,
            margenSup + altoUtil + 18
        );
    }

}
