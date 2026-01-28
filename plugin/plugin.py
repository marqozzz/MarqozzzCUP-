from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from urllib.request import urlopen, urlretrieve
import zipfile
import os
import shutil

def Plugins(**kwargs):
    return [PluginDescriptor(name="MarqozzzCUP",
                            description="Plugin do aktualizacji list kanałów",
                            where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)]

def main(session, **kwargs):
    lists = [
        ("Hotbird @Bzyk83", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/marqozzzcup-complete-HB.zip"),
        ("Hotbird+Astra @Bzyk83", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/marqozzzcup-complete-HB-ASTRA.zip")
    ]

    # Tu ustawiasz daty ręcznie
    lists_with_date = [
        ("%s (28.01.2026)" % lists[0][0], lists[0][1]),
        ("%s (28.01.2026)" % lists[1][0], lists[1][1])
    ]

    session.openWithCallback(
        lambda choice: choiceCallback(session, choice),
        ChoiceBox,
        title="Wybierz listę do zainstalowania:",
        list=lists_with_date
    )

def choiceCallback(session, choice):
    if choice and choice[1]:
        url = choice[1]
        full_name = choice[0]  # np. "Hotbird @Bzyk83 (28.01.2026)"
        session.openWithCallback(
            lambda confirmed: confirmCallback(session, confirmed, url, full_name),
            MessageBox,
            text="Zainstalować listę:\n%s ?" % full_name,
            type=MessageBox.TYPE_YESNO
        )

def confirmCallback(session, confirmed, url, full_name):
    if confirmed:
        installList(session, url, full_name)

def installList(session, url, full_name):
    try:
        print("MarqozzzCUP:", full_name)

        # Backup
        if os.path.exists("/etc/enigma2/bouquets.tv"):
            shutil.copy2("/etc/enigma2/bouquets.tv", "/etc/enigma2/bouquets.tv.bak")

        # Pobranie i rozpakowanie
        urlretrieve(url, "/tmp/list.zip")
        os.makedirs("/tmp/list_unpack", exist_ok=True)

        with zipfile.ZipFile("/tmp/list.zip", 'r') as z:
            z.extractall("/tmp/list_unpack/")

        files_copied = 0
        for root, dirs, files in os.walk("/tmp/list_unpack"):
            for file in files:
                src = os.path.join(root, file)
                dst = "/etc/enigma2/" + file
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    files_copied += 1

        os.unlink("/tmp/list.zip")
        shutil.rmtree("/tmp/list_unpack")

        session.open(
            MessageBox,
            text="lista została zaktualizowana:\n%s\nnadpisano %d plików\nautorestart za 5 sekund"
                 % (full_name, files_copied),
            type=MessageBox.TYPE_INFO,
            timeout=5
        )

        os.system("(sleep 5 && killall -9 enigma2) &")

    except Exception as e:
        session.open(MessageBox, text="BŁĄD %s: %s" % (full_name, str(e)), type=MessageBox.TYPE_ERROR)
