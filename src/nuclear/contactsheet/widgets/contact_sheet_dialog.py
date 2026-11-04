"""Qt dialog for choosing AOVs for a contact sheet."""

import re as _re

from Qt import QtCore as _QtCore, QtGui as _QtGui, QtWidgets as _QtWidgets


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

        main_layout = _QtWidgets.QVBoxLayout(self)
        form_layout = _QtWidgets.QFormLayout()

        # Build the form layout with list and search
        self.aov_list_widget = _QtWidgets.QListWidget()
        self.aov_list_widget.setSelectionMode(_QtWidgets.QAbstractItemView.NoSelection)
        self.aov_list_widget.setVerticalScrollBarPolicy(_QtCore.Qt.ScrollBarAsNeeded)

        # Enable checkable items in the list
        for layer in layers:
            item = _QtWidgets.QListWidgetItem(layer)
            item.setCheckState(_QtCore.Qt.Unchecked)
            self.aov_list_widget.addItem(item)

        # Line edit for filtering AOVs
        self.aov_search_edit = _QtWidgets.QLineEdit()
        self.aov_search_edit.setPlaceholderText("Filter AOVs (regular expression)")

        # Create buttons and the layout
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
        self.cancel_button.clicked.connect(self.reject)
        self.aov_search_edit.textChanged.connect(self.filter_layers_in_list)

        close_shortcut = _QtGui.QShortcut(_QtGui.QKeySequence("Alt+W"), self)
        close_shortcut.activated.connect(self.reject)

        return

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
