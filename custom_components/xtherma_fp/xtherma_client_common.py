"""Common definitions for Xtherma client variants."""

from abc import abstractmethod
from collections.abc import Callable
from datetime import timedelta

from homeassistant.helpers.entity import EntityDescription

Factor = Callable[[int], float | int]
_FACTORS: dict[str, Callable] = {
    "*1000": lambda value: value * 1000,
    "*100": lambda value: value * 100,
    "*10": lambda value: value * 10,
    "1000": lambda value: value * 1000,
    "100": lambda value: value * 100,
    "10": lambda value: value * 10,
    "/1000": lambda value: value / 1000,
    "/100": lambda value: value / 100,
    "/10": lambda value: value / 10,
}

_RFACTORS: dict[str, Callable] = {
    "*1000": lambda value: value / 1000,
    "*100": lambda value: value / 100,
    "*10": lambda value: value / 10,
    "1000": lambda value: value / 1000,
    "100": lambda value: value / 100,
    "10": lambda value: value / 10,
    "/1000": lambda value: value * 1000,
    "/100": lambda value: value * 100,
    "/10": lambda value: value * 10,
}


class XthermaModbusBusyError(Exception):
    """Exception indicating busy on Modbus read or write."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("Modbus is busy")


class XthermaRestBusyError(Exception):
    """Exception indicating busy on REST API read."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("REST API is busy")


class XthermaError(Exception):
    """Exception indicating a unspecified error."""

    def __init__(self, msg: str = "General error") -> None:
        """Class constructor."""
        super().__init__(msg)


class XthermaNotConnectedError(Exception):
    """Exception indicating the client is not connected."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("Not connected error")


class XthermaRestApiError(Exception):
    """Exception indicating a REST API error."""

    def __init__(self, code: int) -> None:
        """Class constructor."""
        super().__init__()
        self.code = code


class XthermaModbusError(Exception):
    """Exception indicating a Modbus error."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__()


class XthermaModbusEmptyDataError(Exception):
    """Exception empty data was received via Modbus."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__()


class XthermaReadOnlyError(Exception):
    """Exception indicating a data is read-only."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__()


class XthermaTimeoutError(Exception):
    """Exception indicating a communication timeout."""

    def __init__(self) -> None:
        """Class constructor."""
        super().__init__("timeout")


class XthermaClient:
    """Base class for Xtherma clients."""

    @abstractmethod
    def update_interval(self) -> timedelta:
        """Return update interval for data coordinator."""
        raise NotImplementedError

    @abstractmethod
    async def connect(self) -> None:
        """Connect client to server endpoint."""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect client."""
        raise NotImplementedError

    @abstractmethod
    async def async_get_data(self) -> dict[str, int | float]:
        """Obtain fresh data."""
        raise NotImplementedError

    @abstractmethod
    async def async_put_data(self, value: int | float, desc: EntityDescription) -> None:
        """Write data."""
        raise NotImplementedError

    @abstractmethod
    def get_entity_descriptions(self) -> list[EntityDescription]:
        """Get all entity descriptions."""
        raise NotImplementedError

    def _apply_input_factor(self, value: int, inputfactor: str | None) -> int | float:
        if not inputfactor:
            return value
        function = _FACTORS.get(inputfactor, lambda v: v)
        return function(value)

    def _reverse_apply_input_factor(self, value: float, inputfactor: str | None) -> int:
        if not isinstance(inputfactor, str):
            return int(value)
        function = _RFACTORS.get(inputfactor, lambda v: v)
        return function(value)
