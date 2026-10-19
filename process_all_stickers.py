import os
from collections import deque
from PIL import Image
import numpy as np

src_dir = 'd:/tool/2010/images/drive'
out_dir = 'd:/tool/2010/images/stickers'
os.makedirs(out_dir, exist_ok=True)

def process_sticker(in_path, out_path):
    img = Image.open(in_path).convert('RGB')
    w, h = img.size
    arr = np.array(img, dtype=float)
    
    # Check corner brightness to determine background color
    corners = np.array([arr[0, 0], arr[0, -1], arr[-1, 0], arr[-1, -1]])
    bg_color = np.median(corners, axis=0)
    
    # Pixel is background candidate if close to bg_color or near white (R,G,B > 220)
    diff = np.max(np.abs(arr - bg_color), axis=2)
    is_bg_candidate = (diff < 30) | ((arr[:, :, 0] > 225) & (arr[:, :, 1] > 225) & (arr[:, :, 2] > 225))
    
    # BFS flood fill from outside borders
    bg_mask = np.zeros((h, w), dtype=bool)
    q = deque()
    for x in range(w):
        q.append((0, x)); q.append((h - 1, x))
        bg_mask[0, x] = True; bg_mask[h - 1, x] = True
    for y in range(h):
        q.append((y, 0)); q.append((y, w - 1))
        bg_mask[y, 0] = True; bg_mask[y, w - 1] = True
        
    while q:
        y, x = q.popleft()
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not bg_mask[ny, nx]:
                if is_bg_candidate[ny, nx]:
                    bg_mask[ny, nx] = True
                    q.append((ny, nx))
                    
    # Anti-alias alpha matting:
    # Outer pure background: alpha = 0
    L = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    alpha = np.ones((h, w), dtype=float)
    alpha[bg_mask & (L > 240)] = 0.0
    
    # Transition zone
    trans = bg_mask & (L <= 240)
    alpha[trans] = np.clip((240.0 - L[trans]) / (240.0 - 60.0), 0.0, 1.0)
    
    # Unblend color to remove white fringe
    out_rgb = np.copy(arr)
    trans_idx = np.where((alpha > 0) & (alpha < 1))
    for c in range(3):
        ch = out_rgb[:, :, c]
        unblended = (ch[trans_idx] - (1.0 - alpha[trans_idx]) * 255.0) / np.maximum(alpha[trans_idx], 0.05)
        ch[trans_idx] = np.clip(unblended, 0.0, 255.0)
        
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
    rgba[:, :, 3] = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    
    coords = np.argwhere(rgba[:, :, 3] > 15)
    if len(coords) == 0:
        print(f"Warning: Empty cutout for {in_path}")
        return False
        
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)
    
    pad = 8
    res = Image.fromarray(rgba)
    res_cropped = res.crop((max(0, x_min - pad), max(0, y_min - pad), min(w, x_max + pad), min(h, y_max + pad)))
    res_cropped.save(out_path)
    return True

processed_files = []
for idx, f in enumerate(sorted(os.listdir(src_dir))):
    if not f.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue
    inp = os.path.join(src_dir, f)
    base_name = os.path.splitext(f)[0]
    out_name = f"sticker_{base_name}.png"
    outp = os.path.join(out_dir, out_name)
    ok = process_sticker(inp, outp)
    if ok:
        processed_files.append(out_name)
        print(f"[{idx+1}] Processed {f} -> {out_name}")

print(f"Successfully processed {len(processed_files)} stickers!")
