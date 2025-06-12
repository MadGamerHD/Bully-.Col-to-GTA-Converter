# Bully .col to GTA Converter

A simple Python Tkinter GUI application that converts Bully collision (`.col`) files into a GTA III/VC/San Andreas compatible `.col` format (COL2), fixing range check issues, trimming oversized data, and minimizing duplicate/corrupt geometry.

---
✅ Your tool does support conversion from Bully .col files to GTA-compatible .col (COL2) format.

⚠️ But the converted files may not be 100% perfect or "clean," just usable — meaning they're good enough to load in Blender or be edited further.

## Features

* **Detects multiple collision chunks** within a single `.col` file.
* **Converts** each chunk to the GTA-compatible COL2 format.
* **Clamps** counts (spheres, boxes, faces, lines) to safe limits to avoid range checks.
* **Trims** large bodies of geometry data to a configurable maximum size (default 256 KB) to reduce lag.
* **Prevents overwriting** the original `.col` file by renaming output when source and destination paths match.
* **Simple GUI**: browse for input file and output folder, then click **Convert Bully .col(s)**.

---

## Requirements

* Python 3.7+
* Tkinter (usually included with Python)

---

## Usage

1. Run the converter:

   ```bash
   python fix_col_gui.py
   ```
2. In the GUI:

   * Click **Browse** to select your Bully `.col` file.
   * Click **Browse** to choose an output folder.
   * Click **Convert Bully .col(s)**.
3. Converted files will appear in the specified output directory, named `converted_<original>.col` (or with an index if multiple chunks).

---

## Configuration

* **Maximum geometry data size** can be adjusted in the script (`max_len` variable, default `256 * 1024`).
* **Clamp limits** (sphere/box/face/line counts) are defined in `convert_bully_col_to_sa`.

---

## Contributing

Feel free to:

* Submit issues or feature requests.
* Fork the repo and open pull requests.

Please keep code style consistent and include tests for new features.
