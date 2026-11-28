#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
  KONVERSI AUDIO (.MP3 / .OGG / .M4A / .AAC) -> .WAV CONSTRUCT 2
  Proyek: Edukasi Recycle Bin (run.bat -> Opsi [7] / audio-to-wav.bat)
====================================================================
Standar Construct 2 r262:
  - Format      : WAV (PCM 16-bit Little-Endian / pcm_s16le)
  - Sample Rate : 44100 Hz (44.1 kHz)
  - Channels    : Stereo (2) atau Mono (1)
"""

import os
import sys
import shutil
import subprocess
import argparse


def find_ffmpeg():
    """Cari lokasi executable ffmpeg di PATH atau folder WinGet."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    winget_base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    if os.path.isdir(winget_base):
        for root_dir, _, files in os.walk(winget_base):
            if "ffmpeg.exe" in files:
                return os.path.join(root_dir, "ffmpeg.exe")
    return "ffmpeg"


def convert_to_wav_c2(input_path, out_dir, sample_rate=44100, channels=2, trim_silence=False, log_fn=print):
    """Konversi file audio ke WAV PCM 16-bit 44.1kHz standar Construct 2."""
    ffmpeg_exe = find_ffmpeg()
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    os.makedirs(out_dir, exist_ok=True)
    out_wav = os.path.join(out_dir, f"{base_name}.wav")

    # Jika input dan output adalah file .wav yang sama, buat file sementara lalu timpa
    temp_out = out_wav + ".tmp.wav" if os.path.abspath(input_path).lower() == os.path.abspath(out_wav).lower() else out_wav

    cmd = [
        ffmpeg_exe, "-y", "-i", input_path,
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", str(channels)
    ]
    if trim_silence:
        cmd.extend(["-af", "silenceremove=start_periods=1:start_silence=0.05:start_threshold=-50dB"])
    cmd.append(temp_out)

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            log_fn(f"[X] Gagal konversi '{os.path.basename(input_path)}': {res.stderr.splitlines()[-1] if res.stderr else 'Unknown error'}")
            return None
        if temp_out != out_wav:
            os.replace(temp_out, out_wav)
        size_kb = os.path.getsize(out_wav) / 1024.0
        size_str = f"{size_kb / 1024.0:.2f} MB" if size_kb >= 1024 else f"{size_kb:.1f} KB"
        log_fn(f"[OK] {os.path.basename(input_path)} -> {os.path.basename(out_wav)} (PCM 16-bit, {sample_rate} Hz, {channels}ch | {size_str})")
        return out_wav
    except Exception as e:
        log_fn(f"[X] Error menjalankan FFmpeg: {e}")
        return None


