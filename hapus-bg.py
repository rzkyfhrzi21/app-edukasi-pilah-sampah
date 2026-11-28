#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
  HAPUS BACKGROUND, DROP-SHADOW & KOMPRESI RINGAN CONSTRUCT 2
  Proyek: Edukasi Recycle Bin (run.bat -> Opsi [5] / hapus-bg.bat)
====================================================================
Penyempurnaan Algoritma v2:
  1. Smart Exterior + Drop-Shadow Removal (HSV + Flood-Fill):
     - Menghapus latar belakang putih/terang SEKALIGUS bayangan abu-abu
       (drop-shadow seperti RGB 165..235 dengan saturasi rendah) yang menempel
       di luar garis tepi (outline) gelap tombol/objek!
     - Tetap melindungi warna putih/terang di dalam objek (seperti tulisan
       "CREDITS", "MULAI BERMAIN", baju seragam putih, mata, nasi, gelas)
       karena bagian dalam terlindungi oleh garis outline tertutup.
  2. Color Decontamination & Edge Anti-Aliasing:
     - Menghilangkan pinggiran/halo putih & abu-abu pada 1-2 piksel terluar.
  3. Standar Ukuran & Kompresi Ringan Construct 2 (AGENTS.md):
     - Selalu menghasilkan angka piksel GENAP.
     - Otomatis menyimpan 2 versi ringan (< 100 KB):
       * <timestamp>_NNN_BG-1X1.png  (Kanvas persegi 1:1)
       * <timestamp>_NNN_BG-ORIG.png (Rasio asli yang sudah di-scale ke layar 1280x720)
