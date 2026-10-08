# Offline background removal

The full Windows build bundles ONNX Runtime CPU and U²-Net's small `u2netp` model
(about 4.6 MB). No installation-time or runtime download is needed by the user.
It is a general saliency model, not an interactive segmentation editor. It can
leave imperfect edges or remove parts of difficult subjects. Settings offers a
small edge smoothing adjustment; erasing and Undo provide manual correction.
GPU is not required; automatic GPU acceleration is not implemented in v0.1.

Contributor setup: install the `ai` extra, then run
`python packaging/fetch_model.py`. The build downloader uses verified HTTPS and
checks the model's pinned SHA-256 before saving. Inference checks the hash again.
The application never invokes the downloader. `PAINTPLUS_MODEL_PATH` can point
to the same verified model in a development environment; arbitrary models are
rejected because tensor shapes/preprocessing must match.

The worker resizes an RGB input to 320×320, applies U²-Net ImageNet normalization,
runs ONNX CPU inference, normalizes and upsamples the predicted alpha mask, then
multiplies it by the image's existing alpha. Color pixels and original image size
are preserved. Inference output is committed only if the same document and image
pixels still exist and the layer is unlocked. Successful edits are undoable.

Model source and checksum: [models/README.md](../models/README.md).
The Apache-2.0 upstream model/project license is bundled alongside it.
