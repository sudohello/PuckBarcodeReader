"""Location, retrieval and reading of Data Matrix-style barcodes.
"""
from dls_barcode.plate import Scanner
from dls_barcode.util.image import Image

# testing
from dls_barcode.datamatrix.reedsolo import RSDecode, ReedSolomonError
from dls_barcode.datamatrix.decode import Decoder
from dls_barcode.gui.store import Record, Store
