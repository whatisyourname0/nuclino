from __future__ import annotations

from collections.abc import ItemsView, Iterable, Iterator, KeysView, Mapping, ValuesView
from copy import deepcopy
from typing import Any, Callable, Protocol, TypeVar, Union, cast

T = TypeVar('T', bound='NuclinoObject')
ListItem = TypeVar('ListItem')


class NuclinoClient(Protocol):
    """Subset of the client interface used by model helper methods."""

    def get_item(self, item_id: str) -> Any: ...
    def get_file(self, file_id: str) -> Any: ...
    def get_team(self, team_id: str) -> Any: ...
    def get_workspace(self, workspace_id: str) -> Any: ...
    def get_workspaces(
        self,
        team_id: str | None = None,
        limit: int | None = None,
        after: str | None = None,
    ) -> Any: ...
    def create_item(self, **kwargs: Any) -> Any: ...
    def update_item(
        self,
        item_id: str,
        title: str | None = None,
        content: str | None = None,
    ) -> Any: ...
    def delete_item(self, item_id: str) -> Any: ...


class NuclinoList(list[ListItem]):
    """List-like wrapper that preserves response metadata."""

    def __init__(
        self,
        items: Iterable[ListItem],
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(items)
        self.metadata: dict[str, Any] = deepcopy(dict(metadata or {}))

    def to_dict(self) -> dict[str, Any]:
        return {
            'object': 'list',
            'results': [
                item.to_dict() if isinstance(item, NuclinoObject) else deepcopy(cast(Any, item))
                for item in self
            ],
            **deepcopy(self.metadata),
        }


LoaderResult = Union[T, NuclinoList[Any], dict[str, Any]]
LoaderCallable = Callable[[Mapping[str, Any], NuclinoClient], LoaderResult]


def _camel_to_snake(name: str) -> str:
    parts: list[str] = []
    for char in name:
        if char.isupper():
            parts.append('_')
            parts.append(char.lower())
        else:
            parts.append(char)
    return ''.join(parts).lstrip('_')


def _snake_to_camel(name: str) -> str:
    head, *tail = name.split('_')
    return head + ''.join(part.capitalize() for part in tail)


class NuclinoObject:
    """
    Base class for all Nuclino objects.

    This class provides dictionary-like access to the underlying data while maintaining
    object-oriented interface. It supports both attribute-style and dictionary-style access
    to the data.

    Attributes:
        _data (dict[str, Any]): The underlying data dictionary
        _nuclino (NuclinoClient): The Nuclino client instance
        _object (str): The type of the object (e.g., 'workspace', 'team', etc.)
    """

    _object: str = ''

    @classmethod
    def load(cls: type[T], props: Mapping[str, Any], nuclino: NuclinoClient) -> T:
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
        props: Mapping[str, Any],
        nuclino: NuclinoClient,
    ) -> None:
        """
        Initialize a new Nuclino object.

        Args:
            props: Dictionary of properties for the object
            nuclino: The Nuclino client instance
        """
        self._data: dict[str, Any] = deepcopy(dict(props))
        self._nuclino: NuclinoClient = nuclino

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
            alias = _snake_to_camel(name)
            if alias in self._data:
                return self._data[alias]
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
        aliases = [_camel_to_snake(key) for key in self._data if key != _camel_to_snake(key)]
        return sorted(set([*super().__dir__(), *self._data.keys(), *aliases]))

    def __iter__(self) -> Iterator[str]:
        """Support iteration over data keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Return the number of items in the data dictionary."""
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        """Support 'in' operator for checking key existence."""
        return key in self._data

    def keys(self) -> KeysView[str]:
        """Return a view over the data dictionary's keys."""
        return self._data.keys()

    def values(self) -> ValuesView[Any]:
        """Return a view over the data dictionary's values."""
        return self._data.values()

    def items(self) -> ItemsView[str, Any]:
        """Return a view over the data dictionary's items."""
        return self._data.items()

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the object to a plain dictionary.

        Returns:
            A dictionary containing all the object's data
        """
        return deepcopy(self._data)


def get_loader(name: str) -> LoaderCallable:
    """
    Get the appropriate loader function for a given object type.

    Args:
        name: The type of object to load (e.g., 'workspace', 'team', etc.)

    Returns:
        A callable that can create an instance of the appropriate class
    """
    from . import file, item, team, user, workspace

    classes: dict[str, LoaderCallable] = {
        'list': lambda props, nuclino: NuclinoList(
            props.get('results', []),
            metadata={key: deepcopy(value) for key, value in props.items() if key not in {'object', 'results'}},
        ),
        'user': user.User.load,
        'team': team.Team.load,
        'workspace': workspace.Workspace.load,
        'item': item.Item.load,
        'collection': item.Collection.load,
        'file': file.File.load,
    }
    return classes.get(name, lambda props, nuclino: dict(props))
