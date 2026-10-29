"""

"""
from builtins import input

import sys
from PySide2 import QtGui, QtWidgets, QtCore

from w import knobs_by_classes
import nuke

stylesheet = f"""
QPushButton#add_button {{
    border: none; 
    max-height: 20px;
    min-height: 20px;
    max-width: 20px;
    min-width: 20px;
}}

QPushButton#add_button:hover {{
    filter: brightness(0) invert(1);

}}
"""

# stylesheet = """
# QPushButton {
#  background-color: white;
#  border-style: solid;
#  border-width:1px;
#  border-radius:20px;
#  border-color: red;
#  max-width:100px;
#  max-height:100px;
#  min-width:100px;
#  min-height:100px;
# }
# """

# Connect the class and knob connections


class PlaceholderReplacement(QtWidgets.QWidget):
    def __init__(self):
        super(PlaceholderReplacement, self).__init__()

        # class_knob_layout = QtWidgets.QHBoxLayout()
        # self.class_combobox = QtWidgets.QComboBox()
        # self.knobs_combobox = QtWidgets.QComboBox()
        # self.add_pushbutton = QtWidgets.QPushButton(icon=QtGui.QPixmap("V:/dev/nuclear/nuke/mimi/widgets/plus_icon.png"))
        # self.add_pushbutton.setObjectName("add_button")
        # self.add_pushbutton.setCursor(QtCore.Qt.PointingHandCursor)
        #
        # for widget in [self.class_combobox, self.knobs_combobox, self.add_pushbutton]:
        #     class_knob_layout.addWidget(widget)
        #
        # layout = QtWidgets.QFormLayout()
        # layout.addRow("class/knobs", class_knob_layout)
        # # layout.addRow("Knobs", self.knobs_combobox)
        # # self.connections()
        # self.setLayout(layout)
        # self.setStyleSheet(stylesheet)

    def connections_knobs(self):
        items = set()
        class_name = self.class_combobox.currentText()
        self.knobs_combobox.clear()
        knobs_structure = knobs_by_classes.structure.get(class_name, [])
        for knob_structure in knobs_structure:
            name = knob_structure.get("name") or knob_structure.get("label")
            if name.strip(" "):
                items.add(name)
            print(repr(name))
        # self.knobs_combobox.addItems(list(sorted(items)))

    def connections(self):
        self.class_combobox.addItems(list(knobs_by_classes.structure.keys()))
        self.class_combobox.currentIndexChanged.connect(self.connections_knobs)
        self.connections_knobs()


def create_mimi_node():
    mimi_node = nuke.createNode("NoOp") or nuke.Node
    mimi_node.setName("Mime1")
    python_widget = nuke.PyCustom_Knob("mimi_widget", "mimi_widget", "temp_design.PlaceholderReplacement()")
    mimi_node.addKnob(python_widget)
    return mimi_node


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    replacement_widget = PlaceholderReplacement()
    replacement_widget.show()
    sys.exit(app.exec_())

