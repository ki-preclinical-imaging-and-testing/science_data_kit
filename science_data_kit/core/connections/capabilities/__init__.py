"""
Capability mixins for Science Data Kit connections.

This module provides mixins that define specific capabilities that connection plugins
can implement, such as browsing, searching, querying, streaming, and versioning.
"""

from .browsable import Browsable
from .queryable import Queryable
from .searchable import Searchable
from .streamable import Streamable
from .versionable import Versionable

__all__ = [
    "Browsable",
    "Queryable",
    "Searchable",
    "Streamable",
    "Versionable",
]