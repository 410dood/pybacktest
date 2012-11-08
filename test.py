#!/usr/bin/env python

try:
    import pyaux
    pyaux.use_exc_ipdb()
    pyaux.use_exc_log()
except:
    pass

import datetime
import matplotlib.pyplot as plt
import IPython
import logging

logging.basicConfig(log_level=logging.DEBUG)

from backtest.testers import SimpleBacktester
from examples.ma_strategy import MACrossoverStrategy as strategy
from datatypes.processing import read_bars

bars = read_bars('examples/testdata/RIZ1.csv')

bt = SimpleBacktester(bars, strategy)

try:
    import pprint
    pprint.pprint(bt.trades_curve.statistics())
except:
    print bt.trades_curve.statistics()

cc = bt.trades_curve

IPython.embed(banner1='trades equity curve stored in `cc`. `cc.series().plot(); plt.show()` to plot equity')