"""

import os
import sys
import argparse
import cv2
import numpy as np
from PIL import Image
from datetime import datetime


def make_ts_prefix(out_dir: str, seq_no: int = 1) -> str:
    """Buat prefix nama file berdasarkan timestamp + nomor urut unik.
    Format: DD-MM-YYYY_HH-MM-SS_NNN  (contoh: 25-11-2026_01-25-40_001)
    Jika sudah ada file di out_dir dengan prefix yang sama (misal dijalankan 2x
    dalam detik yang sama), otomatis menaikkan seq_no sampai tidak bertabrakan.
    """
    base_ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    existing = set()
    if out_dir and os.path.isdir(out_dir):
        for fname in os.listdir(out_dir):
            if fname.startswith(base_ts + "_"):
                existing.add(fname)

    cur = max(1, int(seq_no))
    while True:
        prefix = f"{base_ts}_{cur:03d}"
        if not any(fname.startswith(prefix + "_") for fname in existing):
            return prefix
        cur += 1

# Standar Ukuran Ideal Construct 2 (mengacu pada AGENTS.md)
C2_PRESETS = {
    "auto_smart":        ("Otomatis Deteksi Ukuran Ideal Construct 2 (Rekomendasi)", "auto"),
    "bg_1280x720_jpg":   ("Latar Belakang / Background JPG (1280 x 720 px, < 200 KB)", "bg_jpg"),
    "sampah_140x140":    ("Objek Sampah (140 x 140 px)", (140, 140)),
    "ikon_100x100":      ("Tombol Ikon / Navigasi / D-Pad (100 x 100 px)", (100, 100)),
    "tombol_380x96":     ("Tombol Menu & Opsi Kuis (380 x 96 px)", (380, 96)),
    "judul_660x220":     ("Banner Judul Utama (660 x 220 px)", (660, 220)),
    "dialog_640x380":    ("Papan Dialog, Soal & Pop-up (640 x 380 px)", (640, 380)),
    "tong_200x260":      ("Tempat Sampah / Bins (200 x 260 px)", (200, 260)),
    "karakter_260x380":  ("Karakter Siswa di Menu/Dialog (260 x 380 px)", (260, 380)),
    "karakter_120x160":  ("Karakter Siswa di Simulasi (120 x 160 px)", (120, 160)),
    "rating_320x120":    ("HUD Rating Bintang 1-3 (320 x 120 px)", (320, 120)),
    "skor_220x70":       ("HUD Papan Skor Kecil (220 x 70 px)", (220, 70)),
    "waktu_64x64":       ("HUD Ikon Waktu / Timer (64 x 64 px)", (64, 64)),
}


def make_even(n):
    """Pastikan angka piksel selalu genap sesuai aturan Construct 2."""
    n = max(2, int(round(n)))
    return n if n % 2 == 0 else n + 1


def detect_bg_color(bgr_img):
    """Deteksi warna rata-rata latar belakang dari keempat sudut/tepi gambar."""
    h, w = bgr_img.shape[:2]
    edge_pixels = np.concatenate([
        bgr_img[0, :, :],
        bgr_img[h - 1, :, :],
        bgr_img[:, 0, :],
        bgr_img[:, w - 1, :]
    ], axis=0)
    return np.median(edge_pixels, axis=0).astype(np.float32)


def is_full_background_image(bgr_img, tolerance=30.0):
    """Cek apakah gambar adalah Background penuh (bukan objek di atas latar solid/putih)."""
    h, w = bgr_img.shape[:2]
    edge_pixels = np.concatenate([
        bgr_img[0, :, :],
        bgr_img[h - 1, :, :],
        bgr_img[:, 0, :],
        bgr_img[:, w - 1, :]
    ], axis=0).astype(np.float32)
    med = np.median(edge_pixels, axis=0)
    dist = np.sqrt(np.sum((edge_pixels - med) ** 2, axis=1))
    solid_ratio = np.mean(dist < (tolerance + 25.0))
    return solid_ratio < 0.42


def save_compressed_jpg_1280x720(bgr_img, out_jpg_path, target_w=1280, target_h=720, quality=83):
    """Simpan gambar Background menjadi JPG 1280x720 ringan (< 200 KB)."""
    rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    im = Image.fromarray(rgb)
    sw, sh = im.size
    scale = max(target_w / sw, target_h / sh)
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    im_res = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - target_w) // 2
    top = (nh - target_h) // 2
    im_crop = im_res.crop((left, top, left + target_w, top + target_h))

    q = quality
    im_crop.save(out_jpg_path, "JPEG", quality=q, optimize=True)
    while os.path.getsize(out_jpg_path) > 220 * 1024 and q > 68:
        q -= 3
        im_crop.save(out_jpg_path, "JPEG", quality=q, optimize=True)
    return im_crop.size, os.path.getsize(out_jpg_path) / 1024.0


def save_lightweight_png(pil_rgba, out_png_path):
    """Simpan PNG transparan dengan kompresi optimal agar ukuran file kecil & ringan."""
    pil_rgba.save(out_png_path, "PNG", optimize=True, compress_level=9)
    size_kb = os.path.getsize(out_png_path) / 1024.0
    if size_kb > 160.0:
        try:
            quantized = pil_rgba.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
            quantized.save(out_png_path, "PNG", optimize=True, compress_level=9)
            size_kb = os.path.getsize(out_png_path) / 1024.0
        except Exception:
            pass
    return size_kb


def remove_background_rgba(bgr_crop, tolerance=30.0, remove_shadow=True, remove_text_holes=False):
    """
    Algoritma v2 (Exterior Flood-Fill + HSV Drop-Shadow Removal):
      1. Menambahkan bingkai putih sementara di sekeliling gambar agar seluruh sisi luar terhubung.
      2. Mendeteksi piksel latar belakang:
         - Piksel yang dekat dengan warna background (dist_from_bg < tolerance), ATAU
         - Jika remove_shadow=True: piksel bayangan luar (drop-shadow abu-abu / terang dengan
           saturasi rendah S < 60 dan kecerahan V > 140) yang berada di luar garis outline gelap objek.
      3. Hanya komponen yang terhubung ke tepi luar (0,0) yang dihapus, sehingga warna putih/abu-abu
         di bagian dalam objek (yang dibatasi oleh garis outline gelap) tetap 100% aman!
      4. Melakukan penghalusan tepi (alpha feathering) & color decontamination agar tidak ada
         sisa halo abu-abu/putih di pinggiran objek.
    """
    bg_color = detect_bg_color(bgr_crop)
    border = 14
    # Gunakan bingkai putih jika latar terang, atau warna median tepi
    border_val = (255, 255, 255) if np.mean(bg_color) > 160 else (int(bg_color[0]), int(bg_color[1]), int(bg_color[2]))
    bordered = cv2.copyMakeBorder(
        bgr_crop, border, border, border, border,
        cv2.BORDER_CONSTANT,
        value=border_val
    )
    h, w = bordered.shape[:2]

    b = bordered[:, :, 0].astype(np.float32)
    g = bordered[:, :, 1].astype(np.float32)
    r = bordered[:, :, 2].astype(np.float32)

    dist_from_bg = np.sqrt(
        (border_val[2] - r) ** 2 +
        (border_val[1] - g) ** 2 +
        (border_val[0] - b) ** 2
    )

    hsv = cv2.cvtColor(bordered, cv2.COLOR_BGR2HSV)
    s = hsv[:, :, 1].astype(np.float32)
    v = hsv[:, :, 2].astype(np.float32)

    # Kandidat background utama
    bg_candidate = (dist_from_bg < tolerance)

    # Jika latar belakang terang/putih dan fitur hapus bayangan aktif:
    # Ikut sertakan area bayangan abu-abu luar (desaturated S < 62 dan cukup terang V > 140)
    # Garis outline tombol/kartun selalu gelap (V < 125) atau berwarna pekat (S >= 100),
    # sehingga flood-fill akan berhenti tepat di garis outline tombol!
    if remove_shadow and np.mean(border_val) > 170:
        shadow_candidate = (s < 62.0) & (v > 140.0)
        bg_candidate = bg_candidate | shadow_candidate

    bg_candidate_u8 = bg_candidate.astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(bg_candidate_u8, connectivity=8)
    ext_label = labels[0, 0]
    is_bg = (labels == ext_label)

    if remove_text_holes:
        gray = cv2.cvtColor(bordered, cv2.COLOR_BGR2GRAY)
        for lbl in range(1, num_labels):
            if lbl == ext_label:
                continue
            x_c, y_c, w_c, h_c, area_c = stats[lbl]
            if 10 < area_c < 450 and w_c < 45 and h_c < 45:
                comp_mask = (labels == lbl).astype(np.uint8)
                dilated = cv2.dilate(comp_mask, np.ones((3, 3), np.uint8), iterations=1)
                ring = (dilated - comp_mask) > 0
                if ring.any() and np.mean(gray[ring]) < 75:
                    is_bg = is_bg | (labels == lbl)

    bg_u8 = is_bg.astype(np.uint8) * 255
    edge_zone = cv2.dilate(bg_u8, np.ones((3, 3), np.uint8), iterations=1) > 0

    alpha = np.full((h, w), 255.0, dtype=np.float32)
    alpha[is_bg] = 0.0

    if remove_shadow and np.mean(border_val) > 170:
        # Di zona tepi 1-2px antara outline dan bayangan/latar, hitung kekuatan piksel objek
        # Objek memiliki kepekatan warna tinggi (S) atau garis outline gelap (V rendah)
        fg_strength = np.maximum(
            (165.0 - v) / (165.0 - 95.0),
            (s - 35.0) / (115.0 - 35.0)
        )
        dist_strength = (dist_from_bg - 14.0) / (65.0 - 14.0)
        ramp = np.clip(np.maximum(fg_strength, dist_strength) * 255.0, 0.0, 255.0)
    else:
        low_t = max(8.0, tolerance * 0.4)
        high_t = max(45.0, tolerance * 1.9)
        ramp = np.clip((dist_from_bg - low_t) / (high_t - low_t) * 255.0, 0.0, 255.0)

    alpha[edge_zone] = np.minimum(alpha[edge_zone], ramp[edge_zone])

    # Color decontamination (hilangkan bias warna putih/abu-abu di tepi semi-transparan)
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    a_norm = alpha / 255.0
    ref_rgb = [225.0, 225.0, 225.0] if (remove_shadow and np.mean(border_val) > 170) else [border_val[2], border_val[1], border_val[0]]
    for c_idx, ch in enumerate([r, g, b]):
        fg = np.where(
            a_norm > 0.05,
            (ch - ref_rgb[c_idx] * (1.0 - a_norm)) / np.maximum(a_norm, 0.05),
            0.0
        )
        rgba[:, :, c_idx] = np.clip(fg, 0, 255).astype(np.uint8)
    rgba[:, :, 3] = np.clip(alpha, 0, 255).astype(np.uint8)

    return rgba[border:-border, border:-border]


def guess_c2_size_from_aspect(tw, th, name_hint=""):
    """Menentukan ukuran ideal Construct 2 secara otomatis sesuai tabel AGENTS.md."""
    nh = name_hint.lower()
    aspect = tw / max(1.0, float(th))

    if "judul" in nh or "banner" in nh:
        return (660, 220)
    if "dialog" in nh or "papan" in nh or "popup" in nh or "benar" in nh or "coba" in nh:
        return (640, 380)
    if "sampah" in nh:
        return (140, 140)
    if "tong" in nh or "bin" in nh:
        return (200, 260)
    if "simulasi" in nh and "karakter" in nh:
        return (120, 160)
    if "karakter" in nh:
        return (260, 380)
    if "skor" in nh:
        return (220, 70)
    if "waktu" in nh:
        return (64, 64) if aspect < 1.3 else (220, 70)

    # Berdasarkan geometri rasio objek (mengacu pada tabel AGENTS.md)
    if 0.85 <= aspect <= 1.18:
        return (140, 140)
    elif aspect >= 2.2:
        return (380, 96)
    elif aspect > 1.18:
        return (640, 380)
    elif 0.68 <= aspect < 0.85:
        return (200, 260)
    else:
        return (260, 380)


def fit_rgba_to_box(rgba_img, target_w, target_h, pad_px=2):
    """Fit objek non-transparan secara proporsional ke tengah kanvas target_w x target_h (piksel genap)."""
    tw_target, th_target = make_even(target_w), make_even(target_h)
    pil_in = Image.fromarray(rgba_img, mode="RGBA")
    bbox = pil_in.getbbox()
    tight_pil = pil_in.crop(bbox) if bbox else pil_in
    tw, th = tight_pil.size
    avail_w = max(2, tw_target - 2 * pad_px)
    avail_h = max(2, th_target - 2 * pad_px)
    scale = min(avail_w / tw, avail_h / th)
    nw = max(1, int(round(tw * scale)))
    nh = max(1, int(round(th * scale)))
    resized = tight_pil.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (tw_target, th_target), (0, 0, 0, 0))
    canvas.paste(resized, ((tw_target - nw) // 2, (th_target - nh) // 2), resized)
    return canvas


def scale_original_to_c2_viewport(rgba_img, max_w=640, max_h=480):
    """Mengecilkan versi _original agar proporsional dengan viewport 1280x720 dan hemat memori."""
    pil_in = Image.fromarray(rgba_img, mode="RGBA")
    bbox = pil_in.getbbox()
    tight_pil = pil_in.crop(bbox) if bbox else pil_in
    w, h = tight_pil.size
    scale = min(1.0, max_w / float(w), max_h / float(h))
    nw, nh = make_even(w * scale), make_even(h * scale)
    return tight_pil.resize((nw, nh), Image.Resampling.LANCZOS)


def save_bg_variants(rgba_img, out_dir, name_prefix, log_fn=print, c2_target_size="auto", seq_no=1):
    """
    Menyimpan 2 varian ringan (BG-1X1 dan BG-ORIG) dengan ukuran piksel genap
    dan ukuran file KB kecil (standar Construct 2 1280x720).
    Nama file: DD-MM-YYYY_HH-MM-SS_NNN_BG-1X1.png & DD-MM-YYYY_HH-MM-SS_NNN_BG-ORIG.png
    """
    saved = []

    ys, xs = np.where(rgba_img[:, :, 3] > 15)
    if len(xs) > 0 and len(ys) > 0:
        tw = int(xs.max() - xs.min() + 1)
        th = int(ys.max() - ys.min() + 1)
    else:
        th, tw = rgba_img.shape[:2]

    if c2_target_size == "auto" or c2_target_size is None:
        target_w, target_h = guess_c2_size_from_aspect(tw, th, name_prefix)
    else:
        target_w, target_h = c2_target_size

    ts = make_ts_prefix(out_dir, seq_no)
    actual_seq = ts.split("_")[-1]

    # 1. BG-1X1.png (Kanvas Persegi 1:1 ukuran ideal Construct 2)
    sq_side = make_even(max(target_w, target_h))
    pil_sq = fit_rgba_to_box(rgba_img, sq_side, sq_side, pad_px=2)
    p_sq = os.path.join(out_dir, f"{ts}_BG-1X1.png")
    kb_sq = save_lightweight_png(pil_sq, p_sq)
    saved.append(p_sq)

    # 2. BG-ORIG.png (Rasio asli objek tanpa pengubahan aspek, di-scale ke skala viewport 1280x720)
    pil_orig = scale_original_to_c2_viewport(rgba_img, max_w=max(target_w, 380), max_h=max(target_h, 380))
    p_orig = os.path.join(out_dir, f"{ts}_BG-ORIG.png")
    kb_orig = save_lightweight_png(pil_orig, p_orig)
    saved.append(p_orig)

    log_fn(
        f"[OK] #{actual_seq} {ts} | "
        f"1x1: {pil_sq.size[0]}x{pil_sq.size[1]} ({kb_sq:.1f} KB) | "
        f"orig: {pil_orig.size[0]}x{pil_orig.size[1]} ({kb_orig:.1f} KB)"
    )
    return saved


def find_item_bboxes(rgba_full, min_area_ratio=0.003, merge_gap_px=18):
    """Mendeteksi item-item terpisah di dalam satu gambar (mode Auto-Split / Sprite Sheet)."""
    h, w = rgba_full.shape[:2]
    min_area = max(1500, int(h * w * min_area_ratio))

    fg_mask = (rgba_full[:, :, 3] > 25).astype(np.uint8) * 255
    if merge_gap_px > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (merge_gap_px, merge_gap_px))
        fg_merged = cv2.dilate(fg_mask, k, iterations=1)
    else:
        fg_merged = fg_mask

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(fg_merged, connectivity=8)
    boxes = []
    for i in range(1, num_labels):
        x, y, bw, bh, area = stats[i]
        real_area = np.count_nonzero(fg_mask[y:y + bh, x:x + bw])
        if real_area >= min_area:
            x0 = max(0, x)
            y0 = max(0, y)
            x1 = min(w, x + bw)
            y1 = min(h, y + bh)
            boxes.append((x0, y0, x1, y1))

    boxes.sort(key=lambda b: (b[1] // max(1, h // 8), b[0]))
    return boxes


def process_single_image(img_path, out_dir, split_items=False, tolerance=30.0, remove_shadow=True, c2_target_size="auto", log_fn=print, seq_no=1):
    """Memproses 1 file gambar, menghapus background & bayangan luar, dan menyimpan file ringan Construct 2.
    Nama output berbasis timestamp: DD-MM-YYYY_HH-MM-SS_NNN_BG-*.png/jpg
    """
    raw = np.fromfile(img_path, dtype=np.uint8)
    bgr = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if bgr is None:
        log_fn(f"[X] Gagal membaca gambar: {img_path}")
        return []

    base_name = os.path.splitext(os.path.basename(img_path))[0]
    os.makedirs(out_dir, exist_ok=True)
    saved_paths = []
    ts = make_ts_prefix(out_dir, seq_no)

    if c2_target_size == "bg_jpg" or (c2_target_size == "auto" and not split_items and is_full_background_image(bgr, tolerance=tolerance)):
        out_jpg = os.path.join(out_dir, f"{ts}_BG-JPG.jpg")
        (w_out, h_out), kb_out = save_compressed_jpg_1280x720(bgr, out_jpg, 1280, 720, quality=83)
        log_fn(f"[BG-JPG] #{seq_no:03d} {os.path.basename(out_jpg)} -> {w_out}x{h_out} px ({kb_out:.1f} KB)")
        return [out_jpg]

    rgba_full = remove_background_rgba(bgr, tolerance=tolerance, remove_shadow=remove_shadow, remove_text_holes=False)

    if split_items:
        boxes = find_item_bboxes(rgba_full)
        if len(boxes) <= 1:
            saved_paths.extend(
                save_bg_variants(rgba_full, out_dir, base_name, log_fn=log_fn, c2_target_size=c2_target_size, seq_no=seq_no)
            )
        else:
            log_fn(f"[*] Mendeteksi {len(boxes)} item di dalam '{os.path.basename(img_path)}'...")
            for idx, (x0, y0, x1, y1) in enumerate(boxes, start=1):
                crop_bgr = bgr[y0:y1, x0:x1]
                crop_rgba = remove_background_rgba(crop_bgr, tolerance=tolerance, remove_shadow=remove_shadow, remove_text_holes=False)
                sub_prefix = f"SPLIT-ITEM{idx:02d}"

                ys_c, xs_c = np.where(crop_rgba[:, :, 3] > 15)
                cw = int(xs_c.max() - xs_c.min() + 1) if len(xs_c) > 0 else crop_rgba.shape[1]
                ch = int(ys_c.max() - ys_c.min() + 1) if len(ys_c) > 0 else crop_rgba.shape[0]
                if c2_target_size == "auto" or c2_target_size is None:
                    tw_i, th_i = guess_c2_size_from_aspect(cw, ch, sub_prefix)
                else:
                    tw_i, th_i = c2_target_size

                sq = make_even(max(tw_i, th_i))
                pil_sq = fit_rgba_to_box(crop_rgba, sq, sq, pad_px=2)
                p_sq = os.path.join(out_dir, f"{ts}_BG-ITEM{idx:02d}-1X1.png")
                kb_sq = save_lightweight_png(pil_sq, p_sq)
                saved_paths.append(p_sq)

                pil_orig = scale_original_to_c2_viewport(crop_rgba, max_w=max(tw_i, 380), max_h=max(th_i, 380))
                p_orig = os.path.join(out_dir, f"{ts}_BG-ITEM{idx:02d}-ORIG.png")
                kb_orig = save_lightweight_png(pil_orig, p_orig)
                saved_paths.append(p_orig)

                log_fn(f"[OK] #{seq_no:03d}-item{idx:02d} -> 1X1 {pil_sq.size} ({kb_sq:.1f} KB) | ORIG {pil_orig.size} ({kb_orig:.1f} KB)")
    else:
        saved_paths.extend(
            save_bg_variants(rgba_full, out_dir, base_name, log_fn=log_fn, c2_target_size=c2_target_size, seq_no=seq_no)
        )

    return saved_paths


def launch_gui():
    """Tampilan GUI (Tkinter) lengkap dengan fitur Hapus Bayangan Luar (Drop-Shadow Removal)."""
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk

    root = tk.Tk()
    root.title("Hapus Background & Bayangan -> Standar Construct 2 (AGENTS.md)")
    root.geometry("720x600")
    root.configure(bg="#1e222a")

    selected_files = []
    default_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "output_png")

    fg_text = "#e6efff"
    bg_card = "#282c34"
    accent = "#3b82f6"

    header = tk.Label(
        root,
        text="Hapus Background & Drop-Shadow -> Standar Construct 2 (AGENTS.md)",
        font=("Segoe UI", 12, "bold"),
        bg="#1e222a",
        fg="#60a5fa",
        pady=10
    )
    header.pack(fill="x")

    # Frame Pilih File
    frame_in = tk.LabelFrame(root, text=" 1. Pilih Gambar / Folder ", bg=bg_card, fg=fg_text, font=("Segoe UI", 10, "bold"), padx=10, pady=8)
    frame_in.pack(fill="x", padx=14, pady=5)

    lbl_count = tk.Label(frame_in, text="Belum ada file dipilih", bg=bg_card, fg="#9ca3af", font=("Segoe UI", 9))
    lbl_count.pack(side="left", padx=4)

    def pick_files():
        nonlocal selected_files
        files = filedialog.askopenfilenames(
            title="Pilih File Gambar",
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.bmp"), ("All Files", "*.*")]
        )
        if files:
            selected_files = list(files)
            lbl_count.config(text=f"{len(selected_files)} file dipilih", fg="#34d399")
            out_dir_var.set(os.path.join(os.path.dirname(selected_files[0]), "output_png"))

    def pick_folder():
        nonlocal selected_files
        folder = filedialog.askdirectory(
            title="Pilih Folder Berisi Gambar",
            initialdir=os.path.dirname(os.path.abspath(__file__))
        )
        if folder:
            exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
            selected_files = [
                os.path.join(folder, f) for f in os.listdir(folder)
                if f.lower().endswith(exts) and os.path.isfile(os.path.join(folder, f))
            ]
            lbl_count.config(text=f"{len(selected_files)} file dari folder '{os.path.basename(folder)}'", fg="#34d399")
            out_dir_var.set(os.path.join(folder, "output_png"))

    btn_folder = tk.Button(frame_in, text="Pilih 1 Folder", command=pick_folder, bg="#374151", fg="white", relief="flat", padx=10, pady=4)
    btn_folder.pack(side="right", padx=4)

    btn_files = tk.Button(frame_in, text="Pilih File Gambar...", command=pick_files, bg=accent, fg="white", relief="flat", padx=12, pady=4)
    btn_files.pack(side="right", padx=4)

    # Frame Folder Output
    frame_out = tk.LabelFrame(root, text=" 2. Folder Output ", bg=bg_card, fg=fg_text, font=("Segoe UI", 10, "bold"), padx=10, pady=8)
    frame_out.pack(fill="x", padx=14, pady=5)

    out_dir_var = tk.StringVar(value=default_out)
    entry_out = tk.Entry(frame_out, textvariable=out_dir_var, bg="#181a1f", fg="white", insertbackground="white", relief="flat", font=("Consolas", 9))
    entry_out.pack(side="left", fill="x", expand=True, padx=4, ipady=4)

    def browse_out():
        d = filedialog.askdirectory(title="Pilih Folder Tujuan Output", initialdir=out_dir_var.get())
        if d:
            out_dir_var.set(d)

    btn_out = tk.Button(frame_out, text="Ubah...", command=browse_out, bg="#374151", fg="white", relief="flat", padx=10, pady=3)
    btn_out.pack(side="right", padx=4)

    # Frame Opsi Tambahan
    frame_opt = tk.LabelFrame(root, text=" 3. Kategori Ukuran Construct 2 & Pembersih Bayangan ", bg=bg_card, fg=fg_text, font=("Segoe UI", 10, "bold"), padx=10, pady=8)
    frame_opt.pack(fill="x", padx=14, pady=5)

    tk.Label(frame_opt, text="Kategori Aset:", bg=bg_card, fg=fg_text, font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
    preset_keys = list(C2_PRESETS.keys())
    preset_labels = [C2_PRESETS[k][0] for k in preset_keys]
    combo_preset = ttk.Combobox(frame_opt, values=preset_labels, state="readonly", width=52)
    combo_preset.current(0)
    combo_preset.grid(row=0, column=1, sticky="w", padx=6, pady=4)

    shadow_var = tk.BooleanVar(value=True)
    chk_shadow = tk.Checkbutton(
        frame_opt,
        text="Hapus Bayangan Luar / Drop-Shadow Abu-abu di Sudut Tombol (HSV Smart Shadow Removal)",
        variable=shadow_var,
        bg=bg_card,
        fg="#34d399",
        selectcolor="#1e222a",
        activebackground=bg_card,
        font=("Segoe UI", 9, "bold")
    )
    chk_shadow.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 2))

    split_var = tk.BooleanVar(value=False)
    chk_split = tk.Checkbutton(
        frame_opt,
        text="Auto-Split (Pecah otomatis jika 1 gambar berisi banyak item / sprite sheet)",
        variable=split_var,
        bg=bg_card,
        fg="#fbbf24",
        selectcolor="#1e222a",
        activebackground=bg_card,
        font=("Segoe UI", 9, "bold")
    )
    chk_split.grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 2))

    bw_var = tk.BooleanVar(value=False)
    chk_bw = tk.Checkbutton(
        frame_opt,
        text="Konversi ke Hitam-Putih / Locked Grayscale (Otomatis hapus BG terlebih dahulu)",
        variable=bw_var,
        bg=bg_card,
        fg="#d1d5db",
        selectcolor="#1e222a",
        activebackground=bg_card,
        font=("Segoe UI", 9, "bold")
    )
    chk_bw.grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 4))

    tk.Label(frame_opt, text="Toleransi Warna BG (15-65):", bg=bg_card, fg=fg_text, font=("Segoe UI", 9)).grid(row=4, column=0, sticky="w", pady=2)
    tol_var = tk.DoubleVar(value=30.0)
    scale_tol = tk.Scale(frame_opt, from_=15, to=65, orient="horizontal", variable=tol_var, bg=bg_card, fg=fg_text, highlightthickness=0, length=220)
    scale_tol.grid(row=4, column=1, sticky="w", padx=6)

    # Log Area
    log_box = scrolledtext.ScrolledText(root, height=8, bg="#14161a", fg="#a7f3d0", font=("Consolas", 9), relief="flat")
    log_box.pack(fill="both", expand=True, padx=14, pady=5)

    def log_msg(msg):
        log_box.insert(tk.END, msg + "\n")
        log_box.see(tk.END)
        root.update_idletasks()

    def run_conversion():
        if not selected_files:
            messagebox.showwarning("Belum Ada Gambar", "Silakan pilih file gambar atau folder terlebih dahulu!")
            return
        out_target = out_dir_var.get().strip()
        if not out_target:
            messagebox.showwarning("Folder Output Kosong", "Silakan tentukan folder output!")
            return

        sel_idx = combo_preset.current()
        sel_key = preset_keys[sel_idx] if sel_idx >= 0 else "auto_smart"
        c2_size = C2_PRESETS[sel_key][1]

        log_box.delete("1.0", tk.END)
        log_msg(f"Memulai konversi {len(selected_files)} gambar...")
        log_msg(f"Mode: {C2_PRESETS[sel_key][0]} | Hapus Bayangan: {shadow_var.get()} | Auto-Split: {split_var.get()} | Hitam-Putih: {bw_var.get()}")
        log_msg("-" * 68)

        total_saved = 0
        for seq_no, fpath in enumerate(selected_files, start=1):
            if bw_var.get():
                out_bw = convert_to_bw_game(
                    fpath,
                    out_target,
                    tolerance=tol_var.get(),
                    remove_shadow=shadow_var.get(),
                    c2_target_size=c2_size,
                    log_fn=log_msg,
                    seq_no=seq_no
                )
                if out_bw:
                    total_saved += 1
            else:
                res = process_single_image(
                    fpath,
                    out_target,
                    split_items=split_var.get(),
                    tolerance=tol_var.get(),
                    remove_shadow=shadow_var.get(),
                    c2_target_size=c2_size,
                    log_fn=log_msg,
                    seq_no=seq_no
                )
                total_saved += len(res)

        log_msg("-" * 68)
        log_msg(f"SELESAI! Total {total_saved} file ringan bebas bayangan disimpan di:")
        log_msg(out_target)
        try:
            os.startfile(out_target)
        except Exception:
            pass

    btn_run = tk.Button(
        root,
        text="PROSES & HAPUS BACKGROUND + BAYANGAN SEKARANG",
        command=run_conversion,
        bg="#10b981",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        pady=8
    )
    btn_run.pack(fill="x", padx=14, pady=(2, 12))

    root.mainloop()


def convert_to_bw_game(img_path, out_dir, tolerance=30.0, remove_shadow=True, c2_target_size="auto", log_fn=print, seq_no=1):
    """
    Konversi gambar ke Hitam-Putih bergaya 'Locked State' untuk UI game.
    Otomatis menghapus background & bayangan luar terlebih dahulu jika gambar belum transparan
    (dan bukan foto/latar belakang penuh).
    Algoritma kurva kontras khusus:
      - Teks/area putih murni (R,G,B > 230) -> tetap putih (255) -> TERLINDUNGI
      - Outline hitam tegas (V < 50) -> tetap gelap -> TERLINDUNGI
      - Area berwarna lainnya (body tombol/badge, bintang kuning, dll) ->
        di-remap ke abu-abu elegan 110-185 dengan kontras tetap terjaga
      - Channel Alpha (transparansi PNG) dipertahankan sepenuhnya
    Output: DD-MM-YYYY_HH-MM-SS_NNN_BW.png disimpan di out_dir
    """
    raw = np.fromfile(img_path, dtype=np.uint8)
    bgr = cv2.imdecode(raw, cv2.IMREAD_UNCHANGED)
    if bgr is None:
        log_fn(f"[X] Gagal membaca: {img_path}")
        return None

    if len(bgr.shape) == 2:
        bgr = cv2.cvtColor(bgr, cv2.COLOR_GRAY2BGR)

    base_name = os.path.splitext(os.path.basename(img_path))[0]
    os.makedirs(out_dir, exist_ok=True)

    has_alpha = (bgr.shape[2] == 4) and bool(np.any(bgr[:, :, 3] < 250))
    needs_c2_fit = False

    if has_alpha:
        alpha_ch = bgr[:, :, 3]
        bgr_rgb  = bgr[:, :, :3]
    else:
        bgr_raw = bgr[:, :, :3]
        if not is_full_background_image(bgr_raw, tolerance=tolerance):
            # Belum transparan & bukan foto penuh -> otomatis hapus background & bayangan dulu
            rgba_clean = remove_background_rgba(
                bgr_raw,
                tolerance=tolerance,
                remove_shadow=remove_shadow,
                remove_text_holes=False
            )
            alpha_ch = rgba_clean[:, :, 3]
            bgr_rgb  = cv2.cvtColor(rgba_clean[:, :, :3], cv2.COLOR_RGB2BGR)
            needs_c2_fit = True
        else:
            alpha_ch = None
            bgr_rgb  = bgr_raw

    # -- Konversi ke grayscale via perceptual luminance (OpenCV default: BT.601)
    gray = cv2.cvtColor(bgr_rgb, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # -- Hitung kecerahan HSV untuk membedakan area gelap/outline
    hsv = cv2.cvtColor(bgr_rgb, cv2.COLOR_BGR2HSV)
    v_ch = hsv[:, :, 2].astype(np.float32)

    # -- Mask: area putih murni (teks & sorot cerah) -> keep 255
    white_mask  = (bgr_rgb[:, :, 0].astype(np.int32) > 230) & \
                  (bgr_rgb[:, :, 1].astype(np.int32) > 230) & \
                  (bgr_rgb[:, :, 2].astype(np.int32) > 230)

    # -- Mask: outline/bayangan sangat gelap -> keep near-black
    black_mask  = (v_ch < 55)

    # -- Area body (berwarna, bukan putih, bukan hitam) -> remap ke abu-abu elegan
    body_mask   = (~white_mask) & (~black_mask)

    # -- Remap: angkat bagian gelap ke minimum 110, tekan bagian terang ke maksimum 185
    body_gray   = np.clip(gray, 0, 255)
    body_mapped = 110.0 + (body_gray / 255.0) * (185.0 - 110.0)

    # -- Gabungkan semua mask
    result = np.zeros_like(gray)
    result[white_mask]  = 255.0
    result[black_mask]  = np.clip(gray[black_mask], 0, 70)
    result[body_mask]   = body_mapped[body_mask]

    result_u8 = result.astype(np.uint8)

    # -- Buat output RGBA / RGB (abu-abu di R=G=B)
    rgb_bw = cv2.merge([result_u8, result_u8, result_u8])
    if alpha_ch is not None:
        rgba_out = np.dstack([rgb_bw, alpha_ch])
        if needs_c2_fit:
            ys, xs = np.where(alpha_ch > 15)
            if len(xs) > 0 and len(ys) > 0:
                tw = int(xs.max() - xs.min() + 1)
                th = int(ys.max() - ys.min() + 1)
            else:
                th, tw = rgba_out.shape[:2]
            if c2_target_size in ("auto", "bg_jpg", None):
                target_w, target_h = guess_c2_size_from_aspect(tw, th, base_name)
            else:
                target_w, target_h = c2_target_size
            pil_out = fit_rgba_to_box(rgba_out, target_w, target_h, pad_px=2)
        else:
            pil_out = Image.fromarray(rgba_out, mode="RGBA")
            w_cur, h_cur = pil_out.size
            if w_cur % 2 != 0 or h_cur % 2 != 0:
                pil_out = pil_out.resize((make_even(w_cur), make_even(h_cur)), Image.Resampling.LANCZOS)
    else:
        pil_out = Image.fromarray(cv2.cvtColor(rgb_bw, cv2.COLOR_BGR2RGB))
        if c2_target_size == "bg_jpg":
            pil_out = pil_out.resize((1280, 720), Image.Resampling.LANCZOS)
        else:
            w_cur, h_cur = pil_out.size
            if w_cur % 2 != 0 or h_cur % 2 != 0:
                pil_out = pil_out.resize((make_even(w_cur), make_even(h_cur)), Image.Resampling.LANCZOS)

    ts = make_ts_prefix(out_dir, seq_no)
    out_path = os.path.join(out_dir, f"{ts}_BW.png")
    kb = save_lightweight_png(pil_out, out_path)
    tag_bg = "auto-hapus BG + " if needs_c2_fit else ""
    log_fn(f"[BW] #{seq_no:03d} ({tag_bg}BW) {os.path.basename(out_path)} -> {pil_out.size[0]}x{pil_out.size[1]} px ({kb:.1f} KB)")
    return out_path


def main():
    parser = argparse.ArgumentParser(
        description="Hapus background & bayangan luar (drop-shadow), kompres ke ukuran standar Construct 2 (AGENTS.md)."
    )
    parser.add_argument("inputs", nargs="*", help="Path file atau folder gambar (kosongkan untuk membuka GUI)")
    parser.add_argument("-o", "--output", default="", help="Folder tujuan output")
    parser.add_argument("--split", action="store_true", help="Aktifkan Auto-Split jika 1 gambar berisi banyak item")
    parser.add_argument("--no-shadow-removal", action="store_true", help="Matikan penghapusan bayangan abu-abu luar")
    parser.add_argument("--tolerance", type=float, default=30.0, help="Toleransi kemiripan warna background (default: 30)")
    parser.add_argument("--preset", choices=list(C2_PRESETS.keys()), default="auto_smart", help="Preset ukuran Construct 2 (1280x720)")
    parser.add_argument("--bw", action="store_true", help="Konversi ke Hitam-Putih / Locked Grayscale (UI game)")
    args = parser.parse_args()

    if not args.inputs:
        launch_gui()
        return

    exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    files_to_process = []
    for inp in args.inputs:
        inp = os.path.abspath(inp)
        if os.path.isdir(inp):
            for f in sorted(os.listdir(inp)):
                fp = os.path.join(inp, f)
                if os.path.isfile(fp) and f.lower().endswith(exts):
                    files_to_process.append(fp)
        elif os.path.isfile(inp) and inp.lower().endswith(exts):
            files_to_process.append(inp)

    if not files_to_process:
        print("[!] Tidak ditemukan file gambar yang valid.")
        return

    c2_size = C2_PRESETS[args.preset][1]
    out_dir = args.output if args.output else os.path.join(os.path.dirname(files_to_process[0]), "output_bw" if args.bw else "output_png")

    if args.bw:
        # -- Mode Hitam-Putih / Locked Grayscale (otomatis hapus BG dulu jika belum transparan)
        print(f"=== [BW Mode] Memproses {len(files_to_process)} gambar -> {out_dir} ===")
        total = 0
        for seq_no, fp in enumerate(files_to_process, start=1):
            result = convert_to_bw_game(
                fp,
                out_dir,
                tolerance=args.tolerance,
                remove_shadow=not args.no_shadow_removal,
                c2_target_size=c2_size,
                seq_no=seq_no
            )
            if result:
                total += 1
        print(f"=== Selesai! {total} file hitam-putih berhasil disimpan di: {out_dir} ===")
    else:
        # -- Mode Hapus Background (default)
        print(f"=== Memproses {len(files_to_process)} gambar -> {out_dir} ===")
        total = 0
        for seq_no, fp in enumerate(files_to_process, start=1):
            saved = process_single_image(
                fp,
                out_dir,
                split_items=args.split,
                tolerance=args.tolerance,
                remove_shadow=not args.no_shadow_removal,
                c2_target_size=c2_size,
                seq_no=seq_no
            )
            total += len(saved)
        print(f"=== Selesai! {total} file ringan bebas bayangan berhasil disimpan di: {out_dir} ===")


if __name__ == "__main__":
    main()
