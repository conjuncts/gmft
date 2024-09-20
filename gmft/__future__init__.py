"""
Currently, contains aliases for key classes and functions.

Unfortunately, although at one point the ability to import classes from the top level module was encouraged, 
it is now discouraged and may be removed in future versions. 

The reason is importing through the top level module means that the whole library must be loaded whenever using
even a small part of it, which leads to bloat. 

In lieu, `gmft.auto` is now encouraged.

See https://stackoverflow.com/q/64979364/6844235
"""


from gmft.auto import Rect as RectOrig, \
BasePDFDocument as BasePDFDocumentOrig, \
BasePage as BasePageOrig, \
CroppedTable as CroppedTableOrig, \
RotatedCroppedTable as RotatedCroppedTableOrig, \
TATRDetector as TATRTableDetectorOrig, \
TableDetectorConfig as TableDetectorConfigOrig, \
TableDetector as TableDetectorOrig, \
FormattedTable as FormattedTableOrig, \
TATRFormatConfig as TATRFormatConfigOrig, \
TATRFormattedTable as TATRFormattedTableOrig, \
TATRFormatter as TATRTableFormatterOrig, \
AutoTableFormatter as AutoTableFormatterOrig, \
AutoFormatConfig as AutoFormatConfigOrig, \
AutoTableDetector as AutoTableDetectorOrig

def _deprecation_warning(name):
    import warnings
    warnings.warn(f"DeprecationWarning: Importing {name} (and other classes) from the top level module is deprecated. Please import from gmft.auto instead.", DeprecationWarning, stacklevel=2)
    print(f"DeprecationWarning: Importing {name} (and other classes) from the top level module is deprecated. Please import from gmft.auto instead.")

class Rect(RectOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("Rect")
        super().__init__(**kwargs)

class BasePDFDocument(BasePDFDocumentOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("BasePDFDocument")
        super().__init__(**kwargs)

class BasePage(BasePageOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("BasePage")
        super().__init__(**kwargs)

class CroppedTable(CroppedTableOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("CroppedTable")
        super().__init__(**kwargs)

class RotatedCroppedTable(RotatedCroppedTableOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("RotatedCroppedTable")
        super().__init__(**kwargs)

class TATRTableDetector(TATRTableDetectorOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("TATRTableDetector")
        super().__init__(**kwargs)

class TableDetectorConfig(TableDetectorConfigOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("TableDetectorConfig")
        super().__init__(**kwargs)

class TableDetector(TableDetectorOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("TableDetector")
        super().__init__(**kwargs)

class FormattedTable(FormattedTableOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("FormattedTable")
        super().__init__(**kwargs)

class TATRFormatConfig(TATRFormatConfigOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("TATRFormatConfig")
        super().__init__(**kwargs)

class TATRFormattedTable(TATRFormattedTableOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("TATRFormattedTable")
        super().__init__(**kwargs)

class TATRTableFormatter(TATRTableFormatterOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("TATRTableFormatter")
        super().__init__(**kwargs)
        

class AutoTableFormatter(AutoTableFormatterOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("AutoTableFormatter")
        super().__init__(**kwargs)

class AutoFormatConfig(AutoFormatConfigOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("AutoFormatConfig")
        super().__init__(**kwargs)

class AutoTableDetector(AutoTableDetectorOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """
    
    def __init__(self, **kwargs):
        _deprecation_warning("AutoTableDetector")
        super().__init__(**kwargs)

# class LazyLoader:
#     """A class to handle lazy loading of modules."""
    
#     def __init__(self, module_name):
#         self.module_name = module_name
#         self.module = None

#     def _load(self):
#         if self.module is None:
#             import importlib
#             self.module = importlib.import_module(self.module_name)
#         return self.module

#     def __getattr__(self, name):
#         return getattr(self._load(), name)

# # Create lazy loaders for the necessary modules
# gmft_common = LazyLoader('gmft.common')
# gmft_pdf_bindings = LazyLoader('gmft.pdf_bindings')
# gmft_detectors_common = LazyLoader('gmft.detectors.common')
# gmft_detectors_tatr = LazyLoader('gmft.detectors.tatr')
# gmft_formatters_common = LazyLoader('gmft.formatters.common')
# gmft_formatters_tatr = LazyLoader('gmft.formatters.tatr')

# gmft_aliases = LazyLoader('gmft.auto')

# def _callback():
#     import warnings
#     warnings.warn("Sorry, importing classes from the top level (gmft) is now discouraged and may be removed in future versions. Please import classes from gmft.auto instead. Apologies for the inconvenience", DeprecationWarning)
# class AccessTracker:
#     def __init__(self, get_true_value):
#         self.callback = _callback
#         self._value = None 
#         self._get_value = get_true_value

#     def __get__(self, instance, owner):
#         # Call the callback when accessed
#         if self.callback:
#             self.callback()
#         if self._value is None:
#             self._value = self._get_value()
#         return self._value

#     def __set__(self, instance, value):
#         self._value = value

# # Alias classes and functions using lazy loaders
# class LazyHouse:
#     Rect = AccessTracker(lambda: gmft_common.Rect)
#     BasePDFDocument = AccessTracker(lambda: gmft_pdf_bindings.BasePDFDocument)
#     BasePage = AccessTracker(lambda: gmft_pdf_bindings.BasePage)
#     CroppedTable = AccessTracker(lambda: gmft_detectors_common.CroppedTable)
#     RotatedCroppedTable = AccessTracker(lambda: gmft_detectors_common.RotatedCroppedTable)
#     TATRTableDetector = AccessTracker(lambda: gmft_detectors_tatr.TATRTableDetector)
#     TableDetectorConfig = AccessTracker(lambda: gmft_detectors_tatr.TableDetectorConfig)
#     TableDetector = AccessTracker(lambda: gmft_detectors_tatr.TableDetector)
#     FormattedTable = AccessTracker(lambda: gmft_formatters_common.FormattedTable)
#     TATRFormatConfig = AccessTracker(lambda: gmft_formatters_tatr.TATRFormatConfig)
#     TATRFormattedTable = AccessTracker(lambda: gmft_formatters_tatr.TATRFormattedTable)
#     TATRTableFormatter = AccessTracker(lambda: gmft_formatters_tatr.TATRTableFormatter)

# Rect = LazyHouse.Rect
# BasePDFDocument = LazyHouse.BasePDFDocument
# BasePage = LazyHouse.BasePage
# CroppedTable = LazyHouse.CroppedTable
# RotatedCroppedTable = LazyHouse.RotatedCroppedTable
# TATRTableDetector = LazyHouse.TATRTableDetector
# TableDetectorConfig = LazyHouse.TableDetectorConfig
# TableDetector = LazyHouse.TableDetector
# FormattedTable = LazyHouse.FormattedTable
# TATRFormatConfig = LazyHouse.TATRFormatConfig
# TATRFormattedTable = LazyHouse.TATRFormattedTable
# TATRTableFormatter = LazyHouse.TATRTableFormatter


# AutoTableFormatter = AccessTracker(lambda x: gmft_aliases.AutoTableFormatter)
# AutoFormatConfig = AccessTracker(lambda x: gmft_aliases.AutoFormatConfig)
# AutoTableDetector = AccessTracker(lambda x: gmft_aliases.AutoTableDetector)