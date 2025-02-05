from .Ozon import Ozon
from .Ymarket import Ymarket
from .WB import WB

ozon = Ozon()
ymarket = Ymarket()
wb = WB()

__all__ = [ozon, ymarket, wb]