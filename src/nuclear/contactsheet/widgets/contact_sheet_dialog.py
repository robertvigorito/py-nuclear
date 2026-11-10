"""Qt dialog for choosing AOVs for a contact sheet."""

import json as _json
import re as _re

from Qt import QtCore as _QtCore
from Qt import QtGui as _QtGui
from Qt import QtSvg as _QtSvg
from Qt import QtWidgets as _QtWidgets

_SELECT_PRESET = "Select preset…"
_ADD_PRESET_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
    '<path fill-rule="evenodd" clip-rule="evenodd" d="'
    "M12 22C7.28595 22 4.92893 22 3.46447 20.5355C2 19.0711 2 16.714 2 12C2 7.28595 2 4.92893 3.46447 "
    "3.46447C4.92893 2 7.28595 2 12 2C16.714 2 19.0711 2 20.5355 3.46447C22 4.92893 22 7.28595 22 12 "
    "C22 16.714 22 19.0711 20.5355 20.5355C19.0711 22 16.714 22 12 22ZM12 8.25C12.4142 8.25 12.75 "
    "8.58579 12.75 9V11.25H15C15.4142 11.25 15.75 11.5858 15.75 12C15.75 12.4142 15.4142 12.75 15 "
    "12.75H12.75L12.75 15C12.75 15.4142 12.4142 15.75 12 15.75C11.5858 15.75 11.25 15.4142 11.25 "
    "15V12.75H9C8.58579 12.75 8.25 12.4142 8.25 12C8.25 11.5858 8.58579 11.25 9 11.25H11.25L11.25 "
    '9C11.25 8.58579 11.5858 8.25 12 8.25Z" fill="#ff8c00"/></svg>'
)
_DELETE_PRESET_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'
    '<path fill-rule="evenodd" clip-rule="evenodd" d="'
    "M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 "
    "2 22 6.47715 22 12ZM8.96963 8.96965C9.26252 8.67676 9.73739 8.67676 10.0303 8.96965L12 10.9393 "
    "L13.9696 8.96967C14.2625 8.67678 14.7374 8.67678 15.0303 8.96967C15.3232 9.26256 15.3232 9.73744 "
    "15.0303 10.0303L13.0606 12L15.0303 13.9696C15.3232 14.2625 15.3232 14.7374 15.0303 15.0303 "
    "C14.7374 15.3232 14.2625 15.3232 13.9696 15.0303L12 13.0607L10.0303 15.0303C9.73742 15.3232 "
    "9.26254 15.3232 8.96965 15.0303C8.67676 14.7374 8.67676 14.2625 8.96965 13.9697L10.9393 12L8.96963 "
    '10.0303C8.67673 9.73742 8.67673 9.26254 8.96963 8.96965Z" fill="#ff8c00"/></svg>'
)
_ICON_COLOR = "#ff8c00"
_HOVER_COLOR = "#0078D4"
_PRESET_COMBO_STYLE = """
QComboBox {
    border: 1px solid #C8CDD6;
    border-radius: 6px;
    padding: 5px 10px;
}
QComboBox:hover {
    border-color: #8A94A6;
}
QComboBox:focus {
    border-color: #0078D4;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
"""


def svg_icon(svg: str, color: str) -> _QtGui.QIcon:
    """Render SVG markup in the given fill color as a high-density icon.

    Args:
        svg: Complete SVG document whose fill is the default icon color.
        color: Hex fill color to apply.

    Returns:
        QIcon: Rendered 24px vector icon at 2x device pixel ratio.
    """
    markup = svg.replace(f'fill="{_ICON_COLOR}"', f'fill="{color}"')
    renderer = _QtSvg.QSvgRenderer(_QtCore.QByteArray(markup.encode("utf-8")))
    pixmap = _QtGui.QPixmap(48, 48)
    pixmap.setDevicePixelRatio(2.0)
    pixmap.fill(_QtCore.Qt.transparent)
    painter = _QtGui.QPainter(pixmap)
    painter.setRenderHint(_QtGui.QPainter.Antialiasing)
    renderer.render(painter, _QtCore.QRectF(0, 0, 24, 24))
    painter.end()
    return _QtGui.QIcon(pixmap)


