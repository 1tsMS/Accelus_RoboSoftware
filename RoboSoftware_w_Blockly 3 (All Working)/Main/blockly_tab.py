import os
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout

class BlocklyBridge(QObject):
    @pyqtSlot(str)
    def receiveCode(self, code: str):
        print("Blockly code received from JS:\n", code)
        file_path = os.path.join(os.path.dirname(__file__), "blockly_code.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Code saved to: {file_path}")

class BlocklyTab:
    def __init__(self, container_widget):
        self.container = container_widget
        self.view = QWebEngineView(self.container)

        layout = self.container.layout()
        if not layout:
            layout = QVBoxLayout(self.container)
            self.container.setLayout(layout)
        layout.addWidget(self.view)

        # WebChannel bridge
        self.channel = QWebChannel()
        self.bridge = BlocklyBridge()
        self.channel.registerObject("pyBridge", self.bridge)
        self.view.page().setWebChannel(self.channel)

        # Load your index.html
        path = os.path.abspath("E:/College/projects/RoboSoftware/RoboSoftware_w_Blockly 3/blockly_ankittt.html")
        self.view.load(QUrl.fromLocalFile(path))

    def get_python_code(self, callback):
        js_code = "Blockly.Python.workspaceToCode(workspace);"
        self.view.page().runJavaScript(js_code, callback)
