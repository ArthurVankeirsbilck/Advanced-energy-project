import pyomo.environ as pyomo
import random
import matplotlib.pyplot as plt
import pandas as pd
from Dataclass import *

def Gasprice():
    df = pd.read_csv('../Data/Henry_Hub_Natural_Gas_Spot_Price.csv',sep = ',', decimal='.')

    df.columns = ['Date', 'gasprice']
    df = df[43:56]
    df = df[::-1]
    df["gasprice"] = pd.to_numeric(df["gasprice"])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date').resample('60min').ffill()
    df["gasprice"] = (df["gasprice"]/293.08323)*1000
    df = df[:-1]
    print(df)

    P =  list(df["gasprice"])
    return P

def Heatdemand():
    df = pd.read_csv('../Data/helen_2015_2021b.csv',sep = ';', decimal=',')

    df.columns = ['Date', 'Consumption']
    df = df.loc[26306:35065]
    df['Date']= pd.to_datetime(df['Date'], format='%d.%m.%Y %H:%M')
    df['Date'] = pd.to_datetime(df["Date"].dt.strftime('%Y-%m-%d %H'))
    df["Consumption"] = pd.to_numeric(df["Consumption"])
    P =  list(df["Consumption"])
    
    return P

def Coalprice():
    df = pd.read_csv('../Data/Coal.csv',sep = ',', decimal='.')

    df.columns = ['Date', 'coalprice']
    df["coalprice"] = pd.to_numeric(df["coalprice"])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date').resample('60min').ffill()
    df = df[:-1]
    df["coalprice"] = (df["coalprice"]/2.46)
    print(df)

    P =  list(df["coalprice"])

    return P

def Wasteprice():
    x=[0.05] * 8760
    return x

htdemand = Heatdemand()[0:100]
gasprice = Gasprice()[0:100]
coalprice = Coalprice()[0:100]
wasteprice = Wasteprice()[0:100]

plants = []

P_CHPCOAL = Powerplants("P_CHPCOAL", "CHP", 0, 2.80,0,3.47,1036, coalprice, 0.01*60, 0.25*1036,58)
P_CHPGAs = Powerplants("P_CHPGAS", "CHP", 0,4.20,0,3.17,970, gasprice, 0.04*60, 0.16*970, 22)
P_CHPWaste = Powerplants("P_CHPWaste", "CHP", 0,0.5,0,0,120, wasteprice, 0.03*60, 0.4*120, 58)
# P_HOBGAS= Powerplants("P_HOBGAS", "HOB", 0, 0,1.00,0,1965, gasprice, 0.04*60, 0.16*970, 22)
# P_HOBBIOMASS = Powerplants("P_HOBBIOMASS", "HOB", 0, 0,2.70,0,170)
plants.append(P_CHPCOAL)
plants.append(P_CHPGAs)
plants.append(P_CHPWaste)

m = pyomo.ConcreteModel()

T = len(htdemand)
times = list(range(T))
M = 10000000

Pel = []

for i in range(T):
    Pel.append(random.randint(0,4))

m.time = pyomo.Set(initialize=times)
m.plants = pyomo.Set(initialize=plants)
m.P_CHPCOALht = pyomo.Var(m.time, m.plants, domain=pyomo.Reals)
m.P_CHPCOALel = pyomo.Var(m.time, m.plants, domain=pyomo.Reals)
m.I = pyomo.Var(m.time, m.plants, domain=pyomo.Binary)

m.cons = pyomo.ConstraintList()

