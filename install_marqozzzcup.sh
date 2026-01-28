#!/bin/sh
echo "=== MarqozzzCUP Installer v2 ==="
cd /tmp/

# Pobierz autoinstalator
wget -O MarqozzzCUP-plugin.zip "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/MarqozzzCUP-plugin.zip"

if [ ! -f MarqozzzCUP-plugin.zip ]; then
    echo "BŁĄD: Brak pluginu!"
    exit 1
fi

# Usuń starą wersję
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/

# Utwórz katalog docelowy
mkdir -p /usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/

# Rozpakuj i skopiuj PLIKI (nie folder plugin/)
unzip -j MarqozzzCUP-plugin.zip -d /usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/

# Uprawnienia
chmod 755 /usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/plugin.py
chmod 644 /usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/__init__.py
chmod 644 /usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/icon.png 2>/dev/null || true

# Cleanup
rm -f MarqozzzCUP-plugin.zip

echo "MarqozzzCUP zainstalowany!"
echo "Menu => Plugins => MarqozzzCUP"
init 4 && sleep 2 && init 3
