"""Helpers for creating Nuke Write nodes."""

import nuke


def create() -> nuke.Node:
    """Create a Write node with its embedded custom path widget.

    Returns:
        nuke.Node: The Write node with the custom widget attached.
    """
    node = nuke.createNode("Write", inpanel=False)
    # Add a custom tab
    node.addKnob(nuke.Tab_Knob("WGID"))

    panel_knob = nuke.PyCustom_Knob(
        "pyobject",
        "Custom Write",
        "__import__('nuclear.custom_write.panel', fromlist=['Panel']).Panel()",
    )
    node.addKnob(panel_knob)
    node.showControlPanel()
    return node


import importlib

import nuclear.custom_write.panel

importlib.reload(nuclear.custom_write.panel)

import importlib

import nuclear.custom_write.panel as panel

importlib.reload(panel)


create()
