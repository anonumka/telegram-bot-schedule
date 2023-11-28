import sys
import glob
import importlib
from importlib import util
from pathlib import Path

from app import bot


def load_plugins(module_name):
    path_module = Path(f"app/modules/{module_name}.py")
    name_module = "app.modules.{}".format(module_name)
    spec = importlib.util.spec_from_file_location(name_module, path_module)
    load = importlib.util.module_from_spec(spec)
    # load.logger = logging.getLogger(plugin_name)
    spec.loader.exec_module(load)
    sys.modules["app.modules." + module_name] = load


path = "app/modules/*.py"
files = glob.glob(path)
for name in files:
    with open(name) as a:
        patt = Path(a.name)
        plugin_name = patt.stem
        load_plugins(plugin_name.replace(".py", ""))

bot.infinity_polling()
