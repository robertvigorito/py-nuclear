"""Create and build a Group-based Nuke layer contact sheet."""

from pathlib import Path
from typing import Any

import nuke
from nuclear.widgets import show_contact_sheet_dialog


def clean_up_previous_nodes(group: nuke.Node) -> bool:
    """Remove all existing Text2 nodes within the group.

    Args:
        group: Contact-sheet Group node.

    Returns:
        bool: True if any nodes were removed, otherwise False.
    """
    removed = False

    for node in nuke.allNodes():
        if node.Class() in ["Remove", "Text2"] and not node.name().startswith("ContactSheet"):
            nuke.delete(node)
            removed = True
    return removed


def build_graph(group: Any, selected_layers: list[str], all_layers: list[str]) -> bool:
    """Build the internal AOV-filter, label, and contact-sheet graph.

    Args:
        group: Contact-sheet Group node.
        selected_layers: List of layers to include in the contact sheet.
        all_layers: List of all available layers.

    Returns:
        bool: True if the graph was successfully built, otherwise False.
    """
    knob_names = ["box", "global_font_scale"]

    with group:
        clean_up_previous_nodes(group)

        input_node = nuke.toNode("Input1")
        for layer_to_remove in set(all_layers) - set(selected_layers):
            input_node = nuke.nodes.Remove(
                inputs=[input_node],
                operation="Remove",
                channels=layer_to_remove,
            )

        for _, layer in enumerate(selected_layers, start=1):
            label_node = nuke.nodes.Text2(
                inputs=[input_node],
                message=layer,
                output=layer,
                xjustify=group["xjustify"].value(),
                yjustify=group["yjustify"].value(),
            )
            # Expression link to the main text node
            for knob_name in knob_names:
                label_node[knob_name].setExpression(f"parent.{knob_name}")

            input_node = label_node
        nuke.toNode("START_DOT").setInput(0, input_node)

        # Reposition all nodes within the group
        for node in group.nodes():
            node.autoplace()

    return True


def run(group: Any = None) -> bool:
    """Display AOV choices and build the selected Group's contact sheet.

    Args:
        group: Contact-sheet Group; defaults to Nuke's current node.

    Returns:
        bool: True if a graph was built, otherwise False.
    """
    group = group or nuke.thisNode()

    layers = list(nuke.layers(group.input(0)))
    for layer_to_remove in {"rgb", "alpha"}:
        layers.remove(layer_to_remove) if layer_to_remove in layers else None

    if not layers:
        nuke.message("The connected Read node has no AOV layers.")
        return False

    selected = show_contact_sheet_dialog(group, layers)
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


# Clear node selection
import nukescripts


nukescripts.clear_selection_recursive()
nuke.toNode("Read2").setSelected(True)
group = create_group()
# run(group)
build_graph(group, ["C_LS0", "C_LS1", "C_LS2"], nuke.layers(nuke.toNode("Read2")))
