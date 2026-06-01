#!/usr/bin/env python3
"""Pin the latest jdtls milestone into the mise `http:jdtls` backend.

jdtls is distributed only as timestamped tarballs from download.eclipse.org
(no GitHub releases, dropped from the mise registry), so there is no clean
version->URL contract for mise to follow automatically. This resolves the
newest milestone, finds its actual timestamped filename + sha256, rewrites the
three fields of the `[tools."http:jdtls"]` block in config.toml, and reinstalls.

Wired into topgrade as the `jdtls-refresh` custom command.
"""
import os
import re
import subprocess
import sys
import urllib.request

BASE = "https://download.eclipse.org/jdtls/milestones/"
CONFIG = os.path.expanduser("~/.config/mise/config.toml")
SECTION = '[tools."http:jdtls"]'


def fetch(url: str) -> str:
    # download.eclipse.org serves a themed HTML index; a UA avoids odd responses.
    req = urllib.request.Request(url, headers={"User-Agent": "jdtls-refresh"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode()


def resolve_latest() -> tuple[str, str, str]:
    # Dir entries render as <a href='/jdtls/milestones/1.58.0'>, so scope the
    # match to the path rather than scraping every x.y.z on the themed page.
    versions = sorted(
        set(re.findall(r"/jdtls/milestones/(\d+\.\d+\.\d+)", fetch(BASE))),
        key=lambda v: tuple(int(p) for p in v.split(".")),
    )
    if not versions:
        sys.exit("jdtls-refresh: no milestone versions found")
    ver = versions[-1]
    files = sorted(
        set(re.findall(rf"jdt-language-server-{re.escape(ver)}-\d+\.tar\.gz", fetch(f"{BASE}{ver}/")))
    )
    if not files:
        sys.exit(f"jdtls-refresh: no tarball found for {ver}")
    fname = files[-1]
    url = f"{BASE}{ver}/{fname}"
    sha = fetch(url + ".sha256").split()[0]
    return ver, url, f"sha256:{sha}"


def rewrite_block(text: str, values: dict[str, str]) -> str:
    out, in_section = [], False
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("["):
            in_section = stripped == SECTION
        if in_section:
            key = re.match(r"\s*(\w+)\s*=", line)
            if key and key.group(1) in values:
                out.append(f'{key.group(1)} = "{values[key.group(1)]}"\n')
                continue
        out.append(line)
    return "".join(out)


def main() -> None:
    with open(CONFIG) as f:
        text = f.read()
    if SECTION not in text:
        print(f"jdtls-refresh: no {SECTION} block in config.toml, skipping")
        return

    ver, url, checksum = resolve_latest()
    updated = rewrite_block(text, {"version": ver, "url": url, "checksum": checksum})
    if updated != text:
        with open(CONFIG, "w") as f:
            f.write(updated)
        print(f"jdtls-refresh: pinned {ver} ({url.rsplit('/', 1)[1]})")
    else:
        print(f"jdtls-refresh: already current at {ver}")

    subprocess.run(["mise", "install", "http:jdtls"], check=False)


if __name__ == "__main__":
    main()