class _HoverIconButton(_QtWidgets.QPushButton):
    """Icon-only button that swaps to a hover-colored icon while the pointer is over it."""

    def __init__(self, svg: str, tooltip: str, parent: _QtWidgets.QWidget) -> None:
        """Create a 32px icon button from SVG markup.

        Args:
            svg: SVG markup for the button icon.
            tooltip: Tooltip text shown on hover.
            parent: Parent widget.

        Returns:
            None: Initializes the button in place.
        """
        super().__init__(parent)
        self._normal_icon = svg_icon(svg, _ICON_COLOR)
        self._hover_icon = svg_icon(svg, _HOVER_COLOR)
        self.setIcon(self._normal_icon)
        self.setIconSize(_QtCore.QSize(20, 20))
        self.setFlat(True)
        self.setFixedSize(32, 32)
        self.setToolTip(tooltip)

    def enterEvent(self, event: _QtCore.QEvent) -> None:
        """Show the hover icon when the pointer enters an enabled button.

        Args:
            event: Qt enter event.

        Returns:
            None: Updates the icon in place.
        """
        if self.isEnabled():
            self.setIcon(self._hover_icon)
        super().enterEvent(event)

    def leaveEvent(self, event: _QtCore.QEvent) -> None:
        """Restore the normal icon when the pointer leaves the button.

        Args:
            event: Qt leave event.

        Returns:
            None: Updates the icon in place.
        """
        self.setIcon(self._normal_icon)
        super().leaveEvent(event)


class PresetWidget(_QtWidgets.QWidget):
    """Preset selector with save, load, and delete behavior."""

    def __init__(self, aov_list_widget: _QtWidgets.QListWidget, parent: _QtWidgets.QWidget) -> None:
        """Create the preset controls and connect their actions.

        Args:
            aov_list_widget: AOV checklist controlled by loaded presets.
            parent: Owning contact-sheet dialog.

        Returns:
            None: Initializes the preset widget in place.
        """
        super().__init__(parent)
        self.aov_list_widget = aov_list_widget
        self.settings = _QtCore.QSettings("nuclear", "ContactSheet")
        self.presets = self.read_presets()

        layout = _QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.preset_combo = _QtWidgets.QComboBox(self)
        self.preset_combo.addItem(_SELECT_PRESET)
        self.preset_combo.addItems(sorted(self.presets))
        self.preset_combo.setToolTip("Select a saved AOV preset")
        self.preset_combo.setStyleSheet(_PRESET_COMBO_STYLE)

        self.save_preset_button = _HoverIconButton(_ADD_PRESET_SVG, "Add a new preset", self)
        self.save_preset_button.setObjectName("addPresetButton")
        self.save_preset_button.setAccessibleName("Add preset")

        self.delete_preset_button = _HoverIconButton(_DELETE_PRESET_SVG, "Delete the selected preset", self)
        self.delete_preset_button.setObjectName("deletePresetButton")
        self.delete_preset_button.setAccessibleName("Delete preset")
        self.delete_preset_button.setEnabled(False)

        layout.addWidget(self.preset_combo, 1)
        layout.addWidget(self.save_preset_button)
        layout.addWidget(self.delete_preset_button)

        self.save_preset_button.clicked.connect(self.save_preset)
        self.preset_combo.activated.connect(self.load_preset)
        self.preset_combo.currentIndexChanged.connect(self.update_delete_button)
        self.delete_preset_button.clicked.connect(self.delete_preset)

    def read_presets(self) -> dict[str, list[str]]:
        """Load saved AOV lists from application settings.

        Returns:
            dict[str, list[str]]: Valid preset names and layer selections.
        """
        try:
            data = _json.loads(str(self.settings.value("aov_presets", "{}")))
        except (TypeError, _json.JSONDecodeError):
            return {}
        if not isinstance(data, dict):
            return {}
        return {
            name: layers
            for name, layers in data.items()
            if isinstance(name, str) and isinstance(layers, list) and all(isinstance(layer, str) for layer in layers)
        }

    def save_preset(self, _checked: bool = False) -> bool:
        """Prompt for a name and save the checked AOVs.

        Args:
            _checked: Button signal argument, ignored.

        Returns:
            bool: Whether the preset was saved.
        """
        name, accepted = _QtWidgets.QInputDialog.getText(self, "Add preset", "Preset name:")
        name = name.strip()
        if not accepted or not name or name == _SELECT_PRESET:
            return False
        self.presets[name] = self.get_selected_layers()
        self.write_presets()
        if self.preset_combo.findText(name) < 0:
            self.preset_combo.addItem(name)
        self.preset_combo.setCurrentText(name)
        return True

    def delete_preset(self, _checked: bool = False) -> bool:
        """Confirm and delete the selected preset.

        Args:
            _checked: Button signal argument, ignored.

        Returns:
            bool: Whether a preset was deleted and persisted.
        """
        index = self.preset_combo.currentIndex()
        name = self.preset_combo.currentText()
        if name not in self.presets or index <= 0:
            return False
        answer = _QtWidgets.QMessageBox.question(
            self,
            "Delete preset",
            f"Delete preset '{name}'?",
            _QtWidgets.QMessageBox.Yes | _QtWidgets.QMessageBox.No,
            _QtWidgets.QMessageBox.No,
        )
        if answer != _QtWidgets.QMessageBox.Yes:
            return False
        del self.presets[name]
        self.write_presets()
        self.preset_combo.removeItem(index)
        self.preset_combo.setCurrentIndex(0)
        return True

    def load_preset(self, index: int) -> bool:
        """Apply a saved selection to the AOV checklist.

        Args:
            index: Activated preset combo index.

        Returns:
            bool: Whether a preset was loaded.
        """
        if index <= 0:
            return False
        selected_layers = self.presets.get(self.preset_combo.itemText(index))
        if selected_layers is None:
            return False
        selected = set(selected_layers)
        for item_index in range(self.aov_list_widget.count()):
            item = self.aov_list_widget.item(item_index)
            state = _QtCore.Qt.Checked if item.text() in selected else _QtCore.Qt.Unchecked
            item.setCheckState(state)
        return True

    def get_selected_layers(self) -> list[str]:
        """Return checked AOV names from the associated list.

        Returns:
            list[str]: Checked layer names in list order.
        """
        return [
            self.aov_list_widget.item(index).text()
            for index in range(self.aov_list_widget.count())
            if self.aov_list_widget.item(index).checkState() == _QtCore.Qt.Checked
        ]

    def write_presets(self) -> bool:
        """Persist current presets to application settings.

        Returns:
            bool: Whether settings were synchronized successfully.
        """
        self.settings.setValue("aov_presets", _json.dumps(self.presets))
        self.settings.sync()
        return self.settings.status() == _QtCore.QSettings.NoError

    def update_delete_button(self, index: int) -> bool:
        """Enable deletion only when a saved preset is selected.

        Args:
            index: Current preset combo index.

        Returns:
            bool: Whether the delete button state was updated.
        """
        name = self.preset_combo.itemText(index) if index >= 0 else ""
        self.delete_preset_button.setEnabled(name in self.presets)
        return True


