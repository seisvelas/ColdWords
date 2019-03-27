import matplotlib.pyplot as plt
import seaborn as sns; sns.set() # for prettiness

values = []
def f(x):
    values.append(0 if x % 3 == 0 else x)
    return len(set(values)) / len(values)

plt.plot([f(i) for i in range(200)][10:])
plt.title("TTR Decay")
plt.ylabel("Type Token Ratio")
plt.xlabel("Number of Tokens")
plt.show("ttr_decay.png")