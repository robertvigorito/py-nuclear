"""What I want to achieve is an easy way for users to selected knobs (name and value)
from nodes within the script to copy those values.

[     ] [      ] +

"""
import json

from collections import defaultdict
from pprint import pprint as pp
import pprint
# DCC Imports
import nuke
import nukescripts

structure = defaultdict(list)


def run():
    for node in nuke.allNodes():
        for knob in node.allKnobs():
            values = value = None
            if hasattr(knob, "values"):
                values = knob.values()
            if hasattr(knob, "value"):
                value = knob.value()
            if isinstance(knob, nuke.Format_Knob):
                value = knob.value().name()

            class_structure = {
                "class": knob.Class(),
                "name": knob.name(),
                "label": knob.label(),
                "value": value,
                "values": values,
            }
            structure[node.Class()].append(class_structure)
run()


with open(r"V:\dev\nuclear\nuke\mimi\knobs_by_classes.py", "w") as open_file:
    json.dump(structure, open_file, indent=4, sort_keys=True)