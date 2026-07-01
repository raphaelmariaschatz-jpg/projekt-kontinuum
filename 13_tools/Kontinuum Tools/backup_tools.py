from __future__ import annotations
from pathlib import Path
from datetime import datetime
import zipfile


class BackupTools:
    @staticmethod
    def zip_folder(src: str | Path, dst_zip: str | Path | None = None) -> Path:
        src = Path(src)
        if dst_zip is None:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst_zip = src.parent / f"{src.name}_backup_{stamp}.zip"
        dst_zip = Path(dst_zip)
        dst_zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(dst_zip, "w", zipfile.ZIP_DEFLATED) as z:
            for file in src.rglob("*"):
                if file.is_file():
                    z.write(file, file.relative_to(src))
        return dst_zip