def launch_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext

    root = tk.Tk()
    root.title("Konversi Audio (MP3/OGG/M4A) -> WAV Standar Construct 2")
    root.geometry("680x500")
    root.configure(bg="#1e222a")

    default_audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
    os.makedirs(default_audio_dir, exist_ok=True)
    selected_files = []

    fg_text = "#e6efff"
    bg_card = "#282c34"
    accent = "#3b82f6"

    header = tk.Label(
        root,
        text="Konversi Audio (MP3/M4A/OGG) -> WAV Construct 2 (PCM 16-bit 44.1kHz)",
        font=("Segoe UI", 12, "bold"),
        bg="#1e222a",
        fg="#60a5fa",
        pady=10
    )
    header.pack(fill="x")

    # 1. Pilih File / Folder Audio
    frame_in = tk.LabelFrame(root, text=" 1. Pilih File Audio / Folder ", bg=bg_card, fg=fg_text, font=("Segoe UI", 10, "bold"), padx=10, pady=8)
    frame_in.pack(fill="x", padx=14, pady=5)

    lbl_count = tk.Label(frame_in, text="Belum ada file audio dipilih", bg=bg_card, fg="#9ca3af", font=("Segoe UI", 9))
    lbl_count.pack(side="left", padx=4)

    def pick_files():
        nonlocal selected_files
        files = filedialog.askopenfilenames(
            title="Pilih File Audio",
            initialdir=default_audio_dir,
            filetypes=[("Audio Files", "*.mp3 *.m4a *.ogg *.aac *.flac *.wav *.wma *.mp4"), ("All Files", "*.*")]
        )
        if files:
            selected_files = list(files)
            lbl_count.config(text=f"{len(selected_files)} file audio dipilih", fg="#34d399")
            out_dir_var.set(os.path.dirname(selected_files[0]))

    def pick_folder():
        nonlocal selected_files
        folder = filedialog.askdirectory(
            title="Pilih Folder Berisi Audio",
            initialdir=default_audio_dir
        )
        if folder:
            exts = (".mp3", ".m4a", ".ogg", ".aac", ".flac", ".wma", ".mp4")
            selected_files = [
                os.path.join(folder, f) for f in sorted(os.listdir(folder))
                if f.lower().endswith(exts) and os.path.isfile(os.path.join(folder, f))
            ]
            lbl_count.config(text=f"{len(selected_files)} file audio dari folder '{os.path.basename(folder)}'", fg="#34d399")
            out_dir_var.set(folder)

    btn_folder = tk.Button(frame_in, text="Pilih 1 Folder", command=pick_folder, bg="#374151", fg="white", relief="flat", padx=10, pady=4)
    btn_folder.pack(side="right", padx=4)

    btn_files = tk.Button(frame_in, text="Pilih File Audio (MP3)...", command=pick_files, bg=accent, fg="white", relief="flat", padx=12, pady=4)
    btn_files.pack(side="right", padx=4)

    # 2. Folder Output
    frame_out = tk.LabelFrame(root, text=" 2. Folder Output WAV ", bg=bg_card, fg=fg_text, font=("Segoe UI", 10, "bold"), padx=10, pady=8)
    frame_out.pack(fill="x", padx=14, pady=5)

    out_dir_var = tk.StringVar(value=default_audio_dir)
    entry_out = tk.Entry(frame_out, textvariable=out_dir_var, bg="#181a1f", fg="white", insertbackground="white", relief="flat", font=("Consolas", 9))
    entry_out.pack(side="left", fill="x", expand=True, padx=4, ipady=4)

    def browse_out():
        d = filedialog.askdirectory(title="Pilih Folder Tujuan Output WAV", initialdir=out_dir_var.get())
        if d:
            out_dir_var.set(d)

    btn_out = tk.Button(frame_out, text="Ubah...", command=browse_out, bg="#374151", fg="white", relief="flat", padx=10, pady=3)
    btn_out.pack(side="right", padx=4)

    # 3. Pengaturan Audio Construct 2
    frame_opt = tk.LabelFrame(root, text=" 3. Pengaturan WAV Construct 2 ", bg=bg_card, fg=fg_text, font=("Segoe UI", 10, "bold"), padx=10, pady=8)
    frame_opt.pack(fill="x", padx=14, pady=5)

    ch_var = tk.IntVar(value=2)
    tk.Label(frame_opt, text="Saluran (Channel):", bg=bg_card, fg=fg_text, font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=2)
    tk.Radiobutton(frame_opt, text="Stereo (2 Ch - Standar BGM & SFX)", variable=ch_var, value=2, bg=bg_card, fg=fg_text, selectcolor="#1e222a", activebackground=bg_card).grid(row=0, column=1, sticky="w", padx=6)
    tk.Radiobutton(frame_opt, text="Mono (1 Ch - Lebih Hemat Ukuran 50% untuk SFX)", variable=ch_var, value=1, bg=bg_card, fg=fg_text, selectcolor="#1e222a", activebackground=bg_card).grid(row=1, column=1, sticky="w", padx=6)

    trim_var = tk.BooleanVar(value=False)
    chk_trim = tk.Checkbutton(
        frame_opt,
        text="Potong jeda hening di awal audio ( bagus untuk SFX tombol/efek agar tidak delay )",
        variable=trim_var,
        bg=bg_card,
        fg="#34d399",
        selectcolor="#1e222a",
        activebackground=bg_card,
        font=("Segoe UI", 9, "bold")
    )
    chk_trim.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 2))

    # Log Area
    log_box = scrolledtext.ScrolledText(root, height=8, bg="#14161a", fg="#a7f3d0", font=("Consolas", 9), relief="flat")
    log_box.pack(fill="both", expand=True, padx=14, pady=5)

    def log_msg(msg):
        log_box.insert(tk.END, msg + "\n")
        log_box.see(tk.END)
        root.update_idletasks()

    def run_conversion():
        if not selected_files:
            messagebox.showwarning("Belum Ada File Audio", "Silakan pilih file audio (.mp3, dll.) atau folder terlebih dahulu!")
            return
        out_target = out_dir_var.get().strip()
        if not out_target:
            messagebox.showwarning("Folder Output Kosong", "Silakan tentukan folder output!")
            return

        log_box.delete("1.0", tk.END)
        log_msg(f"Memulai konversi {len(selected_files)} file audio ke WAV Construct 2...")
        log_msg("-" * 65)

        total_ok = 0
        for fpath in selected_files:
            res = convert_to_wav_c2(
                fpath,
                out_target,
                sample_rate=44100,
                channels=ch_var.get(),
                trim_silence=trim_var.get(),
                log_fn=log_msg
            )
            if res:
                total_ok += 1

        log_msg("-" * 65)
        log_msg(f"SELESAI! {total_ok} file .wav siap di-import ke Construct 2 di:")
        log_msg(out_target)
        try:
            os.startfile(out_target)
        except Exception:
            pass

    btn_run = tk.Button(
        root,
        text="KONVERSI KE .WAV CONSTRUCT 2 SEKARANG",
        command=run_conversion,
        bg="#10b981",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        pady=8
    )
    btn_run.pack(fill="x", padx=14, pady=(2, 12))

    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Konversi file audio (MP3/OGG/M4A) ke WAV PCM 16-bit 44.1kHz standar Construct 2.")
    parser.add_argument("inputs", nargs="*", help="Path file atau folder audio (kosongkan untuk membuka GUI)")
    parser.add_argument("-o", "--output", default="", help="Folder tujuan output WAV")
    parser.add_argument("--mono", action="store_true", help="Konversi menjadi Mono (1 channel)")
    parser.add_argument("--trim", action="store_true", help="Hapus jeda hening di awal audio")
    args = parser.parse_args()

    if not args.inputs:
        launch_gui()
        return

    exts = (".mp3", ".m4a", ".ogg", ".aac", ".flac", ".wma", ".mp4", ".wav")
    files = []
    for inp in args.inputs:
        inp = os.path.abspath(inp)
        if os.path.isdir(inp):
            for f in sorted(os.listdir(inp)):
                fp = os.path.join(inp, f)
                if os.path.isfile(fp) and f.lower().endswith(exts):
                    files.append(fp)
        elif os.path.isfile(inp) and inp.lower().endswith(exts):
            files.append(inp)

    if not files:
        print("[!] Tidak ditemukan file audio yang valid.")
        return

    out_dir = args.output if args.output else os.path.dirname(files[0])
    channels = 1 if args.mono else 2
    for fp in files:
        convert_to_wav_c2(fp, out_dir, sample_rate=44100, channels=channels, trim_silence=args.trim)


if __name__ == "__main__":
    main()
