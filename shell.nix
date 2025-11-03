{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.pip
  ];

  shellHook = ''
    export PYTHONPATH=$PWD/.venv/lib/python3.*/site-packages:$PYTHONPATH
    if [ ! -d .venv ]; then
      python3 -m venv .venv
      source .venv/bin/activate
      pip install pandas psutil tabulate dill jsonpickle numpy
    else
      source .venv/bin/activate
    fi
  '';
}
