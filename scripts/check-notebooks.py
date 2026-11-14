"""Validate notebook structure, clean outputs and Python cell syntax."""

from pathlib import Path
import subprocess

import nbformat
from IPython.core.inputtransformer2 import TransformerManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
SMOKE_NOTEBOOK = ROOT / "python-udemy/Jupyter-Notebook/1-İlk Deneme.ipynb"


def main():
    paths = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "*.ipynb"], cwd=ROOT
    ).decode("utf-8").split("\0")
    notebooks = [ROOT / path for path in paths if path]
    if not notebooks:
        raise SystemExit("İzlenen notebook bulunamadı.")

    transformer = TransformerManager()
    checked_cells = 0
    for path in notebooks:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)

        for number, cell in enumerate(notebook.cells, 1):
            if cell.cell_type != "code":
                continue
            if cell.execution_count is not None or cell.outputs:
                raise ValueError(f"{path.name}, hücre {number}: çalıştırma çıktısını temizleyin.")
            code = transformer.transform_cell(cell.source)
            compile(code, f"{path.name}, hücre {number}", "exec")
            checked_cells += 1

    notebook = nbformat.read(SMOKE_NOTEBOOK, as_version=4)
    NotebookClient(notebook, timeout=20, kernel_name="python3").execute()
    print(f"{len(notebooks)} notebook ve {checked_cells} kod hücresi doğrulandı.")
    print("Başlangıç notebook'u bağımsız Python çekirdeğinde çalıştı.")


if __name__ == "__main__":
    main()
