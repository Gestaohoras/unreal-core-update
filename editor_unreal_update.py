"""
editor_unreal_update.py
Editor de atualizacao do Unreal Core.xyz
Gerencia changelog.json e version.json do repositorio de updates.
Desenvolvido por Trollingparty
"""

import os
import sys
import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QComboBox, QFrame,
    QMessageBox, QListWidgetItem, QInputDialog, QDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# ── Config ────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(sys.argv[0]))
CHANGELOG_PATH = os.path.join(BASE_DIR, "changelog.json")
VERSION_PATH   = os.path.join(BASE_DIR, "version.json")

# Prefixos para os itens de changelog
PREFIXOS = {
    "Adicionado":  "[ + ] Adicionado",
    "Corrigido":   "[ * ] Corrigido",
    "Removido":    "[ - ] Removido",
    "Alterado":    "[ ~ ] Alterado",
    "Desativado":  "[ ! ] Desativado temporariamente",
}

# ── Cores ─────────────────────────────────────────────────────
BG       = "#111316"
BG_CARD  = "#181b1f"
BG_INPUT = "rgba(0,0,0,160)"
ACCENT   = "#5b8dd9"
ACCENT_H = "#7aaaf0"
BORDER   = "rgba(255,255,255,18)"
BORDER_F = "#5b8dd9"
TEXT     = "#ffffff"
TEXT_MID = "#aaaaaa"
TEXT_DIM = "#555555"

_BTN = f"""
    QPushButton {{
        background: rgba(60,80,110,200);
        border: 1px solid rgba(91,141,217,120);
        border-radius: 4px;
        padding: 7px 16px;
        color: {TEXT};
        font-family: "Segoe UI";
    }}
    QPushButton:hover {{
        background: rgba(80,110,160,255);
        border-color: rgba(122,170,240,200);
    }}
    QPushButton:pressed {{ background: rgba(50,70,100,255); }}
"""

_BTN_GHOST = f"""
    QPushButton {{
        background: transparent;
        border: 1px solid {BORDER};
        border-radius: 4px;
        color: {TEXT_MID};
        font-family: "Segoe UI";
    }}
    QPushButton:hover {{
        background: rgba(255,255,255,8);
        border-color: rgba(255,255,255,55);
        color: {TEXT};
    }}
"""

_INPUT = f"""
    QLineEdit {{
        background: {BG_INPUT};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 8px 12px;
        color: {TEXT};
        font-family: "Segoe UI";
        font-size: 11px;
    }}
    QLineEdit:focus {{
        border-color: {BORDER_F};
        background: rgba(0,0,0,200);
    }}
"""

_COMBO = f"""
    QComboBox {{
        background: {BG_INPUT};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 6px 10px;
        color: {TEXT};
        font-family: "Segoe UI";
        font-size: 11px;
    }}
    QComboBox:focus {{ border-color: {BORDER_F}; }}
    QComboBox::drop-down {{ border: none; width: 20px; }}
    QComboBox QAbstractItemView {{
        background: #1a1c20;
        border: 1px solid {BORDER};
        selection-background-color: rgba(91,141,217,80);
        color: {TEXT};
    }}
"""

_LIST = f"""
    QListWidget {{
        background: #0d0f11;
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 6px;
        color: {TEXT};
        font-family: "Consolas";
        font-size: 11px;
        outline: none;
    }}
    QListWidget::item {{
        background: rgba(255,255,255,6);
        border-left: 2px solid {ACCENT};
        border-radius: 3px;
        padding: 9px 10px;
        margin-bottom: 4px;
    }}
    QListWidget::item:hover  {{ background: rgba(255,255,255,12); }}
    QListWidget::item:selected {{
        background: rgba(91,141,217,55);
        border-left-color: {ACCENT_H};
        color: {TEXT};
    }}
    QScrollBar:vertical {{
        background: transparent; width: 8px; border-radius: 4px; margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(91,141,217,140); border-radius: 4px; min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{ background: rgba(91,141,217,200); }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical,  QScrollBar::sub-page:vertical {{ background: none; }}
"""


# ── Helpers ───────────────────────────────────────────────────
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def today_str():
    return datetime.now().strftime("%d/%m/%Y")