cost = sum(sum((g.fuelpricing[t])*m.P_CHPCOALel[t,g] - m.P_CHPCOALel[t,g]*Pel[t] for g in m.plants) for t in m.time)
m.cost = pyomo.Objective(expr = cost, sense=pyomo.minimize)
for t in times:
    for g in plants:
        m.cons.add(m.P_CHPCOALel[t,g] - g.yA - ((g.yA-g.CHP_feasible_area()[2])/(g.CHP_feasible_area()[0]-g.CHP_feasible_area()[1])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[0]) <= 0)
        m.cons.add(m.P_CHPCOALel[t,g] - g.CHP_feasible_area()[2] - ((g.CHP_feasible_area()[2]-g.CHP_feasible_area()[4])/(g.CHP_feasible_area()[1]-g.CHP_feasible_area()[3])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[1]) >= M*(m.I[t,g] - 1))
        m.cons.add(m.P_CHPCOALel[t,g] - g.CHP_feasible_area()[4] - ((g.CHP_feasible_area()[4]-g.CHP_feasible_area()[6])/(g.CHP_feasible_area()[3]-g.CHP_feasible_area()[5])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[3]) >= M*(m.I[t,g] - 1))
        m.cons.add(g.CHP_feasible_area()[4]*m.I[t,g] <= m.P_CHPCOALel[t,g])
        m.cons.add(m.P_CHPCOALel[t,g] <= g.yA*m.I[t,g])
        m.cons.add(0 <= m.P_CHPCOALht[t,g])
        m.cons.add(m.P_CHPCOALht[t,g] <= g.CHP_feasible_area()[1]*m.I[t,g])

        m.cons.add(sum(m.P_CHPCOALht[t,g] for g in plants) == htdemand[t])

solver = pyomo.SolverFactory('ipopt')
solver.solve(m, tee=True)
print("Total cost =", m.cost(), ".")

for v in m.component_objects(pyomo.Var, active=True):
    P_CHPCOALlist = []
    P_CHPGASlist = []
    P_CHPWastelist = []
    P_HOBCOALlist = []
    P_HOBGASlist = []
    P_HOBBIOMASSlist = []
    print ("Variable component object",v)
    print ("Type of component object: ", str(type(v))[1:-1]) # Stripping <> for nbconvert
    varobject = getattr(m, str(v))
    print ("Type of object accessed via getattr: ", str(type(varobject))[1:-1])
    for index in varobject:
        # print ("   ", index, round(varobject[index].value, 3))
        if index[1].name == "P_CHPCOAL":
            P_CHPCOALlist.append(round(varobject[index].value))
        if index[1].name == "P_CHPGAS":
            P_CHPGASlist.append(round(varobject[index].value))
        if index[1].name == "P_CHPWaste":
            P_CHPWastelist.append(round(varobject[index].value))
        if index[1].name == "P_HOBCOAL":
            P_HOBCOALlist.append(round(varobject[index].value))
        if index[1].name == "P_HOBGAS":
            P_HOBGASlist.append(round(varobject[index].value))
        if index[1].name == "P_HOBBIOMASS":
            P_HOBBIOMASSlist.append(round(varobject[index].value))
        # print(index, varobject[index].value)
        # print(P)
        # mat.append(round(varobject[index].value, 3))

    # print(P_CHPCOALlist)
    # print(CHPGASlistt)
    # print(P_CHPWastelist)
    # print(P_HOBCOALlist)
    # print(P_HOBGASlist)
    # print(P_HOBBIOMASSlist)

    # fig, axs = plt.subplots(2)
    # fig.suptitle('Vertically stacked subplots')
    # axs[0].plot(P_CHPCOALlist, label="P_CHPCOALlist")
    # axs[0].plot(P_CHPGASlist, label="P_CHPGASlist")
    # axs[0].plot(P_CHPWastelist, label="P_CHPWastelist")
    # axs[0].plot(htdemand, label="demand")
    # axs[1].plot(x, -y)

    plt.plot(P_CHPCOALlist, label="P_CHPCOALlist")
    plt.plot(P_CHPGASlist, label="P_CHPGASlist")
    plt.plot(P_CHPWastelist, label="P_CHPWastelist")

    # plt.plot(P_HOBCOALlist, label="P_HOBCOALlist")
    # plt.plot(P_HOBGASlist, label="P_HOBGASlist")
    # plt.plot(P_HOBBIOMASSlist, label="P_HOBBIOMASSlist")
    # plt.plot(htdemand, label="demand")
    plt.legend(loc="upper left")
    plt.savefig('foo.png')
    plt.show()