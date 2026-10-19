# tablero-flota

Tablero de consulta de la flota Salina Las Barrancas: **https://rodrigo-ctr.github.io/tablero-flota/**

Página de solo lectura. Los datos se cargan en Gestión de Flota (Claude) y el tablero se regenera automáticamente cada viernes.

## Cómo se actualiza

1. Se exportan las colecciones de Gestión de Flota (cargas, config, planes, services, ordenes, ingresos, historial) a una carpeta, un JSON por documento.
2. `python3 build/build.py <carpeta> <AAAA-MM-DD>` genera `index.html` con los datos embebidos.
3. Se publica con un commit a `main` (GitHub Pages sirve la raíz de `main`).

- `build/template.html`: diseño y lógica del tablero.
- `build/fichas.json`: fichas técnicas por equipo (se editan a mano).
- `docs/`: documentos de consulta (PDF y guía del chofer).
