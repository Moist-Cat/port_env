"""CLI commands and helper functions go here"""

import glob
from functools import wraps
import os
from pathlib import Path
import subprocess
import sys
import shutil
import warnings


def exc_cmd(cmd, *args):
    """Execute a command and raise an error if it returns > 0. """
    # XXX it also handles the UnicodeError sed/awk raises when reading a binary file
    # maybe I should blacklist those @ _fix_paths
    try:
        pcs = subprocess.run([cmd, *args], capture_output=True, text=True)
    except UnicodeDecodeError:
        print("Unicode error... must be binary.", args)
        return None

    if pcs.returncode:
        # XXX better exception type?
        raise Exception(pcs.stderr, cmd, args)

    return pcs.stdout


def _old_env(activate_path: Path) -> Path:
    """Get the old (broken) virtual env path with awk"""
    # no active_path being a Path instance doesn't break subprocess.run. It is converted to a string nicely.
    # NOTE \x3D is "=" in HEX
    out = exc_cmd("awk", r'BEGIN {FS="\x3D"} /^VIRTUAL_ENV/ {print $2}', activate_path)

    old_env = Path(out.strip().strip('"').strip("'"))

    assert old_env, "There is no VIRTUAL_ENV variable in your activate script."

    return old_env


def _fix_paths(old_env, new_env, bin_path, _test=False):
    """Fix all strings matching the old env path with sed"""
    res = []
    for _path in glob.glob(bin_path + "/*"):
        # yes, I will use mocks if it gets bigger
        # (probably)
        _write_out = "" if not _test else " w /dev/stdout"
        _commit = "-i" if not _test else "-n"
        res.append(
            exc_cmd(
                "sed",
                # NOTE Used a new character delimiter "~" to avoid escaping "/"
                # and remember that sed also uses {} so no f""
                r's~%s~%s~'
                % (old_env, new_env) + _write_out,
                _commit,
                _path,
            )
        )
    # XXX do not capture output if we use mocks
    return res

def fix_third_party(path, _test=False):
    """Move lib/python3.* if necessary to match the current version"""
    ver = "python" + ".".join(sys.version.split(".")[:2])
    site_packages = path / "lib" / ver

    if not site_packages.exists():
        warning.warn("Site packages is OK.")
        return None

    lib = path / "lib"
    assert lib.exists(), lib + " does not exist"

    # we move the old dir
    dirs = os.listdir(lib)
    # NOTE there is a small chance someone has another file there or even an
    # entire folder or other pyhton site packages
    # we just move the first one and give a warning if required
    for _dir in dirs:
        if _dir.startswith("python"):
            if not _test:
                shutil.move(lib / _dir, site_packages)
            else:
                return site_packages
            break
    else:
        raise FileNotFoundError(lib / "python*")
    if len(dirs) > 1:
        warnings.warn("Too many files or directories at site-packages: {dirs}")

def fix_env(path: Path):
    """Wrapper. Gets the old env and globally replaces it by the new one"""
    new_env = path.absolute()
    bin_path = path / "bin"
    activate_path = bin_path / "activate"

    # --- 1 ---
    # the problem is usually the first line "#!" with an absolute path
    # we fetch the bad path and globally change it
    old_env = _old_env(activate_path)

    if old_env.exists():
        warnings.warn("The environment is fine. Skipping...")
        return None

    # I think Path objects are transformed into strings (__str__ returns the raw path) but I prefer to be explicit
    _fix_paths(str(old_env), str(new_env), str(bin_path))


def main(args):
    """Fix the environment path. Also fix third-party libs is required."""
    # 1. fix paths with sed
    # 2. fix python site-packages if it contained another version
    # XXX 2 is optional, could break stuff if depending of the tooling the user employs for envs

    path = Path(args.path)

    fix_env(path)

    if args.fix_third_party:
        fix_third_party(path)
