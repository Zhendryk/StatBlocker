import sys
from pathlib import Path
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QFileDialog, QInputDialog
from statblocker.data.db import MM2024DB, MM2024DBColumn, OperationType
from statblocker.view.main_view import MainView
from statblocker.data.stat_block import StatBlock
from statblocker.data.enums import Size


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
        self.view.ui.btn_db_populate_statblock.pressed.connect(
            self._handler_db_populate_statblock
        )
        self.view.ui.btn_create_new_statblock.pressed.connect(
            self._handler_create_new_statblock_pressed
        )
        self.view.ui.btn_load_statblock.pressed.connect(
            self._handler_load_statblock_pressed
        )
        self.view.ui.btn_db_query.pressed.connect(self._handler_query_db)
        self.view.deleteStatblock.connect(self._handler_delete_statblock)
        self.view.ui.btn_open_folder.pressed.connect(self._handler_open_folder)
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

    def _handler_db_populate_statblock(self) -> None:
        operation = OperationType.from_display_name(
            self.view.ui.cb_db_operation.currentText()
        )
        current_statblock = self.view.statblock
        query_filters: dict[MM2024DBColumn, object] = {}
        if self.view.ui.checkbox_db_cr.isChecked():
            query_filters[MM2024DBColumn.CR] = current_statblock.challenge_rating.rating
        if self.view.ui.checkbox_db_size.isChecked() and current_statblock.size:
            max_size = Size(max([sz.value for sz in current_statblock.size]))
            query_filters[MM2024DBColumn.SIZE] = max_size.display_name
        if self.view.ui.checkbox_db_creature_type.isChecked():
            query_filters[MM2024DBColumn.CREATURE_TYPE] = (
                current_statblock.creature_type.display_name
            )
        if self.view.ui.checkbox_db_legendary.isChecked():
            query_filters[MM2024DBColumn.LEGENDARY] = 1
        filter_str = (
            "{" + ", ".join([f"{k.name}:{v}" for k, v in query_filters.items()]) + "}"
        )
        ac, ac_ss = MM2024DB.query(
            query_filters,
            MM2024DBColumn.AC,
            operation=operation,
        )
        self.view.ui.spinbox_ac.setValue(int(ac))
        print(
            f"Calculated {operation.display_name} AC of {ac} for filter: {filter_str}. Sample Size: {ac_ss}"
        )
        hp, hp_ss = MM2024DB.query(
            query_filters,
            MM2024DBColumn.AVG_HP,
            operation=operation,
        )
        # self.view.ui.lineedit_hp.setValue(int(hp)) # TODO: Do this right
        print(
            f"Calculated {operation.display_name} HP of {hp} for filter: {filter_str}. Sample Size: {hp_ss}"
        )
        strength, str_ss = MM2024DB.query(
            query_filters,
            MM2024DBColumn.STR,
            operation=operation,
        )
        self.view.ui.spinbox_str.setValue(int(strength))
        print(
            f"Calculated {operation.display_name} STR of {strength} for filter: {filter_str}. Sample Size: {str_ss}"
        )
        dex, dex_ss = MM2024DB.query(
            query_filters,
            MM2024DBColumn.DEX,
            operation=operation,
        )
        self.view.ui.spinbox_dex.setValue(int(dex))
        print(
            f"Calculated {operation.display_name} DEX of {dex} for filter: {filter_str}. Sample Size: {dex_ss}"
        )
        con, con_ss = MM2024DB.query(
            query_filters,
            MM2024DBColumn.CON,
            operation=operation,
        )
        self.view.ui.spinbox_con.setValue(int(con))
        print(
            f"Calculated {operation.display_name} CON of {con} for filter: {filter_str}. Sample Size: {con_ss}"
        )
        intelligence, int_ss = MM2024DB.query(
            query_filters,
            MM2024DBColumn.INT,
            operation=operation,
        )
        self.view.ui.spinbox_int.setValue(int(intelligence))
        print(
            f"Calculated {operation.display_name} INT of {intelligence} for filter: {filter_str}. Sample Size: {int_ss}"
        )
        wis, wis_ss = MM2024DB.query(
            query_filters,
            MM2024DBColumn.WIS,
            operation=operation,
        )
        self.view.ui.spinbox_wis.setValue(int(wis))
        print(
            f"Calculated {operation.display_name} WIS of {wis} for filter: {filter_str}. Sample Size: {wis_ss}"
        )
        cha, cha_ss = MM2024DB.query(
            query_filters,
            MM2024DBColumn.CHA,
            operation=operation,
        )
        self.view.ui.spinbox_cha.setValue(int(cha))
        print(
            f"Calculated {operation.display_name} CHA of {cha} for filter: {filter_str}. Sample Size: {cha_ss}"
        )

    def _handler_query_db(self) -> None:
        operation = OperationType.from_display_name(
            self.view.ui.cb_db_operation.currentText()
        )
        aggregate_column = MM2024DBColumn.from_column_str(
            self.view.ui.cb_db_column.currentText()
        )
        current_statblock = self.view.statblock
        query_filters: dict[MM2024DBColumn, object] = {}
        if self.view.ui.checkbox_db_cr.isChecked():
            query_filters[MM2024DBColumn.CR] = current_statblock.challenge_rating.rating
        if self.view.ui.checkbox_db_size.isChecked() and current_statblock.size:
            max_size = Size(max([sz.value for sz in current_statblock.size]))
            query_filters[MM2024DBColumn.SIZE] = max_size.display_name
        if self.view.ui.checkbox_db_creature_type.isChecked():
            query_filters[MM2024DBColumn.CREATURE_TYPE] = (
                current_statblock.creature_type.display_name
            )
        if self.view.ui.checkbox_db_legendary.isChecked():
            query_filters[MM2024DBColumn.LEGENDARY] = 1
        filter_str = (
            "{" + ", ".join([f"{k.name}:{v}" for k, v in query_filters.items()]) + "}"
        )
        value, value_ss = MM2024DB.query(
            query_filters,
            aggregate_column,
            operation=operation,
        )
        self.view.ui.lineedit_db_result.setText(str(value))
        print(
            f"Calculated {operation.display_name} {aggregate_column.column_str} of {value} for filter: {filter_str}. Sample Size: {value_ss}"
        )

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
