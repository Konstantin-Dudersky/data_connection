from typing import Generic
from typing_extensions import Self

from .signals import SignalType, Signal
from .channel import ChannelItem


class DatapointSignal(Generic[SignalType]):
    sig: Signal[SignalType]
    __channels: list[ChannelItem[SignalType]] | None

    def __init__(
        self: Self,
        default: SignalType,
        channels: list[ChannelItem[SignalType]] | None = None,
    ) -> None:
        self.sig = Signal[SignalType](default=default)
        self.__channels = channels
        if channels is not None:
            for ch in channels:
                ch.set_signal_link(self.sig)
