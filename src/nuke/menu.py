"""Nuke menu setup for nuclear."""

import nuke  # noqa: I001 -- Nuke provides this host API module.


pipeline_menu = nuke.menu("Nodes").addMenu("wgid")
pipeline_menu.addCommand(
    "Create Layer Contact Sheet Group",
    "import nuclear.contactsheet.layer_contact_sheet as contactsheet; contactsheet.create_group()",
)
pipeline_menu.addCommand(
    "Create Custom Write",
    "import nuclear.custom_write.write as custom_write; custom_write.create()",
)
