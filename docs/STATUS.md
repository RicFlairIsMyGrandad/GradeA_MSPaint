# Version 0.1.0 scope

Implemented: offline native Qt editor; Paint-style Home/View ribbon and palette;
collapsible Assets/Layers; pencil, brushes, eraser, bucket, eyedropper, basic
shapes, editable text; object and rectangular selection; crop/zoom/undo/redo;
image clipboard; PNG/JPEG/BMP/TIFF/WebP; original-pixel resize with eight handles,
aspect lock, pixels/percent entry, Lanczos export and pixel-art mode; free/numeric
rotation, flips; PNG folder references, search, favorites, recent, multi-insert,
drag/drop, thumbnail size and folder/category management; simple image layers,
locking, reorder, duplicate, rename, merge and group transforms; project saving;
Quick Save with duplicate-name numbering; editable shortcuts and special blue;
local CPU background removal with a bundled model and edge smoothing.

Limitations: first usable preview, not a complete clone of Microsoft Paint. No
lasso selection, full Paint brush/shape catalog, live editable vector shapes,
asset-specific shortcuts, group numeric transform dialog, GPU AI, manual AI mask
brush, custom color-slot persistence, autosave or crash recovery. Painting strokes
are separate objects/layers. Per-object background removal is destructive to
that object's stored pixels after completion (Undo restores it); resize/rotation
remain nondestructive. Rotated selection resize handles use an axis-aligned
bounding box; more precise local-axis handles are future polish. Group selection
supports shared ID transforms, not nested groups. Asset enumeration is synchronous
and top-level per folder; very large collections can take time to scan. Asset
drops insert at staggered default positions, not exactly at the pointer.

Validation: 46 automated editor tests passed on Linux and native Windows. The
Windows CI run also verified the assembled runtime, clipboard, saving/export,
project loading and local CPU AI, then performed a silent installation, checked
the installed runtime, and ran the uninstaller. The published installer and
portable ZIP are available in the GitHub preview release with their SHA-256 hashes.

Build evidence: https://github.com/RicFlairIsMyGrandad/GradeA_MSPaint/actions/runs/37773645577
Downloads: https://github.com/RicFlairIsMyGrandad/GradeA_MSPaint/releases/tag/v0.1.0-preview

Manual clean-PC Windows 10/11 testing, display scaling, file association behavior,
and broad usability checks remain outstanding. This is an unsigned preview, with
no publisher signature or malware-scanner verdict supplied.
