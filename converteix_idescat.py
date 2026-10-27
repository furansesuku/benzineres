"""
Converteix la taula de correspondències de l'Idescat al format que espera app.py.

Ús (des de PowerShell, dins de C:\\PROVES_IA\\Benzineres):
    python converteix_idescat.py taula_idescat.csv

Entrada: el fitxer descarregat de l'Idescat (separat per punts i coma).
Sortida: data\\municipis_comarques.csv amb les columnes municipi,comarca.
"""

import csv
import sys
from pathlib import Path

SORTIDA = Path(__file__).resolve().parent / "data" / "municipis_comarques.csv"


def llegeix_entrada(ruta):
    """Prova diverses codificacions habituals de fitxers de Windows."""
    for codificacio in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return ruta.read_text(encoding=codificacio).splitlines()
        except UnicodeDecodeError:
            continue
    raise RuntimeError("No s'ha pogut llegir el fitxer amb cap codificació coneguda.")


def main():
    if len(sys.argv) != 2:
        print("Ús: python converteix_idescat.py taula_idescat.csv")
        sys.exit(1)

    entrada = Path(sys.argv[1])
    linies = llegeix_entrada(entrada)

    # Saltem les línies de títol fins a la capçalera (la que comença per "Codi municipi")
    inici = next(
        (i for i, l in enumerate(linies) if l.lower().startswith("codi municipi")),
        None,
    )
    if inici is None:
        print("No s'ha trobat la capçalera 'Codi municipi'. Revisa el fitxer.")
        sys.exit(1)

    lector = csv.DictReader(linies[inici:], delimiter=";")
    files = []
    for fila in lector:
        municipi = (fila.get("Nom municipi") or "").strip()
        comarca = (fila.get("Nom comarca") or "").strip()
        if municipi and comarca:
            files.append((municipi, comarca))

    if not files:
        print("No s'ha trobat cap municipi. Revisa el format del fitxer.")
        sys.exit(1)

    SORTIDA.parent.mkdir(exist_ok=True)
    with open(SORTIDA, "w", encoding="utf-8", newline="") as f:
        escriptor = csv.writer(f)
        escriptor.writerow(["municipi", "comarca"])
        escriptor.writerows(files)

    comarques = {c for _, c in files}
    print(f"Fet: {len(files)} municipis en {len(comarques)} comarques.")
    print(f"Fitxer generat: {SORTIDA}")


if __name__ == "__main__":
    main()
