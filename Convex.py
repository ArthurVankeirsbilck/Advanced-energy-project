import pyomo.environ as pyomo
import matplotlib.pyplot as plt
import pandas as pd

#A

P_CHP = 6
HCHP = 0
yA = 10
yD = 5
xC = 6
yC = 2
xB = 8
yB = 8
xA = 0
xD = 0
M = 10^6
I = 1

uitkomst1 = P_CHP - yA - ((yA-yB)/(xA-xB)) * (HCHP - xA) 
uitkomst2 = P_CHP - yB - ((yB-yC)/(xB-xC)) * (HCHP - xB)
uitkomst3 = P_CHP - yC - ((yC-yD)/(xC-xD)) * (HCHP - xC)

print(uitkomst1)
print(uitkomst2)
print(uitkomst3)

if uitkomst1 <= 0:
    print("constraint 1 ok")

if uitkomst2 >= (M*(I - 1)):
    print("Constraint 2 ok")

if uitkomst3 >= (M*(I - 1)):
    print("Constraint 3 ok")

