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
                            description="4 listy kanałów z datami i licznikami", 
                            where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)]

def getDates():
    try:
        dates_raw = urlopen("https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/daty.txt").read().decode()
        dates = {}
        for line in dates_raw.split('\n'):
            if '=' in line:
                name, date = line.split('=', 1)
                dates[name.strip()] = date.strip()
        return dates
    except:
        return {}

def getCounters():
    try:
        counters_raw = urlopen("https://marqozzz.github.io/MarqozzzCUP-/lists/pobrania.php").read().decode()
        counters = {}
        for line in counters_raw.split('\n'):
            if ':' in line:
                name, count = line.split(':', 1)
                counters[name.strip()] = count.strip()
        return counters
    except:
        return {}

def main(session, **kwargs):
    lists = [
        ("Hotbird @Bzyk83 mod. Republika", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/marqozzzcup-complete-HB-REPUBLIKA.zip"),
        ("Hotbird+Astra @Bzyk83 mod. Republika", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/marqozzzcup-complete-HB-ASTRA-REPUBLIKA.zip"),
        ("Hotbird @Bzyk83", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/marqozzzcup-complete-HB.zip"),
        ("Hotbird+Astra @Bzyk83", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/marqozzzcup-complete-HB-ASTRA.zip")
    ]
    
    dates = getDates()
    counters = getCounters()
    
    lists_display = []
    for name, url in lists:
        date = dates.get(name, "brak daty")
        count = counters.get(name, "0")
        display = "%s | 📊%s | ⏰%s" % (name, count, date)
        lists_display.append((display, url, name))  # name do licznika
    
    def choiceCallback(choice):
        if choice and len(choice) > 1:
            url = choice[1]
            full_name = choice[0]
            real_name = choice[2]
            confirmCallback(session, True, url, full_name, real_name)
    
    session.openWithCallback(choiceCallback, ChoiceBox, 
                            title="🛰️ MarqozzzCUP - Wybierz listę:", list=lists_display)

def confirmCallback(session, confirmed, url, full_name, real_name):
    if confirmed:
        installList(session, url, full_name, real_name)

def installList(session, url, full_name, real_name):
    # INKREMENTUJ LICZNIK
    try:
        urlopen("https://marqozzz.github.io/MarqozzzCUP-/lists/pobrania.php?list=%s" % real_name)
        print("✅ Licznik zaktualizowany: %s" % real_name)
    except:
        print("⚠️ Błąd licznika")
    
    try:
        print("MarqozzzCUP: Instaluję %s" % full_name)
        
        if os.path.exists("/etc/enigma2/bouquets.tv"):
            shutil.copy2("/etc/enigma2/bouquets.tv", "/etc/enigma2/bouquets.tv.bak")
        
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
        
        session.open(MessageBox, text="✅ ZAINSTALOWANO!\n%s\n📊 Plików: %d\n🔄 Restart za 5s..." % (full_name, files_copied), 
                     type=MessageBox.TYPE_INFO, timeout=5)
        
        os.system("(sleep 5 && killall -9 enigma2) &")
        
    except Exception as e:
        session.open(MessageBox, text="❌ BŁĄD!\n%s\n%s" % (full_name, str(e)), type=MessageBox.TYPE_ERROR)
