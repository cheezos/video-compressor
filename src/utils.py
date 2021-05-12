from datetime import datetime


def log(msg) -> str:
    print('PVC: ' + str(msg))
    return msg


def pretty_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


def raw_time() -> float:
    return datetime.now()
