import importlib.util
import pathlib

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"


def load(name):
    """Import scripts/<name>.py as a module (scripts/ is not a package)."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
