I want you to build me a Windows desktop image-editing program based very closely on the current version of Microsoft Paint.

**IMPORTANT: I am not tech savvy.** Please handle the technical decisions yourself wherever reasonable. The finished program needs to be extremely easy for me to install and use. Ideally I should download/install it like a normal Windows program without needing to install Python, use Command Prompt, compile code, edit configuration files, or understand programming.

I will provide a screenshot of Microsoft Paint. I want the program's interface to look **as close to/identical to the current Paint interface in my screenshot as reasonably possible**, while using original/non-proprietary assets where necessary. The idea is that I should immediately feel like I am using Paint rather than learning a completely different image editor.

## Core Paint functionality

Reproduce the normal Paint experience, including the usual things such as:

- Canvas
- Pencil
- Brushes
- Eraser
- Fill/bucket
- Eyedropper/colour picker
- Shapes
- Text
- Selection tools
- Crop
- Zoom
- Undo/redo
- Copy/paste and Windows clipboard support
- PNG/JPEG/BMP and other sensible image formats
- Normal Paint-like colour palette
- Normal keyboard/mouse interactions wherever practical

The application should work **locally/offline**. No telemetry, accounts, cloud requirement, or unnecessary internet access.

## Much better object resizing

This is particularly important.

I dislike the way current Microsoft Paint resizes pasted/selected images. I sometimes paste an image into Microsoft Word, resize it there, and copy it back into Paint because Word produces much nicer-looking results.

I want this program's resizing to be noticeably better.

Use high-quality image resampling such as Lanczos/bicubic where appropriate. Pasted images/objects should retain their original image data while I am manipulating them, rather than repeatedly degrading the image every time I resize it.

I want:

- Smooth resizing by dragging handles
- Corner and edge resize handles
- Aspect-ratio locking
- Exact width/height entry
- Percentage resizing
- High-quality interpolation
- Optional nearest-neighbour/pixel-art resizing
- Smooth visual preview while resizing
- Avoid quality degradation if I make something smaller and then larger again before committing it

The overall goal is resizing that feels at least as pleasant as resizing an image in Microsoft Word.

## Object rotation

Selected objects/images need to be rotatable.

Include:

- Free rotation using a rotation handle
- Exact numerical angle entry
- Quick 90°, 180° etc. rotations
- Flip horizontal/vertical

Rotation should retain good image quality.

## Custom keyboard shortcuts

I want to be able to assign my own keyboard shortcuts to tools/actions.

In particular, I want the option to make the number keys **0–9 select different tools**.

There should be a simple shortcut settings screen so I can decide what each key does rather than having the shortcuts permanently hard-coded.

## PNG Asset Library

A major part of my workflow involves repeatedly adding PNG images I already have saved on my computer onto pictures/scenes I am making.

Build a **collapsible Asset Library drawer/bar** into the application. It should stay out of the way when closed and quickly expand when needed.

The asset library should:

- Display PNG assets as thumbnail previews
- Let me choose between different asset folders/categories
- Let me create new folders/categories
- Let me add new PNGs to existing folders very quickly
- Let me rename/manage folders
- Allow drag-and-drop where sensible
- Have Favorites
- Have Recently Used assets
- Have search
- Allow adjustable thumbnail sizes

I should be able to select/deselect assets easily by clicking them.

I also want to be able to select **multiple assets at once** and add them to the canvas together.

A single asset should also have a very fast way of being inserted, such as double-clicking it.

When inserted, PNG transparency must be preserved.

Ideally the program should reference my existing asset folders rather than copying every PNG into the program itself. That way a huge asset collection doesn't make the application itself huge.

Each inserted asset should initially remain independently editable so I can:

- Move it
- Resize it
- Rotate it
- Duplicate it
- Delete it
- Run background removal on it

Frequently used assets could optionally have their own keyboard shortcuts.

## Simple Layers

Add layers, but **keep them much simpler and easier than Photoshop**.

The layers system is mainly for creating animation scenes where I need to move characters, props and backgrounds around without everything becoming fiddly.

Have a collapsible Layers panel with:

- Layer thumbnail
- Layer name
- Show/hide
- Lock/unlock
- Drag to reorder
- Create
- Delete
- Duplicate
- Rename
- Merge

PNG assets should have the option to automatically be inserted onto their own layer.

