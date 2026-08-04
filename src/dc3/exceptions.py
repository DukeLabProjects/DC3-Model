"""Exceptions raised by DC3 Model."""


class DC3Error(Exception):
    """Base class for all package-specific errors."""


class DC3InputError(DC3Error, ValueError):
    """Raised when a single DC3 input value cannot be interpreted."""


class DC3ValidationError(DC3Error):
    """Raised when a dataset cannot be validated or processed."""
