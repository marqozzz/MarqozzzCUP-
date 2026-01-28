#!/bin/sh
echo "=== MarqozzzCUP Installer ==="
cd /tmp/

# Pobierz autoinstalator
wget -O MarqozzzCUP-plugin.zip "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/MarqozzzCUP-plugin.zip"

if [ ! -f MarqozzzCUP-plugin.zip ]; then
    echo "BŁĄD: Nie udało się pobrać pluginu!"
    exit 1
fi

# Usuń starą wersję
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/

# Rozpakuj i zainstaluj
unzip MarqozzzCUP-plugin.zip
cp -r plugin/* /usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/
chmod 755 /usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/plugin.py
chmod 644 /usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/__init__.py

# Cleanup
rm -rf MarqozzzCUP-plugin.zip plugin/

echo "Plugin zainstalowany!"
echo "Menu → Plugins → MarqozzzCUP"
init 4 && sleep 2 && init 3
