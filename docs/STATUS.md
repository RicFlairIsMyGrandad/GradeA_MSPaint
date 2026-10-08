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

Linux offscreen GUI and document/CPU inference tests verify the development build.
The Windows packages can be assembled on Linux, but native Windows clipboard,
file associations, install/uninstall, display scaling and launch must be checked
on Windows. The CI configuration includes those packaged runtime checks but
must actually run before reporting them passed. No signing or malware scanner
verdict is supplied. Do not describe the preview as a verified production release.

Validation in the development environment: 46 automated tests passed, including
actual Qt mouse/keyboard gestures, clipboard roundtrip, PNG transparency, every
export format, project roundtrip, undo/redo, asset multi-insert, transforms, groups,
Quick Save duplicate handling, panel persistence and real local ONNX CPU inference.
An original example subject retained opaque face pixels while its white background
was removed. A Windows x64 installer and portable runtime were assembled using
verified dependencies. Native Windows validation remains outstanding.
