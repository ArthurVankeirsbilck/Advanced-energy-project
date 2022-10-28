import pyomo.environ as pyomo
import matplotlib.pyplot as plt
import pandas as pd

# #A

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

P = [18,20,19]
Pelec = [0.2,0.5,0.7]
T = 24
m = pyomo.ConcreteModel()
times = range(T)
t_minus_1 = range(T-1)

Cfix = {
    "HOB,COAL" : 0,
    "CHP,COAL" : 83.16
}
Cfix = [0, 83.16]
Cvar = {
    "HOB,COAL" : 2.70,
    "CHP,COAL" : 2.80
}
Cvar = [2.70, 2.80]
Ccm = {
    "HOB,COAL" : 59,
    "CHP,COAL" : 59
}
Ccm = [59, 59]
P_HOBCOALmin = 0
P_CHPCOALmin = 0
P_HOBCOALmax = 10
P_CHPCOALmax = 12

m.P_HOBCOAL = pyomo.Var(times, domain=pyomo.Integers, bounds=(P_HOBCOALmin, P_HOBCOALmax))
m.P_CHPCOAL = pyomo.Var(times, domain=pyomo.Integers, bounds=(P_CHPCOALmin, P_CHPCOALmax))
print(Cvar['HOB,COAL'])
cost = sum(
    m.P_HOBCOAL[t] *(Cvar[0]+(Cfix[0]/(365*24))) +
    m.P_CHPCOAL[t] *(Cvar[1] +(Cfix[0]/(365*24))) - m.PCHPcoal[t]*Pelec[t] 
    for t in times)

m.cost = pyomo.Objective(expr = cost, sense=pyomo.minimize)
m.cons = pyomo.ConstraintList()

for t in times:
    m.cons.add(m.P_HOBCOAL[t] + m.P_CHPCOAL[t] == P[t])

solver = pyomo.SolverFactory('ipopt')
solver.solve(m, tee=True)

mat = []

print("Total cost =", m.cost(), ".")
for v in m.component_objects(pyomo.Var, active=True):
    mat = []
    print ("Variable component object",v)
    print ("Type of component object: ", str(type(v))[1:-1]) # Stripping <> for nbconvert
    varobject = getattr(m, str(v))
    print ("Type of object accessed via getattr: ", str(type(varobject))[1:-1])
 
    for index in varobject:
        # print ("   ", index, round(varobject[index].value, 3))
        
        if v.name == "SOCnext":
            mat.append(varobject[index].value)
        else:
            mat.append(round(varobject[index].value))

        # mat.append(round(varobject[index].value, 3))
    plt.plot(mat)
    plt.show()