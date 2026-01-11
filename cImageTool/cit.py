#!/usr/bin/env python3
import pathlib, tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import PIL.Image as Image

PAD = 3
MAX_ATLAS_WIDTH = 2048

root = tk.Tk()
root.withdraw()
paths = filedialog.askopenfilenames(
    title="选择 PNG 图（可多选）",
    filetypes=[("PNG", "*.png"), ("All files", "*.*")]
)
if not paths:
    raise SystemExit(0)
paths = sorted(paths)
imgs = [Image.open(p).convert("RGBA") for p in paths]
n = len(imgs)

def ask_pack_method(n_pic: int):
    """返回 (mode, rows, cols)
       mode in {'h','v','grid'}
       后两项仅 grid 模式有意义"""
    top = tk.Toplevel(root)
    top.title("选择打包方式")
    top.geometry("320x220")
    top.grab_set()
    top.resizable(False, False)

    var_mode = tk.StringVar(value='grid')
    var_rows = tk.StringVar()
    var_cols = tk.StringVar()

    def nearest_square(n):
        cols = int(n**0.5 + 0.5)
        rows = (n + cols - 1) // cols
        return rows, cols
    def_rows, def_cols = nearest_square(n_pic)
    var_rows.set(str(def_rows))
    var_cols.set(str(def_cols))

    def validate(_=None):
        try:
            r, c = int(var_rows.get()), int(var_cols.get())
            ok = r * c >= n_pic
        except ValueError:
            ok = False
        lbl_hint.config(text='' if ok else '行×列 必须 ≥ 图片数', fg='red')
        btn_ok.config(state='normal' if ok else 'disabled')

    tk.Radiobutton(top, text="长条（水平）", variable=var_mode, value='h').pack(anchor='w', padx=20, pady=5)
    tk.Radiobutton(top, text="竖条（垂直）", variable=var_mode, value='v').pack(anchor='w', padx=20, pady=5)
    tk.Radiobutton(top, text="图集（行列可调）", variable=var_mode, value='grid').pack(anchor='w', padx=20, pady=5)

    frm = tk.Frame(top)
    frm.pack(pady=5)
    tk.Label(frm, text="行数").grid(row=0, column=0, padx=5)
    tk.Entry(frm, textvariable=var_rows, width=5, justify='center').grid(row=0, column=1, padx=5)
    tk.Label(frm, text="列数").grid(row=0, column=2, padx=5)
    ent_cols = tk.Entry(frm, textvariable=var_cols, width=5, justify='center')
    ent_cols.grid(row=0, column=3, padx=5)
    var_rows.trace_add('write', validate)
    var_cols.trace_add('write', validate)

    lbl_hint = tk.Label(top, text='')
    lbl_hint.pack()

    result = {'mode': 'grid', 'rows': def_rows, 'cols': def_cols}

    def on_ok():
        result.update(mode=var_mode.get(),
                      rows=int(var_rows.get()),
                      cols=int(var_cols.get()))
        top.destroy()

    btn_ok = tk.Button(top, text="确定", command=on_ok, width=10)
    btn_ok.pack(pady=10)
    validate()
    root.wait_window(top)
    return result['mode'], result['rows'], result['cols']

mode, rows, cols = ask_pack_method(n)

folder = pathlib.Path(filedialog.askdirectory(title="输出到哪里？"))
if not folder:
    raise SystemExit(0)
folder.mkdir(parents=True, exist_ok=True)

def add_border(img: Image.Image, pad: int) -> Image.Image:
    ow, oh = img.size
    nw, nh = ow + pad * 2, oh + pad * 2
    out = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    out.paste(img, (pad, pad))
    return out

if mode == 'h':        # hbox
    total_w = sum(img.width + PAD * 2 for img in imgs)
    max_h = max(img.height + PAD * 2 for img in imgs)
    sheet = Image.new("RGBA", (total_w, max_h), (0, 0, 0, 0))
    x = 0
    pos = []          # (x+PAD, y+PAD, w, h)
    for img in imgs:
        bordered = add_border(img, PAD)
        sheet.paste(bordered, (x, 0))
        pos.append((x + PAD, PAD, img.width, img.height))
        x += bordered.width

elif mode == 'v':      # vbox
    max_w = max(img.width + PAD * 2 for img in imgs)
    total_h = sum(img.height + PAD * 2 for img in imgs)
    sheet = Image.new("RGBA", (max_w, total_h), (0, 0, 0, 0))
    y = 0
    pos = []
    for img in imgs:
        bordered = add_border(img, PAD)
        sheet.paste(bordered, (0, y))
        pos.append((PAD, y + PAD, img.width, img.height))
        y += bordered.height

else:                  # grid
    cell_w = max(img.width + PAD * 2 for img in imgs)
    cell_h = max(img.height + PAD * 2 for img in imgs)
    sheet_w = cell_w * cols
    sheet_h = cell_h * rows
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    pos = []
    for idx, img in enumerate(imgs):
        r, c = divmod(idx, cols)
        if r >= rows:
            break
        bordered = add_border(img, PAD)
        x = c * cell_w
        y = r * cell_h
        off_x = (cell_w - bordered.width) // 2
        off_y = (cell_h - bordered.height) // 2
        sheet.paste(bordered, (x + off_x, y + off_y))
        pos.append((x + off_x + PAD, y + off_y + PAD, img.width, img.height))

first_name = pathlib.Path(paths[0]).stem
tex_file = f"{first_name}_texSET.png"
txt_file = folder / f"{first_name}_crop.txt"
lines = [f"# {tex_file}\n"]
for i, (x, y, w, h) in enumerate(pos):
    lines.append(
        f'image {pathlib.Path(paths[i]).stem} = Crop('
        f'({x}, {y}, {w}, {h}), '
        f'"{folder / tex_file}")'
    )
sheet.save(folder / tex_file, optimize=True)
txt_file.write_text("\n".join(lines), encoding="utf-8")
messagebox.showinfo("OKAY", f"已输出：\n{folder / tex_file}\n{txt_file}")