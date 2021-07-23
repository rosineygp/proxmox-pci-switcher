import unittest
from unittest.mock import patch
from proxmox_pci_switcher import expand_config_path

from pathlib import Path


class TestExpandConfigPath(unittest.TestCase):
    @patch("proxmox_pci_switcher.os.name", "posix")
    def test_expand_config_path_default_linux(self):

        _home = Path.home()

        self.assertEqual(
            f"{_home}/.config/proxmox-pci-switcher/config.yaml",
            expand_config_path("~/.config/proxmox-pci-switcher/config.yaml"),
        )

    @patch("proxmox_pci_switcher.os.name", "nt")
    def test_expand_config_path_default_windows(self):

        self.assertEqual(
            "~\\AppData\\Local\\proxmox-pci-switcher\\config.yaml",
            expand_config_path("~/.config/proxmox-pci-switcher/config.yaml"),
        )

    @patch("proxmox_pci_switcher.os.name", "posix")
    def test_expand_config_path_custom_path(self):
        self.assertEqual(
            "/etc/ppw/config.yaml",
            expand_config_path("/etc/ppw/config.yaml"),
        )


if __name__ == "__main__":
    unittest.main()
