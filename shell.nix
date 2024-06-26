{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs.python3Packages; [
    setuptools
    wheel
    build
    pip
    tkinter
    black
    flake8
    pytest
    fpdf 
    pandas
  ] ++ [ pkgs.sqlite ];

  shellHook = ''
    echo "Development environment for mahlzeit is ready."
  '';
}
