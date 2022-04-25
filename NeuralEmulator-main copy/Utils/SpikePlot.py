import numpy as np
import math
import matplotlib.pyplot as plt

lower = 0.000001

def f(t):
    global lower
    return 0.2*(math.log(t,2) - math.log(lower,2))

upper = 30.0
incre = (upper-lower)/30.0

t1 = np.arange(lower, upper, incre)
y = [f(x) for x in t1]

plt.plot(t1, y, 'bo')
plt.show()
