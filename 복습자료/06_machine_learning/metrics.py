
###### 평가 모듈 -> 다양한 평가지표들을 계산/출력하는 함수들가지는 모듈
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, recall_score, precision_score, f1_score, accuracy_score

__version__ = 1.0

def plot_confusion_matrix(y, pred, title=None):
    """Confusion matrix 시각화 함수
    Args:
        y: ndarray - 정답
        pred: ndarray - 모델 추정결과
        title: str - 출력할 제목. default=None
    Returns:
    Raises:
    """
    cm = confusion_matrix(y, pred)
    disp = ConfusionMatrixDisplay(cm)
    disp.plot(cmap="Blues")
    if title:
        plt.title(title)
    plt.show()

def print_binary_classification_metrics(y, pred, title=None):
    """정확도, 재현율, 정밀도, f1 점수를 계산해서 출력하는 함수
    Args
        y: ndarray - 정답
        pred: ndarray - 모델 추정결과
        title: str - 결과에 대한 제목 default=None
    Returns
    Raises
    """
    if title:
        print(title)
    print("정확도:", accuracy_score(y, pred))
    print("재현율:", recall_score(y, pred))
    print("정밀도:", precision_score(y, pred))
    print("F1 점수:", f1_score(y, pred))
