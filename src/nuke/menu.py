"""Nuke menu setup for nuclear."""

import nuke  # noqa: I001 -- Nuke provides this host API module.


package_menu = nuke.menu("Nuke").addMenu("nuclear")
package_menu.addCommand(
    "About",
    lambda: nuke.message("nuclear Nuke tools"),
)
