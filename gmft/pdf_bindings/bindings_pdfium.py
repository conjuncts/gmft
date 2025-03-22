"""
Legacy module to import PyPDFium2 bindings. Please use gmft.pdf_bindings.pdfium instead.
"""
import warnings

warnings.warn(
    'gmft.pdf_bindings.bindings_pdfium has been moved to gmft.pdf_bindings.pdfium.', 
    DeprecationWarning, 
    stacklevel=2
)


# PyPDFium2 bindings
from gmft.pdf_bindings.pdfium import PyPDFium2Page, PyPDFium2Document, PyPDFium2Utils
 