class Unset:
    """Sentinel type distinguishing an omitted field from an explicit null."""

    __slots__ = ()


UNSET = Unset()
