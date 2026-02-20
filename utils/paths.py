from pathlib import Path

def project_root() -> Path:
    # utils/paths.py is at <root>/utils/paths.py
    return Path(__file__).resolve().parents[1]

def asset_path(*parts: str) -> Path:
    return project_root().joinpath("assets", *parts)