# ── Janela principal ──────────────────────────────────────────
class EditorWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unreal Core — Editor de Atualização")
        self.setFixedSize(700, 620)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._drag_pos = None
        self.current_page = "changelog"

        # Dados
        self.changelog: list = load_json(CHANGELOG_PATH, [])
        self.version_data: dict = load_json(VERSION_PATH, {"app_release": ""})

        # Índice da entrada de changelog selecionada (0 = mais recente)
        self._entry_idx = 0

        self._build()

    # ── Build ──────────────────────────────────────────────────
    def _build(self):
        self.setStyleSheet(f"QWidget {{ background: {BG}; }}")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._titlebar())
        root.addWidget(self._header())
        root.addWidget(self._tabbar())

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(18, 16, 18, 18)
        self.content_layout.setSpacing(0)
        root.addWidget(self.content_widget, 1)

        self._show_page("changelog")

    def _titlebar(self):
        bar = QWidget()
        bar.setFixedHeight(32)
        bar.setStyleSheet(f"""
            background: #0a0b0d;
            border-bottom: 1px solid {BORDER};
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(12, 0, 10, 0)

        t = QLabel("UNREAL CORE — EDITOR DE ATUALIZAÇÃO")
        t.setFont(QFont("Consolas", 8))
        t.setStyleSheet(f"color:{TEXT_MID}; letter-spacing:1px; background:transparent; border:none;")
        hl.addWidget(t)
        hl.addStretch()

        close = QPushButton("✕")
        close.setFont(QFont("Segoe UI", 11))
        close.setFixedSize(24, 24)
        close.setCursor(Qt.PointingHandCursor)
        close.setStyleSheet(f"""
            QPushButton {{ color:#cc3333; background:transparent; border:none; border-radius:2px; }}
            QPushButton:hover {{ color:#ff5555; background:rgba(255,50,50,30); }}
        """)
        close.clicked.connect(self.close)
        hl.addWidget(close)
        return bar

    def _header(self):
        hdr = QWidget()
        hdr.setStyleSheet(f"background:transparent; border-bottom:1px solid {BORDER};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(22, 16, 22, 14)

        t = QLabel("Unreal Core — Update Manager")
        t.setFont(QFont("Segoe UI", 17, QFont.DemiBold))
        t.setStyleSheet(f"color:{TEXT}; background:transparent; border:none;")
        hl.addWidget(t)
        hl.addStretch()

        ver = QLabel(f"v{self.version_data.get('app_release', '—')}")
        ver.setFont(QFont("Consolas", 10))
        ver.setStyleSheet(f"color:{ACCENT}; background:transparent; border:none;")
        hl.addWidget(ver)
        return hdr

    def _tabbar(self):
        bar = QWidget()
        bar.setStyleSheet(f"background:rgba(0,0,0,60); border-bottom:1px solid {BORDER};")
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)

        self._tabs = {}
        for tid, lbl in [("changelog", "Changelog"), ("version", "Versão")]:
            tab = QLabel(lbl)
            tab.setFont(QFont("Segoe UI", 11))
            tab.setCursor(Qt.PointingHandCursor)
            tab.setFixedHeight(36)
            tab.setProperty("tid", tid)
            tab.mousePressEvent = lambda _e, t=tid: self._show_page(t)
            hl.addWidget(tab)
            self._tabs[tid] = tab

        hl.addStretch()
        return bar

    def _style_tabs(self):
        for tid, tab in self._tabs.items():
            if tid == self.current_page:
                tab.setStyleSheet(f"""
                    QLabel {{
                        color:{TEXT}; background:rgba(91,141,217,18);
                        border-bottom:2px solid {ACCENT}; padding:0 22px;
                    }}
                """)
            else:
                tab.setStyleSheet(f"""
                    QLabel {{
                        color:{TEXT_MID}; background:transparent;
                        border-bottom:2px solid transparent; padding:0 22px;
                    }}
                    QLabel:hover {{ color:{TEXT}; }}
                """)

    def _show_page(self, page_id: str):
        self.current_page = page_id
        self._style_tabs()
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if page_id == "changelog":
            self._page_changelog()
        else:
            self._page_version()

    # ── Aba Changelog ─────────────────────────────────────────
    def _page_changelog(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD};
                border:1px solid {BORDER};
                border-radius:6px;
            }}
        """)
        vl = QVBoxLayout(card)
        vl.setContentsMargins(16, 16, 16, 16)
        vl.setSpacing(12)

        # ── Seletor de versão ─────────────────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        lbl = QLabel("Versão:")
        lbl.setFont(QFont("Segoe UI", 10))
        lbl.setStyleSheet(f"color:{TEXT_MID}; background:transparent; border:none;")
        top_row.addWidget(lbl)

        self._ver_combo = QComboBox()
        self._ver_combo.setFixedHeight(32)
        self._ver_combo.setMinimumWidth(160)
        self._ver_combo.setStyleSheet(_COMBO)
        self._ver_combo.setFont(QFont("Segoe UI", 10))
        self._refresh_ver_combo()
        self._ver_combo.currentIndexChanged.connect(self._on_ver_changed)
        top_row.addWidget(self._ver_combo)

        btn_new_ver = QPushButton("+ Nova versão")
        btn_new_ver.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
        btn_new_ver.setCursor(Qt.PointingHandCursor)
        btn_new_ver.setStyleSheet(_BTN)
        btn_new_ver.clicked.connect(self._add_version)
        top_row.addWidget(btn_new_ver)

        btn_del_ver = QPushButton("Remover versão")
        btn_del_ver.setFont(QFont("Segoe UI", 9))
        btn_del_ver.setCursor(Qt.PointingHandCursor)
        btn_del_ver.setStyleSheet(_BTN_GHOST)
        btn_del_ver.clicked.connect(self._remove_version)
        top_row.addWidget(btn_del_ver)

        top_row.addStretch()
        vl.addLayout(top_row)

        # ── Campos da versão selecionada ──────────────────────
        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)

        meta_row.addWidget(self._field("Número da versão:", "entry_ver_num"))
        meta_row.addWidget(self._field("Data (dd/mm/aaaa):", "entry_ver_date"))
        vl.addLayout(meta_row)

        self._load_entry_fields()

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{BORDER}; border:none;")
        vl.addWidget(sep)

        # ── Input para novo item ──────────────────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(list(PREFIXOS.keys()))
        self.combo_tipo.setFixedWidth(130)
        self.combo_tipo.setFixedHeight(32)
        self.combo_tipo.setStyleSheet(_COMBO)
        self.combo_tipo.setFont(QFont("Segoe UI", 10))
        input_row.addWidget(self.combo_tipo)

        self.entry_texto = QLineEdit()
        self.entry_texto.setPlaceholderText("Descrição da alteração...")
        self.entry_texto.setFont(QFont("Segoe UI", 10))
        self.entry_texto.setFixedHeight(32)
        self.entry_texto.setStyleSheet(_INPUT)
        self.entry_texto.returnPressed.connect(self._add_item)
        input_row.addWidget(self.entry_texto, 1)

        btn_add = QPushButton("Adicionar")
        btn_add.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        btn_add.setFixedHeight(32)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet(_BTN)
        btn_add.clicked.connect(self._add_item)
        input_row.addWidget(btn_add)

        vl.addLayout(input_row)

        # ── Lista de itens ────────────────────────────────────
        self.listbox = QListWidget()
        self.listbox.setFont(QFont("Consolas", 10))
        self.listbox.setDragDropMode(QListWidget.InternalMove)
        self.listbox.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listbox.setWordWrap(True)
        self.listbox.setStyleSheet(_LIST)
        self.listbox.setMinimumHeight(200)
        vl.addWidget(self.listbox, 1)
        self._refresh_list()

        # ── Ações da lista ────────────────────────────────────
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background:{BORDER}; border:none;")
        vl.addWidget(sep2)

        act_row = QHBoxLayout()
        act_row.setSpacing(6)

        for icon, tip, fn in [
            ("✎", "Editar",           self._edit_item),
            ("↑", "Mover para cima",  self._move_up),
            ("↓", "Mover para baixo", self._move_down),
        ]:
            b = QPushButton(icon)
            b.setFont(QFont("Segoe UI", 13))
            b.setFixedSize(32, 32)
            b.setToolTip(tip)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(_BTN_GHOST)
            b.clicked.connect(fn)
            act_row.addWidget(b)

        btn_rem = QPushButton("Remover")
        btn_rem.setFont(QFont("Segoe UI", 10))
        btn_rem.setFixedHeight(32)
        btn_rem.setCursor(Qt.PointingHandCursor)
        btn_rem.setStyleSheet(_BTN_GHOST)
        btn_rem.clicked.connect(self._remove_item)
        act_row.addWidget(btn_rem)

        act_row.addStretch()

        btn_save = QPushButton("Salvar changelog.json")
        btn_save.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        btn_save.setFixedHeight(32)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet(_BTN)
        btn_save.clicked.connect(self._save_changelog)
        act_row.addWidget(btn_save)

        vl.addLayout(act_row)

        self.content_layout.addWidget(card)

    def _field(self, label_text: str, attr_name: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        vl = QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(4)
        lbl = QLabel(label_text)
        lbl.setFont(QFont("Segoe UI", 9))
        lbl.setStyleSheet(f"color:{TEXT_MID}; background:transparent; border:none;")
        vl.addWidget(lbl)
        inp = QLineEdit()
        inp.setFont(QFont("Segoe UI", 10))
        inp.setFixedHeight(30)
        inp.setStyleSheet(_INPUT)
        vl.addWidget(inp)
        setattr(self, attr_name, inp)
        return w

    # ── Aba Versão ────────────────────────────────────────────
    def _page_version(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD};
                border:1px solid {BORDER};
                border-radius:6px;
            }}
        """)
        vl = QVBoxLayout(card)
        vl.setContentsMargins(36, 36, 36, 36)
        vl.setSpacing(16)

        lbl = QLabel("RELEASE DO UNREAL CORE")
        lbl.setFont(QFont("Segoe UI", 9))
        lbl.setStyleSheet(f"color:{TEXT_MID}; letter-spacing:1px; background:transparent; border:none;")
        vl.addWidget(lbl)

        self.entry_release = QLineEdit()
        self.entry_release.setText(self.version_data.get("app_release", ""))
        self.entry_release.setFont(QFont("Segoe UI", 13))
        self.entry_release.setFixedHeight(42)
        self.entry_release.setPlaceholderText("ex: 1.0.5")
        self.entry_release.setStyleSheet(_INPUT)
        vl.addWidget(self.entry_release)

        note = QLabel("Este valor será comparado com o version.json local do cliente para decidir se há atualização.")
        note.setFont(QFont("Segoe UI", 9))
        note.setWordWrap(True)
        note.setStyleSheet(f"color:{TEXT_DIM}; background:transparent; border:none;")
        vl.addWidget(note)

        vl.addSpacing(8)

        btn_save = QPushButton("Salvar version.json")
        btn_save.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet(_BTN)
        btn_save.clicked.connect(self._save_version)
        vl.addWidget(btn_save)

        vl.addStretch()
        self.content_layout.addWidget(card)
        self.content_layout.addStretch()

    # ── Lógica de versões ─────────────────────────────────────
    def _refresh_ver_combo(self):
        self._ver_combo.blockSignals(True)
        self._ver_combo.clear()
        if not self.changelog:
            self._ver_combo.addItem("(nenhuma versão)")
        else:
            for entry in self.changelog:
                self._ver_combo.addItem(f"v{entry.get('version','?')}  —  {entry.get('date','')}")
        self._ver_combo.setCurrentIndex(self._entry_idx)
        self._ver_combo.blockSignals(False)

    def _on_ver_changed(self, idx: int):
        if 0 <= idx < len(self.changelog):
            self._entry_idx = idx
            self._load_entry_fields()
            self._refresh_list()

    def _load_entry_fields(self):
        if not self.changelog or self._entry_idx >= len(self.changelog):
            self.entry_ver_num.setText("")
            self.entry_ver_date.setText(today_str())
            return
        entry = self.changelog[self._entry_idx]
        self.entry_ver_num.setText(entry.get("version", ""))
        self.entry_ver_date.setText(entry.get("date", ""))

    def _add_version(self):
        ver, ok = QInputDialog.getText(self, "Nova versão", "Número da versão (ex: 1.0.5):")
        if not ok or not ver.strip():
            return
        ver = ver.strip()
        new_entry = {"version": ver, "date": today_str(), "changes": []}
        self.changelog.insert(0, new_entry)
        self._entry_idx = 0
        self._refresh_ver_combo()
        self._load_entry_fields()
        self._refresh_list()

    def _remove_version(self):
        if not self.changelog:
            return
        entry = self.changelog[self._entry_idx]
        ans = QMessageBox.question(
            self, "Remover versão",
            f'Remover a entrada "v{entry.get("version","?")}"?\nEsta ação não pode ser desfeita.',
            QMessageBox.Yes | QMessageBox.No,
        )
        if ans != QMessageBox.Yes:
            return
        self.changelog.pop(self._entry_idx)
        self._entry_idx = max(0, self._entry_idx - 1)
        self._refresh_ver_combo()
        self._load_entry_fields()
        self._refresh_list()

    # ── Lógica de itens ───────────────────────────────────────
    def _current_changes(self) -> list:
        if not self.changelog or self._entry_idx >= len(self.changelog):
            return []
        return self.changelog[self._entry_idx].setdefault("changes", [])

    def _refresh_list(self):
        self.listbox.clear()
        for item in self._current_changes():
            self.listbox.addItem(QListWidgetItem(f"  {item}"))

    def _add_item(self):
        texto = self.entry_texto.text().strip()
        if not texto:
            QMessageBox.warning(self, "Aviso", "Digite a descrição da alteração.")
            return
        if not self.changelog:
            QMessageBox.warning(self, "Aviso", "Crie uma versão antes de adicionar itens.")
            return
        frase = f"{PREFIXOS[self.combo_tipo.currentText()]} {texto}"
        self._current_changes().append(frase)
        self._refresh_list()
        self.entry_texto.clear()
        self.entry_texto.setFocus()

    def _edit_item(self):
        row = self.listbox.currentRow()
        changes = self._current_changes()
        if row < 0 or row >= len(changes):
            QMessageBox.warning(self, "Aviso", "Selecione um item para editar.")
            return
        atual = changes[row]
        prefixo_key = ""
        texto_limpo = atual
        for key, pfx in PREFIXOS.items():
            if atual.startswith(pfx):
                prefixo_key = key
                texto_limpo = atual[len(pfx):].strip()
                break
        novo, ok = QInputDialog.getText(self, "Editar item", "Descrição:", text=texto_limpo)
        if ok and novo.strip():
            if prefixo_key:
                changes[row] = f"{PREFIXOS[prefixo_key]} {novo.strip()}"
            else:
                changes[row] = novo.strip()
            self._refresh_list()
            self.listbox.setCurrentRow(row)

    def _move_up(self):
        row = self.listbox.currentRow()
        changes = self._current_changes()
        if row <= 0:
            return
        changes[row], changes[row - 1] = changes[row - 1], changes[row]
        self._refresh_list()
        self.listbox.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.listbox.currentRow()
        changes = self._current_changes()
        if row < 0 or row >= len(changes) - 1:
            return
        changes[row], changes[row + 1] = changes[row + 1], changes[row]
        self._refresh_list()
        self.listbox.setCurrentRow(row + 1)

    def _remove_item(self):
        row = self.listbox.currentRow()
        changes = self._current_changes()
        if 0 <= row < len(changes):
            del changes[row]
            self._refresh_list()

    # ── Salvar ────────────────────────────────────────────────
    def _save_changelog(self):
        # Sincroniza campos de versão e data antes de salvar
        if self.changelog and self._entry_idx < len(self.changelog):
            # Sincroniza ordem da lista (drag & drop)
            nova_ordem = []
            for i in range(self.listbox.count()):
                txt = self.listbox.item(i).text().strip()
                nova_ordem.append(txt)
            self.changelog[self._entry_idx]["changes"] = nova_ordem
            self.changelog[self._entry_idx]["version"] = self.entry_ver_num.text().strip()
            self.changelog[self._entry_idx]["date"]    = self.entry_ver_date.text().strip()
            self._refresh_ver_combo()

        save_json(CHANGELOG_PATH, self.changelog)
        QMessageBox.information(self, "Salvo", "changelog.json atualizado com sucesso!")

    def _save_version(self):
        release = self.entry_release.text().strip()
        if not release:
            QMessageBox.warning(self, "Aviso", "Informe o número da versão.")
            return
        self.version_data["app_release"] = release
        save_json(VERSION_PATH, self.version_data)
        QMessageBox.information(self, "Salvo", "version.json atualizado com sucesso!")

    # ── Drag da janela ────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(self.pos() + event.globalPos() - self._drag_pos)
            self._drag_pos = event.globalPos()


# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    os.chdir(BASE_DIR)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = EditorWindow()
    window.show()
    sys.exit(app.exec_())
