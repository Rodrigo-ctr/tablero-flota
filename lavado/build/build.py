"""Genera lavado/index.html: vista de solo lectura de PROD · Registros de lavado para Dirección.
Uso: python3 lavado/build/build.py <carpeta_dias>
<carpeta_dias> = colección "dias" exportada del artefacto con ArtifactData (list, out_dir): un JSON por día.
Sin argumento usa la SEMILLA embebida en script2.part.
html.part y script2.part son copia de la herramienta (calidad/registros-build/ del proyecto): si cambia, se vuelven a copiar.
Se quitan: Bitácora, Trazabilidad, "Cómo se cruza", notas de carga, operadores, choferes, transportistas
(pasan a "Chofer 1", "Transporte A"), patentes (enmascaradas) y enlaces a Drive."""
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
base = lambda t: unicodedata.normalize('NFD', str(t or '')).encode('ascii', 'ignore').decode().lower().strip().split(' ')[0] if str(t or '').strip() else ''
CH, TR = {}, {}
def alias(tab, t, pref, f):
    k = base(t)
    if not k: return ''
    if k not in tab: tab[k] = pref + f(len(tab))
    return tab[k]
ch = lambda t: alias(CH, t, 'Chofer ', lambda i: str(i + 1))
tr = lambda t: alias(TR, t, 'Transporte ', lambda i: chr(65 + i))
pat = lambda p: (str(p).strip()[:2] + ' •••') if str(p or '').strip() else ''
for d in D:
    d['operador'] = ''; d['notas'] = []; d.pop('analisis', None)
    if d.get('fuente'): d['fuente'] = {'nombre': d['fuente'].get('nombre', '')}
    for b in (d.get('bateas') or {}).get('cargas', []):
        b['chofer'] = ch(b.get('chofer')); b['trans'] = tr(b.get('trans')); b['pat'] = pat(b.get('pat')); b.pop('obs_int', None)
    dp = d.get('desp') or {}
    if dp.get('pdf'): dp['pdf'] = {}
    for v in dp.get('viajes', []):
        v['chofer'] = ch(v.get('chofer')); v['transporte'] = tr(v.get('transporte'))
    g = d.get('granel') or {}
    if 'chofer' in g: g['chofer'] = ''
    for f in g.get('filas', []): f.pop('chofer', None)
data = json.dumps(D, ensure_ascii=False).replace('</', '<\\/')
js = js[:m.start()] + '\nconst SEMILLA=' + data + ';\n' + js[m.end():]
assert js.count('const PUBLICA=false;') == 1
js = js.replace('const PUBLICA=false;', 'const PUBLICA=true;')
js = re.sub(r'(?<=[;{}]) *//[^\n]*', '', js)
js = re.sub(r'\n *//[^\n]*', '', js)
html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
js = re.sub(r'const CRUCES=\[.*?\n\];', 'const CRUCES=[];', js, count=1, flags=re.S)
for v in ['tra', 'bit', 'cru']:
    html, n = re.subn(r'\n *<button role="tab" id="t-%s"[^\n]*' % v, '', html); assert n == 1, v
    html, n = re.subn(r'\n  <div id="v-%s" hidden>.*?\n  </div>' % v, '', html, flags=re.S); assert n == 1, v
html, n = re.subn(r'\n *<dt>Bitácora y análisis del día</dt>\s*<dd>.*?</dd>', '', html, flags=re.S); assert n == 1
html = html.replace('Cómo se cruza', '')
banda = rd('banda-salina.html').strip()
CINTA = '</div></header>'
assert html.count(CINTA) == 1
html = html.replace(CINTA, CINTA + '\n' + banda + '\n<div class="slb-banda" role="img" aria-label="Cosechadoras sobre la salina"></div>', 1)
head = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="robots" content="noindex, nofollow"><title>Registros de lavado · SLB</title>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@600;700&display=swap">'
        '<style>body{margin:0}[hidden]{display:none!important}</style></head><body>\n')
out = head + rd('piel-slb.html') + html + js + '\n</body></html>\n'
NOMBRES = ['Rodrigo', 'Camila', 'Gerber', 'Saavedra', 'Padilla', 'Mendez', 'Méndez', 'Zúñiga', 'Zuñiga', 'Jonathan', 'Joni', 'Luis', 'Mario', 'Barth', 'Soto', 'Calzada', 'Álvarez', 'Alvarez', 'Aguilera', 'Girotti', 'Reynoso', 'drive.google']
bad = [n for n in NOMBRES if n in out]
if bad: [print(n, out[max(0,out.find(n)-120):out.find(n)+60].replace('\n',' ')) for n in bad]
assert not bad, bad
open(os.path.join(HERE, '..', 'index.html'), 'w', encoding='utf8').write(out)
print('lavado/index.html generado:', len(D), 'días, último', D[-1]['fecha'])
