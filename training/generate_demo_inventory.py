"""Genera un CSV sintético de inventario para pruebas de CI; nunca usa Supabase."""
from pathlib import Path
import pandas as pd


def main() -> None:
    filas = []
    for periodo in pd.date_range("2026-01-01", periods=10, freq="MS"):
        for plaza_id in (1, 3):
            for producto_id in (2, 7, 9):
                filas.append({
                    "plaza_id": plaza_id,
                    "producto_id": producto_id,
                    "periodo": periodo.date().isoformat(),
                    "consumo": 2 + plaza_id + producto_id % 4 + periodo.month % 3,
                })
    target = Path("data/dataset_inventario_demo.csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas).to_csv(target, index=False)
    print(f"Generados {len(filas)} registros sintéticos en {target}")


if __name__ == "__main__":
    main()
