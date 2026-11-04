"""Qt dialog for choosing contact-sheet AOVs and saved presets."""

import json
from typing import Any

from Qt import QtCore, QtWidgets


def _get_presets(settings: QtCore.QSettings) -> dict[str, dict[str, Any]]:
    """Read presets from persistent Qt settings.

    Args:
        settings: Settings store for this tool.

    Returns:
        dict[str, dict[str, Any]]: Stored presets.
    """
    try:
        data = json.loads(str(settings.value(_PRESET_KEY, "{}")))
    except (TypeError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


class ContactSheetDialog(QtWidgets.QDialog):
    """AOV and preset selector."""

    def __init__(self, group: Any, layers: list[str]) -> None:
        """Create the contact-sheet options dialog.

        Args:
            group: Contact-sheet Group carrying exposed font controls.
            layers: Available AOV names.

        Returns:
            None: Initializes the dialog.
        """
        super().__init__()
        self.group = group
        self.settings = QtCore.QSettings("nuclear", "ContactSheet")
        self.presets = _get_presets(self.settings)
        self.setWindowTitle("Build Layer Contact Sheet")
        self.setMinimumWidth(440)

        layout = QtWidgets.QVBoxLayout(self)
        preset_row = QtWidgets.QHBoxLayout()
        self.preset_combo = QtWidgets.QComboBox()
        self.preset_combo.addItem("Select preset…")
        self.preset_combo.addItems(sorted(self.presets))
        save_button = QtWidgets.QPushButton("Save Preset")
        delete_button = QtWidgets.QPushButton("Delete")
        preset_row.addWidget(QtWidgets.QLabel("Preset:"))
        preset_row.addWidget(self.preset_combo, 1)
        preset_row.addWidget(save_button)
        preset_row.addWidget(delete_button)
        layout.addLayout(preset_row)
        self.preset_combo.currentTextChanged.connect(self._load_preset)
        save_button.clicked.connect(self._save_preset)
        delete_button.clicked.connect(self._delete_preset)

        layout.addWidget(QtWidgets.QLabel("AOVs to include:"))
        self.layer_list = QtWidgets.QListWidget()
        self.layer_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.layer_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.layer_list.setMinimumHeight(150)
        self.layer_list.setMaximumHeight(300)
        for layer in layers:
            item = QtWidgets.QListWidgetItem(layer)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.layer_list.addItem(item)
        layout.addWidget(self.layer_list)

        selection_buttons = QtWidgets.QHBoxLayout()
        select_all = QtWidgets.QPushButton("Select All")
        deselect_all = QtWidgets.QPushButton("Deselect All")
        selection_buttons.addWidget(select_all)
        selection_buttons.addWidget(deselect_all)
        layout.addLayout(selection_buttons)
        select_all.clicked.connect(lambda: self._set_all(True))
        deselect_all.clicked.connect(lambda: self._set_all(False))

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _set_all(self, checked: bool) -> None:
        """Set all AOV checkboxes to the requested state.

        Args:
            checked: True to select all, False to clear all.

        Returns:
            None: Updates the list in place.
        """
        state = QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked
        for index in range(self.layer_list.count()):
            self.layer_list.item(index).setCheckState(state)

    def selected_layers(self) -> list[str]:
        """Return the checked AOV names.

        Returns:
            list[str]: Selected AOVs in list order.
        """
        return [
            self.layer_list.item(index).text()
            for index in range(self.layer_list.count())
            if self.layer_list.item(index).checkState() == QtCore.Qt.Checked
        ]

    def _preset_data(self) -> dict[str, Any]:
        """Collect the current AOV and output settings.

        Returns:
            dict[str, Any]: JSON-serializable preset data.
        """
        return {
            "layers": self.selected_layers(),
            "font_type": self.group["font_type"].value(),
            "font_size": self.group["font_size"].value(),
        }

    def _load_preset(self, name: str) -> None:
        """Apply a saved preset to the dialog and Group controls.

        Args:
            name: Preset name to load.

        Returns:
            None: Updates the current settings.
        """
        preset = self.presets.get(name)
        if not preset:
            return
        selected = set(preset.get("layers", []))
        for index in range(self.layer_list.count()):
            item = self.layer_list.item(index)
            item.setCheckState(QtCore.Qt.Checked if item.text() in selected else QtCore.Qt.Unchecked)
        self.group["font_type"].setValue(str(preset.get("font_type", _DEFAULT_FONT)))
        self.group["font_size"].setValue(float(preset.get("font_size", 0.5)))

    def _save_preset(self) -> None:
        """Save the current selections and settings under a chosen name.

        Returns:
            None: Saves when the user enters a non-empty name.
        """
        name, accepted = QtWidgets.QInputDialog.getText(self, "Save preset", "Preset name:")
        name = name.strip()
        if not accepted or not name:
            return
        self.presets[name] = self._preset_data()
        self.settings.setValue(_PRESET_KEY, json.dumps(self.presets))
        self.settings.sync()
        if self.preset_combo.findText(name) < 0:
            self.preset_combo.addItem(name)
        self.preset_combo.setCurrentText(name)

    def _delete_preset(self) -> None:
        """Delete the selected preset.

        Returns:
            None: Deletes the preset when one is selected.
        """
        name = self.preset_combo.currentText()
        if name not in self.presets:
            return
        del self.presets[name]
        self.settings.setValue(_PRESET_KEY, json.dumps(self.presets))
        self.settings.sync()
        self.preset_combo.removeItem(self.preset_combo.currentIndex())


def show_contact_sheet_dialog(group: Any, layers: list[str]) -> list[str] | None:
    """Show the AOV selector and return checked layers when accepted.

    Args:
        group: Contact-sheet Group with font controls.
        layers: Available AOV names.

    Returns:
        list[str] | None: Selected layers, or None when cancelled.
    """
    dialog = ContactSheetDialog(group, layers)
    execute = getattr(dialog, "exec_", None) or dialog.exec
    if execute() != QtWidgets.QDialog.Accepted:
        return None
    return dialog.selected_layers()



