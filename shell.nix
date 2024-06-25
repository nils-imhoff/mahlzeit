{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.virtualenv
    pkgs.python3Packages.tkinter
    pkgs.python3Packages.black
    pkgs.python3Packages.flake8
    pkgs.python3Packages.pytest
    pkgs.sqlite
  ];

  shellHook = ''
    # Erstelle eine virtuelle Umgebung und aktiviere sie
    if [ ! -d "venv" ]; then
      virtualenv venv
    fi
    source venv/bin/activate

    # Installiere zusätzliche Python-Pakete
    pip install --upgrade pip
    pip install black flake8 pytest tk
  '';
}
