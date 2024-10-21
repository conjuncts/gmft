"""
Sadly, dataclasses do not allow a distinction between set and unset values. That is, there is no way
to distinguish between an unset value and a user-set value that happens to coincide with the default value.

See: https://github.com/pydantic/pydantic/discussions/5716
https://stackoverflow.com/q/56430869/6844235
"""

from dataclasses import fields, replace
import dataclasses
import functools
import inspect
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

string_types = (type(b''), type(u''))

def removed_property(reason):
    """
    Custom decorator for marking class properties as removed.
    Automatically raises a DeprecationWarning when the property is accessed or set.
    
    See https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
    """
    if isinstance(reason, string_types):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(
                    fmt1.format(name=func1.__name__, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2
                )
                warnings.simplefilter('default', DeprecationWarning)
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(
                fmt2.format(name=func2.__name__),
                category=DeprecationWarning,
                stacklevel=2
            )
            warnings.simplefilter('default', DeprecationWarning)
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))