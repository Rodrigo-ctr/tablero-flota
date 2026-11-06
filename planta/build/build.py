"""Genera planta/index.html: vista pública de solo lectura de EQUIPOS · Planta de lavado.
Uso: python3 planta/build/build.py <carpeta_datos> <fecha AAAA-MM-DD>
<carpeta_datos> contiene las colecciones exportadas del artefacto
(equipos/, tareas/, registros/, docs/), un JSON por documento, tal como las guarda ArtifactData con out_dir.
template.html es una copia de la página del artefacto: cuando cambia el artefacto, se vuelve a copiar."""
import json, glob, os, sys
D, FECHA = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
def L(p):
    d = json.load(open(p))
    return d['data'] if isinstance(d, dict) and 'data' in d and 'version' in d else d
def docs(col):
    return [dict(L(f), id=os.path.basename(f)[:-5]) for f in sorted(glob.glob(os.path.join(D, col, '*.json')))]
snap = {
    'equipos': [{k: v for k, v in e.items() if k not in ('chapaFoto', 'fotos')} for e in docs('equipos')],
    'tareas': docs('tareas'),
    # sin nombres de personas ni adjuntos en la página pública
    'registros': [{k: v for k, v in r.items() if k not in ('quien', 'adjunto')} for r in docs('registros')],
    # manuales y planos: solo el título; archivos y enlaces (Drive, guías) tienen derechos de terceros y no se publican
    'docs': [{k: v for k, v in d.items() if k not in ('asset', 'archivo', 'link')} for d in docs('docs')],
}
# sin nombres de personas en la página pública (notas cargadas con "dato de Rodrigo", etc.)
import re
def anon(v):
    if isinstance(v, str):
        v = re.sub(r'\bde Rodrigo\b', 'de planta', v)
        v = re.sub(r'\bpor Rodrigo\b', 'en planta', v)
        v = re.sub(r'(^|[.;:(] ?)Rodrigo\b', lambda m: m.group(1) + 'Planta', v)
        return re.sub(r'\bRodrigo\b', 'planta', v)
    if isinstance(v, list): return [anon(x) for x in v]
    if isinstance(v, dict): return {k: anon(x) for k, x in v.items()}
    return v
snap = anon(snap)
data = json.dumps(snap, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
tpl = open(os.path.join(HERE, 'template.html')).read()
f = FECHA[8:10] + '/' + FECHA[5:7] + '/' + FECHA[:4]
shim = ('<script>(function(){const D=' + data + ';'
        'const no=()=>Promise.reject({code:"not_granted"});const ro={set:no,update:no,delete:no};'
        'const col=c=>({onSnapshot(cb){setTimeout(()=>cb({docs:(D[c]||[]).map(x=>({id:x.id,data:()=>x}))}),0);return()=>{}},doc:()=>ro});'
        'window.claude={use:async n=>n==="db"?{collection:col,doc:()=>ro}:null};document.documentElement.classList.add("ro")})()</script>\n')
acts = ['neweq', 'editeq', 'conf', 'newtarea', 'edittarea', 'hecho', 'newreg', 'newajuste', 'editajuste', 'newconstr', 'editconstr', 'newdoc', 'editdoc', 'chapa', 'pickdoc', 'pickreg', 'addfoto', 'delfoto']
css = '<style>' + ','.join('html.ro [data-act="%s"]' % a for a in acts) + ',html.ro #btnExport{display:none!important}</style>\n'
banner = '<div class="status" style="margin-top:14px">Vista de solo lectura · datos al ' + f + '. Se actualiza los viernes.</div>\n  <div id="msg"'
assert tpl.count('<div id="msg"') == 1 and tpl.count("<script>\n'use strict';") == 1
tpl = re.sub(r"\[(?:'[^']+',?)+\]\.map\(n=>`<option value=\"\$\{n\}\">`\)", "[].map(n=>``)", tpl)
tpl = tpl.replace('Pedile a Rodrigo', 'Pedí').replace('Avisale a Rodrigo', 'Avisá al responsable')
assert 'De la Iglesia' not in tpl and 'Rodrigo' not in tpl
# foto de la salina debajo de la cinta, solo en la vista pública (OK de Rodrigo 06/11)
banda = open(os.path.join(HERE, 'banda-salina.html')).read().strip()
assert tpl.count('</div></header>\n<div class="wrap">') == 1
tpl = tpl.replace('</div></header>\n<div class="wrap">', '</div></header>\n<div class="slb-banda" role="img" aria-label="Cosechadoras sobre la salina"></div>\n<div class="wrap">', 1)
tpl = tpl.replace('<style>\n/* Layout:', banda + '\n<style>\n/* Layout:', 1)
tpl = tpl.replace('<div id="msg"', banner, 1).replace("<script>\n'use strict';", shim + "<script>\n'use strict';", 1)
head = '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex, nofollow"><style>body{margin:0}[hidden]{display:none!important}</style></head><body>\n'
open(os.path.join(HERE, '..', 'index.html'), 'w').write(head + css + tpl + '\n</body></html>\n')
print('planta/index.html generado:', len(snap['equipos']), 'equipos,', len(snap['tareas']), 'tareas, datos al', FECHA)
