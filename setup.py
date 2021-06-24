from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="proxmox-pci-switcher",
    version="0.0.0",
    description="Switch among Guest VMs organized by Resource Pool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rosineygp/proxmox-pci-switcher",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: System :: Networking",
    ],
    author="Rosiney Gomes Pereira",
    author_email="rosiney.gp@gmail.com",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "proxmoxer==1.1.1",
        "requests==2.25.1",
        "paramiko==2.7.2",
        "argh==0.26.2",
        "PyYAML==5.4.1",
        "tabulate==0.8.9",
    ],
    entry_points={
        "console_scripts": [
            "proxmox-pci-switcher = proxmox_pci_switcher.proxmox_pci_switcher:__main",
        ],
    },
)
