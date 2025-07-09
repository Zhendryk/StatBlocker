# PyQt5 View wrapper for MVC pattern
from functools import partial
from PyQt5.QtCore import pyqtSignal, Qt, QPoint
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QMenu,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QLineEdit,
    QMessageBox,
)
from .qt_generated_code.main_view import Ui_MainView
from typing import TypeAlias
from statblocker.data.challenge_rating import ChallengeRating
from statblocker.data.enums import (
    Habitat,
    Treasure,
    Size,
    CreatureType,
    Alignment,
    Ability,
    Proficiency,
    DamageType,
    Condition,
    Sense,
    Language,
    Skill,
    SpeedType,
    LanguageProficiency,
    Resistance,
)
from statblocker.data.speed import Speed
from statblocker.data.ability_scores import AbilityScores
from statblocker.data.skills import Skills
from statblocker.data.senses import Senses
from statblocker.data.languages import Languages
from statblocker.data.db import MM2024DBColumn, OperationType
from statblocker.data.action import (
    Trait,
    Action,
    BonusAction,
    Reaction,
    LegendaryAction,
    CombatCharacteristic,
    LimitedUsageType,
)
from statblocker.data.stat_block import StatBlock


DamageOrCondition: TypeAlias = (
    object  # Using object because pyqtSignal does not allow union types (e.g. DamageType | Condition)
)


