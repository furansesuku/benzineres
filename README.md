# Benzineres més econòmiques

Rànquing de benzineres de Catalunya per comarca i municipi, per a diesel o súper 95. Les dades provenen del Geoportal de Gasolineras del MITECO.

**Adreça pública:** http://142.132.183.54/festeve/benzineres/

## Estructura

```
Benzineres/
├── app.py                        backend Flask (API i descàrrega de dades)
├── converteix_idescat.py         converteix la taula de l'Idescat al CSV del projecte
├── requirements.txt              dependències (Flask i Gunicorn)
├── static/index.html             frontend (desplegables i taula)
├── data/municipis_comarques.csv  taula municipi → comarca
├── .gitignore
└── README.md
```

## Requisits

- Python 3.12 (una versió estable; amb versions de prova no funciona la connexió HTTPS)
- `curl` instal·lat (l'aplicació l'usa per descarregar les dades)
- Git (per pujar el codi a GitHub)

## Instal·lació en local (Windows, PowerShell)

```powershell
cd C:\PROVES_IA\Benzineres
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Preparar la taula de municipis

1. Descarrega la taula de correspondències municipis-comarques de l'Idescat i desa-la com a `taula_idescat.csv` (UTF-8).
2. Executa:

```powershell
python converteix_idescat.py taula_idescat.csv
```

Això genera `data/municipis_comarques.csv` amb les columnes `municipi,comarca`.

## Execució en local

```powershell
python app.py
```

Després obre `http://127.0.0.1:8022` al navegador. Per aturar el servidor, prem `Ctrl + C`.

## Prova des de la línia de comandes

```powershell
python -c "from app import app; c = app.test_client(); r = c.get('/api/ranking?comarca=Anoia&municipi=Piera&carburant=diesel'); print('Codi:', r.status_code); print(r.get_json())"
```

## Desplegament al servidor (Linux)

El projecte està al servidor a `/var/www/festeve/benzineres`. L'aplicació s'executa amb Gunicorn al port **8203**, només accessible en local (`127.0.0.1`), i Nginx la publica a la ruta `/festeve/benzineres/`.

### 1. Entorn virtual i dependències

```bash
cd /var/www/festeve/benzineres
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Rutes relatives al frontend

Perquè l'aplicació funcioni sota `/festeve/benzineres/`, les crides del frontend han de ser relatives (sense la barra inicial). A `static/index.html` estan així:

```javascript
const r = await fetch('api/geo');
const r = await fetch('api/ranking?' + params.toString());
```

### 3. Arrencada de Gunicorn

Gunicorn s'executa dins d'una sessió de `tmux`, perquè continuï en marxa en tancar la sessió SSH:

```bash
tmux new -s benzineres
cd /var/www/festeve/benzineres
source venv/bin/activate
gunicorn --workers 2 --bind 127.0.0.1:8203 app:app
```

Per sortir de la sessió sense aturar Gunicorn, prem `Ctrl + B` i després `D`. Per tornar-hi: `tmux attach -t benzineres`.

### 4. Configuració de Nginx

Nginx carrega els fitxers de `/etc/nginx/snippets/festeve/*.conf`. La configuració de Benzineres és el fitxer `benzineres.conf` d'aquesta carpeta:

```nginx
location = /festeve/benzineres {
    return 301 /festeve/benzineres/;
}

location /festeve/benzineres/ {
    proxy_pass http://127.0.0.1:8203/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /festeve/benzineres;
}
```

Després de crear o modificar el fitxer, prova la configuració i recarrega Nginx (mai `restart`):

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 5. Comprovació

```bash
curl -I http://142.132.183.54/festeve/benzineres/
curl -s "http://142.132.183.54/festeve/benzineres/api/geo" | head -c 200
```

La primera ha de retornar `HTTP/1.1 200 OK` i la segona l'inici d'un JSON amb `"comarques"`.

## Endpoints

- `GET /` : pàgina web.
- `GET /api/geo` : comarques i municipis disponibles.
- `GET /api/ranking?comarca=...&municipi=...&carburant=diesel|super95` : llista d'estacions ordenades per preu. El paràmetre `municipi` és opcional.

## Variables d'entorn

| Variable | Per defecte | Descripció |
|---|---|---|
| `GEOPORTAL_API_URL` | endpoint del MITECO | Endpoint de l'API del Geoportal |
| `REFRESH_SECONDS` | 900 | Temps abans de tornar a descarregar les dades (15 minuts) |
| `HOST` | 127.0.0.1 | Adreça on escolta el servidor de desenvolupament. Al servidor, Gunicorn escolta sempre a `127.0.0.1` |
| `PORT` | 8022 | Port del servidor de desenvolupament |

## Funcionament

- Les dades es descarreguen del Geoportal la primera vegada que es fa una consulta i després es guarden a la memòria durant 15 minuts.
- La descàrrega es fa amb `curl`, perquè la connexió HTTPS de Python era bloquejada en aquest entorn.
- El filtre es fa per municipi, no per codi postal.

## Pujar a GitHub

```powershell
git init
git add .
git status
git commit -m "Versió inicial"
git branch -M main
git remote add origin https://github.com/el-teu-usuari/benzineres.git
git push -u origin main
```

Abans del `git push`, revisa amb `git status` que no hi surtin `.venv`, `mostra.json` ni `taula_idescat.csv`.

## Limitacions conegudes

- **Reinici del servidor:** Gunicorn no s'arrenca automàticament. Després d'un reinici cal tornar a executar la comanda del punt 3 dins de `tmux`.
- Les dades són les que publica el Ministeri. Les estacions poden canviar els preus en qualsevol moment, així que el rànquing és orientatiu fins a la següent actualització.
- Els noms de municipi del CSV han de coincidir amb els del Geoportal. Si un municipi no apareix, cal revisar-ne el nom.
- El projecte només inclou municipis catalans.
