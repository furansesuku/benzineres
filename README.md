# Benzineres més econòmiques

Rànquing de benzineres per comarca i municipi (diesel o súper 95), a partir del Geoportal de Gasolineras del MITECO.

## Estructura

```
Benzineres/
├── app.py                       backend Flask
├── requirements.txt             dependències
├── static/index.html            frontend
├── data/municipis_comarques.csv taula municipi → comarca
├── .gitignore
└── README.md
```

## Estat actual

- `GEOPORTAL_API_URL` està buit: cal posar-hi l'endpoint verificat abans que funcioni la consulta.
- Els noms dels camps de l'API (`Municipio`, `Precio Gasoleo A`, etc.) són provisionals i s'han de comprovar amb una resposta real.
- `data/municipis_comarques.csv` només té uns quants municipis de mostra. Cal completar-lo amb la taula de l'Idescat.

## Instal·lació en local (Windows, PowerShell)

```powershell
cd C:\PROVES_IA\Benzineres
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execució

```powershell
$env:GEOPORTAL_API_URL = "https://..."   # endpoint verificat
python app.py
```

Després obre el navegador a `http://127.0.0.1:8022`.

El port per defecte és el 8022 i es pot canviar amb la variable `PORT`. Per al servidor, la variable `HOST` ha de ser `0.0.0.0` perquè accepti connexions externes.

## Variables d'entorn

| Variable | Per defecte | Descripció |
|---|---|---|
| `GEOPORTAL_API_URL` | (buit) | Endpoint de l'API del Geoportal |
| `REFRESH_SECONDS` | 900 | Temps abans de tornar a descarregar les dades |
| `HOST` | 127.0.0.1 | Adreça on escolta el servidor |
| `PORT` | 8022 | Port del servidor |

## Pujar a GitHub

```powershell
git init
git add .
git commit -m "Versió inicial"
```

El fitxer `.gitignore` evita pujar l'entorn virtual i fitxers temporals.
