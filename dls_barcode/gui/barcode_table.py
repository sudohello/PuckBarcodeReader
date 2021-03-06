from __future__ import division

import os

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QGroupBox, QVBoxLayout, QHBoxLayout

from dls_barcode.plate import NOT_FOUND_SLOT_SYMBOL, EMPTY_SLOT_SYMBOL


class BarcodeTable(QGroupBox):
    """ GUI component. Displays a list of barcodes for the currently selected puck.
    """
    def __init__(self, options):
        super(BarcodeTable, self).__init__()

        self._options = options

        self.setTitle("Plate Barcodes")
        self._init_ui()
        self.clear()

    def _init_ui(self):
        # Plate being displayed
        self._plate_lbl = QtGui.QLabel()

        # Create barcode table - lists all the barcodes in a record
        self._table = QtGui.QTableWidget()
        self._table.setMinimumWidth(110)
        self._table.setMinimumHeight(600)
        self._table.setColumnCount(1)
        self._table.setRowCount(10)
        self._table.setHorizontalHeaderLabels(['Barcode'])
        self._table.setColumnWidth(0, 100)

        # Clipboard button - copy the selected barcodes to the clipboard
        self._btn_clipboard = QtGui.QPushButton('Copy To Clipboard')
        self._btn_clipboard.setToolTip('Copy barcodes for the selected record to the clipboard')
        self._btn_clipboard.resize(self._btn_clipboard.sizeHint())
        self._btn_clipboard.clicked.connect(self.copy_to_clipboard)

        hbox = QHBoxLayout()
        hbox.setSpacing(10)
        hbox.addWidget(self._btn_clipboard)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(self._plate_lbl)
        vbox.addWidget(self._table)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def populate(self, holder_barcode, barcodes):
        """ Called when a new row is selected on the record table.
        """
        self._holder_barcode = holder_barcode
        self._barcodes = barcodes[:]
        self._update_state()

    def clear(self):
        self._holder_barcode = None
        self._barcodes = []
        self._update_state()

    def _update_state(self):
        self._populate_table()
        self._update_button_state()
        self._update_plate_label()

    def _populate_table(self):
        """Displays all of the barcodes from the selected record in the barcode table. By default, valid barcodes are
        highlighted green, invalid barcodes are highlighted red, and empty slots are grey.
        """
        self._table.clearContents()
        self._table.setRowCount(len(self._barcodes))

        for index, barcode in enumerate(self._barcodes):
            if barcode == NOT_FOUND_SLOT_SYMBOL:
                cell_color = self._options.col_bad()
            elif barcode == EMPTY_SLOT_SYMBOL:
                cell_color = self._options.col_empty()
            else:
                cell_color = self._options.col_ok()

            cell_color.a = 192

            # Set table item
            barcode = QtGui.QTableWidgetItem(barcode)
            barcode.setBackgroundColor(cell_color.to_qt())
            barcode.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self._table.setItem(index, 0, barcode)

    def _update_button_state(self):
        self._btn_clipboard.setEnabled(self._has_barcodes())

    def copy_to_clipboard(self):
        """ Called when the copy to clipboard button is pressed. Copies the list/s of
        barcodes for the currently selected records to the clipboard so that the user
        can paste it elsewhere.
        """
        clipboard_barcodes = [self._holder_barcode] + self._barcodes[:]
        for i, barcode in enumerate(clipboard_barcodes):
            if barcode in [NOT_FOUND_SLOT_SYMBOL, EMPTY_SLOT_SYMBOL]:
                clipboard_barcodes[i] = ""

        sep = os.linesep
        if clipboard_barcodes:
            import pyperclip
            pyperclip.copy(sep.join(clipboard_barcodes))

    def _update_plate_label(self):
        text = "Plate : " + str(self._holder_barcode) if self._has_barcodes() else "Plate:"
        self._plate_lbl.setText(text)

    def _has_barcodes(self):
        return self._barcodes is not None and len(self._barcodes) > 0
