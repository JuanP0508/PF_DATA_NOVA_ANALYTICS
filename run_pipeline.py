import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

notebooks = [
    BASE_DIR / "notebooks" / "PipelineV_3.0.ipynb",
    BASE_DIR / "notebooks" / "feature_engineering_final.ipynb",
    BASE_DIR / "notebooks" / "Clustering_Kmeans.ipynb",
    BASE_DIR / "notebooks" / "Notebook_Clustering_NMM.ipynb",
]

for nb in notebooks:
    print(f"Ejecutando: {nb.name}")
    subprocess.run(
        [
            "python",
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--inplace",
            str(nb),
        ],
        check=True,
    )

print("Pipeline completado.")