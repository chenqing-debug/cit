import pathlib
from PIL import Image

PAD = 3

def build_atlas(imgs, mode, rows, cols, out_folder, stem):
    """
    imgs: List[PIL.Image]
    mode: 'h'|'v'|'grid'
    rows,cols: int
    out_folder: Path
    stem: name
    return: (png_path, txt_path)
    """
    bordered = [add_border(im, PAD) for im in imgs]

    if mode == 'h':
        total_w = sum(b.width for b in bordered)
        max_h   = max(b.height for b in bordered)
        sheet = Image.new("RGBA", (total_w, max_h))
        x = 0
        pos = []
        for b, im in zip(bordered, imgs):
            sheet.paste(b, (x, 0))
            pos.append((x + PAD, PAD, im.width, im.height))
            x += b.width

    elif mode == 'v':
        max_w   = max(b.width for b in bordered)
        total_h = sum(b.height for b in bordered)
        sheet = Image.new("RGBA", (max_w, total_h))
        y = 0
        pos = []
        for b, im in zip(bordered, imgs):
            sheet.paste(b, (0, y))
            pos.append((PAD, y + PAD, im.width, im.height))
            y += b.height

    else:  # grid
        cell_w = max(b.width for b in bordered)
        cell_h = max(b.height for b in bordered)
        sheet_w = cell_w * cols
        sheet_h = cell_h * rows
        sheet = Image.new("RGBA", (sheet_w, sheet_h))
        pos = []
        for idx, (b, im) in enumerate(zip(bordered, imgs)):
            r, c = divmod(idx, cols)
            if r >= rows:
                break
            x = c * cell_w
            y = r * cell_h
            off_x = (cell_w - b.width) // 2
            off_y = (cell_h - b.height) // 2
            sheet.paste(b, (x + off_x, y + off_y))
            pos.append((x + off_x + PAD, y + off_y + PAD, im.width, im.height))

    png_path = out_folder / f"{stem}_texSET.png"
    txt_path = out_folder / f"{stem}_crop.txt"

    sheet.save(png_path, optimize=True)
    lines = [f"# {png_path.name}\n"]
    for i, (x, y, w, h) in enumerate(pos):
        pic_name = pathlib.Path(f"pic{i}").stem
        lines.append(f'image {pic_name} = Crop(({x},{y},{w},{h}), "{png_path}")')
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return png_path, txt_path


def add_border(img: Image.Image, pad: int) -> Image.Image:
    ow, oh = img.size
    nw, nh = ow + pad * 2, oh + pad * 2
    out = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    out.paste(img, (pad, pad))
    return out