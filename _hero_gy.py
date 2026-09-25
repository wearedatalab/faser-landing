# -*- coding: utf-8 -*-
"""Hero con Georgetown real: la foto original del boceto (background-guyana.jpg) es JFK/Jamaica Bay (Nueva York).
Se recorta la costanera de Kingston del aéreo de Duke Tower (placa fotográfica real, sin la torre) y se amplía con ESRGAN x4."""
import base64, io, json, os, urllib.request
from PIL import Image
KEY = os.environ['FAL_KEY']
src = Image.open('_originales/diseno-v04/images/duke-main.png').convert('RGB').crop((1000, 104, 2048, 1101))  # luego se recortan 300px (x4) a la izquierda: asomaba el podio del render
b = io.BytesIO(); src.save(b, 'PNG')
req = urllib.request.Request('https://fal.run/fal-ai/esrgan', data=json.dumps({'image_url': 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode(), 'scale': 4, 'model': 'RealESRGAN_x4plus', 'output_format': 'png'}).encode(),
                             headers={'Authorization': 'Key ' + KEY, 'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=600) as r:
    url = json.loads(r.read())['image']['url']
with urllib.request.urlopen(url, timeout=300) as r:
    big = Image.open(io.BytesIO(r.read())).convert('RGB')
big.save('_originales/kingston-x4.png'); print('x4', big.size)
for w, q in [(2400, 74), (1400, 72), (900, 70)]:
    im = big.resize((w, round(big.height * w / big.width)), Image.LANCZOS)
    name = 'hero-kingston' + ('' if w == 2400 else f'-{w}')
    im.save(f'img/{name}.webp', 'WEBP', quality=q, method=6); print(name, im.size, os.path.getsize(f'img/{name}.webp') // 1024, 'KB')
