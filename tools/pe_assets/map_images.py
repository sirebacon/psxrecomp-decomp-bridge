exec(open(__file__.replace('map_images', 'render_models')).read().split("if __name__ == '__main__':")[0])
for idx in range(0, 80):
    s0 = u16(ram, 0x930D8 + 2 * idx); s1 = u16(ram, 0x930D8 + 2 * idx + 2)
    if not 0 < s1 - s0 < 2000: print(idx, 'size', s1 - s0); continue
    try:
        b = image_blob(idx)
        d = word(b, 4)
        if d + 0x30 > len(b): print(idx, 'no dir'); continue
        desc = word(b, d + 0x28); at = desc & 0x3fffff; tims = []
        for i in range(min(desc >> 22, 12)):
            r = at + 20 * i; src = word(b, r + 4); rect = word(b, r + 8); rect2 = word(b, r + 16); sec = word(b, r + 12)
            tims.append(((rect >> 10) & 0x7ff, rect >> 21, rect & 0x3ff, src >> 24 or 256, 'pal', (rect2 >> 10) & 0x7ff, rect2 >> 21) if sec & 0xffffff else ((rect >> 10) & 0x7ff, rect >> 21, rect & 0x3ff, src >> 24 or 256))
        print(idx, 'sectors', s1 - s0, 'models', word(b, d + 0x0C) >> 22, 'rows', word(b, d + 0x10) >> 22, 'tims', desc >> 22, tims[:6])
    except Exception as e: print(idx, 'err', str(e)[:40])
