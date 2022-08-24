import glob
from functools import wraps
from pathlib import Path
import subprocess
import warnings


def exc_cmd(cmd, *args):
    pcs = subprocess.run([cmd, *args], capture_output=True, text=True)

    if pcs.returncode:
        raise Exception(pcs.stderr, cmd, args)

    return pcs.stdout


def _old_env(activate_path):
    out = exc_cmd("awk", r'BEGIN {FS="\x3D"} /VIRTUAL_ENV=/ {print $2}', activate_path)

    old_env = Path(out.strip().strip('"'))

    return old_env


def _fix_paths(old_env, new_env, bin_path, _test=False):
    res = []
    for _path in glob.glob(bin_path + "/*"):
        res.append(
            exc_cmd(
                "sed",
                # NOTE Used a new character delimiter "~" to avoid escaping "/"
                r"s~%s~%s~"
                % (old_env, new_env) +
                " w /dev/stdout" if _test else "",
                _path,
            )
        )
    return res

def _fix_third_party():
    # 


def fix_env(path):
    new_env = path.absolute()
    bin_path = path / "bin"
    activate_path = bin_path / "activate"

    # --- 1 ---
    # the problem is usually the first line "#!" with an absolute path
    # we fetch the bad path and globally change it
    old_env = _old_env(activate_path)

    if not old_env.exists():
        _fix_paths(str(old_env), str(new_env), str(bin_path))
    else:
        warnings.warn("The environment is fine. Skipping...")


def main(args):
    # 1. fix paths with sed
    # 2. fix python ln
    # 3. fix python site-packages if it contained another version
    # XXX 3 is optional, could break stuff if depending of the tooling the user employs for envs

    path = Path(args.path)

    fix_env(path)