class ContactSheetDialog(_QtWidgets.QDialog):
    """AOV selector dialog."""

    def __init__(self, layers: list[str]) -> None:
        """Create the contact-sheet options dialog.

        Args:
            layers: Available AOV names.

        Returns:
            None: Initializes the dialog.
        """
        super().__init__()
        self.setWindowTitle("Build Layer Contact Sheet")
        self.setMinimumWidth(440)
        self.setMinimumHeight(300)

        main_layout = _QtWidgets.QVBoxLayout(self)
        form_layout = _QtWidgets.QFormLayout()

        # Build the form layout with list and search
        self.aov_list_widget = _QtWidgets.QListWidget()
        self.aov_list_widget.setSelectionMode(_QtWidgets.QAbstractItemView.ExtendedSelection)
        self.aov_list_widget.setVerticalScrollBarPolicy(_QtCore.Qt.ScrollBarAsNeeded)

        # Enable checkable items in the list
        for layer in layers:
            item = _QtWidgets.QListWidgetItem(layer)
            item.setFlags(
                item.flags() | _QtCore.Qt.ItemIsUserCheckable | _QtCore.Qt.ItemIsEnabled | _QtCore.Qt.ItemIsSelectable
            )
            item.setCheckState(_QtCore.Qt.Unchecked)
            self.aov_list_widget.addItem(item)

        # Line edit for filtering AOVs
        self.aov_search_edit = _QtWidgets.QLineEdit()
        self.aov_search_edit.setPlaceholderText("Filter AOVs (regular expression)")
        self.aov_search_edit.setClearButtonEnabled(True)

        self.preset_widget = PresetWidget(self.aov_list_widget, self)

        self.button_layout = _QtWidgets.QHBoxLayout()
        self.select_all_button = _QtWidgets.QPushButton("Select All")
        self.deselect_all_button = _QtWidgets.QPushButton("Deselect All")
        self.button_layout.addWidget(self.select_all_button)
        self.button_layout.addWidget(self.deselect_all_button)

        # Run and cancel buttons
        run_cancel_layout = _QtWidgets.QHBoxLayout()
        self.run_button = _QtWidgets.QPushButton("Run")
        self.cancel_button = _QtWidgets.QPushButton("Cancel")

        run_cancel_layout.addWidget(self.run_button)
        run_cancel_layout.addWidget(self.cancel_button)

        # Combine all in the form layout
        form_layout.addRow("Preset:", self.preset_widget)
        form_layout.addRow("AOVs to include:", self.aov_list_widget)
        form_layout.addRow("Filter AOVs:", self.aov_search_edit)
        # form_layout.addRow("", self.filter_error_label)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(self.button_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(run_cancel_layout)
        self.setLayout(main_layout)

        # Connect signals
        self.select_all_button.clicked.connect(lambda: self.set_check_state(True))
        self.deselect_all_button.clicked.connect(lambda: self.set_check_state(False))
        self.run_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.aov_search_edit.textChanged.connect(self.filter_layers_in_list)
        self.aov_list_widget.itemChanged.connect(self.sync_selected_check_state)

        return

    def sync_selected_check_state(self, item: _QtWidgets.QListWidgetItem) -> bool:
        """Apply a changed selected AOV's check state to every selected AOV.

        Args:
            item: AOV whose checkbox state changed.

        Returns:
            bool: True if selected AOVs were updated, False otherwise.
        """
        if not item.isSelected():
            return False
        state = item.checkState()
        self.aov_list_widget.blockSignals(True)
        try:
            for selected in self.aov_list_widget.selectedItems():
                selected.setCheckState(state)
        finally:
            self.aov_list_widget.blockSignals(False)
        return True

    @property
    def get_compiled_search_pattern(self) -> _re.Pattern | None:
        """Return the compiled regular expression from the search field.

        Returns:
            re.Pattern | None: Compiled pattern, or None if the field is empty or invalid.
        """
        expression = self.aov_search_edit.text()
        if not expression:
            return None
        try:
            pattern = _re.compile(expression)
        except _re.error:
            return None

        return pattern

    def set_check_state(self, checked: bool) -> bool:
        """Set all AOV checkboxes to the requested state.

        Args:
            checked: True to select all, False to clear all.

        Returns:
            bool: True if any items were updated, False otherwise.
        """
        pattern = self.get_compiled_search_pattern

        state = _QtCore.Qt.Checked if checked else _QtCore.Qt.Unchecked
        for index in range(self.aov_list_widget.count()):
            item = self.aov_list_widget.item(index)
            if not self.aov_search_edit.text() or (pattern and pattern.search(item.text())):
                item.setCheckState(state)
        return True

    def filter_layers_in_list(self, expression: str) -> bool:
        """Show only layer names matching the current regular expression.

        Args:
            expression: Updated filter text from the search field.

        Returns:
            bool: True if any items are visible, False otherwise.
        """
        pattern = _re.compile(expression) if expression else None

        for index in range(self.aov_list_widget.count()):
            item = self.aov_list_widget.item(index)
            visible = pattern.search(item.text()) is not None if pattern else True
            item.setHidden(not visible)
        return True

    def get_selected_layers(self) -> list[str]:
        """Return the checked AOV names.

        Returns:
            list[str]: Selected AOVs in list order.
        """
        selected_layers: list[str] = []
        for index in range(self.aov_list_widget.count()):
            item = self.aov_list_widget.item(index)
            if item.checkState() == _QtCore.Qt.Checked:
                selected_layers.append(item.text())
        return selected_layers


def show_contact_sheet_dialog(layers: list[str]) -> list[str] | None:
    """Show the AOV selector and return checked layers when accepted.

    Args:
        layers: Available AOV names.

    Returns:
        list[str] | None: Selected layers, or None when cancelled.
    """
    dialog = ContactSheetDialog(layers)
    execute = getattr(dialog, "exec_", None) or dialog.exec
    if execute() != _QtWidgets.QDialog.Accepted:
        return None
    return dialog.get_selected_layers()


if __name__ == "__main__":
    import sys

    app = _QtWidgets.QApplication(sys.argv)
    layers = ["diffuse", "specular", "normal"]
    # Add a massive list to test scrolling and performance
    layers.extend([f"layer_{i}" for i in range(100)])
    selected = show_contact_sheet_dialog(layers)
    print("Selected layers:", selected)
    sys.exit(0)
