"""A Qt panel for assembling a Nuke Write path from scene context."""

from pathlib import Path

from necessities.assemble import Scene as _SceneSpecification
from nuix.lineedit import LineEditValidator as _LineEdit
from nuix.node_preset import NodePresetWidget as _NodePresetWidget
from Qt import QtCore as _QtCore
from Qt import QtGui as _QtGui
from Qt import QtWidgets as _QtWidgets

import nuke


class Panel(_QtWidgets.QWidget):
    """Embedded editor for the project, sequence, shot, description, and version."""

    REQUIRED_FIELDS = ("project", "sequence", "shot", "description", "version")

    def __init__(self, node: nuke.Node | None = None, parent: _QtWidgets.QWidget | None = None) -> None:
        """Build the output-path editor for the current Nuke Write node.

        Args:
            node: The Write node whose file knob is edited. Defaults to Nuke's current node.
            parent: Optional parent widget.

        Returns:
            None: The embedded widget is initialized in place.
        """
        super().__init__(parent)
        self.node = node if node is not None else nuke.thisNode()
        self.specification = _SceneSpecification.from_application(application="nuke")
        self.current_path = ""
        self.setMinimumWidth(420)

        self.fields: dict[str, _LineEdit] = {}
        form = _QtWidgets.QFormLayout(self)
        for field_name, label in (
            ("project", "Project"),
            ("sequence", "Sequence"),
            ("shot", "Shot"),
            ("description", "Description"),
            ("version", "Version"),
        ):
            initial_text = "1" if field_name == "version" else ""
            editor = _LineEdit(parent=self, text=initial_text, no_validation=True)
            self.fields[field_name] = editor
            form.addRow(label, editor)

        self.preset_widget = _NodePresetWidget(
            node=self.node,
            after_apply=self.update_path,
            parent=self,
        )
        form.addRow("Node preset", self.preset_widget)

        self.preview = _QtWidgets.QLabel()
        self.preview.setWordWrap(True)
        self.preview.setTextInteractionFlags(_QtCore.Qt.TextSelectableByMouse)
        form.addRow("Path preview", self.preview)

        self.options_button = _QtWidgets.QPushButton("Options")
        self.options_menu = _QtWidgets.QMenu(self.options_button)
        self.copy_action = self.options_menu.addAction("Copy path to clipboard")
        self.open_folder_action = self.options_menu.addAction("Open output folder")
        self.options_button.setMenu(self.options_menu)

        form.addRow(self.options_button)

        for editor in self.fields.values():
            editor.textChanged.connect(self.update_path)
        self.copy_action.triggered.connect(lambda _checked=False: self.copy_to_clipboard())
        self.open_folder_action.triggered.connect(lambda _checked=False: self.open_output_folder())
        self.update_path()

    def makeUI(self) -> _QtWidgets.QWidget:
        """Return this widget for Nuke's PyCustom_Knob.

        Returns:
            QtWidgets.QWidget: The embedded path editor.
        """
        return self

    def get_path(self) -> str:
        """Return the assembled path currently shown in the preview.

        Returns:
            str: The output path.
        """
        return self.current_path

    def update_path(self, _text: str = "") -> bool:
        """Rebuild the path preview and update the node when all fields are filled.

        Args:
            _text: Optional textChanged signal argument.

        Returns:
            bool: Whether a complete path was assembled and written to the node.
        """
        values = {name: editor.text().strip() for name, editor in self.fields.items()}
        missing_fields = [name for name in self.REQUIRED_FIELDS if not values[name]]
        if missing_fields:
            self.current_path = ""
            self.preview.setText(f"Enter {', '.join(missing_fields)} to build the path.")
            return False

        specification = self.specification.replace(
            show=values["project"],
            sequence=values["sequence"],
            shot=values["shot"],
            description=values["description"],
            version=values["version"],
        )
        self.current_path = specification.resolve()
        self.preview.setText(self.current_path)
        self.node["file"].setValue(self.current_path)
        return True

    def copy_to_clipboard(self) -> bool:
        """Copy the current output path to the application clipboard.

        Returns:
            bool: Whether the path was copied.
        """
        if not self.get_path():
            return False
        _QtWidgets.QApplication.clipboard().setText(self.get_path())
        return True

    def open_output_folder(self) -> bool:
        """Open the directory containing the current output path.

        Returns:
            bool: Whether the desktop service accepted the open request.
        """
        if not self.get_path():
            return False
        directory = Path(self.get_path()).expanduser().resolve().parent
        return _QtGui.QDesktopServices.openUrl(_QtCore.QUrl.fromLocalFile(str(directory)))
