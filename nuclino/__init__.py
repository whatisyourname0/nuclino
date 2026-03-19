from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .api import Nuclino

__all__ = ['Nuclino', 'NuclinoAPI']


def __getattr__(name: str) -> Any:
    if name in {'Nuclino', 'NuclinoAPI'}:
        from .api import Nuclino

        return Nuclino
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
