import os
from setuptools import find_packages, setup

_version = os.getenv("MKDKR_BRANCH_NAME", "0.0.0").replace("v", "")

with open("README.md") as f:
    long_description = f.read()

setup(
    name="proxmox-pci-switcher",
    version=_version,
    description="Switch among Guest VMs organized by Resource Pool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rosineygp/proxmox-pci-switcher",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: System :: Networking",
    ],
    author="Rosiney Gomes Pereira",
    author_email="rosiney.gp@gmail.com",
    packages=find_packages(),
    package_data={"": ["*.kv", "*.png"]},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "proxmoxer==1.3.1",
        "requests==2.27.1",
        "paramiko==2.10.4",
        "argh==0.26.2",
        "PyYAML==6.0",
        "tabulate==0.8.9",
        "Kivy==2.1.0",
        "kivymd==0.104.2",
    ],
    entry_points={
        "console_scripts": [
            "proxmox-pci-switcher = proxmox_pci_switcher.proxmox_pci_switcher:__main",
        ],
    },
)
