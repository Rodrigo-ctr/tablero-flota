"""Genera index.html del Tablero de Flota.
Uso: python3 build/build.py <carpeta_datos> <fecha AAAA-MM-DD>
<carpeta_datos> contiene las colecciones exportadas de Gestión de Flota
(cargas/, config/, planes/, services/, ordenes/, ingresos/, historial/, controles/, especiales/),
un JSON por documento, tal como las guarda ArtifactData con out_dir."""
import json, glob, os, sys
D, FECHA = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
def L(p):
    d = json.load(open(p))
    return d['data'] if isinstance(d, dict) and 'data' in d and 'version' in d else d
def docs(col):
    return [(os.path.basename(f)[:-5], L(f)) for f in sorted(glob.glob(os.path.join(D, col, '*.json')))]
cargas = [{k: v for k, v in c.items() if k not in ('obs', 'origen', 'creado')} for _, d in docs('cargas') for c in d.get('items', {}).values()]
ingresos = [{k: v for k, v in c.items() if k not in ('remito', 'creado', 'proveedor', 'obs')} for _, d in docs('ingresos') for c in d.get('items', {}).values()]
cfg = dict(docs('config'))
snap = {
    'fecha': FECHA,
    'equipos': cfg['equipos']['lista'],
    'stock': cfg['stock'],
    'cargas': cargas,
    'ingresos': ingresos,
    'planes': [dict(d, id=i) for i, d in docs('planes')],
    'services': [dict(d, id=i) for i, d in docs('services')],
    'ordenes': [dict(d, id=i) for i, d in docs('ordenes')],
    'historial': {i: d.get('items', []) for i, d in docs('historial')},
    # controles de agua en el aceite: sin nombres de personas en la página pública
    'controles': [dict({k: v for k, v in d.items() if k not in ('operador', 'jefe', 'creado')}, visado=bool(d.get('jefe'))) for _, d in docs('controles')],
    # aceites especiales (latas): movimientos sin texto libre, que puede nombrar personas
    'especiales': [dict({k: v for k, v in d.items() if k != 'movs'}, id=i, movs=[{k: m.get(k) for k in ('fecha', 'tipo', 'cant', 'equipo')} for m in (d.get('movs') or {}).values()]) for i, d in docs('especiales')],
    'fichas': json.load(open(os.path.join(HERE, 'fichas.json'))),
}
data = json.dumps(snap, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
tpl = open(os.path.join(HERE, 'template.html')).read()
head = '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex, nofollow"><title>Tablero de Flota</title></head><body>\n'
out = head + tpl.replace('/*__DATA__*/', data, 1) + '\n</body></html>\n'
open(os.path.join(HERE, '..', 'index.html'), 'w').write(out)
print('index.html generado:', len(cargas), 'cargas,', len(snap['ordenes']), 'órdenes, datos al', FECHA)
