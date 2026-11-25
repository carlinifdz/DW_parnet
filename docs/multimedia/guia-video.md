# Guía de Integración del Video Institucional (Parte 11)

## Cómo publicar el video institucional (sin tocar código)
El módulo `multimedia` ya se encuentra preparado para detectar y reproducir automáticamente el video institucional en cuanto se copie el archivo a la carpeta:

```
media/multimedia/video-institucional.mp4
```

Opcionalmente también puedes agregar en `media/multimedia/`:
- `video-institucional.webm` (formato alternativo WebM)
- `video-institucional-poster.jpg` (imagen de portada)
- `video-institucional.vtt` (subtítulos en español)

O bien, si prefieres alojarlo externamente (por ejemplo en YouTube), basta con definir en `.env`:
```env
VIDEO_INSTITUCIONAL_URL=https://www.youtube.com/embed/ID_DEL_VIDEO
```

## Especificaciones recomendadas para cuando produzcas el video (11.1 a 11.4)
- **Duración requerida por la rúbrica:** entre **2 y 4 minutos**.
- **Contenido sugerido:** objetivo de la página web de ParNet Ingeniería, servicios ofertados, uso de estándares de calidad en proyectos y consejos técnicos.
- **Formato:** MP4 (códec de video H.264, códec de audio AAC a 128 kbps, resolución 1280×720 a 30 fps).
- **Optimización con FFmpeg (opcional):**
  ```bash
  ffmpeg -i original.mp4 -vf scale=1280:720 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k -movflags +faststart media/multimedia/video-institucional.mp4
  ```
