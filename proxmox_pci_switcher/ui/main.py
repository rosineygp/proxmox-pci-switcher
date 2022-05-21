from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivy.clock import Clock
from kivy import Logger

from proxmox_pci_switcher import (
    DEFAULT_LINUX_PATH,
    expand_config_path,
    load_config_file,
    connection_proxmox,
    list_resources,
    proxmox_pci_switcher,
)

config = load_config_file(expand_config_path(DEFAULT_LINUX_PATH))
px = connection_proxmox(config["proxmox"])


class AvatarIcon(TwoLineAvatarIconListItem):

    _data = None
    _dialog = None

    def on_release(self, *args):

        if self._data["status"] == "running":
            return

        if not self._dialog:

            def _power_on():
                Snackbar(
                    text=f"Power On {self._data['vmid']} ({self._data['name']})"
                ).open()
                proxmox_pci_switcher(px, self._data)
                Logger.info(
                    f"Power On {self._data['vmid']}. Please wait machine start."
                )
                self._dialog.dismiss()

            self._dialog = MDDialog(
                text=f"Power On [b]{self._data['vmid']} ({self._data['name']})[/b] member of [b]{self._data['pool']}[/b] ?",
                buttons=[
                    MDFlatButton(
                        text="CANCEL", on_release=lambda _: self._dialog.dismiss()
                    ),
                    MDRaisedButton(text="Power On", on_release=lambda _: _power_on()),
                ],
            )
        self._dialog.open()


class MainApp(MDApp):

    _theme_style = "Light"
    _md_list = []
    _clock_init = None
    _list_verify = []

    def theme_switch(self):
        try:
            self.theme_cls.theme_style = config["gui"]["theme"]
        except (KeyError, ValueError):
            self.theme_cls.theme_style = "Light"

    def refresh(self, *args):
        self.main_list_load()
        Snackbar(text="Refresh!").open()

    def main_list_load(self, *args):
        _list = list_resources(px, config["pools"])

        if self._list_verify == _list:
            return

        self._list_verify = _list

        _list_size = len(self._md_list)
        if _list_size > 0:
            for i in range(_list_size):
                self.root.ids.container.remove_widget(self._md_list.pop())

        for i in list_resources(px, config["pools"])[0]:

            li = AvatarIcon(text=f"{i['vmid']} ({i['name']})", secondary_text=i["pool"])

            if i["status"] == "running":
                li.add_widget(IconLeftWidget(icon="play-circle-outline"))
            else:
                li.add_widget(IconLeftWidget(icon="stop-circle"))

            li._data = i

            self._md_list.append(li)

            self.root.ids.container.add_widget(li)

    def on_start(self, *args):
        self.theme_switch()
        self.main_list_load()

        self.title = "Proxmox PCI Switcher"
        self.icon = "logo.png"

        if not self._clock_init:
            self._clock_init = True
            Clock.schedule_interval(self.main_list_load, 1)


MainApp().run()
