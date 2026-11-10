"""Create and build a Group-based Nuke layer contact sheet."""

from pathlib import Path

import nuke
from nuclear.contactsheet.widgets import show_contact_sheet_dialog


def knob_changed_callback():
    """Callback function for when a knob value changes.

    Returns:
        bool: True if the knob change was handled, otherwise False.
    """
    this_knob = nuke.thisKnob()
    if not this_knob:
        return False
    if this_knob.name() not in {"xjustify", "yjustify", "font"}:
        return
    for node in nuke.thisNode().parent().nodes():
        if node.name() == "ContactSheetText":
            continue
        if node.knob(this_knob.name()):
            node[this_knob.name()].fromScript(this_knob.toScript())
    return True


def clean_up_previous_nodes() -> bool:
    """Remove all existing Text2 nodes within the current group.

    Returns:
        bool: True if any nodes were removed, otherwise False.
    """
    removed = False

    for node in nuke.allNodes():
        if node.Class() in ["Remove", "Text2"] and not node.name().startswith("ContactSheet"):
            nuke.delete(node)
            removed = True
    return removed


def build_graph(group: nuke.Node, selected_layers: list[str], all_layers: list[str]) -> bool:
    """Build the internal AOV-filter, label, and contact-sheet graph.

    Args:
        group: Contact-sheet Group node.
        selected_layers: List of layers to include in the contact sheet.
        all_layers: List of all available layers.

    Returns:
        bool: True if the graph was successfully built, otherwise False.
    """

    with group:
        clean_up_previous_nodes()
        input_node = nuke.toNode("Input1")
        # Always add rgba

        for layer_to_remove in set(all_layers) - set(selected_layers):
            if layer_to_remove in {"rgb", "alpha"}:
                continue
            input_node = nuke.nodes.Remove(inputs=[input_node], operation="Remove", channels=layer_to_remove)

        for _, layer in enumerate(selected_layers, start=1):
            label_node = nuke.nodes.Text2(
                inputs=[input_node],
                message=layer,
                output=layer,
                xjustify=group["xjustify"].value(),
                yjustify=group["yjustify"].value(),
                font=group["font"].value(),
            )
            # Expression link to the main text node
            for knob_name in {"box", "global_font_scale"}:
                label_node[knob_name].setExpression(f"parent.{knob_name}")

            input_node = label_node
        # Connect the final node to the START_DOT node
        nuke.toNode("START_DOT").setInput(0, input_node)

        # Reposition all nodes within the group
        for node in group.nodes():
            node.autoplace()

    return True


def run(group: nuke.Node | None = None) -> bool:
    """Display AOV choices and build the selected Group's contact sheet.

    Args:
        group: Contact-sheet Group; defaults to Nuke's current node.

    Returns:
        bool: True if a graph was built, otherwise False.
    """
    group = group or nuke.thisNode()

    # Check the inputs since the existing layers might be corrupted by previous run.
    layers = list(nuke.layers(group.input(0)) or nuke.layers())[
        3:
    ]  # Skip the first three default layers (rgba, rgb, alpha)
    selected = show_contact_sheet_dialog(layers)
    if selected is None:
        return False
    if not selected:
        nuke.message("Select at least one AOV to build a contact sheet.")
        return False
    build_graph(group, selected, layers)
    return True


def create_group(*_, **kwargs) -> nuke.Node | None:
    """Create a Group, optionally wire a Read node, and expose its controls.

    Args:
        **kwargs: Arbitrary keyword arguments to set on the created Group node.

    Returns:
        nuke.Node | None: Created Group, or None if an invalid node was provided.
    """
    group_script = Path(__file__).parent / "LayerContactSheet.nk"

    group = nuke.nodePaste(str(group_script))
    if not group:
        return None

    for knob_name, knob_value in kwargs.items():
        if group.knob(knob_name):
            group[knob_name].setValue(knob_value)

    return group
