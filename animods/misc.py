# pylint: disable:F0001
class c:
    black = '\033[30m'
    red = '\033[31m'
    green = '\033[32m'
    yellow = '\033[33m'
    orange = '\033[34m'
    purple = '\033[35m'
    blue = '\033[36m'
    white = '\033[37m'
    b_test = '\033[164m'
    b_black = '\033[90m'
    b_red = '\033[91m'
    b_green = '\033[92m'
    b_yellow = '\033[93m'
    b_orange = '\033[94m'
    b_purple = '\033[95m'
    b_blue = '\033[96m'
    b_white = '\033[97m'
    bold = '\033[1m'
    faint = '\033[2m'
    italic = '\033[3m'
    underline = '\033[4m'
    o = '\033[0m'


def print_progress_bar(iteration, total, prefix='Progress:', suffix='Complete ', decimals=1, length=25, fill='█', unfill='–', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + unfill * (length - filledLength)
    # Progress bar printing
    print(f'\r{prefix} │{bar}│ {percent}% {suffix}', end=printEnd)

__all__ = ["c","print_progress_bar"]