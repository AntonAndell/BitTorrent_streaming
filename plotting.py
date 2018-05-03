import numpy as np
import matplotlib.pyplot as plt
filename = "tes"

data1 = np.genfromtxt('test.txt', delimiter=',')[:-1]
data2 = np.genfromtxt('tes.txt', delimiter=',')[:-1]


x1 = data1[0::2]
y1 = data1[1::2]

x2 = data2[0::2]
y2 = data2[1::2]

plt.ylabel('Sequentially downloaded pieces')
plt.xlabel('Total downloaded pieces')


plt.subplot(2, 1, 1)
plt.gca().set_title('Zipf')
plt.plot(x1, y1)

plt.subplot(2, 1, 2)
plt.gca().set_title('Sequential')
plt.plot(x2, y2)

plt.savefig("plot.png")
plt.show()
