import pandas as pd
import time

a = 1
b = 2



print(a + b)


def ttt():
    try:
        c = a + b
        return c
    except Exception as e:
        print(e)
    finally:
        time.sleep(2)
        print(a - b)