Include a very convenient **Lock Background** function so I can't accidentally move/select my background while arranging characters.

Support selecting multiple objects/layers and **grouping them**. For example, if a character consists of several separate PNG pieces, I should be able to group them and then move, resize or rotate the whole character together.

I should still be able to completely ignore layers and use the application like ordinary Paint if I want.

When exporting a normal PNG/JPEG, layers should flatten automatically.

The application's own project format should preserve layers, objects, groups, rotations, text and other editable information so I can reopen a scene later and continue editing it.

## Quick Save system

I don't want to constantly use Save As, navigate folders and enter filenames.

Add a permanent but unobtrusive **Quick Save area**, probably around the bottom-right of the interface.

It should have something like:

Output folder: [chosen folder]
Filename: [text box]
Format: [PNG/JPEG/etc.]
[SAVE]

I should be able to choose my output folder once using a folder icon/button.

After that, I type a filename and click SAVE and the image immediately saves there.

Normal Ctrl+S and Save As should still exist.

Handle duplicate filenames sensibly, either by warning me or automatically offering something like:

image.png
image (2).png

## Special default blue colour

Add this exact colour to the built-in palette:

**RGB: 24, 71, 241**
**Hex: #1847F1**

This colour is particularly important to me.

Put it as the **last colour in the normal palette** and visually distinguish it slightly from the ordinary colours so I can immediately find it. Don't make the distinction ugly or distracting.

## Offline AI background removal

Include a simple **Remove Background** feature powered by a local AI model.

Important requirements:

- Works completely offline once installed
- Images do not need to be uploaded anywhere
- Simple one-click background removal
- Preserve transparency
- Preferably offer basic edge/refinement controls if practical
- CPU operation should work
- GPU acceleration can be used when available, but should not be required

Keep the AI component reasonably compact. A total application installation somewhere around **150–350 MB** would be perfectly acceptable if practical, although functionality and reliability matter more than hitting an exact number.

## General design philosophy

This should NOT feel like Photoshop or a complicated professional graphics package.

Think:

**"Microsoft Paint, except specifically improved for quickly assembling images and animation scenes from lots of reusable PNG assets."**

The most important improvements over Paint are:

1. Much better pasted-image/object resizing quality
2. Easy move/resize/rotation of objects
3. Simple layers
4. Extremely fast reusable PNG asset workflow
5. Custom shortcuts
6. Quick saving
7. Offline background removal

Despite those additions, keep the interface uncluttered and familiar.

**Visually, stay extremely close to the Microsoft Paint screenshot I provide.** New functionality such as Layers and Assets should preferably use collapsible panels/drawers so that when they are closed the program still looks and feels very much like normal Paint.

## Installation and safety

I use Windows and I am not technically knowledgeable.

Please make installation **as foolproof as possible**.

I do NOT want instructions like:

- Install Python
- Open Command Prompt
- Run pip
- Compile this
- Install dependencies manually
- Modify PATH
- Edit configuration files

Ideally give me a normal Windows installer or self-contained application where the experience is basically:

**Download → scan it if desired → double-click installer → follow simple installer → launch program.**

If Windows SmartScreen or antivirus warnings are likely because the application is unsigned, explain this clearly in plain English rather than assuming I understand developer terminology.

Keep the source code available as well so the application is transparent and inspectable.

Do not include telemetry, advertising, unnecessary network connections, hidden background processes, startup persistence or unrelated software.

Please also provide a SHA-256 checksum for downloadable builds so the file can be verified.

I will probably scan the installer/application with Windows Security or another malware scanner before installing it, so please make the build straightforward to inspect and scan.

## Development approach

Please build this as a proper Windows application rather than merely giving me example code.

You can develop it in stages, but I ultimately want an **installable program I can actually use and test**.

For the first usable version, prioritize the fundamental Paint interface plus:

- Canvas/editing
- Clipboard
- High-quality object movement/resizing
- Rotation
- Layers
- PNG Asset Library
- Custom shortcuts
- Special #1847F1 colour
- Quick Save

Then add/refine offline AI background removal and more advanced polish.

Please test the application as much as reasonably possible before giving me an installer.

Most importantly: **I am going to attach a screenshot of the version of Microsoft Paint whose appearance I want copied. Use that screenshot as the primary visual reference for the UI.**