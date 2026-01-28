from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.ChoiceList import ChoiceList
from urllib.request import urlopen, urlretrieve
import zipfile
import os

def Plugins(**kwargs):
    return [PluginDescriptor(
        name="MarqozzzCUP", 
        description="Channel Updater", 
        where=PluginDescriptor.WHERE_PLUGINMENU,
        fnc=main
    )]

def main(session, **kwargs):
    session.open(MarqozzzCUPScreen)

class MarqozzzCUPScreen(Screen):
    skin = """
    <screen position="100,100" size="500,350" title="MarqozzzCUP - Channel Updater" flags="wfNoBorder">
        <ePixmap position="10,10" size="140,140" zPosition="1" 
                 pixmap="Extensions/MarqozzzCUP/icon.png" 
                 transparent="1" alphatest="blend" scale="1" />
        <widget name="choicelist" position="170,20" size="320,300" 
                zPosition="2" itemHeight="35" scrollbarMode="showOnDemand" />
        <ePixmap position="10,320" size="140,25" pixmap="skin_default/buttons/red.png" 
                 transparent="1" alphatest="on" />
        <ePixmap position="170,320" size="140,25" pixmap="skin_default/buttons/green.png" 
                 transparent="1" alphatest="on" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self["choicelist"] = ChoiceList(list=self.getLists())
        self["actions"] = ActionMap(["WizardActions", "ColorActions"],
            {"ok": self.ok, "back": self.cancel, "green": self.ok, "red": self.cancel}, -1)

    def getLists(self):
        return [
            ("Pełny Backup ZIP (Release)", "https://github.com/marqozzz/MarqozzzCUP-/releases/latest/download/fullbackup.zip"),
            ("Hotbird 13E", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/hotbird.tv"),
            ("Astra 19.2E", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/astra.tv")
        ]

    def ok(self):
        current = self["choicelist"].l.getCurrent()
        if current:
            self.current_url = current[1]
            self.session.openWithCallback(self.confirmUpdate, MessageBox, 
                text="Pobrać: %s?" % current[0])

    def confirmUpdate(self, confirmed):
        if confirmed:
            self.downloadList()
        self.close()

    def downloadList(self):
        try:
            if self.current_url.endswith('.zip'):
                self.installZip()
            else:
                data = urlopen(self.current_url).read()
                path = "/etc/enigma2/userbouquet.marqozzzcup.tv"
                with open(path, "wb") as f:
                    f.write(data)
                self.session.open(MessageBox, text="Lista pobrana!\nRestart GUI zalecany.", 
                                type=MessageBox.TYPE_INFO, timeout=5)
        except Exception as e:
            self.session.open(MessageBox, text="Błąd: %s" % str(e), type=MessageBox.TYPE_ERROR)

    def installZip(self):
        zip_path = "/tmp/marqozzzcup.zip"
        try:
            urlretrieve(self.current_url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("/etc/enigma2/")
            os.unlink(zip_path)
            self.session.open(MessageBox, text="Pełny backup zainstalowany!\nEnigma2 restart...", 
                            type=MessageBox.TYPE_INFO, timeout=5)
            os.system("init 4 && sleep 2 && init 3")
        except Exception as e:
            self.session.open(MessageBox, text="Błąd ZIP: %s" % str(e), type=MessageBox.TYPE_ERROR)
