"""
Backend del rànquing de benzineres (Geoportal de Gasolineras, MITECO).

Executa:  python app.py
Després obre:  http://127.0.0.1:8022
"""

import csv
import json
import os
import subprocess
import threading
import time
import unicodedata
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DATA_CSV = BASE_DIR / "data" / "municipis_comarques.csv"
STATIC_DIR = BASE_DIR / "static"

# ---------------------------------------------------------------------------
# Configuració (es pot sobreescriure amb variables d'entorn)
# ---------------------------------------------------------------------------
API_URL = os.getenv(
    "GEOPORTAL_API_URL",
    "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/",
)
REFRESH_SECONDS = int(os.getenv("REFRESH_SECONDS", "900"))  # 15 minuts
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8022"))

# Noms dels camps verificats amb una resposta real de l'API
CLAU_LLISTA = "ListaEESSPrecio"
CAMP_MUNICIPI = "Municipio"
CAMP_ROTULO = "Rótulo"
CAMP_ADRECA = "Dirección"
CAMPS_PREU = {
    "diesel": "Precio Gasoleo A",
    "super95": "Precio Gasolina 95 E5",
}

# ---------------------------------------------------------------------------
# Utilitats
# ---------------------------------------------------------------------------


def normalitza(text):
    """Passa a majúscules i treu accents i espais sobrers, per comparar noms."""
    text = (text or "").strip().upper()
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def carrega_municipis():
    """
    Llegeix data/municipis_comarques.csv (columnes: municipi,comarca).
    Retorna:
      - per_municipi: {nom_normalitzat: comarca}
      - per_comarca: {comarca: [municipis ordenats]}
    """
    per_municipi = {}
    per_comarca = {}
    # utf-8-sig tolera la marca BOM que Windows PowerShell pot afegir al desar el CSV
    with open(DATA_CSV, encoding="utf-8-sig", newline="") as f:
        for fila in csv.DictReader(f):
            municipi = fila["municipi"].strip()
            comarca = fila["comarca"].strip()
            if not municipi or not comarca:
                continue
            per_municipi[normalitza(municipi)] = comarca
            per_comarca.setdefault(comarca, []).append(municipi)
    for llista in per_comarca.values():
        llista.sort()
    return per_municipi, per_comarca


MUNICIPI_COMARCA, COMARQUES_MUNICIPIS = carrega_municipis()

# ---------------------------------------------------------------------------
# Cache de les estacions
# ---------------------------------------------------------------------------

_cache = {"estacions": [], "ts": 0.0}
_lock = threading.Lock()


def descarrega_dades():
    """
    Descarrega les dades amb curl (no amb requests), perquè la biblioteca TLS
    de Python pot ser bloquejada per alguns antivirus o xarxes, mentre que curl funciona.
    """
    if not API_URL:
        raise RuntimeError("Falta configurar GEOPORTAL_API_URL (endpoint de l'API).")
    resultat = subprocess.run(
        ["curl", "-sS", "-f", "--max-time", "60", API_URL],
        capture_output=True,
        timeout=90,
    )
    if resultat.returncode != 0:
        missatge = resultat.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"curl ha fallat: {missatge}")
    dades = json.loads(resultat.stdout.decode("utf-8"))
    _cache["estacions"] = dades.get(CLAU_LLISTA, [])
    _cache["ts"] = time.time()


def estacions():
    """Retorna les estacions, refrescant la cache si ha caducat."""
    with _lock:
        if time.time() - _cache["ts"] > REFRESH_SECONDS or not _cache["estacions"]:
            descarrega_dades()
        return list(_cache["estacions"])


def preu_de(estacio, carburant):
    valor = (estacio.get(CAMPS_PREU[carburant]) or "").replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Aplicació web
# ---------------------------------------------------------------------------

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/geo")
def geo():
    """Comarques i municipis disponibles per als desplegables."""
    return jsonify({"comarques": COMARQUES_MUNICIPIS})


@app.route("/api/ranking")
def ranking():
    comarca = request.args.get("comarca", "").strip()
    municipi = request.args.get("municipi", "").strip()
    carburant = request.args.get("carburant", "diesel")

    if carburant not in CAMPS_PREU:
        return jsonify({"error": "Carburant no vàlid (diesel o super95)."}), 400
    if comarca not in COMARQUES_MUNICIPIS:
        return jsonify({"error": "Comarca no vàlida."}), 400

    try:
        dades = estacions()
    except Exception as e:
        return jsonify({"error": f"No s'han pogut obtenir les dades: {e}"}), 503

    resultat = []
    for e in dades:
        nom_municipi = normalitza(e.get(CAMP_MUNICIPI))
        if MUNICIPI_COMARCA.get(nom_municipi) != comarca:
            continue
        if municipi and nom_municipi != normalitza(municipi):
            continue
        preu = preu_de(e, carburant)
        if preu is None:
            continue
        resultat.append({
            "rotulo": e.get(CAMP_ROTULO, ""),
            "adreca": e.get(CAMP_ADRECA, ""),
            "municipi": e.get(CAMP_MUNICIPI, ""),
            "preu": preu,
        })

    resultat.sort(key=lambda x: x["preu"])
    return jsonify({
        "carburant": carburant,
        "total": len(resultat),
        "actualitzat": datetime.fromtimestamp(_cache["ts"]).strftime("%d/%m/%Y %H:%M:%S")
        if _cache["ts"] else None,
        "resultat": resultat,
    })


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)