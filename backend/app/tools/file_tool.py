from pathlib import Path

def read_file(path:str,workspace:str)->dict:
    root=Path(workspace).resolve(strict=True)

    if not root.is_dir():
        raise NotADirectoryError("The workspace must be a dictionary")

    target= (root / path).resolve(strict=True)
    if not target.is_relative_to(root):
        raise PermissionError("Access outside the workspace is denied.")

    if not target.is_file():
        raise ValueError("The requested path is not a file.")

    # Limit the amount of data read.
    if target.stat().st_size > 1_000_000:
        raise ValueError("File exceeds the 1 MB limit.")

    return {
        "path":str(target),
        "content":target.read_text(encoding="utf-8")
    }