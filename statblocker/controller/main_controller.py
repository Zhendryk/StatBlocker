import sys
from pathlib import Path
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QListWidgetItem,
    QFileDialog,
    QInputDialog,
    QMessageBox,
)
from statblocker.data.db import MM2024DB, MM2024DBColumn, OperationType
from statblocker.view.main_view import MainView
from statblocker.data.stat_block import StatBlock
from statblocker.data.enums import Size
from statblocker.data.action import get_all_templates, CharacteristicType


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
        self.view.ui.actionExport_Statblock_to_Markdown.triggered.connect(
            self._handler_export_markdown_pressed
        )
        self.view.ui.actionSave_Statblock.triggered.connect(
            self._handler_save_statblock_pressed
        )
        self.view.ui.actionOpen_Folder.triggered.connect(self._handler_open_folder)
        self.view.ui.action_markdown_reference.triggered.connect(
            self._handler_show_markdown_reference
        )
        self.view.ui.actionLoad_Trait_Template.triggered.connect(
            self._handler_load_trait_template
        )
        self.view.ui.actionLoad_Action_Template.triggered.connect(
            self._handler_load_action_template
        )
        self.view.ui.actionLoad_Bonus_Action_Template.triggered.connect(
            self._handler_load_bonus_action_template
        )
        self.view.ui.actionLoad_Reaction_Template.triggered.connect(
            self._handler_load_reaction_template
        )
        self.view.ui.actionLoad_Legendary_Action_Template.triggered.connect(
            self._handler_load_legendary_action_template
        )

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

    def _handler_show_markdown_reference(self) -> None:
        reference_window = QMessageBox()
        reference_window.setWindowTitle("Markdown Reference")
        reference_text = """
The following markdown syntax can be used when creating Traits, Actions, Bonus Actions, Reactions and Legendary Actions:
<br>
<br>
<i>Use _ to italicize and ** to bold.</i>
<ul>
    <li><b>[MON]:</b> <i>Shows the monster's name.</i></li>
    <li><b>[CHA]:</b> <i>Shows the monster's charisma modifier.</i></li>
    <li><b>[3D6]:</b> <i>Computes 3d6.</i></li>
    <li><b>[STR ATK]:</b> <i>Calculates the modifier to the monster's attack roll for a strength-based attack.</i></li>
    <li><b>[DEX 2D8]:</b> <i>Calculates the damage roll for a dexterity-based attack with damage dice 2d8.</i></li>
    <li><b>[WIS SAVE]:</b> <i>Calculates the save DC vs the monster's wisdom.</i></li>
    <li><b>[3D6 + 1]</b>, <b>[STR ATK - 2]</b>, <b>[WIS SAVE + 3]</b>: <i>Adds a modifier to the given values.</i></li>
</ul>
"""
        reference_window.setText(reference_text)
        reference_window.setTextFormat(Qt.TextFormat.RichText)
        reference_window.setIcon(QMessageBox.Icon.NoIcon)
        reference_window.exec_()

    def _handler_load_trait_template(self) -> None:
        all_templates = get_all_templates()
        choices = [
            t for t in all_templates.values() if t.ctype == CharacteristicType.TRAIT
        ]
        if choices:
            choice, ok = QInputDialog.getItem(
                None,
                "Load Trait Template",
                "Select a Trait Template to load:",
                [c.label for c in choices],
                0,
                False,
            )
            if ok and choice:
                chosen_template = next((t for t in choices if t.label == choice), None)
                if chosen_template is None:
                    raise RuntimeError
                self.view.ui.lineedit_trait_title.setText(chosen_template.name)
                self.view.ui.textedit_trait.setText(chosen_template.description)
        else:
            print("No trait templates to load, cancelling...")

    def _handler_load_action_template(self) -> None:
        all_templates = get_all_templates()
        choices = [
            t for t in all_templates.values() if t.ctype == CharacteristicType.ACTION
        ]
        if choices:
            choice, ok = QInputDialog.getItem(
                None,
                "Load Action Template",
                "Select a Action Template to load:",
                [c.label for c in choices],
                0,
                False,
            )
            if ok and choice:
                chosen_template = next((t for t in choices if t.label == choice), None)
                if chosen_template is None:
                    raise RuntimeError
                self.view.ui.lineedit_action_title.setText(chosen_template.name)
                self.view.ui.textedit_action.setText(chosen_template.description)
        else:
            print("No action templates to load, cancelling...")

    def _handler_load_bonus_action_template(self) -> None:
        all_templates = get_all_templates()
        choices = [
            t
            for t in all_templates.values()
            if t.ctype == CharacteristicType.BONUS_ACTION
        ]
        if choices:
            choice, ok = QInputDialog.getItem(
                None,
                "Load Bonus Action Template",
                "Select a Bonus Action Template to load:",
                [c.label for c in choices],
                0,
                False,
            )
            if ok and choice:
                chosen_template = next((t for t in choices if t.label == choice), None)
                if chosen_template is None:
                    raise RuntimeError
                self.view.ui.lineedit_bonus_action_title.setText(chosen_template.name)
                self.view.ui.textedit_bonus_action.setText(chosen_template.description)
        else:
            print("No bonus action templates to load, cancelling...")

    def _handler_load_reaction_template(self) -> None:
        all_templates = get_all_templates()
        choices = [
            t for t in all_templates.values() if t.ctype == CharacteristicType.REACTION
        ]
        if choices:
            choice, ok = QInputDialog.getItem(
                None,
                "Load Reaction Template",
                "Select a Reaction Template to load:",
                [c.label for c in choices],
                0,
                False,
            )
            if ok and choice:
                chosen_template = next((t for t in choices if t.label == choice), None)
                if chosen_template is None:
                    raise RuntimeError
                self.view.ui.lineedit_reaction_title.setText(chosen_template.name)
                self.view.ui.textedit_reaction.setText(chosen_template.description)
        else:
            print("No reaction templates to load, cancelling...")

    def _handler_load_legendary_action_template(self) -> None:
        all_templates = get_all_templates()
        choices = [
            t
            for t in all_templates.values()
            if t.ctype == CharacteristicType.LEGENDARY_ACTION
        ]
        if choices:
            choice, ok = QInputDialog.getItem(
                None,
                "Load Legendary Action Template",
                "Select a Legendary Action Template to load:",
                [c.label for c in choices],
                0,
                False,
            )
            if ok and choice:
                chosen_template = next((t for t in choices if t.label == choice), None)
                if chosen_template is None:
                    raise RuntimeError
                self.view.ui.lineedit_legendary_action_title.setText(
                    chosen_template.name
                )
                self.view.ui.textedit_legendary_action.setText(
                    chosen_template.description
                )
        else:
            print("No legendary action templates to load, cancelling...")

    def run(self) -> None:
        self.view.show()
        sys.exit(self._app.exec_())
