# Benzineres més econòmiques

Rànquing de benzineres de Catalunya per comarca i municipi, per a diesel o súper 95. Les dades provenen del Geoportal de Gasolineras del MITECO.

## Estructura

```
Benzineres/
├── app.py                        backend Flask (API i descàrrega de dades)
├── converteix_idescat.py         converteix la taula de l'Idescat al CSV del projecte
├── requirements.txt              dependències
├── static/index.html             frontend (desplegables i taula)
├── data/municipis_comarques.csv  taula municipi → comarca
├── .gitignore
└── README.md
```

## Requisits

- Python 3.12 (una versió estable; amb versions de prova no funciona la connexió HTTPS)
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

## Execució

```powershell
python app.py
```

Després obre `http://127.0.0.1:8022` al navegador. Per aturar el servidor, prem `Ctrl + C`.

## Prova des de la línia de comandes

```powershell
python -c "from app import app; c = app.test_client(); r = c.get('/api/ranking?comarca=Anoia&municipi=Piera&carburant=diesel'); print('Codi:', r.status_code); print(r.get_json())"
```

## Endpoints

- `GET /` : pàgina web.
- `GET /api/geo` : comarques i municipis disponibles.
- `GET /api/ranking?comarca=...&municipi=...&carburant=diesel|super95` : llista d'estacions ordenades per preu. El paràmetre `municipi` és opcional.

## Variables d'entorn

| Variable | Per defecte | Descripció |
|---|---|---|
| `GEOPORTAL_API_URL` | endpoint del MITECO | Endpoint de l'API del Geoportal |
| `REFRESH_SECONDS` | 900 | Temps abans de tornar a descarregar les dades (15 minuts) |
| `HOST` | 127.0.0.1 | Adreça on escolta el servidor. Per al servidor propi, `0.0.0.0` |
| `PORT` | 8022 | Port del servidor |

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

- Les dades són les que publica el Ministeri. Les estacions poden canviar els preus en qualsevol moment, així que el rànquing és orientatiu fins a la següent actualització.
- Els noms de municipi del CSV han de coincidir amb els del Geoportal. Si un municipi no apareix, cal revisar-ne el nom.
- El projecte només inclou municipis catalans.
