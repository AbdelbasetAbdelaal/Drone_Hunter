DRONE HUNTER — INDIVIDUAL ENVIRONMENT ASSETS v05

Source:
The exact environment sheet supplied in this conversation.

Extraction:
The sheet was segmented using its alpha/foreground information into
298 detectable individual foreground components, organized into
five sector folders.

Each sector:
  individual_assets/png/            = extracted PNG at source resolution
  individual_assets/4x_reference/   = 4x Lanczos inspection/reference copy
  MANIFEST.json                     = exact source coordinates and files

Important quality limitation:
The supplied master image is 1536x1024. The individual assets cannot
contain more real visual detail than that source. The 4x files are
upscaled references, NOT native 4K artwork.

Recommended Antigravity workflow:
1. Use each extracted PNG as the visual reference for one asset.
2. Recreate important assets as independent native 2048x2048 or 4096x4096
   transparent PNGs.
3. Do NOT use the master sheet as a gameplay background.
4. Build each sector procedurally/modularly from the individual assets.
