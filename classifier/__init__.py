"""
ScopeSignal Classification Engine
Conservative classifier for NYC construction project updates.
"""

from .agent import ScopeSignalClassifier, classify_update, ClassificationError
from .cache import ResultCache
from .export import export_to_csv, export_to_json, export_summary_report
from .__version__ import __version__, __author__, __license__, __description__

__all__ = [
    "ScopeSignalClassifier", 
    "classify_update", 
    "ClassificationError",
    "ResultCache",
    "export_to_csv",
    "export_to_json",
    "export_summary_report",
    "__version__",
]