class MainView(QMainWindow):
    deleteStatblock = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ui = Ui_MainView()
        self.ui.setupUi(self)
        self.setWindowTitle("StatBlocker")
        self.init_ui()
        self._configure_ctx_menus()
        self._configure_btns()

    def _init_comboboxes(self) -> None:
        self.ui.cb_habitat.clear()
        self.ui.cb_habitat.addItems([h.display_name for h in Habitat])
        self.ui.cb_habitat.setCurrentIndex(-1)
        self.ui.cb_treasure.clear()
        self.ui.cb_treasure.addItems([t.display_name for t in Treasure])
        self.ui.cb_treasure.setCurrentIndex(-1)
        self.ui.cb_size.clear()
        self.ui.cb_size.addItems([s.display_name for s in Size])
        self.ui.cb_size.setCurrentIndex(-1)
        self.ui.cb_alignment.clear()
        self.ui.cb_alignment.addItems([a.display_name for a in Alignment])
        self.ui.cb_creature_type.clear()
        self.ui.cb_creature_type.addItems([ct.display_name for ct in CreatureType])
        self.ui.cb_immunities.clear()
        self.ui.cb_immunities.addItems(
            [dt.display_name for dt in DamageType] + [c.display_name for c in Condition]
        )
        self.ui.cb_languages.clear()
        self.ui.cb_languages.addItems([l.display_name for l in Language])
        self.ui.cb_senses.clear()
        self.ui.cb_senses.addItems([s.display_name for s in Sense])
        self.ui.cb_skills.clear()
        self.ui.cb_skills.addItems([s.display_name for s in Skill])
        self.ui.cb_speed.clear()
        self.ui.cb_speed.addItems([s.display_name for s in SpeedType])
        self.ui.cb_db_column.clear()
        self.ui.cb_db_column.addItems([c.column_str for c in MM2024DBColumn])
        self.ui.cb_db_operation.clear()
        self.ui.cb_db_operation.addItems([o.display_name for o in OperationType])

    def _init_listwidgets(self) -> None:
        self.ui.listview_speed.clear()
        self.ui.listview_skills.clear()
        self.ui.listview_immunities.clear()
        self.ui.listview_senses.clear()
        self.ui.listview_languages.clear()
        self.ui.listview_traits.clear()
        self.ui.listview_actions.clear()
        self.ui.listview_bonus_actions.clear()
        self.ui.listview_reactions.clear()
        self.ui.listview_legendary_actions.clear()
        self.ui.listview_available_statblocks.setSelectionMode(
            QListWidget.SelectionMode.SingleSelection
        )

    def _init_spinboxes(self) -> None:
        self.ui.spinbox_challenge_rating.setValue(0)
        self.ui.spinbox_ac.setValue(10)
        self.ui.spinbox_speed_range.setValue(0)
        self.ui.spinbox_str.setValue(10)
        self.ui.spinbox_dex.setValue(10)
        self.ui.spinbox_con.setValue(10)
        self.ui.spinbox_int.setValue(10)
        self.ui.spinbox_wis.setValue(10)
        self.ui.spinbox_cha.setValue(10)
        self.ui.spinbox_sense_range.setValue(0)
        self.ui.spinbox_telepathy_range.setValue(0)

    def _init_checkboxes(self) -> None:
        self.ui.checkbox_has_lair.setChecked(False)
        self.ui.checkbox_str_proficient.setChecked(False)
        self.ui.checkbox_dex_proficient.setChecked(False)
        self.ui.checkbox_con_proficient.setChecked(False)
        self.ui.checkbox_int_proficient.setChecked(False)
        self.ui.checkbox_wis_proficient.setChecked(False)
        self.ui.checkbox_cha_proficient.setChecked(False)
        self.ui.checkbox_telepathy.setChecked(False)

    def _init_lineedits(self) -> None:
        self.ui.lineedit_name.clear()
        self.ui.lineedit_hp.clear()
        self.ui.lineedit_initiative.clear()

    def _init_textedits(self) -> None:
        self.ui.textedit_action.clear()
        self.ui.textedit_bonus_action.clear()
        self.ui.textedit_reaction.clear()
        self.ui.textedit_legendary_action.clear()

    def _configure_ctx_menus(self) -> None:
        self.ui.listview_speed.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_speed.customContextMenuRequested.connect(
            partial(self._handler_ctx_menu, self.ui.listview_speed)
        )

        self.ui.listview_immunities.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_immunities.customContextMenuRequested.connect(
            partial(self._handler_ctx_menu, self.ui.listview_immunities)
        )
        self.ui.listview_languages.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_languages.customContextMenuRequested.connect(
            partial(self._handler_ctx_menu, self.ui.listview_languages)
        )
        self.ui.listview_senses.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_senses.customContextMenuRequested.connect(
            partial(self._handler_ctx_menu, self.ui.listview_senses)
        )
        self.ui.listview_skills.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_skills.customContextMenuRequested.connect(
            partial(self._handler_ctx_menu, self.ui.listview_skills)
        )
        self.ui.listview_traits.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_traits.customContextMenuRequested.connect(
            partial(
                self._handler_ctx_menu_textedits,
                self.ui.lineedit_trait_title,
                self.ui.textedit_trait,
                self.ui.listview_traits,
            )
        )
        self.ui.listview_actions.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_actions.customContextMenuRequested.connect(
            partial(
                self._handler_ctx_menu_textedits,
                self.ui.lineedit_action_title,
                self.ui.textedit_action,
                self.ui.listview_actions,
            )
        )
        self.ui.listview_bonus_actions.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_bonus_actions.customContextMenuRequested.connect(
            partial(
                self._handler_ctx_menu_textedits,
                self.ui.lineedit_bonus_action_title,
                self.ui.textedit_bonus_action,
                self.ui.listview_bonus_actions,
            )
        )
        self.ui.listview_reactions.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_reactions.customContextMenuRequested.connect(
            partial(
                self._handler_ctx_menu_textedits,
                self.ui.lineedit_reaction_title,
                self.ui.textedit_reaction,
                self.ui.listview_reactions,
            )
        )
        self.ui.listview_legendary_actions.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_legendary_actions.customContextMenuRequested.connect(
            partial(
                self._handler_ctx_menu_textedits,
                self.ui.lineedit_legendary_action_title,
                self.ui.textedit_legendary_action,
                self.ui.listview_legendary_actions,
            )
        )
        self.ui.listview_available_statblocks.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.listview_available_statblocks.customContextMenuRequested.connect(
            self._handler_ctx_menu_left_pane
        )

    def _configure_btns(self) -> None:
        self.ui.btn_add_speed.pressed.connect(self.add_speed)
        self.ui.btn_proficient_skill.pressed.connect(self.add_skill_proficiency)
        self.ui.btn_expertise_skill.pressed.connect(self.add_skill_expertise)
        self.ui.btn_vulnerable.pressed.connect(self.add_damage_vulnerability)
        self.ui.btn_resistant.pressed.connect(self.add_damage_resistance)
        self.ui.btn_immune.pressed.connect(self.add_immunity)
        self.ui.btn_add_sense.pressed.connect(self.add_sense)
        self.ui.btn_understands_language.pressed.connect(self.add_understood_language)
        self.ui.btn_speaks_language.pressed.connect(self.add_spoken_language)
        self.ui.btn_add_trait.pressed.connect(self.add_trait)
        self.ui.btn_add_action.pressed.connect(self.add_action)
        self.ui.btn_add_bonus_action.pressed.connect(self.add_bonus_action)
        self.ui.btn_add_reaction.pressed.connect(self.add_reaction)
        self.ui.btn_add_legendary_action.pressed.connect(self.add_legendary_action)

    def init_ui(self) -> None:
        self._init_comboboxes()
        self._init_listwidgets()
        self._init_spinboxes()
        self._init_checkboxes()
        self._init_lineedits()
        self._init_textedits()
        self.ui.lineedit_name.textChanged.connect(self._handler_textedit_availability)
        self._handler_textedit_availability()

    def _handler_textedit_availability(self) -> None:
        enabled = True if self.name else False
        self._toggle_textedit_availability(enabled)

    def _toggle_textedit_availability(self, enabled: bool) -> None:
        # Traits
        self.ui._lbl_traits.setEnabled(enabled)
        self.ui.lineedit_trait_title.setEnabled(enabled)
        self.ui.textedit_trait.setEnabled(enabled)
        self.ui.btn_add_trait.setEnabled(enabled)
        self.ui.listview_traits.setEnabled(enabled)
        # Actions
        self.ui._lbl_actions.setEnabled(enabled)
        self.ui.lineedit_action_title.setEnabled(enabled)
        self.ui.textedit_action.setEnabled(enabled)
        self.ui.btn_add_action.setEnabled(enabled)
        self.ui.listview_actions.setEnabled(enabled)
        # Bonus Actions
        self.ui._lbl_bonus_actions.setEnabled(enabled)
        self.ui.lineedit_bonus_action_title.setEnabled(enabled)
        self.ui.textedit_bonus_action.setEnabled(enabled)
        self.ui.btn_add_bonus_action.setEnabled(enabled)
        self.ui.listview_bonus_actions.setEnabled(enabled)
        # Reactions
        self.ui._lbl_reactions.setEnabled(enabled)
        self.ui.lineedit_reaction_title.setEnabled(enabled)
        self.ui.textedit_reaction.setEnabled(enabled)
        self.ui.btn_add_reaction.setEnabled(enabled)
        self.ui.listview_reactions.setEnabled(enabled)
        # Legendary Actions
        self.ui._lbl_legendary_actions.setEnabled(enabled)
        self.ui.lineedit_legendary_action_title.setEnabled(enabled)
        self.ui.textedit_legendary_action.setEnabled(enabled)
        self.ui.btn_add_legendary_action.setEnabled(enabled)
        self.ui.listview_legendary_actions.setEnabled(enabled)

    def _handler_ctx_menu(self, listview: QListWidget, position: QPoint) -> None:
        item = listview.itemAt(position)
        if item:
            menu = QMenu()
            delete_action = menu.addAction("Delete")
            action = menu.exec_(listview.viewport().mapToGlobal(position))
            if action == delete_action:
                row = listview.row(item)
                listview.takeItem(row)  # Removes the item from the widget

    def _handler_ctx_menu_textedits(
        self,
        lineedit: QLineEdit,
        textedit: QTextEdit,
        listview: QListWidget,
        position: QPoint,
    ) -> None:
        item = listview.itemAt(position)
        if item:
            menu = QMenu()
            view_formatted_action = menu.addAction("View Formatted")
            edit_action = menu.addAction("Edit")
            delete_action = menu.addAction("Delete")
            action = menu.exec_(listview.viewport().mapToGlobal(position))
            if action == delete_action:
                row = listview.row(item)
                listview.takeItem(row)  # Removes the item from the widget
            elif action == edit_action:
                itemdata = item.data(Qt.ItemDataRole.UserRole)
                assert isinstance(itemdata, CombatCharacteristic)
                lineedit.setText(itemdata.title)
                textedit.setText(itemdata.description)
            elif action == view_formatted_action:
                itemdata = item.data(Qt.ItemDataRole.UserRole)
                assert isinstance(itemdata, CombatCharacteristic)
                QMessageBox.information(
                    self, itemdata.title, itemdata.resolved_description
                )

    def _handler_ctx_menu_left_pane(self, position: QPoint) -> None:
        item = self.ui.listview_available_statblocks.itemAt(position)
        if item:
            menu = QMenu()
            delete_action = menu.addAction("Delete")
            action = menu.exec_(
                self.ui.listview_available_statblocks.viewport().mapToGlobal(position)
            )
            if action == delete_action:
                self.deleteStatblock.emit(item.text())
                row = self.ui.listview_available_statblocks.row(item)
                self.ui.listview_available_statblocks.takeItem(
                    row
                )  # Removes the item from the widget

    def load_statblock(self, statblock: StatBlock) -> None:
        self.init_ui()
        self.ui.lineedit_name.setText(statblock.name)
        self.ui.spinbox_challenge_rating.setValue(statblock.challenge_rating.rating)
        self.ui.checkbox_has_lair.setChecked(statblock.challenge_rating.has_lair)
        self.ui.cb_habitat.setItemsChecked([h.display_name for h in statblock.habitat])
        self.ui.cb_treasure.setItemsChecked(
            [t.display_name for t in statblock.treasure]
        )
        self.ui.cb_size.setItemsChecked([s.display_name for s in statblock.size])
        ct_idx = next(
            (
                idx
                for idx in range(self.ui.cb_creature_type.count())
                if self.ui.cb_creature_type.itemText(idx)
                == statblock.creature_type.display_name
            ),
            0,
        )
        self.ui.cb_creature_type.setCurrentIndex(ct_idx)
        al_idx = next(
            (
                idx
                for idx in range(self.ui.cb_alignment.count())
                if self.ui.cb_alignment.itemText(idx)
                == statblock.alignment.display_name
            ),
            0,
        )
        self.ui.cb_alignment.setCurrentIndex(al_idx)
        self.ui.spinbox_ac.setValue(statblock.armor_class)
        self.ui.lineedit_hp.setText(statblock.hit_points_str)
        self.ui.lineedit_initiative.setText(statblock.initiative_str)
        for speed_type, speed_range in statblock.speed.values.items():
            self.add_speed(speed_type=speed_type, speed_range=speed_range)
        self.ui.checkbox_str_proficient.setChecked(
            statblock.ability_scores.is_str_proficient
        )
        self.ui.spinbox_str.setValue(statblock.ability_scores.strength_score)
        self.ui.checkbox_dex_proficient.setChecked(
            statblock.ability_scores.is_dex_proficient
        )
        self.ui.spinbox_dex.setValue(statblock.ability_scores.dexterity_score)
        self.ui.checkbox_con_proficient.setChecked(
            statblock.ability_scores.is_con_proficient
        )
        self.ui.spinbox_con.setValue(statblock.ability_scores.constitution_score)
        self.ui.checkbox_int_proficient.setChecked(
            statblock.ability_scores.is_int_proficient
        )
        self.ui.spinbox_int.setValue(statblock.ability_scores.intelligence_score)
        self.ui.checkbox_wis_proficient.setChecked(
            statblock.ability_scores.is_wis_proficient
        )
        self.ui.spinbox_wis.setValue(statblock.ability_scores.wisdom_score)
        self.ui.checkbox_cha_proficient.setChecked(
            statblock.ability_scores.is_cha_proficient
        )
        self.ui.spinbox_cha.setValue(statblock.ability_scores.charisma_score)
        for skill_type, skill_proficiency in statblock.skills.values.items():
            if skill_proficiency == Proficiency.PROFICIENT:
                self.add_skill_proficiency(skill_type=skill_type)
            elif skill_proficiency == Proficiency.EXPERTISE:
                self.add_skill_expertise(skill_type=skill_type)
        for dmg_type in statblock.vulnerabilities:
            self.add_damage_vulnerability(dmg_type=dmg_type)
        for dmg_type in statblock.resistances:
            self.add_damage_resistance(dmg_type=dmg_type)
        for dmg_type_or_con in statblock.immunities:
            self.add_immunity(dmg_type_or_con=dmg_type_or_con)
        for sense_type, sense_range in statblock.senses.values.items():
            self.add_sense(sense_type=sense_type, sense_range=sense_range)
        for language, lang_prof in statblock.languages.values.items():
            if lang_prof == LanguageProficiency.UNDERSTANDS:
                self.add_understood_language(language=language)
            elif lang_prof == LanguageProficiency.SPEAKS:
                self.add_spoken_language(language=language)
        self.ui.checkbox_telepathy.setChecked(statblock.languages.telepathy[0])
        self.ui.spinbox_telepathy_range.setValue(statblock.languages.telepathy[1])
        for trait in statblock.traits:
            self.add_trait(new_trait=trait)
        for action in statblock.actions:
            self.add_action(new_action=action)
        for baction in statblock.bonus_actions:
            self.add_bonus_action(new_baction=baction)
        for reaction in statblock.reactions:
            self.add_reaction(new_reaction=reaction)
        for laction in statblock.legendary_actions:
            self.add_legendary_action(new_laction=laction)

    def create_new_statblock(self, new_name: str) -> None:
        self.clear_view()
        self.ui.lineedit_name.setText(new_name)

    def clear_view(self) -> None:
        self.init_ui()

    @property
    def name(self) -> str:
        return self.ui.lineedit_name.text()

    @property
    def challenge_rating(self) -> ChallengeRating:
        return ChallengeRating(
            self.ui.spinbox_challenge_rating.value(),
            has_lair=self.ui.checkbox_has_lair.isChecked(),
        )

    @property
    def habitat(self) -> list[Habitat]:
        return [Habitat.from_display_name(h) for h in self.ui.cb_habitat.currentData()]

    @property
    def treasure(self) -> list[Treasure]:
        return [
            Treasure.from_display_name(t) for t in self.ui.cb_treasure.currentData()
        ]

    @property
    def size(self) -> list[Size]:
        return [Size.from_display_name(s) for s in self.ui.cb_size.currentData()]

    @property
    def creature_type(self) -> CreatureType:
        return CreatureType.from_display_name(self.ui.cb_creature_type.currentText())

    @property
    def alignment(self) -> Alignment:
        return Alignment.from_display_name(self.ui.cb_alignment.currentText())

    @property
    def ac(self) -> int:
        return self.ui.spinbox_ac.value()

    @property
    def hp(self) -> str:
        return self.ui.lineedit_hp.text().strip()

    @property
    def initiative(self) -> str:
        return self.ui.lineedit_initiative.text().strip()

    @property
    def selected_speed_type(self) -> SpeedType:
        return SpeedType.from_display_name(self.ui.cb_speed.currentText())

    @property
    def selected_speed_range(self) -> int:
        return self.ui.spinbox_speed_range.value()

    @property
    def speed(self) -> Speed:
        speed_values = {}
        for i in range(self.ui.listview_speed.count()):
            li = self.ui.listview_speed.item(i)
            idata = li.data(Qt.ItemDataRole.UserRole)
            assert isinstance(idata, tuple)
            assert len(idata) == 2
            stype = idata[0]
            assert isinstance(stype, SpeedType)
            srange = idata[1]
            assert isinstance(srange, int)
            speed_values[stype] = srange
        return Speed(values=speed_values)

    def add_speed(
        self, speed_type: SpeedType | None = None, speed_range: int | None = None
    ) -> None:
        if speed_type is None:
            speed_type = self.selected_speed_type
        if speed_range is None:
            speed_range = self.selected_speed_range
        li = QListWidgetItem()
        li.setText(f"{speed_type.display_name}: {speed_range} ft.")
        li.setData(Qt.ItemDataRole.UserRole, (speed_type, speed_range))
        self.ui.listview_speed.addItem(li)

    @property
    def ability_scores(self) -> AbilityScores:
        proficiency_bonus = self.challenge_rating.proficiency_bonus
        ability_scores = {
            Ability.STRENGTH: self.ui.spinbox_str.value(),
            Ability.DEXTERITY: self.ui.spinbox_dex.value(),
            Ability.CONSTITUTION: self.ui.spinbox_con.value(),
            Ability.INTELLIGENCE: self.ui.spinbox_int.value(),
            Ability.WISDOM: self.ui.spinbox_wis.value(),
            Ability.CHARISMA: self.ui.spinbox_cha.value(),
        }
        proficiency_levels = {
            Ability.STRENGTH: (
                Proficiency.PROFICIENT
                if self.ui.checkbox_str_proficient.isChecked()
                else Proficiency.NORMAL
            ),
            Ability.DEXTERITY: (
                Proficiency.PROFICIENT
                if self.ui.checkbox_dex_proficient.isChecked()
                else Proficiency.NORMAL
            ),
            Ability.CONSTITUTION: (
                Proficiency.PROFICIENT
                if self.ui.checkbox_con_proficient.isChecked()
                else Proficiency.NORMAL
            ),
            Ability.INTELLIGENCE: (
                Proficiency.PROFICIENT
                if self.ui.checkbox_int_proficient.isChecked()
                else Proficiency.NORMAL
            ),
            Ability.WISDOM: (
                Proficiency.PROFICIENT
                if self.ui.checkbox_wis_proficient.isChecked()
                else Proficiency.NORMAL
            ),
            Ability.CHARISMA: (
                Proficiency.PROFICIENT
                if self.ui.checkbox_cha_proficient.isChecked()
                else Proficiency.NORMAL
            ),
        }
        return AbilityScores(proficiency_bonus, ability_scores, proficiency_levels)

    @property
    def selected_skill(self) -> Skill:
        return Skill.from_display_name(self.ui.cb_skills.currentText())

    @property
    def skills(self) -> Skills:
        skills_values = {}
        for i in range(self.ui.listview_skills.count()):
            li = self.ui.listview_skills.item(i)
            idata = li.data(Qt.ItemDataRole.UserRole)
            assert isinstance(idata, tuple)
            assert len(idata) == 2
            skill = idata[0]
            assert isinstance(skill, Skill)
            prof = idata[1]
            assert isinstance(prof, Proficiency)
            skills_values[skill] = prof
        return Skills(values=skills_values)

    def add_skill_proficiency(self, skill_type: Skill | None = None) -> None:
        if skill_type is None:
            skill_type = self.selected_skill
        li = QListWidgetItem()
        li.setText(f"{skill_type.display_name} - Proficient")
        li.setData(Qt.ItemDataRole.UserRole, (skill_type, Proficiency.PROFICIENT))
        self.ui.listview_skills.addItem(li)

    def add_skill_expertise(self, skill_type: Skill | None = None) -> None:
        if skill_type is None:
            skill_type = self.selected_skill
        li = QListWidgetItem()
        li.setText(f"{skill_type.display_name} - Expertise")
        li.setData(Qt.ItemDataRole.UserRole, (skill_type, Proficiency.EXPERTISE))
        self.ui.listview_skills.addItem(li)

    @property
    def selected_damage_or_condition(self) -> DamageType | Condition:
        selected_text = self.ui.cb_immunities.currentText()
        try:
            return DamageType.from_display_name(selected_text)
        except ValueError:
            return Condition.from_display_name(selected_text)

    @property
    def vulnerabilities(self) -> list[DamageType]:
        vs = []
        for i in range(self.ui.listview_immunities.count()):
            li = self.ui.listview_immunities.item(i)
            idata = li.data(Qt.ItemDataRole.UserRole)
            assert isinstance(idata, tuple)
            assert len(idata) == 2
            res = idata[1]
            assert isinstance(res, Resistance)
            if res == Resistance.VULNERABLE:
                dt = idata[0]
                assert isinstance(dt, DamageType)
                vs.append(dt)
        return vs

    def add_damage_vulnerability(self, dmg_type: DamageType | None = None) -> None:
        if dmg_type is None:
            dmg_type = self.selected_damage_or_condition
        if not isinstance(dmg_type, DamageType):
            print("Cannot add vulnerability to a Condition, skipping...")
            return
        li = QListWidgetItem()
        li.setText(f"{dmg_type.display_name} - Vulnerable")
        li.setData(Qt.ItemDataRole.UserRole, (dmg_type, Resistance.VULNERABLE))
        self.ui.listview_immunities.addItem(li)

    @property
    def resistances(self) -> list[DamageType]:
        rs = []
        for i in range(self.ui.listview_immunities.count()):
            li = self.ui.listview_immunities.item(i)
            idata = li.data(Qt.ItemDataRole.UserRole)
            assert isinstance(idata, tuple)
            assert len(idata) == 2
            res = idata[1]
            assert isinstance(res, Resistance)
            if res == Resistance.RESISTANT:
                dt = idata[0]
                assert isinstance(dt, DamageType)
                rs.append(dt)
        return rs

    def add_damage_resistance(self, dmg_type: DamageType | None = None) -> None:
        if dmg_type is None:
            dmg_type = self.selected_damage_or_condition
        if not isinstance(dmg_type, DamageType):
            print("Cannot add resistance to a Condition, skipping...")
            return
        li = QListWidgetItem()
        li.setText(f"{dmg_type.display_name} - Resistant")
        li.setData(Qt.ItemDataRole.UserRole, (dmg_type, Resistance.RESISTANT))
        self.ui.listview_immunities.addItem(li)

    @property
    def immunities(self) -> list[DamageType | Condition]:
        ims = []
        for i in range(self.ui.listview_immunities.count()):
            li = self.ui.listview_immunities.item(i)
            idata = li.data(Qt.ItemDataRole.UserRole)
            assert isinstance(idata, tuple)
            assert len(idata) == 2
            res = idata[1]
            assert isinstance(res, Resistance)
            if res == Resistance.IMMUNE:
                dt_or_con = idata[0]
                assert isinstance(dt_or_con, (DamageType, Condition))
                ims.append(dt_or_con)
        return ims

    def add_immunity(
        self, dmg_type_or_con: DamageType | Condition | None = None
    ) -> None:
        if dmg_type_or_con is None:
            dmg_type_or_con = self.selected_damage_or_condition
        li = QListWidgetItem()
        li.setText(f"{dmg_type_or_con.display_name} - Immune")
        li.setData(Qt.ItemDataRole.UserRole, (dmg_type_or_con, Resistance.IMMUNE))
        self.ui.listview_immunities.addItem(li)

    @property
    def selected_sense(self) -> Sense:
        return Sense.from_display_name(self.ui.cb_senses.currentText())

    @property
    def selected_sense_range(self) -> int:
        return self.ui.spinbox_sense_range.value()

    @property
    def senses(self) -> Senses:
        senses_values = {}
        for i in range(self.ui.listview_senses.count()):
            li = self.ui.listview_senses.item(i)
            idata = li.data(Qt.ItemDataRole.UserRole)
            assert isinstance(idata, tuple)
            assert len(idata) == 2
            sense = idata[0]
            assert isinstance(sense, Sense)
            sense_range = idata[1]
            assert isinstance(sense_range, int)
            senses_values[sense] = sense_range
        return Senses(values=senses_values)

    def add_sense(
        self, sense_type: Sense | None = None, sense_range: int | None = None
    ) -> None:
        if sense_type is None:
            sense_type = self.selected_sense
        if sense_range is None:
            sense_range = self.selected_sense_range
        li = QListWidgetItem()
        li.setText(f"{sense_type.display_name}: {sense_range} ft.")
        li.setData(Qt.ItemDataRole.UserRole, (sense_type, sense_range))
        self.ui.listview_senses.addItem(li)

    @property
    def selected_language(self) -> Language:
        return Language.from_display_name(self.ui.cb_languages.currentText())

    @property
    def languages(self) -> Languages:
        languages_values = {}
        for i in range(self.ui.listview_languages.count()):
            li = self.ui.listview_languages.item(i)
            idata = li.data(Qt.ItemDataRole.UserRole)
            assert isinstance(idata, tuple)
            assert len(idata) == 2
            language = idata[0]
            assert isinstance(language, Language)
            lang_prof = idata[1]
            assert isinstance(lang_prof, LanguageProficiency)
            languages_values[language] = lang_prof
        return Languages(
            values=languages_values,
            telepathy=(
                self.ui.checkbox_telepathy.isChecked(),
                self.ui.spinbox_telepathy_range.value(),
            ),
        )

    def add_understood_language(self, language: Language | None = None) -> None:
        if language is None:
            language = self.selected_language
        li = QListWidgetItem()
        li.setText(f"{language.display_name}: Understands")
        li.setData(
            Qt.ItemDataRole.UserRole,
            (language, LanguageProficiency.UNDERSTANDS),
        )
        self.ui.listview_languages.addItem(li)

    def add_spoken_language(self, language: Language | None = None) -> None:
        if language is None:
            language = self.selected_language
        li = QListWidgetItem()
        li.setText(f"{language.display_name}: Speaks")
        li.setData(
            Qt.ItemDataRole.UserRole,
            (language, LanguageProficiency.SPEAKS),
        )
        self.ui.listview_languages.addItem(li)

    @property
    def traits(self) -> list[Trait]:
        retval = []
        for i in range(self.ui.listview_traits.count()):
            item = self.ui.listview_traits.item(i)
            trait = item.data(Qt.ItemDataRole.UserRole)
            assert isinstance(trait, Trait)
            retval.append(trait)
        return retval

    def add_trait(self, new_trait: Trait | None = None) -> None:
        if new_trait is None:
            trait_title = self.ui.lineedit_trait_title.text()
            if not trait_title:
                return
            trait_description = self.ui.textedit_trait.toPlainText()
            if not trait_description:
                return
            new_trait = Trait(
                self.name,
                self.ability_scores,
                self.challenge_rating.proficiency_bonus,
                self.ability_scores.saving_throws,
                self.ui.checkbox_has_lair.isChecked(),
                trait_title,
                trait_description,
                # TODO: Implement these
                limited_use_type=LimitedUsageType.UNLIMITED,
                limited_use_charges={},
                lair_charge_bonuses={},
            )
        existing_item = next(
            (
                True
                for idx in range(self.ui.listview_traits.count())
                if self.ui.listview_traits.item(idx).text() == trait_title
            ),
            False,
        )
        if not existing_item:
            li = QListWidgetItem()
            li.setText(new_trait.title)
            li.setData(Qt.ItemDataRole.UserRole, new_trait)
            self.ui.listview_traits.addItem(li)
        self.ui.lineedit_trait_title.clear()
        self.ui.textedit_trait.clear()

    @property
    def actions(self) -> list[Action]:
        retval = []
        for i in range(self.ui.listview_actions.count()):
            item = self.ui.listview_actions.item(i)
            action = item.data(Qt.ItemDataRole.UserRole)
            assert isinstance(action, Action)
            retval.append(action)
        return retval

    def add_action(self, new_action: Action | None = None) -> None:
        if new_action is None:
            action_title = self.ui.lineedit_action_title.text()
            if not action_title:
                return
            action_description = self.ui.textedit_action.toPlainText()
            if not action_description:
                return
            new_action = Action(
                self.name,
                self.ability_scores,
                self.challenge_rating.proficiency_bonus,
                self.ability_scores.saving_throws,
                self.ui.checkbox_has_lair.isChecked(),
                action_title,
                action_description,
            )
        existing_item = next(
            (
                True
                for idx in range(self.ui.listview_actions.count())
                if self.ui.listview_actions.item(idx).text() == action_title
            ),
            False,
        )
        if not existing_item:
            li = QListWidgetItem()
            li.setText(new_action.title)
            li.setData(Qt.ItemDataRole.UserRole, new_action)
            self.ui.listview_actions.addItem(li)
        self.ui.lineedit_action_title.clear()
        self.ui.textedit_action.clear()

    @property
    def bonus_actions(self) -> list[BonusAction]:
        retval = []
        for i in range(self.ui.listview_bonus_actions.count()):
            item = self.ui.listview_bonus_actions.item(i)
            baction = item.data(Qt.ItemDataRole.UserRole)
            assert isinstance(baction, Action)
            retval.append(baction)
        return retval

    def add_bonus_action(self, new_baction: BonusAction | None = None) -> None:
        if new_baction is None:
            baction_title = self.ui.lineedit_bonus_action_title.text()
            if not baction_title:
                return
            baction_description = self.ui.textedit_bonus_action.toPlainText()
            if not baction_description:
                return
            new_baction = BonusAction(
                self.name,
                self.ability_scores,
                self.challenge_rating.proficiency_bonus,
                self.ability_scores.saving_throws,
                self.ui.checkbox_has_lair.isChecked(),
                baction_title,
                baction_description,
            )
        existing_item = next(
            (
                True
                for idx in range(self.ui.listview_bonus_actions.count())
                if self.ui.listview_bonus_actions.item(idx).text() == baction_title
            ),
            False,
        )
        if not existing_item:
            li = QListWidgetItem()
            li.setText(new_baction.title)
            li.setData(Qt.ItemDataRole.UserRole, new_baction)
            self.ui.listview_bonus_actions.addItem(li)
        self.ui.lineedit_bonus_action_title.clear()
        self.ui.textedit_bonus_action.clear()

    @property
    def reactions(self) -> list[Reaction]:
        retval = []
        for i in range(self.ui.listview_reactions.count()):
            item = self.ui.listview_reactions.item(i)
            reaction = item.data(Qt.ItemDataRole.UserRole)
            assert isinstance(reaction, Reaction)
            retval.append(reaction)
        return retval

    def add_reaction(self, new_reaction: Reaction | None = None) -> None:
        if new_reaction is None:
            reaction_title = self.ui.lineedit_reaction_title.text()
            if not reaction_title:
                return
            reaction_description = self.ui.textedit_reaction.toPlainText()
            if not reaction_description:
                return
            new_reaction = Reaction(
                self.name,
                self.ability_scores,
                self.challenge_rating.proficiency_bonus,
                self.ability_scores.saving_throws,
                self.ui.checkbox_has_lair.isChecked(),
                reaction_title,
                reaction_description,
            )
        existing_item = next(
            (
                True
                for idx in range(self.ui.listview_reactions.count())
                if self.ui.listview_reactions.item(idx).text() == reaction_title
            ),
            False,
        )
        if not existing_item:
            li = QListWidgetItem()
            li.setText(new_reaction.title)
            li.setData(Qt.ItemDataRole.UserRole, new_reaction)
            self.ui.listview_reactions.addItem(li)
        self.ui.lineedit_reaction_title.clear()
        self.ui.textedit_reaction.clear()

    @property
    def legendary_actions(self) -> list[LegendaryAction]:
        retval = []
        for i in range(self.ui.listview_legendary_actions.count()):
            item = self.ui.listview_legendary_actions.item(i)
            laction = item.data(Qt.ItemDataRole.UserRole)
            assert isinstance(laction, LegendaryAction)
            retval.append(laction)
        return retval

    def add_legendary_action(self, new_laction: LegendaryAction | None = None) -> None:
        if new_laction is None:
            laction_title = self.ui.lineedit_legendary_action_title.text()
            if not laction_title:
                return
            laction_description = self.ui.textedit_legendary_action.toPlainText()
            if not laction_description:
                return
            new_laction = LegendaryAction(
                self.name,
                self.ability_scores,
                self.challenge_rating.proficiency_bonus,
                self.ability_scores.saving_throws,
                self.ui.checkbox_has_lair.isChecked(),
                laction_title,
                laction_description,
            )
        existing_item = next(
            (
                True
                for idx in range(self.ui.listview_legendary_actions.count())
                if self.ui.listview_legendary_actions.item(idx).text() == laction_title
            ),
            False,
        )
        if not existing_item:
            li = QListWidgetItem()
            li.setText(new_laction.title)
            li.setData(Qt.ItemDataRole.UserRole, new_laction)
            self.ui.listview_legendary_actions.addItem(li)
        self.ui.lineedit_legendary_action_title.clear()
        self.ui.textedit_legendary_action.clear()

    @property
    def statblock(self) -> StatBlock:
        return StatBlock(
            name=self.name,
            challenge_rating=self.challenge_rating,
            habitat=self.habitat,
            treasure=self.treasure,
            size=self.size,
            creature_type=self.creature_type,
            tags=[],
            alignment=self.alignment,
            armor_class=self.ac,
            speed=self.speed,
            ability_scores=self.ability_scores,
            skills=self.skills,
            vulnerabilities=self.vulnerabilities,
            resistances=self.resistances,
            immunities=self.immunities,
            gear=[],
            senses=self.senses,
            languages=self.languages,
            traits=self.traits,
            actions=self.actions,
            bonus_actions=self.bonus_actions,
            reactions=self.reactions,
            legendary_actions=self.legendary_actions,
        )

    @property
    def selected_statblock(self) -> str:
        return self.ui.listview_available_statblocks.selectedItems()[0].text()
