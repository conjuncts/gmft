has_warned = False


def _deprecation_warning(name):
    global has_warned
    if has_warned:
        return
    import warnings

    msg = (
        f"(Deprecation) Importing {name} et al. from the top level module is deprecated. \
Refer to the import guide, or import from gmft.auto."  # TODO: add documentation link
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    print(msg)
    has_warned = True


class DeprecationMirrorMeta(type):
    """
    A metaclass that wraps a class to issue a deprecation warning when instantiated.

    It mirrors a class (which needs to provided as a classmethod `get_mirrored_class`).

    Though the power of magic, the class and wrapped class will be nearly equivalent.
    `isinstance()` is modified so that the original class and wrapped class are interchangeable.
    """

    def __init__(cls, name, bases, dct):
        # Call the classmethod to get the real class
        # cls._orig_cls = cls.get_mirrored_class()
        super().__init__(name, bases, dct)

    def __call__(cls, *args, **kwargs):
        # Issue warning once per instantiation
        _deprecation_warning(cls.__name__)
        instance = cls.get_mirrored_class()(*args, **kwargs)
        # instance.__class__ = cls  # Make it look like the wrapper
        return instance

    def __instancecheck__(cls, instance):
        """
        Allow isinstance checks to work with the original class OR the wrapped class.
        """
        return isinstance(instance, cls.get_mirrored_class()) or isinstance(
            instance, cls
        )
