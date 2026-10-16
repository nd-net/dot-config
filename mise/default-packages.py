#!/usr/bin/env python3
"""Install default packages into a Python or Ruby that mise just installed.

Replaces mise's `python.default_packages_file` / `ruby.default_packages_file`
settings, which mise stops reading in 2027.11.0. Wired up as the per-tool
`postinstall` of the global config's python/ruby entries, which mise runs only
when it installs the version that entry requests: versions pinned by a
project's mise.toml or `.python-version` / `.ruby-version` stay vanilla.

The hook only fires when mise actually installs the version. If a project
installs a version first (say 3.16) and the global "latest" later resolves to
that same, already installed version, the global default never gets the
packages. Run this script by hand for that version:

    MISE_TOOL_NAME=python MISE_TOOL_INSTALL_PATH=$(mise where python) \\
        python3 ~/.config/mise/default-packages.py

(likewise with `ruby`).
"""
# Keeps `str | Path` annotations unevaluated for macOS's /usr/bin/python3 (3.9).
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
PYTHON_PACKAGES = CONFIG_HOME / "python" / "default-python-packages"
RUBY_GEMS = CONFIG_HOME / "ruby" / "default-gems"


class SetupError(Exception):
    """A problem worth a one-line explanation instead of a traceback."""


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SetupError(
            f"{name} is not set; this script expects to run as a mise tool"
            " postinstall, or with it set by hand (see the docstring)"
        )
    return value


def require_file(path: Path, what: str) -> Path:
    if not path.is_file():
        raise SetupError(f"{what} not found at {path}")
    return path


def run(args: list[str | Path]) -> None:
    result = subprocess.run(args)
    if result.returncode != 0:
        raise SetupError(f"`{shlex.join(map(str, args))}` failed with exit code {result.returncode}")


def install_python(install_path: Path) -> None:
    uv = shutil.which("uv")
    if uv is None:
        raise SetupError(
            "uv is not on PATH; it must be installed before python"
            ' (`depends = ["uv"]` on the python entry)'
        )
    python = require_file(install_path / "bin" / "python3", "python3 interpreter")
    packages = require_file(PYTHON_PACKAGES, "default Python packages file")
    run([uv, "pip", "install", "--system", "--python", python, "--requirements", packages])


def install_ruby(install_path: Path) -> None:
    gem = require_file(install_path / "bin" / "gem", "gem executable")
    lines = require_file(RUBY_GEMS, "default gems file").read_text().splitlines()
    for number, line in enumerate(lines, start=1):
        # One gem per line, optionally followed by `gem install` arguments
        # such as `--version 2.5`, matching mise's default-gems format.
        try:
            args = shlex.split(line, comments=True)
        except ValueError as e:
            raise SetupError(f"{RUBY_GEMS}:{number}: cannot parse line: {e}") from e
        if args:
            run([gem, "install", "--no-document", *args])


INSTALLERS = {"python": install_python, "ruby": install_ruby}


def main() -> int:
    try:
        name = require_env("MISE_TOOL_NAME")
        install_path = Path(require_env("MISE_TOOL_INSTALL_PATH"))
        installer = INSTALLERS.get(name)
        if installer is None:
            raise SetupError(
                f"no default packages defined for tool {name!r}"
                f" (supported: {', '.join(INSTALLERS)})"
            )
        if not install_path.is_dir():
            raise SetupError(f"install path {install_path} is not a directory")
        installer(install_path)
    except (SetupError, OSError) as e:
        # A failing postinstall fails the mise install; say why up front.
        print(f"default-packages: error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
