
"""
Sadly, dataclasses do not allow a distinction between set and unset values. That is, there is no way
to distinguish between an unset value and a user-set value that happens to coincide with the default value.

The main feature of dataclasses is the automatic generation of __init__ and __repr__ methods
See: https://github.com/pydantic/pydantic/discussions/5716
"""

import typing_extensions


@typing_extensions.dataclass_transform()
def auto_init(cls):
    # Get class attributes (i.e., the fields with default values)
    # attrs = {k: v for k, v in cls.__dict__.items() if not k.startswith('__') and not callable(v)}
    # attrs
    
    # Define a custom __init__ method that assigns arguments to instance variables
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # Use kwargs for user-provided values, fallback to the default class attribute
            # if key in attrs:
            setattr(self, key, kwargs[key])
    
    # Replace the class's __init__ with the dynamically created one
    cls.__init__ = __init__
    return cls