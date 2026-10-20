import collections
exec(open(__file__.replace('anim_bones', 'render_models')).read().split("if __name__ == '__main__':")[0])
for idx in list(range(18, 39)):
    b = image_blob(idx)
    rows = records(b, 0x10)
    info = sorted((s, b[o + 1] + 1, b[o + 2], b[o] & 3) for o, s, g in rows)
    mdl = records(b, 0x0C)
    parts = b[mdl[0][0] + 2] if mdl else None
    print(idx, 'model parts', parts, 'rows (id, bones, frames, enc):', info)
