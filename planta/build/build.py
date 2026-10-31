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
    'equipos': [{k: v for k, v in e.items() if k != 'chapaFoto'} for e in docs('equipos')],
    'tareas': docs('tareas'),
    # sin nombres de personas ni adjuntos en la página pública
    'registros': [{k: v for k, v in r.items() if k not in ('quien', 'adjunto')} for r in docs('registros')],
    # manuales y planos: solo el título; los archivos tienen derechos de terceros y no se publican
    'docs': [{k: v for k, v in d.items() if k not in ('asset', 'archivo')} for d in docs('docs')],
}
data = json.dumps(snap, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
tpl = open(os.path.join(HERE, 'template.html')).read()
f = FECHA[8:10] + '/' + FECHA[5:7] + '/' + FECHA[:4]
shim = ('<script>(function(){const D=' + data + ';'
        'const no=()=>Promise.reject({code:"not_granted"});const ro={set:no,update:no,delete:no};'
        'const col=c=>({onSnapshot(cb){setTimeout(()=>cb({docs:(D[c]||[]).map(x=>({id:x.id,data:()=>x}))}),0);return()=>{}},doc:()=>ro});'
        'window.claude={use:async n=>n==="db"?{collection:col,doc:()=>ro}:null};document.documentElement.classList.add("ro")})()</script>\n')
acts = ['neweq', 'editeq', 'conf', 'newtarea', 'edittarea', 'hecho', 'newreg', 'newajuste', 'editajuste', 'newdoc', 'editdoc', 'chapa', 'pickdoc', 'pickreg']
css = '<style>' + ','.join('html.ro [data-act="%s"]' % a for a in acts) + ',html.ro #btnExport{display:none!important}</style>\n'
banner = '<div class="status" style="margin-top:14px">Vista de solo lectura · datos al ' + f + '. Se actualiza los viernes.</div>\n  <div id="msg"'
assert tpl.count('<div id="msg"') == 1 and tpl.count("<script>\n'use strict';") == 1
tpl = tpl.replace('<div id="msg"', banner, 1).replace("<script>\n'use strict';", shim + "<script>\n'use strict';", 1)
head = '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex, nofollow"><style>body{margin:0}[hidden]{display:none!important}</style></head><body>\n'
open(os.path.join(HERE, '..', 'index.html'), 'w').write(head + css + tpl + '\n</body></html>\n')
print('planta/index.html generado:', len(snap['equipos']), 'equipos,', len(snap['tareas']), 'tareas, datos al', FECHA)
