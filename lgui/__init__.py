"""
Root-level lgui objects.
These can be imported directly from lgui.
"""

from .editor import NotebookEditor
import pkg_resources

__version__ = pkg_resources.require('lcapy')[0].version
