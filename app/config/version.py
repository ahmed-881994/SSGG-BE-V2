"""Application version management."""
import os
from pathlib import Path

VERSION_FILE = Path(__file__).parent.parent.parent / "VERSION"
def get_version() -> str:
    """
    Get the application version from VERSION file or fallback to environment variable.
    
    Priority:
    1. VERSION file in repository root
    2. APP_VERSION environment variable
    3. Fallback to '0.0.0-dev'
    
    Returns:
        str: Version string (e.g., '2.1.0')
    """
    try:
        if VERSION_FILE.exists():
            version = VERSION_FILE.read_text().strip()
            if version:
                return version
    except Exception:
        pass
    
    # Fallback to environment variable
    version = os.environ.get('APP_VERSION', '0.0.0-dev')
    return version

__version__ = get_version()