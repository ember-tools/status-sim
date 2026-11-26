{ pkgs ? import <nixpkgs> {}, ... }:

pkgs.mkShell {
  packages = with pkgs; [
    python314
    pipenv
    nodejs_24
  ];
  shellHook = ''
    export PIPENV_VENV_IN_PROJECT=1
  '';
}
