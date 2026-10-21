"""Datos sintéticos para verificar el sistema, no datos de SIGO."""
from pathlib import Path
import csv
from datetime import date, timedelta
import random


def main():
    random.seed(2026)
    output = Path("data/dataset_demo.csv")
    output.parent.mkdir(exist_ok=True)
    start = date(2026, 8, 1)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["fecha", "plaza_id", "turno_id", "programados", "ausentes"])
        writer.writeheader()
        for day in range(65):
            fecha = start + timedelta(days=day)
            for plaza in (1, 4, 8):
                for turno in (1, 2, 3):
                    programados = 14 + plaza // 4 + turno
                    base = 1 + int(turno == 2) + int(fecha.weekday() == 0)
                    ausentes = max(0, min(programados, base + random.choice((-1, 0, 0, 1))))
                    writer.writerow({"fecha": fecha.isoformat(), "plaza_id": plaza,
                        "turno_id": turno, "programados": programados, "ausentes": ausentes})
    print(f"Dataset sintético creado: {output}")


if __name__ == "__main__":
    main()
