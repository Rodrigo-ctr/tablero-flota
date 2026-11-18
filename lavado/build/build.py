"""Genera lavado/index.html: vista de solo lectura de PROD · Registros de lavado para Dirección.
Uso: python3 lavado/build/build.py <export>/dias   (la colección "notas" exportada en <export>/notas)
Desde 18/11 (pedido de Rodrigo): todo igual que la herramienta, con nombres, patentes, Trazabilidad, Cómo se cruza
y el Análisis del día. Se quitan solo la pestaña Bitácora, las consultas de la carga (links a Drive sí: Rodrigo comparte las carpetas con Dirección)."""
import json, glob, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
rd = lambda n: open(os.path.join(HERE, n), encoding='utf8').read()
html, js = rd('html.part'), rd('script2.part')
m = re.search(r'\nconst SEMILLA=(\[.*\]);\n', js)
if len(sys.argv) > 1:
    def L(p):
        d = json.load(open(p, encoding='utf8'))
        return d['data'] if isinstance(d, dict) and 'data' in d and 'version' in d else d
    D = [L(f) for f in sorted(glob.glob(os.path.join(sys.argv[1], '**', '*.json'), recursive=True))]
    D = sorted([d for d in D if d.get('fecha')], key=lambda d: d['fecha'])
else:
    D = json.loads(m.group(1))
# 18/11: los links a los PDF de Drive se dejan (Rodrigo comparte las carpetas con Dirección)
# notas de la bitácora (colección "notas", exportada junto a "dias"): se muestran en Día e Indicadores
NOMBRES_USR = {'u_4XNCAzY54AolHW456wUSfQ': 'Rodrigo'}
NOTAS = []
if len(sys.argv) > 1:
    base_dir = os.path.dirname(os.path.normpath(sys.argv[1]))
    for f in sorted(glob.glob(os.path.join(base_dir, 'notas', '*.json'))):
        n = json.load(open(f, encoding='utf8')); n = n.get('data', n) if 'version' in n and 'data' in n else n
        n['id'] = os.path.basename(f)[:-5]; n['porNombre'] = NOMBRES_USR.get(n.get('por'), '')
        NOTAS.append(n)
    NOTAS.sort(key=lambda n: str(n.get('creado', '')), reverse=True)
data = json.dumps(D, ensure_ascii=False).replace('</', '<\\/')
js = js[:m.start()] + '\nconst SEMILLA=' + data + ';\nconst NOTAS_PUB=' + json.dumps(NOTAS, ensure_ascii=False).replace('</', '<\\/') + ';\n' + js[m.end():]
assert js.count('const PUBLICA=false;') == 1
js = js.replace('const PUBLICA=false;', 'const PUBLICA=true;')
js = js.replace('https://drive.google.com/file/d/', '#')  # consultas: internas, no se muestran sin base
js = re.sub(r'(?<=[;{}]) *//[^\n]*', '', js)
js = re.sub(r'\n *//[^\n]*', '', js)
html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
for v in ['bit']:
    html, n = re.subn(r'\n *<button role="tab" id="t-%s"[^\n]*' % v, '', html); assert n == 1, v
    html, n = re.subn(r'\n  <div id="v-%s" hidden>.*?\n  </div>' % v, '', html, flags=re.S); assert n == 1, v
banda = rd('banda-salina.html').strip()
CINTA = '</div></header>'
assert html.count(CINTA) == 1
html = html.replace(CINTA, CINTA + '\n' + banda + '\n<div class="slb-banda" role="img" aria-label="Cosechadoras sobre la salina"></div>', 1)
head = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="robots" content="noindex, nofollow"><title>Registros de lavado · SLB</title>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@600;700&display=swap">'
        '<style>body{margin:0}[hidden]{display:none!important}</style></head><body>\n')
out = head + rd('piel-slb.html') + html + js + '\n</body></html>\n'
NOMBRES = []
bad = [n for n in NOMBRES if n in out]
if bad: [print(n, out[max(0,out.find(n)-120):out.find(n)+60].replace('\n',' ')) for n in bad]
assert not bad, bad
open(os.path.join(HERE, '..', 'index.html'), 'w', encoding='utf8').write(out)
print('lavado/index.html generado:', len(D), 'días, último', D[-1]['fecha'])
