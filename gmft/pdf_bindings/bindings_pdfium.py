"""
Legacy module to import PyPDFium2 bindings. Please use gmft.pdf_bindings.pdfium instead.
"""
import warnings

warnings.warn(
    'gmft.pdf_bindings.bindings_pdfium has moved to gmft.pdf_bindings.pdfium. Importing here will break in v0.6.0.', 
    DeprecationWarning, 
    stacklevel=2
)


# PyPDFium2 bindings
from gmft.pdf_bindings.pdfium import PyPDFium2Page, PyPDFium2Document, PyPDFium2Utils
 