import pyomo.environ as pyomo
import matplotlib.pyplot as plt
import pandas as pd

def demanddata():
    df = pd.read_csv('helen_2015_2021b.csv',sep = ';', decimal=',')

    df.columns = ['Date', 'Consumption']
    df = df.loc[26306:35065]
    df['Date']= pd.to_datetime(df['Date'], format='%d.%m.%Y %H:%M')
    df['Date'] = pd.to_datetime(df["Date"].dt.strftime('%Y-%m-%d %H'))
    df["Consumption"] = pd.to_numeric(df["Consumption"])
    print(df.head())
    
    return df

Pgasmax = 5
Pcoalmax = 10
Phobmax = 4

Pgasmin = 0
Pcoalmin = 2
Phobmin = 0

#Data
Pricegas = [2,2,4,4,2]
Pricecoal = [0.5,0.5,0.5,0.5,0.5]
PriceHOB = [1,1,1,1,1]
demand = [10,15,12,8,19]

T = 5
m = pyomo.ConcreteModel()
times = range(T)

m.Pgas = pyomo.Var(times, domain=pyomo.Integers, bounds=(Pgasmin, Pgasmax))
m.Pcoal = pyomo.Var(times, domain=pyomo.Integers, bounds=(Pcoalmin, Pcoalmax))
m.Phob = pyomo.Var(times, domain=pyomo.Integers, bounds=(Phobmin, Phobmax))

# cost = sum(P[t]*(m.PGB[t]+m.PGL[t]) - FiT[t]*m.PPVG[t] for t in times)
cost = sum(sum(Pricegas[t]*m.Pgas[t]+Pricecoal[t]*m.Pcoal[t]+PriceHOB[t]*m.Phob[t] for t in times) for g in G)

m.cost = pyomo.Objective(expr = cost, sense=pyomo.minimize)

m.cons = pyomo.ConstraintList()

for t in times:
    m.cons.add((m.Pgas[t] + m.Pcoal[t] + m.Phob[t] == demand[t]))

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
        # print(varobject[index].name)
        print(round(varobject[index].value))
        mat.append(round(varobject[index].value))

        mat.append(round(varobject[index].value, 3))
    plt.plot(mat)
    plt.show()