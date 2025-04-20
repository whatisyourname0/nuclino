from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    pass

class NuclinoObject:
    """Base class for all Nuclino objects"""
    _object: str = ''

    @classmethod
    def load(cls, props: dict, nuclino) -> NuclinoObject:
        return cls(props, nuclino)

    def __init__(
        self,
        props: dict,
        nuclino
    ):
        self._data = dict(props)
        self._nuclino = nuclino

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Safely get a value from the internal data dictionary.
        
        :param key: The key to look up
        :param default: The value to return if key is not found
        :returns: The value associated with the key, or default if not found
        """
        return self._data.get(key, default)

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._data}>"


def get_loader(name: str) -> Callable:
    """Get the appropriate loader function for a given object type"""
    from . import file, item, team, user, workspace
    
    classes = {
        'list': lambda props, nuclino: props.get('results', []),
        'user': user.User.load,
        'team': team.Team.load,
        'workspace': workspace.Workspace.load,
        'item': item.Item.load,
        'collection': item.Collection.load,
        'file': file.File.load,
    }
    return classes[name] 