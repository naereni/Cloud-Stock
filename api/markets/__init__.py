from .Ozon import Ozon
from .WB import WB
from .Ymarket import Ymarket

ozon = Ozon()
ymarket = Ymarket()
wb = WB()

__all__ = [ozon, ymarket, wb]
