# tablero-flota

Tablero de consulta de la flota Salina Las Barrancas: **https://rodrigo-ctr.github.io/tablero-flota/**

Página de solo lectura. Los datos se cargan en Gestión de Flota (Claude) y el tablero se regenera automáticamente cada viernes.

## Cómo se actualiza

1. Se exportan las colecciones de Gestión de Flota (cargas, config, planes, services, ordenes, ingresos, historial, controles) a una carpeta, un JSON por documento.
2. `python3 build/build.py <carpeta> <AAAA-MM-DD>` genera `index.html` con los datos embebidos.
3. Se publica con un commit a `main` (GitHub Pages sirve la raíz de `main`).

- `build/template.html`: diseño y lógica del tablero.
- `build/fichas.json`: fichas técnicas por equipo (se editan a mano).
- `docs/`: documentos de consulta (PDF y guía del chofer).

## Equipos · Planta de lavado

Vista de solo lectura de los equipos de la planta de lavado: **https://rodrigo-ctr.github.io/tablero-flota/planta/**

- Los datos se cargan en el artefacto EQUIPOS · Planta de lavado (Claude) y la vista se regenera cada viernes junto con el tablero de flota.
- `python3 planta/build/build.py <carpeta> <AAAA-MM-DD>` genera `planta/index.html` desde las colecciones exportadas (equipos, tareas, registros, docs).
- `planta/build/template.html` es una copia de la página del artefacto: cuando el artefacto cambia, se copia de nuevo.
- No se publican nombres de personas, fotos ni archivos de manuales o planos (solo sus títulos).
