import numpy
import pandas
import performance_statistics

class TradeError(Exception):
    pass

class EquityCalculator(object):
    ''' Calculates EquityCurve from trades and price changes '''

    def __init__(self, full_curve=None, trades_curve=None):
        self.full_curve = full_curve or EquityCurve()
        self.trades_curve = trades_curve or EquityCurve()
        self.pos = 0
        self.var = 0

    def new_price(self, timestamp, price):
        self.full_curve.add_point(timestamp, self.var + self.pos * price)

    def new_trade(self, timestamp, price, volume, direction):
        if timestamp < self.full_curve._times[-1]:
            raise TradeError('Attempting to make trade in the past')
        if direction == 'sell':
            volume *= -1
        self.var -= price * volume
        self.pos += volume
        equity = self.var + self.pos * price
        self.trades_curve.add_point(timestamp, equity)
        self.trades_curve.add_trade((timestamp, price, volume))


class EquityCurve(object):
    ''' Keeps history of equity changes and calculates various performance
        statistics. Optional: keeps track of trades. '''

    def __init__(self):
        self._changes = []
        self._times = []
        self._cumsum = 0
        self.trades = []

    def add_change(self, timestamp, equity_change):
        self._changes.append(equity_change)
        self._cumsum += equity_change
        self._times.append(timestamp)

    def add_point(self, timestamp, equity):
        self._changes.append(equity - self._cumsum)
        self._cumsum = equity
        self._times.append(timestamp)

    def add_trade(self, trade):
        ''' Add trade. Not used in any computation currently. '''
        self.trades.append(trade)

    @property
    def series(self):
        ''' Pandas TimeSeries object of equity '''
        return pandas.TimeSeries(data=numpy.cumsum(self._changes),
          index=self._times)

    def __getitem__(self, stat):
        ''' Calculate statistic `stat` on equity dynamics '''
        if len(self._changes) == 0:
            raise Exception('Cannot calculate statistics on empty EquityCurve')
        s = stat.lower()
        func = getattr(performance_statistics, stat.lower(), None)
        if func:
            return func(numpy.array(self._changes))
        else:
            raise KeyError('Cannot calculate statistic with name `%s`', stat)

    def statistics(self, mode='full'):
        ''' Calculate all possible statistics, as specified in
            `performance_statistics` '''
        if mode == 'full':
            return dict((k, self[k]) for k in performance_statistics.full)
        else:
            raise Exception('Unsupported `mode` of statistics request')
