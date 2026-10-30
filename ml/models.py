"""
Định nghĩa kiến trúc các mô hình dự báo.
Tách riêng class BaselinePersistenceModel để tương thích hoàn toàn với pickle/joblib.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.data_processing import FEATURE_COLS

class BaselinePersistenceModel:
    """Mô hình cơ sở dự báo bằng giá trị PM2.5 của bước thời gian trước (t-1)."""
    def __init__(self):
        self.lag_col_idx = FEATURE_COLS.index("pm25_lag_1")

    def fit(self, X, y=None):
        return self

    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            return X["pm25_lag_1"].values
        elif isinstance(X, np.ndarray):
            return X[:, self.lag_col_idx]
        return np.array(X)[:, self.lag_col_idx]
