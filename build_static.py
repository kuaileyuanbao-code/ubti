import os
import shutil
from pathlib import Path

from app import app


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def main() -> None:
    DIST.mkdir(exist_ok=True)

    base_url = os.getenv("SITE_URL", "https://example.com").rstrip("/") + "/"
    with app.test_client() as client:
        response = client.get("/ubti", base_url=base_url)
        if response.status_code >= 400:
            raise RuntimeError(f"Failed to build static page: HTTP {response.status_code}")
        (DIST / "index.html").write_text(response.get_data(as_text=True), encoding="utf-8")

    shutil.copytree(ROOT / "static", DIST / "static", dirs_exist_ok=True)


if __name__ == "__main__":
    main()
