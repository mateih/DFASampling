from scipy.stats import ttest_rel
from scipy.stats import shapiro
from scipy.stats import friedmanchisquare
import scikit_posthocs as sp
import numpy as np
from scipy.stats import wilcoxon


binary50_scores = [1,0.97,1,0.94,1,0.97,0.97,0.97,0.97,0.97,1,1,0.91,0.93,1,0.96,1,0.93,0.89,0.96,0.97,0.98,0.98,0.98,0.98]
random50_scores = [1,1,0.96,1,1,0.82,0.97,0.97,0.92,0.97,0.92,0.9,0.91,0.91,0.81,0.94,0.86,0.86,0.91,0.96,0.98,0.98,0.95,0.98,0.98]
edsm_scores = [0.85,0.82,0.6,0.69,0.81,0.7,0.65,0.82,0.73,0.8,1,0.94,0.97,1,0.97,0.77,0.72,0.83,0.79,0.86,0.75,0.71,0.71,0.83,0.85]
dynamic50_scores = [1,1,1,1,1,0.92,0.97,0.95,0.97,0.97,0.98,0.98,1,1,0.93,0.91,0.89,0.88,0.91,0.89,0.98,0.95,0.98,0.98,0.98]

# print(len(binary50_scores))
# print(len(random50_scores))
# print(len(dynamic50_scores))
# print(len(edsm_scores))
#
#



# stat, p = wilcoxon(binary50_scores, dynamic50_scores)
# print(f"Statistic: {stat:.4f}, p-value: {p:.6f}")

bin50 = [1,1,0.95,1,0.99,0.99,0.99,0.96,0.99,1,1,0.99,0.97,1,0.98,1,0.97,0.97,0.96,0.99,0.99,0.99,0.99]
print(sum(bin50)/len(bin50))
ran50 = [1,1,0.98,1,1,0.94,0.99,0.99,0.93,0.99,0.95,0.92,0.98,0.97,0.94,0.98,0.91,0.90,0.95,0.97,0.99,0.99,0.99,0.99,0.99]
print(sum(ran50)/len(ran50))
dyn50 = [1,1,1,1,1,0.99,0.99,0.96,0.99,0.98,0.96,0.99,0.98,0.97,0.97,0.95,0.96,0.95,0.96,0.91,0.98,0.96,0.99,0.99,0.99]
print(sum(dyn50)/len(dyn50))
