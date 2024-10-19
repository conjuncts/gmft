"""
Sadly, dataclasses do not allow a distinction between set and unset values. That is, there is no way
to distinguish between an unset value and a user-set value that happens to coincide with the default value.

See: https://github.com/pydantic/pydantic/discussions/5716
https://stackoverflow.com/q/56430869/6844235
"""

from dataclasses import fields, replace
import dataclasses
from typing import TypeVar, Union

DataClass = TypeVar('DataClass')


def with_config(config: DataClass, config_overrides: Union[DataClass, dict, None]) -> DataClass:
    """
    Merges an existing config with possible overrides.

    New behavior in v0.3: 
    If `config_overrides` is provided, it completely replaces everything in `config`. For instance, if a value is
    set in `config` but left unassigned in `config_overrides`, the resultant object will **revert** to
    the default value.

    In versions <0.3, assigned values in `config_overrides` would have been merged into `config`. 
    In the above example, the resultant object would have previously contained the value from `config`. 
    To retain this old behavior, a dict can be passed.
    """

    if config_overrides is None:
        return config

    if isinstance(config_overrides, dict):
        # only update if it's a dict
        return replace(config, **config_overrides)
    else:
        # override everything
        return config_overrides

def non_defaults_only(config: object) -> dict:
    """
    Returns a dictionary of only the attributes that differ from the default values.
    """
    # return {k: v for k, v in config.__dict__.items() if v != getattr(config.__class__, k)}
    result = {}
    for f in fields(config):
        current_value = getattr(config, f.name)
        if f.default_factory != dataclasses.MISSING:
            default_value = f.default_factory()
        else:
            default_value = f.default
        if default_value != current_value:
            result[f.name] = current_value
    return result

import warnings

def removed_property(name, message=None):
    """
    Custom decorator for marking class properties as removed.
    Automatically raises a DeprecationWarning when the property is accessed or set.
    """
    if message is None:
        message = "{name} has been removed."
    msg = message.format(name=name)
    def getter(self):
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        raise DeprecationWarning(msg)
    
    def setter(self, value):
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        raise DeprecationWarning(msg)
    
    return property(getter, setter)