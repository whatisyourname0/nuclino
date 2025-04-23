from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, TypeVar, Union

if TYPE_CHECKING:
    from nuclino.api.client import Client

T = TypeVar('T', bound='NuclinoObject')
LoaderCallable = Callable[[Dict[str, Any], 'Client'], Union[T, list[T], Dict[str, Any]]]

class NuclinoObject:
    """
    Base class for all Nuclino objects.
    
    This class provides dictionary-like access to the underlying data while maintaining
    object-oriented interface. It supports both attribute-style and dictionary-style access
    to the data.

    Attributes:
        _data (Dict[str, Any]): The underlying data dictionary
        _nuclino (Client): The Nuclino client instance
        _object (str): The type of the object (e.g., 'workspace', 'team', etc.)
    """
    _object: str = ''

    @classmethod
    def load(cls: type[T], props: Dict[str, Any], nuclino: Client) -> T:
        """
        Create a new instance from a dictionary of properties.
        
        Args:
            props: Dictionary of properties for the object
            nuclino: The Nuclino client instance
            
        Returns:
            A new instance of the class
        """
        return cls(props, nuclino)

    def __init__(
        self,
        props: Dict[str, Any],
        nuclino: Client
    ) -> None:
        """
        Initialize a new Nuclino object.
        
        Args:
            props: Dictionary of properties for the object
            nuclino: The Nuclino client instance
        """
        self._data: Dict[str, Any] = dict(props)
        self._nuclino: Client = nuclino

    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access to the data."""
        return self._data[key]

    def __getattr__(self, name: str) -> Any:
        """
        Support attribute-style access to the data.
        This will be called only if the attribute is not found through normal lookup.
        """
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Safely get a value from the internal data dictionary.
        
        Args:
            key: The key to look up
            default: The value to return if key is not found
            
        Returns:
            The value associated with the key, or default if not found
        """
        return self._data.get(key, default)

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        """Return a detailed string representation including all data."""
        return f"{self.__class__.__name__}({self._data!r})"

    def __dir__(self) -> list[str]:
        """Support auto-completion of data keys in interactive environments."""
        return super().__dir__() + list(self._data.keys())

    def __iter__(self) -> Iterator[str]:
        """Support iteration over data keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Return the number of items in the data dictionary."""
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        """Support 'in' operator for checking key existence."""
        return key in self._data

    def keys(self) -> Iterator[str]:
        """Return an iterator over the data dictionary's keys."""
        return self._data.keys()

    def values(self) -> Iterator[Any]:
        """Return an iterator over the data dictionary's values."""
        return self._data.values()

    def items(self) -> Iterator[tuple[str, Any]]:
        """Return an iterator over the data dictionary's items."""
        return self._data.items()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the object to a plain dictionary.
        
        Returns:
            A dictionary containing all the object's data
        """
        return dict(self._data)


def get_loader(name: str) -> LoaderCallable:
    """
    Get the appropriate loader function for a given object type.
    
    Args:
        name: The type of object to load (e.g., 'workspace', 'team', etc.)
        
    Returns:
        A callable that can create an instance of the appropriate class
    """
    from . import file, item, team, user, workspace
    
    classes: Dict[str, LoaderCallable] = {
        'list': lambda props, nuclino: props.get('results', []),
        'user': user.User.load,
        'team': team.Team.load,
        'workspace': workspace.Workspace.load,
        'item': item.Item.load,
        'collection': item.Collection.load,
        'file': file.File.load,
    }
    return classes[name] 