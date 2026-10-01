from pathlib import Path


def load_style(widget, path):
    qss = Path(path)
    if not qss.is_absolute():
        qss = Path.cwd() / qss
    if qss.exists():
        widget.setStyleSheet(qss.read_text(encoding="utf-8"))
