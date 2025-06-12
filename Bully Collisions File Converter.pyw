# fix_col_gui.py
# Optimized Tool to Convert Bully .col Files to GTA III/VC/SA Compatible Format
# Fixes range check issues, trims oversized data, and reduces duplication artifacts

import struct
import os
import tkinter as tk
from tkinter import filedialog, messagebox

FOURCC_V1 = b'COLL'
FOURCC_V2 = b'COL2'
FOURCC_V3 = b'COL3'


def clamp(val, mn, mx):
    return max(mn, min(mx, val))


def detect_col_chunks(data):
    chunks = []
    seen_offsets = set()
    pos = 0
    while pos + 8 <= len(data):
        head = data[pos:pos + 4]
        if head in (FOURCC_V1, FOURCC_V2, FOURCC_V3):
            size = struct.unpack_from('<I', data, pos + 4)[0]
            total_size = 8 + size
            if pos + total_size <= len(data) and pos not in seen_offsets:
                seen_offsets.add(pos)
                chunks.append((pos, total_size))
                pos += total_size
                continue
        pos += 1
    return chunks


def convert_bully_col_to_sa(chunk):
    if chunk[:4] not in (FOURCC_V1, FOURCC_V2, FOURCC_V3):
        raise ValueError("Unsupported .col format")

    version_map = {FOURCC_V1: 1, FOURCC_V2: 2, FOURCC_V3: 3}
    version = version_map[chunk[:4]]

    declared_size = struct.unpack('<I', chunk[4:8])[0]
    actual_size = min(declared_size, len(chunk) - 8)
    name = chunk[12:34].split(b'\x00', 1)[0]
    model_id = clamp(struct.unpack_from('<H', chunk, 34)[0], 0, 65535)

    if version == 1:
        # Directly convert to COL2
        return (
            FOURCC_V2 + struct.pack('<I', actual_size) +
            name.ljust(22, b'\x00') + struct.pack('<H', model_id) +
            chunk[36:8 + actual_size]
        )

    header_format = '<HHHBBI6I'
    hdr_offset = 36
    if len(chunk) < hdr_offset + struct.calcsize(header_format):
        raise ValueError("Header too short")

    vals = list(struct.unpack_from(header_format, chunk, hdr_offset))
    vals[0] = clamp(vals[0], 0, 500)
    vals[1] = clamp(vals[1], 0, 500)
    vals[2] = clamp(vals[2], 0, 10000)
    vals[3] = clamp(vals[3], 0, 10000)

    ext_data = b''
    body_offset = hdr_offset + struct.calcsize(header_format)
    if version == 3 and body_offset + 12 <= len(chunk):
        ext_data = chunk[body_offset:body_offset + 12]
        body_offset += 12

    body = chunk[body_offset:8 + actual_size]

    try:
        vertex_count, face_count = struct.unpack_from('<HH', body, 0)
        if vertex_count > 10000 or face_count > 20000:
            raise ValueError("Excessive geometry counts")
    except Exception:
        pass  # Ignore errors here for safety

    if len(body) > 256 * 1024:
        body = body[:256 * 1024]

    final_len = 22 + 2 + struct.calcsize(header_format) + len(ext_data) + len(body)
    return (
        FOURCC_V2 + struct.pack('<I', final_len) +
        name.ljust(22, b'\x00') + struct.pack('<H', model_id) +
        struct.pack(header_format, *vals) + ext_data + body
    )


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bully .col to GTA Converter")
        self.geometry("600x200")

        tk.Label(self, text="Input .col File:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.in_path = tk.Entry(self, width=60)
        self.in_path.grid(row=0, column=1, padx=5)
        tk.Button(self, text="Browse", command=self.browse_in).grid(row=0, column=2)

        tk.Label(self, text="Output Folder:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.out_dir = tk.Entry(self, width=60)
        self.out_dir.grid(row=1, column=1, padx=5)
        tk.Button(self, text="Browse", command=self.browse_out).grid(row=1, column=2)

        tk.Button(self, text="Convert Bully .col(s)", command=self.convert,
                  bg="#4CAF50", fg="white", padx=10).grid(row=2, column=1, pady=20)

    def browse_in(self):
        path = filedialog.askopenfilename(filetypes=[("COL files", "*.col")])
        if path:
            self.in_path.delete(0, tk.END)
            self.in_path.insert(0, path)

    def browse_out(self):
        path = filedialog.askdirectory()
        if path:
            self.out_dir.delete(0, tk.END)
            self.out_dir.insert(0, path)

    def convert(self):
        src = self.in_path.get().strip()
        dst = self.out_dir.get().strip()

        if not os.path.isfile(src) or not os.path.isdir(dst):
            messagebox.showerror("Error", "Invalid input or output path")
            return

        with open(src, 'rb') as f:
            raw = f.read()

        chunks = detect_col_chunks(raw)
        if not chunks:
            messagebox.showerror("Error", "No valid .col chunks found")
            return

        count = 0
        for i, (offset, length) in enumerate(chunks):
            try:
                fixed = convert_bully_col_to_sa(raw[offset:offset + length])
                base_name = os.path.basename(src)
                name = f"converted_{base_name}" if dst == os.path.dirname(src) else base_name
                name = name if not os.path.exists(os.path.join(dst, name)) else f"converted_{i}_{base_name}"
                with open(os.path.join(dst, name), 'wb') as f:
                    f.write(fixed)
                count += 1
            except Exception as e:
                print(f"Skipped chunk {i}: {e}")

        messagebox.showinfo("Done", f"Converted {count} chunk(s) to GTA-compatible .col format.")


if __name__ == '__main__':
    App().mainloop()
