import glob
from functools import wraps
import os
from pathlib import Path
import subprocess
import sys
import shutil
import warnings


def exc_cmd(cmd, *args):
    try:
        pcs = subprocess.run([cmd, *args], capture_output=True, text=True)
    except UnicodeDecodeError:
        print("Unicode error... must be binary.", args)
        return None

    if pcs.returncode:
        raise Exception(pcs.stderr, cmd, args)

    return pcs.stdout


def _old_env(activate_path):
    out = exc_cmd("awk", r'BEGIN {FS="\x3D"} /^VIRTUAL_ENV/ {print $2}', activate_path)

    old_env = Path(out.strip().strip('"').strip("'"))

    assert old_env, ""

    return old_env


def _fix_paths(old_env, new_env, bin_path, _test=False):
    res = []
    for _path in glob.glob(bin_path + "/*"):
        to_cli = "" if not _test else " w /dev/stdout"
        res.append(
            exc_cmd(
                "sed",
                # NOTE Used a new character delimiter "~" to avoid escaping "/"
                r's~%s~%s~'
                % (old_env, new_env),
                "-i",
                _path,
            )
        )
    return res

def fix_third_party(path, _test=False):
    ver = "python" + ".".join(sys.version.split(".")[:2])
    site_packages = path / "lib" / ver
    if not path.exists():
        warning.warn("Site packages is OK.")
        return None

    lib = path / "lib"
    assert lib.exists(), lib + " does not exists"

    # we move the old dir
    dirs = os.listdir(lib)
    # NOTE there is a small chance someone has another file there or even an
    # entire folder or other pyhton site packages
    # we just move the first one and give a warning
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

def fix_env(path):
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
    # 1. fix paths with sed
    # 2. fix python ln
    # 3. fix python site-packages if it contained another version
    # XXX 3 is optional, could break stuff if depending of the tooling the user employs for envs

    path = Path(args.path)

    fix_env(path)

    if args.fix_third_party:
        fix_third_party(path)
