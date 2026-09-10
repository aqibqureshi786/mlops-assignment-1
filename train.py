from sklearn.linear_model import LinearRegression
import joblib
import numpy as np


def train_model() -> None:
    """
    Train a very simple regression model.
    The model learns this relationship:
    input value -> prediction = value * 2
    """

    X = np.array([[1], [2], [3], [4], [5], [10]], dtype=float)
    y = np.array([2, 4, 6, 8, 10, 20], dtype=float)

    model = LinearRegression()
    model.fit(X, y)

    joblib.dump(model, "model.joblib")
    print("Model trained and saved as model.joblib")


if __name__ == "__main__":
    train_model()