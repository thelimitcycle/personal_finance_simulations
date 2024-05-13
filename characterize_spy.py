import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def spy_log_returns():
    spy = pd.read_csv('SPY.csv')
    spy['pct_change'] =spy.Close.pct_change()
    spy['log_ret'] = np.log(spy.Close) - np.log(spy.Close.shift(1))
    log_ret = spy['log_ret'].dropna().to_numpy()

    return log_ret
