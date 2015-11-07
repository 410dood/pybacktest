from pybacktest.blocks import Entry
from pybacktest.blotter import Blotter
from pybacktest.plot import Plotter


class Performance(object):
    def __init__(self, blotter):
        self.blotter = blotter

    @property
    def equity(self):
        return (self.blotter.continuous_returns + 1).cumprod()

    @property
    def trade_equity(self):
        return (self.blotter.trade_returns + 1).cumprod()


class BacktestError(Exception):
    pass


class Backtest(object):
    def __init__(self, spec):
        self.spec = spec

        if not isinstance(spec, Entry):
            if isinstance(spec, (list, tuple)):
                raise NotImplementedError('Backtest with multiple entries is not supported yet')
            else:
                raise ValueError('Incorrect spec (should be Entry)')

        self.blotter = Blotter(spec)
        self.performance = Performance(self.blotter)
        self.plotter = Plotter(self.blotter)
