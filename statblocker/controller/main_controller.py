import sys
from pathlib import Path
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QFileDialog, QInputDialog
from statblocker.view.main_view import MainView
from statblocker.data.stat_block import StatBlock


class MainController(QObject):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self._app = app
        self._current_dirpath: Path | None = None
        self.view = MainView()
        self.view.ui.btn_save_statblock.pressed.connect(
            self._handler_save_statblock_pressed
        )
        self.view.ui.btn_export_markdown.pressed.connect(
            self._handler_export_markdown_pressed
        )
        self.view.ui.btn_populate_based_on_cr.pressed.connect(
            self._handler_populate_based_on_cr_pressed
        )
        self.view.ui.btn_create_new_statblock.pressed.connect(
            self._handler_create_new_statblock_pressed
        )
        self.view.ui.btn_load_statblock.pressed.connect(
            self._handler_load_statblock_pressed
        )
        self.view.deleteStatblock.connect(self._handler_delete_statblock)
        self.view.ui.actionOpen_Folder.triggered.connect(self._handler_open_folder)

    def _handler_open_folder(self) -> None:
        selected_folder = QFileDialog.getExistingDirectory(
            None,
            "Select Folder",
            "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        if selected_folder:
            self._current_dirpath = Path(selected_folder).resolve()
            self.view.ui._frame_statblock.setEnabled(True)
            self._load_statblocks_from_folder()
        else:
            print("Invalid folder selection, disabling panel...")
            self.view.ui._frame_statblock.setEnabled(False)

    def _load_statblocks_from_folder(self) -> None:
        if self._current_dirpath is not None:
            self.view.ui.listview_available_statblocks.clear()
            for filepath in self._current_dirpath.iterdir():
                if filepath.is_file() and filepath.suffix.lower() == ".json":
                    filename = filepath.stem
                    li = QListWidgetItem()
                    li.setText(filename)
                    self.view.ui.listview_available_statblocks.addItem(li)
            print(f"Loaded statblocks from: {self._current_dirpath}")

    def _handler_save_statblock_pressed(self) -> None:
        current_statblock = self.view.statblock
        export_path = (
            (self._current_dirpath / current_statblock.name)
            .with_suffix(".json")
            .resolve()
        )
        export_path.write_text(current_statblock.to_json(), encoding="utf-8")
        item_exists = any(
            self.view.ui.listview_available_statblocks.item(idx).text()
            == current_statblock.name
            for idx in range(self.view.ui.listview_available_statblocks.count())
        )
        if not item_exists:
            li = QListWidgetItem()
            li.setText(current_statblock.name)
            self.view.ui.listview_available_statblocks.addItem(li)
        print(f"Statblock saved: {export_path}")

    def _handler_export_markdown_pressed(self) -> None:
        current_statblock = self.view.statblock
        export_path = (
            (self._current_dirpath / current_statblock.name)
            .with_suffix(".md")
            .resolve()
        )
        md_str = current_statblock.hb_v3_markdown()
        export_path.write_text(md_str, encoding="utf-8")
        print(f"Statblock saved: {export_path}")

    def _handler_populate_based_on_cr_pressed(self) -> None:
        # TODO:
        # query database for all CR-related calculatable values
        # Set all the values in the view
        pass

    def _handler_create_new_statblock_pressed(self) -> None:
        text, ok = QInputDialog.getText(None, "Enter Creature Name", "Creature Name:")
        if ok and text:
            self.view.create_new_statblock(text)
            self._handler_save_statblock_pressed()
        else:
            print("Cancelled statblock creation")

    def _handler_load_statblock_pressed(self) -> None:
        statblock_name = self.view.selected_statblock
        statblock_filepath = (self._current_dirpath / statblock_name).with_suffix(
            ".json"
        )
        if not statblock_filepath.exists() or not statblock_filepath.is_file():
            print(f"Unable to locate statblock file: {statblock_filepath}")
            return
        json_str = statblock_filepath.read_text(encoding="utf-8")
        statblock = StatBlock.from_json(json_str)
        self.view.load_statblock(statblock)
        print(f"Loaded statblock: {statblock_filepath}")

    def _handler_delete_statblock(self, statblock_name: str) -> None:
        statblock_filepath = (self._current_dirpath / statblock_name).with_suffix(
            ".json"
        )
        statblock_filepath.unlink(missing_ok=True)
        print(f"Deleted statblock: {statblock_filepath}")

    def run(self) -> None:
        self.view.show()
        sys.exit(self._app.exec_())
