import pandas


class SignalError(Exception):
    pass


def dummy_signals_to_positions(signals):
    return signals


def type1_signals_to_positions(signals):
    long_entry = signals.get('long_entry')
    short_entry = signals.get('short_entry')
    long_exit = signals.get('long_exit')
    short_exit = signals.get('short_exit')

    assert long_entry is not None or short_entry is not None
    if long_entry is not None and short_entry is not None:
        assert long_entry.index.equals(short_entry.index)
    if long_entry is not None and long_entry.dtype != bool:
        raise SignalError("long_entry dtype != bool (use X.astype('bool')")
    if short_entry is not None and short_entry.dtype != bool:
        raise SignalError("short_entry dtype != bool (use X.astype('bool')")
    if long_exit is not None:
        assert long_exit.index.equals(long_entry.index)
        if long_exit.dtype != bool:
            raise SignalError("long_exit dtype != bool (use X.astype('bool')")
    if short_exit is not None:
        assert short_exit.index.equals(short_entry.index)
        if short_exit.dtype != bool:
            raise SignalError("short_exit dtype != bool (use X.astype('bool')")

    p = None
    if long_entry is not None:
        l = pandas.Series(index=long_entry.index, dtype='float')
        l.ix[long_entry] = 1.0
        if long_exit is not None:
            l.ix[long_exit] = 0.0
        if short_entry is not None:
            l.ix[short_entry] = 0.0
        p = l.ffill()
    if short_entry is not None:
        s = pandas.Series(index=long_entry.index, dtype='float')
        s.ix[short_entry] = -1.0
        if short_exit is not None:
            s.ix[short_exit] = 0.0
        if long_entry is not None:
            s.ix[long_entry] = 0.0

        if p is None:
            p = s.ffill()
        else:
            p = p + s.ffill()
    p = p.fillna(value=0.0)
    return p


def type2_signals_to_positions(signals):
    long_pos = signals.get('long')
    short_pos = signals.get('short')
    assert long_pos is not None or short_pos is not None
    p = None
    if long_pos is not None:
        assert long_pos.dtype == bool
        l = pandas.Series(index=long_pos.index, dtype='float')
        l.ix[long_pos] = 1.0
        p = l.fillna(value=0.0)
    if short_pos is not None:
        assert short_pos.dtype == bool
        s = pandas.Series(index=long_pos.index, dtype='float')
        s.ix[short_pos] = -1.0
        if p is None:
            p = s
        else:
            p = p + s.fillna(value=0.0)
    p = p.fillna(value=0.0)
    return p


def fast_execute(price, positions):
    """ Fast vectorized execute.

        Works with standard position/fixed-price market order entries,
        but not with conditional trades like stops or limit orders.
    """

    # find trade end points
    long_close = (positions <= 0) & (positions > 0).shift()
    short_close = (positions >= 0) & (positions < 0).shift()
    crosspoint = long_close | short_close
    crosspoint[0] = True
    crosspoint[1] = True

    # efficient way to calculate equity curve
    strategy_returns = (price.pct_change() * positions.shift())

    trade_returns = (strategy_returns + 1).cumprod()[crosspoint].pct_change().dropna()

    result = pandas.DataFrame()
    result['equity'] = strategy_returns.fillna(value=0)
    result['trade_equity'] = trade_returns
    result['long_equity'] = trade_returns[long_close]
    result['short_equity'] = trade_returns[short_close]
    result['positions'] = positions
    result['crosspoint'] = crosspoint.astype(int)
    return result
