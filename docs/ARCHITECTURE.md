# Architecture and future changes

- `model.py`: PIL-backed document, immutable-original transform rendering,
  undo/redo, atomic project saving, compositing, export and filename handling.
- `canvas.py`: Qt canvas and mouse gestures, live smooth source-image preview,
  move/resize/rotate group transforms, drawing, rectangular extraction and crop.
- `app.py`: main window, Paint-style ribbon, clipboard, save flows and layer actions.
- `assets.py`: reference-based library, persistent favorites/recent/search and drag data.
- `dialogs.py`: transforms, shortcuts and editable text.
- `background.py`: checksum-pinned optional offline U²-Net inference, CPU-only by
  default, performed in a worker thread. No runtime download path exists.
- `packaging`: hash-locked Windows runtime assembly, NSIS installer and packaged
  smoke test. Runtime binaries are separate from inspectable Python source.

The current scene model deliberately treats each placed image, text raster or
paint stroke as one layer/object. Groups are shared IDs and can be transformed
as a selection. Text retains content/font metadata as well as its rendering.
This keeps the UI simpler than a general vector/multilayer graphics package.

A version-1 `.paintplus` file is a ZIP with `document.json` and original RGBA PNGs
in `images/`. Metadata includes canvas dimensions and ordered layers with IDs,
position, displayed width/height, clockwise angle, visibility, locking, flips,
group, resampling mode and text properties. Loading checks the version/canvas
bounds and caps total uncompressed content at 512 MB. It never extracts archive
paths onto disk. Unsupported versions fail visibly rather than being guessed.
Saving uses a temporary file and atomic replacement. Assets are embedded when
inserted so projects survive moving/deleting the source PNG collection.

To improve/replace AI background removal, keep `remove_background(image)` as an
RGBA-in/RGBA-out service and change the local backend. Update provenance/hash,
license notices, packaging and inference tests together. The UI already isolates
inference in a QThread, rejects stale results after document/pixel changes, and
makes completed edits undoable. GPU providers and interactive masks can be added
without replacing the app or project model.

Performance boundary: CPU raster rendering and full document snapshots favor
small/medium scenes. History is capped at 30 states; large canvases/many assets
can consume significant memory. A tiled raster cache and delta undo history would
be appropriate future improvements. Imported images are capped at 64 million
pixels; all image transformations are export-time resampling of original pixels.
