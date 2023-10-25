#!/usr/bin/env python3
"""General utils for use throughout the package."""
import copy
from collections import defaultdict
from typing import Any, Callable, Mapping, Union


def get_empty_nested_defaultdict():
    """Return an empty nested (recursive) defaultdict object."""
    return defaultdict(get_empty_nested_defaultdict)


def modify_mappings(obj: Mapping, operator: Union[Mapping, Callable[[Mapping], Any]]):
    """Descend recursively into `obj` and modify encountered mappings using `operator`."""
    if not isinstance(obj, Mapping):
        raise TypeError("`obj` must be a Mapping (`dict`-like object).")

    if callable(operator):
        return _modify_mappings_via_callable(obj=obj, operator=operator)

    if isinstance(operator, Mapping):
        return _update_mapping(obj=obj, updates=operator)

    raise TypeError("`operator` must either be callable or implement an `items` method.")


def _modify_mappings_via_callable(obj, operator: Callable[[Mapping], Any]):
    """Descend recursively into `obj` and modify encountered mappings using `operator`."""
    if not isinstance(obj, Mapping):
        try:
            return copy.deepcopy(obj)
        except TypeError:
            return obj
    return operator(
        {k: _modify_mappings_via_callable(v, operator=operator) for k, v in obj.items()}
    )


def _update_mapping(obj, updates: Mapping):
    """Descend recursively into `obj` and update nested mappings using `updates`."""
    new_obj = copy.deepcopy(obj)

    if not isinstance(new_obj, Mapping):
        return new_obj

    for key, updated_value in updates.items():
        if isinstance(updated_value, Mapping):
            new_obj[key] = _update_mapping(new_obj.get(key, {}), updated_value)
        else:
            new_obj[key] = updated_value
    return new_obj
