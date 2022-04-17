import nuke
import yaml
import re
import os
import cProfile
import pstats



__PATTERN = r"nuke.createNode.+\"([\w.]+)"
__CLASS_FROM_SCRIPT = re.compile(__PATTERN)
__data_dump_path = os.path.join(os.path.dirname(__file__), "classes.yaml")
__class_data = {}


__KNOB_TO_AVOID = {
    "Axis_Knob",
    "Disable_Knob",
}


def node_knobs_structure(node):
    node_knob_data = {}
    for name, knob in node.knobs().items():
        if knob.Class() in __KNOB_TO_AVOID:
            continue
        value, values = knob.value(), None
        values = getattr(knob, "values", None)  # .009
        if isinstance(value, nuke.Format):
            value = knob.value().name()
        node_knob_data[name] = dict(type=knob.Class(), value=value, values=values)

    __class_data[node.Class()] = node_knob_data

    return node_knob_data


# Search the menus for the class information, from that generate knob names
def do(menu):
    for menu_item in menu.items():
        if isinstance(menu_item, nuke.Menu):
            do(menu_item)
        elif isinstance(menu_item, nuke.MenuItem):
            try:
                class_name = __CLASS_FROM_SCRIPT.findall(string=menu_item.script())[0]
                if not class_name:
                    continue
                node = nuke.createNode(class_name, inpanel=False)
                node_knobs_structure(node)
                nuke.delete(node)
            except (RuntimeError, IndexError):
                pass

    return True


def dump():
    with open(__data_dump_path, "r") as open_data_dump:
        previous = yaml.full_load(open_data_dump) or {}

    with open(__data_dump_path, "wb") as open_data_dump:
        previous.update(__class_data)
        yaml.dump(previous, open_data_dump)


def run():
    menu = nuke.menu("Nodes")
    profiler = cProfile.Profile()
    profiler.enable()
    do(menu)
    profiler.disable()
    dump()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()






