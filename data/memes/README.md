# data/memes/

Placeholder images shown when a model has no image yet, or its image was
rejected (wrong aspect ratio / unsupported format) — see
`data/images/README.md` and `src/physics/models/artwork.py`.

Any `.png`, `.jpg`, `.jpeg`, or `.svg` file in this directory is eligible.
Which one a given model gets is picked deterministically (a stable hash of
the model_id, not directory order or randomness) — the same model always
gets the same placeholder.

Keep these original, not screenshots of existing meme templates or
copyrighted characters — this repo is public and these ship in the
deployed artifact. `shrug.svg` and `under-construction.svg` are small
hand-drawn SVGs in the same visual language as the apparatus schematics
(`web/schematics.js`), not a reference to any existing meme.
