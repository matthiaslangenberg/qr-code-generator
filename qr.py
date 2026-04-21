import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

PLACEHOLDER = "Text oder URL eingeben …\n\nMehrere QR-Codes: Blöcke mit einer Leerzeile trennen."

# --- Farbpalette (Light Theme) ---
BG       = "#f5f5f7"   # Fensterhintergrund
SURFACE  = "#ffffff"   # Eingabefelder
FG       = "#1d1d1f"   # Text
FG_MUTED = "#9a9a9f"   # Placeholder / Hinweis
BTN      = "#e5e5ea"   # Button-Hintergrund
BTN_ACT  = "#c7c7cc"   # Button hover
BORDER   = "#d1d1d6"   # Rahmen / Trenner

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

    # Footer-Text unterhalb des QR-Codes zeichnen (bei Mehrzeilen nur kurze Vorschau)
    footer_text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if "\n" in footer_text:
        erste_zeile = footer_text.splitlines()[0].strip()
        footer_text = f"{erste_zeile} ..."

    schriftgroesse = max(16, qr_img.width // 20)
    try:
        font = ImageFont.truetype("arial.ttf", schriftgroesse)
    except OSError:
        font = ImageFont.load_default()

    # Textgröße messen
    dummy = ImageDraw.Draw(qr_img)
    bbox = dummy.textbbox((0, 0), footer_text, font=font)
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
    draw.text((x, y), footer_text, fill="black", font=font)

    return gesamt


# ---------------------------------------------------------------------------
# Dateiname aus Eingabe ableiten (Sonderzeichen ersetzen)
# ---------------------------------------------------------------------------
def sicherer_dateiname(text: str) -> str:
    name = re.sub(r'[\\/:*?"<>|\s]+', "_", text.strip())
    return name[:80] or "qr"


def vcard_anzeige_name(vcard_text: str) -> str:
    for zeile in vcard_text.splitlines():
        if zeile.upper().startswith("FN:"):
            return zeile[3:].strip() or "vcard"
    return "vcard"


def eindeutiger_pfad(ordner: Path, basisname: str, suffix: str = ".png") -> Path:
    basis = sicherer_dateiname(basisname)
    kandidat = ordner / f"{basis}{suffix}"
    zaehler = 2
    while kandidat.exists():
        kandidat = ordner / f"{basis}_{zaehler}{suffix}"
        zaehler += 1
    return kandidat


# ---------------------------------------------------------------------------
# Vorschau-Popup für ein einzelnes Bild
# ---------------------------------------------------------------------------
def zeige_vorschau(parent: tk.Tk, text: str, img: Image.Image):
    popup = tk.Toplevel(parent)
    titel = text.replace("\n", " ")[:40]
    popup.title(f"QR-Vorschau - {titel}")
    popup.resizable(False, False)
    popup.configure(bg=BG)

    vorschau = img.copy()
    vorschau.thumbnail((350, 350), Image.LANCZOS)
    tk_img = ImageTk.PhotoImage(vorschau)

    lbl = tk.Label(popup, image=tk_img, bg=BG)
    lbl.image = tk_img  # Referenz halten
    lbl.pack(padx=10, pady=10)

    tk.Label(popup, text=text, wraplength=330, bg=BG, fg=FG).pack(pady=(0, 10))
    ttk.Button(popup, text="Schließen", command=popup.destroy).pack(pady=(0, 10))


# ---------------------------------------------------------------------------
# Haupt-GUI
# ---------------------------------------------------------------------------
class QRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR-Code Generator")
        self.minsize(560, 500)
        self._apply_theme()
        self._build_ui()

    def _apply_theme(self):
        self.configure(bg=BG)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".",          background=BG,  foreground=FG,  fieldbackground=SURFACE)
        style.configure("TFrame",     background=BG)
        style.configure("TLabel",     background=BG,  foreground=FG)
        style.configure("TLabelframe",       background=BG, foreground=FG,
                         relief="flat", bordercolor=BORDER)
        style.configure("TLabelframe.Label", background=BG, foreground=FG)
        style.configure("TNotebook",  background=BG,  bordercolor=BORDER)
        style.configure("TNotebook.Tab", background=BTN, foreground=FG,
                         padding=[12, 5], focuscolor=BG)
        style.map("TNotebook.Tab",
                  background=[("selected", SURFACE)],
                  foreground=[("selected", FG)])
        style.configure("TButton",    background=BTN, foreground=FG,
                         relief="flat", padding=[10, 5], focuscolor=BG)
        style.map("TButton",
                  background=[("active", BTN_ACT), ("pressed", BTN_ACT)])
        style.configure("TEntry",     fieldbackground=SURFACE, foreground=FG,
                         bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
        style.configure("TSeparator", background=BORDER)
        # Statusleiste
        style.configure("Status.TLabel", background=BTN, foreground=FG_MUTED,
                         relief="flat", padding=[6, 3])

    # --- UI aufbauen ---
    def _build_ui(self):
        # Tabs
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self._tab_text = ttk.Frame(self._nb)
        self._nb.add(self._tab_text, text="  Text / URL  ")
        self._build_text_tab()

        self._tab_vcard = ttk.Frame(self._nb)
        self._nb.add(self._tab_vcard, text="  Visitenkarte  ")
        self._build_vcard_tab()

        self._nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Speicherort
        frm_path = ttk.Frame(self)
        frm_path.pack(fill="x", padx=10, pady=(8, 0))
        ttk.Label(frm_path, text="Speicherort:").pack(side="left")
        self.var_pfad = tk.StringVar(value=str(Path.home() / "Desktop"))
        ttk.Entry(frm_path, textvariable=self.var_pfad).pack(side="left", fill="x", expand=True, padx=(5, 5))
        ttk.Button(frm_path, text="…", width=3, command=self._waehle_ordner).pack(side="left")

        # Aktionen
        frm_actions = ttk.Frame(self)
        frm_actions.pack(fill="x", padx=10, pady=(6, 0))
        ttk.Button(frm_actions, text="👁  Vorschau", command=self._vorschau).pack(side="left", padx=(0, 5))
        ttk.Button(frm_actions, text="💾  Speichern", command=self._speichern).pack(side="left")

        # Status
        self.var_status = tk.StringVar(value="Bereit.")
        ttk.Label(self, textvariable=self.var_status, style="Status.TLabel", anchor="w").pack(
            fill="x", padx=10, pady=(6, 10)
        )

    # --- Tab 1: Text / URL ---
    def _build_text_tab(self):
        self._placeholder_active = True
        self.txt_input = tk.Text(
            self._tab_text, height=10, wrap="word",
            bg=SURFACE, fg=FG_MUTED,
            insertbackground=FG,
            relief="flat", bd=0,
            font=("Helvetica", 13),
            highlightthickness=1, highlightbackground=BORDER, highlightcolor=BORDER,
        )
        self.txt_input.insert("1.0", PLACEHOLDER)
        self.txt_input.pack(fill="both", expand=True, padx=5, pady=(5, 0))
        self.txt_input.bind("<FocusIn>", self._placeholder_clear)
        self.txt_input.bind("<FocusOut>", self._placeholder_restore)
        self.txt_input.bind("<KeyRelease>", self._aktualisiere_zaehler)

        frm_hint = ttk.Frame(self._tab_text)
        frm_hint.pack(fill="x", padx=5, pady=(3, 5))
        ttk.Button(frm_hint, text="+ Block hinzufügen", command=self._block_hinzufuegen).pack(side="left")
        self.lbl_zaehler = ttk.Label(frm_hint, text="")
        self.lbl_zaehler.pack(side="right")

    # --- Tab 2: Visitenkarte ---
    def _build_vcard_tab(self):
        felder = [
            ("Vorname",  "var_vname"),
            ("Nachname", "var_nname"),
            ("Firma",    "var_org"),
            ("Funktion", "var_titel"),
            ("Telefon",  "var_tel"),
            ("E-Mail",   "var_email"),
            ("Website",  "var_url"),
        ]
        frm = ttk.Frame(self._tab_vcard)
        frm.pack(fill="both", expand=True, padx=15, pady=12)
        for i, (label, attr) in enumerate(felder):
            ttk.Label(frm, text=label + ":").grid(row=i, column=0, sticky="e", padx=(0, 8), pady=5)
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(frm, textvariable=var, width=36).grid(row=i, column=1, sticky="ew", pady=5)
        frm.columnconfigure(1, weight=1)

    # --- Placeholder-Logik ---
    def _placeholder_clear(self, _event=None):
        if self._placeholder_active:
            self.txt_input.delete("1.0", "end")
            self.txt_input.config(fg=FG)
            self._placeholder_active = False
            self._aktualisiere_zaehler()

    def _placeholder_restore(self, _event=None):
        if not self.txt_input.get("1.0", "end").strip():
            self.txt_input.config(fg=FG_MUTED)
            self.txt_input.insert("1.0", PLACEHOLDER)
            self._placeholder_active = True
            self.lbl_zaehler.config(text="")

    # --- Live-Zähler ---
    def _aktualisiere_zaehler(self, _event=None):
        if self._placeholder_active:
            return
        n = len(self._eintraege_text(warn=False))
        self.lbl_zaehler.config(text=f"{n} QR-Code{'s' if n != 1 else ''}" if n else "")
        self.var_status.set(f"{n} QR-Code{'s' if n != 1 else ''} erkannt." if n else "Bereit.")

    def _on_tab_changed(self, _event=None):
        self.var_status.set("Bereit.")

    # --- Block-Separator einfügen ---
    def _block_hinzufuegen(self):
        if self._placeholder_active:
            self.txt_input.delete("1.0", "end")
            self.txt_input.config(fg="black")
            self._placeholder_active = False
        self.txt_input.insert("end", "\n\n")
        self.txt_input.focus_set()
        self._aktualisiere_zaehler()

    # --- Ordner wählen ---
    def _waehle_ordner(self):
        ordner = filedialog.askdirectory(initialdir=self.var_pfad.get())
        if ordner:
            self.var_pfad.set(ordner)

    # --- Einträge ermitteln ---
    def _eintraege_text(self, warn=True) -> list[str]:
        if self._placeholder_active:
            if warn:
                messagebox.showwarning("Keine Eingabe", "Bitte Text oder URL eingeben.")
            return []
        raw = self.txt_input.get("1.0", "end").strip()
        if not raw:
            if warn:
                messagebox.showwarning("Keine Eingabe", "Bitte Text oder URL eingeben.")
            return []
        normalisiert = raw.replace("\r\n", "\n").replace("\r", "\n")
        return [b.strip() for b in re.split(r"\n\s*\n", normalisiert) if b.strip()]

    def _eintraege_vcard(self, warn=True) -> list[str]:
        vname = self.var_vname.get().strip()
        nname = self.var_nname.get().strip()
        fn = f"{vname} {nname}".strip()
        if not fn:
            if warn:
                messagebox.showwarning("Keine Eingabe", "Bitte mindestens Vor- oder Nachname eingeben.")
            return []
        zeilen = ["BEGIN:VCARD", "VERSION:3.0", f"N:{nname};{vname};;;", f"FN:{fn}"]
        if self.var_org.get().strip():
            zeilen.append(f"ORG:{self.var_org.get().strip()}")
        if self.var_titel.get().strip():
            zeilen.append(f"TITLE:{self.var_titel.get().strip()}")
        if self.var_tel.get().strip():
            zeilen.append(f"TEL;TYPE=CELL:{self.var_tel.get().strip()}")
        if self.var_email.get().strip():
            zeilen.append(f"EMAIL:{self.var_email.get().strip()}")
        if self.var_url.get().strip():
            url = self.var_url.get().strip()
            if not re.match(r"https?://", url, re.I):
                url = "https://" + url
            zeilen.append(f"URL:{url}")
        zeilen.append("END:VCARD")
        return ["\n".join(zeilen)]

    def _eintraege(self, warn=True) -> list[str]:
        if self._nb.index("current") == 0:
            return self._eintraege_text(warn=warn)
        return self._eintraege_vcard(warn=warn)

    # --- Aktionen ---
    def _vorschau(self):
        eintraege = self._eintraege()
        if not eintraege:
            return
        for text in eintraege:
            zeige_vorschau(self, text, erzeuge_qr(text))
        n = len(eintraege)
        self.var_status.set(f"{n} Vorschau-Fenster geöffnet.")

    def _speichern(self):
        eintraege = self._eintraege()
        if not eintraege:
            return
        ist_vcard_tab = self._nb.index("current") == 1
        ordner = Path(self.var_pfad.get())
        if not ordner.is_dir():
            messagebox.showerror("Fehler", f"Ordner existiert nicht:\n{ordner}")
            return
        gespeichert = []
        for text in eintraege:
            img = erzeuge_qr(text)
            if ist_vcard_tab:
                kontaktname = vcard_anzeige_name(text)
                basisname = f"qr_vcard_{kontaktname}"
            else:
                basisname = f"qr_{text}"
            datei = eindeutiger_pfad(ordner, basisname)
            img.save(datei)
            gespeichert.append(datei.name)
        self.var_status.set(f"{len(gespeichert)} QR-Code(s) gespeichert in {ordner}")
        messagebox.showinfo("Gespeichert", f"{len(gespeichert)} QR-Code(s) gespeichert:\n\n" + "\n".join(gespeichert))


if __name__ == "__main__":
    app = QRApp()
    app.mainloop()