# data/images/

Drop in a real photo or illustration for a physical model here, named
`<model_id>.png`, `<model_id>.jpg`, or `<model_id>.jpeg` — e.g.
`mass_spring_damper.png`. Picked up automatically at registry-load time
(process start), no code change needed.

**Aspect ratio**: must land within ~15% of either 1:1 (square) or 16:9
(widescreen), judged multiplicatively (i.e. an image twice as wide as it
"should" be is rejected the same way one twice as narrow would be — not
just "too wide"). An image outside both windows is rejected at
registry-load time: a warning prints to the server log
(`[registry] image warning for '<model_id>': ...`) explaining why, and the
apparatus falls back to a placeholder from `data/memes/` instead of
breaking anything.

Only PNG and JPEG are read (no Pillow dependency — see
`src/physics/models/artwork.py`'s module docstring for why). Other formats
are treated as unsupported and rejected the same way a bad aspect ratio is.

No image for a model_id at all isn't a warning-worthy problem — it's just
an unfilled slot, and gets the same placeholder fallback silently.
