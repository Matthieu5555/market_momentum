import pandas as pd
import numpy as np
from market_momentum import calculate_recent_volume_mean, calculate_z_score, calculate_volume_percentile, sort_by_volume_extremity

def test_calculate_recent_volume_mean():
    data = pd.Series([100, 200, 300, 400, 500])
    period_slice = (-3, -1)
    expected_mean = np.mean(data.iloc[-3:-1])
    assert calculate_recent_volume_mean(data, period_slice) == expected_mean, "The calculate_recent_volume_mean function failed."

def test_calculate_z_score():
    data = pd.Series([100, 200, 300, 400, 500])
    recent_volume = 400
    mean = np.mean(data)
    std_dev = np.std(data, ddof=0)  # Using population standard deviation to match the function
    expected_z_score = (recent_volume - mean) / std_dev
    assert calculate_z_score(data, recent_volume) == expected_z_score, "The calculate_z_score function failed."

def test_calculate_volume_percentile():
    data = pd.Series([100, 200, 300, 400, 500])
    recent_volume_mean = 250
    expected_percentile = 40.0  # 40% of values are less than or equal to 250 in the data set.
    calculated_percentile = calculate_volume_percentile(data, recent_volume_mean)
    assert calculated_percentile == expected_percentile, "The calculate_volume_percentile function failed."

def test_sort_by_volume_extremity():
    results = {
        'AAPL': {'Percentile': 10},
        'GOOGL': {'Percentile': 20},
        'MSFT': {'Percentile': 30},
        'AMZN': {'Percentile': 40}
    }
    sorted_results = sort_by_volume_extremity(results, 2)
    assert sorted_results[0][0] == 'AAPL' and sorted_results[1][0] == 'GOOGL', "The sort_by_volume_extremity function failed to correctly sort the tickers by extremity."

