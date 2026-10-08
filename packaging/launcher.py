"""Normal windowed launch with a visible error if startup fails."""

import ctypes
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
try:
    from paintplus.app import main

    raise SystemExit(main())
except Exception:
    message = traceback.format_exc()
    folder = (
        Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "GradeA" / "PaintPlus"
    )
    folder.mkdir(parents=True, exist_ok=True)
    log = folder / "startup-error.txt"
    log.write_text(message, encoding="utf-8")
    if sys.platform == "win32":
        ctypes.windll.user32.MessageBoxW(
            None,
            f"PaintPlus could not start.\n\nDetails were saved to:\n{log}\n\n{message[-1500:]}",
            "GradeA PaintPlus",
            0x10,
        )
    else:
        print(message, file=sys.stderr)
    raise SystemExit(1)
