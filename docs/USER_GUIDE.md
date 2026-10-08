# Using PaintPlus

## Familiar drawing

Home contains Select, Pencil, Brush, Eraser, Fill, Text, Shapes, Eyedropper and
Crop. Left-click uses Color 1; right-click uses Color 2 for drawing. Right-click a
palette square assigns Color 2. Edit colors opens the normal color chooser.
Your special blue, **#1847F1 / RGB 24, 71, 241**, is the final palette square with
a slightly stronger border. Brushes have a pixel size control and Round/Marker/Calligraphy/Airbrush styles. Shapes include
rectangle, rounded rectangle, ellipse, line and triangle with optional fill.

Undo/redo: Ctrl+Z / Ctrl+Y. The history retains up to 30 changes in memory and is
not persisted in project files. Drawing strokes become editable image objects;
merge drawing layers when you want one raster layer. You can hide the layers and
assets using View, and continue drawing without managing them.

Select moves an object. Ctrl+click adds/removes objects from the selection; drag
empty space to select objects fully within a rectangle. The Select dropdown also
has **Rectangular selection**, which lifts pixels from the selected unlocked,
unrotated image onto an independent object. Choose a layer first when selecting
pixels from overlapping images. Undo restores the original pixels. This version
does not have a free-form lasso.

Crop: drag a rectangle to crop the whole scene. Original layer pixels outside the
new canvas remain in the project; Undo restores the canvas. Zoom with Ctrl+mouse wheel or the bottom
slider; View → Fit canvas fits the scene without changing its pixels.

## Assemble a scene

1. File → Open a background image.
2. Click **Lock Background** so it cannot be accidentally moved or painted on.
3. In Assets, click **+ Folder** and choose an existing folder of PNGs.
4. Double-click a thumbnail to insert it. Ctrl+click multiple thumbnails, then
   **Insert selected** to add them together. You can also drag them to the canvas.
5. Drag an object to move it (or use arrow keys; Shift moves 10 pixels). Drag corner/edge handles to resize. The round handle
   rotates; hold Shift for 15° steps. View lets you turn off aspect-ratio locking.
6. **Resize / Rotate** offers exact pixels or percentages, angle entry, flips,
   90°/180° buttons and nearest-neighbour resizing for pixel art.

Each image is its own layer/object. Original pixels are retained across repeated
resizing. Live preview uses Qt smooth interpolation; exported images use Lanczos
resizing and bicubic rotation. Resize operations never replace the original image.

## Assets

Assets references existing folders; it does not copy a whole collection into the
app. Search filters names. Favorites and Recently used provide fast access.
Thumbnail size is adjustable. Ctrl+click selects multiple thumbnails.
**+ PNGs** explicitly copies chosen files into the selected folder, using a new
number if a filename already exists. Manage renames library labels, creates real
subfolders, or removes a library reference without deleting its files. Renaming a
category does not rename your disk folder. Only top-level PNGs in each referenced
folder are listed; add subfolders separately. New insertions read current disk
files; existing scene objects are embedded in the project.

## Layers and groups

Check/uncheck a layer to show/hide it. Select layers with Ctrl+click. Double-click
or F2 renames. + adds a transparent layer. Duplicate, delete, lock/unlock, arrows
and drag reordering are available. Ctrl+G groups selected objects; Ctrl+Shift+G
ungroups. Canvas selection of one group member selects the group. Drag handles
move/resize/rotate the selected group together. Exact numeric transform entry
currently applies to one object at a time.

Merge rasterizes selected layers at canvas resolution; it loses their independent
editing information. Use Undo if needed. Merge adjacent layers for a predictable
stacking result. Text objects stay editable until you paint/erase on or merge them;
use **Edit selected text** to change their content/font later.

## Save

**Ctrl+S** saves an editable `.paintplus` project. Keep this file if you want to
reopen and adjust objects later. Ctrl+Shift+S saves a new project copy.

For **Quick Save**, choose an output folder once with Folder, type a filename,
choose PNG/JPEG/BMP/TIFF/WebP, then click Quick Save or F6. Existing exports are
never overwritten: `Scene.png`, `Scene (2).png`, etc. Hover Folder to see the full
output path. Quick Save exports an image; it does not replace saving your project.
Ctrl+E is normal Export/Save As for images. JPEG/BMP flatten transparency on white.

Ctrl+C copies selected objects as one transparent clipboard image; with no
selection it copies the whole scene. Ctrl+X cuts unlocked selected objects.
Ctrl+V inserts a clipboard image or copied local image files. PNG clipboard alpha
is preserved when the receiving program supports it. Other programs may flatten it.

## Shortcuts and background removal

Settings → Edit shortcuts lets you assign keys to tools/actions; duplicate
assignments are rejected. Defaults: 0 Select, 1 Pencil, 2 Brush, 3 Eraser, 4 Fill,
5 Text, 6 Shape, 7 Eyedropper, 8 Crop, 9 Move. Typing in input boxes stays ordinary
text input. Frequently used asset-specific shortcuts are not in this version.

Select one unlocked image and click **Remove Background**. The bundled small model
runs on your CPU locally. You can undo the result. Settings offers edge smoothing
from 0–5 pixels. Quality depends on the subject; this small general model may need
manual erasing for fine hair, low contrast or complex scenes. No images leave
this computer. Original transparent pixels stay transparent.
