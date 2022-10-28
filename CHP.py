import pyomo.environ as pyomo
import random
import matplotlib.pyplot as plt

m = pyomo.ConcreteModel()

T = 96
times = range(T)
M = 100000
yA = 10
yD = 5
xC = 6
yC = 2
xB = 8
yB = 8
xA = 0
xD = 0
M = 10^6
m.P_CHPCOALht = pyomo.Var(times, domain=pyomo.Integers)
m.P_CHPCOALel = pyomo.Var(times, domain=pyomo.Integers)
m.I = pyomo.Var(times, domain=pyomo.Binary)
P = []
Pel = []
Ch = []
for i in range(T):
    P.append(random.randint(xD,xB))
    Pel.append(random.randint(0,4))
    Ch.append(random.randint(4,15))
plt.plot(P)
# m.P_CHPCOALel[t] - yA - ((yA-yB)/(xA-xB)) * (m.P_CHPCOALht[t] - xA) <= 0
# m.P_CHPCOALel[t] - yB - ((yB-yC)/(xB-xC)) * (m.P_CHPCOALht[t] - xB) >= M(m.I[t] - 1)
# m.P_CHPCOALel[t] - yC - ((yC-yD)/(xC-xD)) * (m.P_CHPCOALht[t] - xC) >= M(m.I[t] - 1)

# 0 <= m.P_CHPCOALel[t] <= yA*m.I
# 0 <= m.P_CHPCOALht[t] <= xB*m.I

m.cons = pyomo.ConstraintList()

cost = sum(Ch[t]*m.P_CHPCOALht[t] - m.P_CHPCOALel[t]*Pel[t] for t in times)

m.cost = pyomo.Objective(expr = cost, sense=pyomo.minimize)

for t in times:
    m.cons.add(m.P_CHPCOALht[t] == P[t])
    m.cons.add(m.P_CHPCOALel[t] - yA - ((yA-yB)/(xA-xB)) * (m.P_CHPCOALht[t] - xA) <= 0)
    m.cons.add(m.P_CHPCOALel[t] - yB - ((yB-yC)/(xB-xC)) * (m.P_CHPCOALht[t] - xB) >= M*(m.I[t] - 1))
    m.cons.add(m.P_CHPCOALel[t] - yC - ((yC-yD)/(xC-xD)) * (m.P_CHPCOALht[t] - xC) >= M*(m.I[t] - 1))
    m.cons.add(0 <= m.P_CHPCOALel[t])
    m.cons.add(m.P_CHPCOALel[t] <= yA*m.I[t])
    m.cons.add(0 <= m.P_CHPCOALht[t])
    m.cons.add(m.P_CHPCOALht[t] <= xB*m.I[t])


solver = pyomo.SolverFactory('ipopt')
solver.solve(m, tee=True)
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