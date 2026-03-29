#!/bin/zsh
set -e

SCRIPT_DIR="${0:A:h}"
cd "$SCRIPT_DIR"

echo "==> Aktiviere venv..."
source .venv/bin/activate

echo "==> PyInstaller Build..."
pyinstaller --clean --noconfirm qr.spec

echo "==> Bereinige Extended Attributes..."
xattr -cr dist/qr.app
find dist/qr.app -name '._*' -delete

echo "==> Signiere App Bundle (ad-hoc)..."
codesign --force --deep --sign - dist/qr.app

echo "==> Entferne Quarantäne-Flag (falls gesetzt)..."
xattr -d com.apple.quarantine dist/qr.app 2>/dev/null || true

echo ""
echo "✓ Build fertig: dist/qr.app"
open -R dist/qr.app
