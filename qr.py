import re
import tkinter as tk
from io import BytesIO
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageTk


# ---------------------------------------------------------------------------
# QR-Code erzeugen mit Eingabetext als Footer (gibt PIL-Image zurück)
# ---------------------------------------------------------------------------
def erzeuge_qr(text: str) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Footer-Text unterhalb des QR-Codes zeichnen
    schriftgroesse = max(16, qr_img.width // 20)
    try:
        font = ImageFont.truetype("arial.ttf", schriftgroesse)
    except OSError:
        font = ImageFont.load_default()

    # Textgröße messen
    dummy = ImageDraw.Draw(qr_img)
    bbox = dummy.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    padding = 10
    footer_h = text_h + 2 * padding

    # Neues Bild: QR + Footer
    gesamt = Image.new("RGB", (qr_img.width, qr_img.height + footer_h), "white")
    gesamt.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(gesamt)
    x = (gesamt.width - text_w) // 2
    y = qr_img.height + padding
    draw.text((x, y), text, fill="black", font=font)

    return gesamt


# ---------------------------------------------------------------------------
# Dateiname aus Eingabe ableiten (Sonderzeichen ersetzen)
# ---------------------------------------------------------------------------
def sicherer_dateiname(text: str) -> str:
    name = re.sub(r'[\\/:*?"<>|\s]+', "_", text.strip())
    return name[:80] or "qr"


# ---------------------------------------------------------------------------
# Vorschau-Popup für ein einzelnes Bild
# ---------------------------------------------------------------------------
def zeige_vorschau(parent: tk.Tk, text: str, img: Image.Image):
    popup = tk.Toplevel(parent)
    popup.title(f"QR-Vorschau – {text[:40]}")
    popup.resizable(False, False)

    vorschau = img.copy()
    vorschau.thumbnail((350, 350), Image.LANCZOS)
    tk_img = ImageTk.PhotoImage(vorschau)

    lbl = tk.Label(popup, image=tk_img)
    lbl.image = tk_img  # Referenz halten
    lbl.pack(padx=10, pady=10)

    tk.Label(popup, text=text, wraplength=330).pack(pady=(0, 10))
    ttk.Button(popup, text="Schließen", command=popup.destroy).pack(pady=(0, 10))


# ---------------------------------------------------------------------------
# Haupt-GUI
# ---------------------------------------------------------------------------
class QRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR-Code Generator")
        self.minsize(520, 460)
        self._build_ui()

    # --- UI aufbauen ---
    def _build_ui(self):
        # Eingabebereich
        frm_input = ttk.LabelFrame(self, text="Eingaben (eine Zeile = ein QR-Code)")
        frm_input.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        self.txt_input = tk.Text(frm_input, height=12, wrap="word")
        self.txt_input.pack(fill="both", expand=True, padx=5, pady=5)

        # Speicherort
        frm_path = ttk.Frame(self)
        frm_path.pack(fill="x", padx=10, pady=5)

        ttk.Label(frm_path, text="Speicherort:").pack(side="left")
        self.var_pfad = tk.StringVar(value=str(Path.home() / "Desktop"))
        ent_pfad = ttk.Entry(frm_path, textvariable=self.var_pfad)
        ent_pfad.pack(side="left", fill="x", expand=True, padx=(5, 5))
        ttk.Button(frm_path, text="…", width=3, command=self._waehle_ordner).pack(side="left")

        # Aktionen
        frm_actions = ttk.Frame(self)
        frm_actions.pack(fill="x", padx=10, pady=(5, 10))

        ttk.Button(frm_actions, text="💾  Alle speichern", command=self._alle_speichern).pack(side="left", padx=(0, 5))
        ttk.Button(frm_actions, text="👁  Vorschau anzeigen", command=self._alle_vorschau).pack(side="left", padx=5)
        ttk.Button(frm_actions, text="💾+👁  Speichern & Vorschau", command=self._speichern_und_vorschau).pack(side="left", padx=5)

        # Status
        self.var_status = tk.StringVar(value="Bereit.")
        ttk.Label(self, textvariable=self.var_status, relief="sunken", anchor="w").pack(fill="x", padx=10, pady=(0, 10))

    # --- Ordner wählen ---
    def _waehle_ordner(self):
        ordner = filedialog.askdirectory(initialdir=self.var_pfad.get())
        if ordner:
            self.var_pfad.set(ordner)

    # --- Zeilen lesen & validieren ---
    def _zeilen(self) -> list[str]:
        raw = self.txt_input.get("1.0", "end").strip()
        if not raw:
            messagebox.showwarning("Keine Eingabe", "Bitte mindestens eine Zeile eingeben.")
            return []
        return [z.strip() for z in raw.splitlines() if z.strip()]

    # --- Speichern ---
    def _alle_speichern(self):
        zeilen = self._zeilen()
        if not zeilen:
            return
        ordner = Path(self.var_pfad.get())
        if not ordner.is_dir():
            messagebox.showerror("Fehler", f"Ordner existiert nicht:\n{ordner}")
            return

        gespeichert = []
        for text in zeilen:
            img = erzeuge_qr(text)
            datei = ordner / f"qr_{sicherer_dateiname(text)}.png"
            img.save(datei)
            gespeichert.append(datei.name)

        self.var_status.set(f"{len(gespeichert)} QR-Code(s) gespeichert in {ordner}")
        messagebox.showinfo("Fertig", f"{len(gespeichert)} QR-Code(s) gespeichert:\n\n" + "\n".join(gespeichert))

    # --- Vorschau ---
    def _alle_vorschau(self):
        zeilen = self._zeilen()
        if not zeilen:
            return
        for text in zeilen:
            img = erzeuge_qr(text)
            zeige_vorschau(self, text, img)
        self.var_status.set(f"{len(zeilen)} Vorschau-Fenster geöffnet.")

    # --- Beides ---
    def _speichern_und_vorschau(self):
        zeilen = self._zeilen()
        if not zeilen:
            return
        ordner = Path(self.var_pfad.get())
        if not ordner.is_dir():
            messagebox.showerror("Fehler", f"Ordner existiert nicht:\n{ordner}")
            return

        for text in zeilen:
            img = erzeuge_qr(text)
            datei = ordner / f"qr_{sicherer_dateiname(text)}.png"
            img.save(datei)
            zeige_vorschau(self, text, img)

        self.var_status.set(f"{len(zeilen)} QR-Code(s) gespeichert & Vorschau geöffnet.")


if __name__ == "__main__":
    app = QRApp()
    app.mainloop()