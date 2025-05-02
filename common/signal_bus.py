# coding: utf-8
from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    """Signal bus"""

    switchToSampleCard = Signal(str, int)
    micaEnableChanged = Signal(bool)
    supportSignal = Signal()
    editor_interface_generate_finished_signal = Signal(str)


signalBus = SignalBus()
