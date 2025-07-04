"""
Science Data Kit - Integrations Package

This package provides integration with various external platforms and services,
allowing users to access and analyze data from these sources within the Science Data Kit environment.
"""

from typing import Dict, Any, List

# Dictionary to store available integration providers
INTEGRATION_PROVIDERS: Dict[str, Any] = {}

def register_provider(name: str, provider_class: Any) -> None:
    """
    Register an integration provider.

    Args:
        name: The name of the provider.
        provider_class: The provider class.
    """
    INTEGRATION_PROVIDERS[name] = provider_class

def get_provider(name: str) -> Any:
    """
    Get an integration provider by name.

    Args:
        name: The name of the provider.

    Returns:
        The provider class if found, None otherwise.
    """
    return INTEGRATION_PROVIDERS.get(name)

def list_providers() -> List[str]:
    """
    List all available integration providers.

    Returns:
        A list of provider names.
    """
    return list(INTEGRATION_PROVIDERS.keys())

# Import and register providers
try:
    from .nextsee_provider import NExtSEEKProvider
    register_provider("nextsee", NExtSEEKProvider)
except ImportError:
    pass

try:
    from .fairdom_provider import FAIRDOMProvider
    register_provider("fairdom", FAIRDOMProvider)
except ImportError:
    pass

try:
    from .nc3rs_provider import NC3RsEDAProvider
    register_provider("nc3rs", NC3RsEDAProvider)
except ImportError:
    pass

try:
    from .pubmed_provider import PubMedProvider
    register_provider("pubmed", PubMedProvider)
except ImportError:
    pass

try:
    from .isa_tools_provider import ISAToolsProvider
    register_provider("isa", ISAToolsProvider)
except ImportError:
    pass
