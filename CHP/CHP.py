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
    df["gasprice"] = pd.to_numeric(df["gasprice"])
    df = df[:-1]

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
    plt.plot(P)
    plt.show()
    return P

def Coalprice():
    df = pd.read_csv('../Data/Coal.csv',sep = ',', decimal='.')

    df.columns = ['Date', 'coalprice']
    df["coalprice"] = pd.to_numeric(df["coalprice"])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date').resample('60min').ffill()
    df = df[:-1]
    df["coalprice"] = (df["coalprice"]/8.14)
    df["coalprice"] = pd.to_numeric(df["coalprice"])

    P =  list(df["coalprice"])

    return P

def Wasteprice():
    x=[0.05] * 8760
    return x

def Nuclear():
    x=[0.01] * 8760
    return x

def Pellet():
    x=[0.01] * 8760
    return x

htdemand = Heatdemand()[0:1000]
gasprice = Gasprice()[0:1000]
coalprice = Coalprice()[0:1000]
wasteprice = Wasteprice()[0:1000]
Nuclearprice = Nuclear()[0:1000]
Pelletprice = Pellet()[0:1000]

plants = []
P_CHPCOAL = Powerplants("P_CHPCOAL", "CHP", 0, 2.80,0,3.47,1036, coalprice, 0.01*60, 0.25*1036,58)
P_HOBCOAL = Powerplants("P_HOBCOAL", "HOB", 0, 2.80,0,3.47,420, coalprice, 0.01*60, 0.25*420,58)
P_CHPGAs = Powerplants("P_CHPGAS", "CHP", 0,4.20,0,3.17,970, gasprice, 0.04*60, 0.16*970, 22)
P_HOBGAs = Powerplants("P_HOBGAS", "HOB", 0,4.20,0,3.17,1965, gasprice, 0.04*60, 0.16*1965, 22)
NUSCALE = Powerplants("NUSCALE", "HOB", 0,1.26,0,3.17,50, Nuclearprice, 0.01*60, 0.6*50, 100)
P_CHPWaste = Powerplants("P_CHPWaste", "CHP", 0,45.15,0,0,120, wasteprice, 0.03*60, 0.4*120, 58)
P_HOBpellet = Powerplants("P_HOBpellet", "HOB", 0,1.85,0,0,170, Pelletprice, 0.03*60, 0.4*170, 58)

plants.append(P_CHPCOAL)
plants.append(P_HOBCOAL)
plants.append(P_CHPGAs)
plants.append(P_HOBGAs)
plants.append(P_CHPWaste)
plants.append(NUSCALE)
plants.append(P_HOBpellet)

m = pyomo.ConcreteModel()

T = len(htdemand)
times = list(range(T))
M = 10000000


m.time = pyomo.Set(initialize=times)
m.plants = pyomo.Set(initialize=plants)
m.Cramp = pyomo.Var(m.time, m.plants, domain=pyomo.Reals)
m.P_CHPCOALht = pyomo.Var(m.time, m.plants, domain=pyomo.Reals)
m.P_CHPCOALel = pyomo.Var(m.time, m.plants, domain=pyomo.Reals)
m.I = pyomo.Var(m.time, m.plants, domain=pyomo.Binary)
m.z = pyomo.Var(m.time, m.plants, domain=pyomo.Binary)

Pel = []

for i in range(T):
    Pel.append(random.uniform(1,1.2))

m.cons = pyomo.ConstraintList()

cost = sum(sum((g.variable_costs_el+g.fuelpricing[t])*(m.P_CHPCOALht[t,g]) - m.P_CHPCOALel[t,g]*Pel[t] +m.Cramp[t,g]*g.rampcost for g in m.plants) for t in m.time)

m.cost = pyomo.Objective(expr = cost, sense=pyomo.minimize)
# m.display()
for t in times:
    m.cons.add(sum(m.P_CHPCOALht[t,g] for g in plants) == htdemand[t])
    for g in plants:
        if g.plant_type == "CHP":
            if t == 0:
                m.cons.add(m.P_CHPCOALel[t,g] - g.yA - ((g.yA-g.CHP_feasible_area()[2])/(g.CHP_feasible_area()[0]-g.CHP_feasible_area()[1])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[0]) <= 0)
                m.cons.add(m.P_CHPCOALel[t,g] - g.CHP_feasible_area()[2] - ((g.CHP_feasible_area()[2]-g.CHP_feasible_area()[4])/(g.CHP_feasible_area()[1]-g.CHP_feasible_area()[3])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[1]) >= M*(m.I[t,g] - 1))
                m.cons.add(m.P_CHPCOALel[t,g] - g.CHP_feasible_area()[4] - ((g.CHP_feasible_area()[4]-g.CHP_feasible_area()[6])/(g.CHP_feasible_area()[3]-g.CHP_feasible_area()[5])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[3]) >= M*(m.I[t,g] - 1))
                m.cons.add(g.CHP_feasible_area()[4]*m.I[t,g] <= m.P_CHPCOALel[t,g])
                m.cons.add(m.P_CHPCOALel[t,g] <= g.yA*m.I[t,g])
                m.cons.add(0 <= m.P_CHPCOALht[t,g])
                m.cons.add(m.P_CHPCOALht[t,g] <= g.CHP_feasible_area()[1]*m.I[t,g])
                m.cons.add(m.Cramp[t,g] == m.P_CHPCOALht[t,g])
            else:
                m.cons.add(m.P_CHPCOALel[t,g] - g.yA - ((g.yA-g.CHP_feasible_area()[2])/(g.CHP_feasible_area()[0]-g.CHP_feasible_area()[1])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[0]) <= 0)
                m.cons.add(m.P_CHPCOALel[t,g] - g.CHP_feasible_area()[2] - ((g.CHP_feasible_area()[2]-g.CHP_feasible_area()[4])/(g.CHP_feasible_area()[1]-g.CHP_feasible_area()[3])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[1]) >= M*(m.I[t,g] - 1))
                m.cons.add(m.P_CHPCOALel[t,g] - g.CHP_feasible_area()[4] - ((g.CHP_feasible_area()[4]-g.CHP_feasible_area()[6])/(g.CHP_feasible_area()[3]-g.CHP_feasible_area()[5])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[3]) >= M*(m.I[t,g] - 1))
                m.cons.add(g.CHP_feasible_area()[4]*m.I[t,g] <= m.P_CHPCOALel[t,g])
                m.cons.add(m.P_CHPCOALel[t,g] <= g.yA*m.I[t,g])
                m.cons.add(0 <= m.P_CHPCOALht[t,g])
                m.cons.add(m.P_CHPCOALht[t,g] <= g.CHP_feasible_area()[1]*m.I[t,g])
                m.cons.add(-g.ramprate*g.yA <= m.P_CHPCOALht[t,g] - m.P_CHPCOALht[t-1,g])
                m.cons.add(m.P_CHPCOALht[t,g] - m.P_CHPCOALht[t-1,g] <= g.ramprate*g.yA)
                m.cons.add(0 <= m.Cramp[t,g] -  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]))
                m.cons.add(m.Cramp[t,g] -  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]) <= (2*g.ramprate*g.yA) * m.z[t,g])
                m.cons.add(0 <= m.Cramp[t,g] +  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]))
                m.cons.add(m.Cramp[t,g] +  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]) <= (2*g.ramprate*g.yA) * (1-m.z[t,g]))
        if g.plant_type == "HOB":
            if t==0:
                m.cons.add(m.P_CHPCOALel[t,g] == 0)
                m.cons.add(m.Cramp[t,g] == m.P_CHPCOALht[t,g])
                m.cons.add(m.P_CHPCOALht[t,g] <= g.yA)
                m.cons.add(m.P_CHPCOALht[t,g] >= g.minload) 
            else:
                m.cons.add(m.P_CHPCOALel[t,g] == 0)
                m.cons.add(-g.ramprate*g.yA <= m.P_CHPCOALht[t,g] - m.P_CHPCOALht[t-1,g])
                m.cons.add(m.P_CHPCOALht[t,g] - m.P_CHPCOALht[t-1,g] <= g.ramprate*g.yA)
                m.cons.add(0 <= m.Cramp[t,g] -  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]))
                m.cons.add(m.Cramp[t,g] -  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]) <= (2*g.ramprate*g.yA) * m.z[t,g])
                m.cons.add(0 <= m.Cramp[t,g] +  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]))
                m.cons.add(m.Cramp[t,g] +  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]) <= (2*g.ramprate*g.yA) * (1-m.z[t,g]))
                m.cons.add(m.P_CHPCOALht[t,g] <= g.yA)
                m.cons.add(m.P_CHPCOALht[t,g] >= g.minload) 
            

solver = pyomo.SolverFactory('gurobi')
solver.solve(m, tee=True, report_timing=True)
print("Total cost =", m.cost(), ".")

for v in m.component_objects(pyomo.Var, active=True):
    P_CHPCOALlist = []
    P_CHPGASlist = []
    P_CHPWastelist = []
    P_HOBCOALlist = []
    P_HOBGASlist = []
    NUSCALElist = []
    P_HOBpelletlist = []
    print ("Variable component object",v)
    print ("Type of component object: ", str(type(v))[1:-1]) # Stripping <> for nbconvert
    varobject = getattr(m, str(v))
    print ("Type of object accessed via getattr: ", str(type(varobject))[1:-1])
    for index in varobject:
        # print ("   ", index, round(varobject[index].value, 3))
        if index[1].name == "P_CHPCOAL":
            P_CHPCOALlist.append(varobject[index].value)
        if index[1].name == "P_CHPGAS":
            P_CHPGASlist.append(varobject[index].value)
        if index[1].name == "P_CHPWaste":
            P_CHPWastelist.append(varobject[index].value)
        if index[1].name == "P_HOBCOAL":
            P_HOBCOALlist.append(varobject[index].value)
        if index[1].name == "P_HOBGAS":
            P_HOBGASlist.append(varobject[index].value)
        if index[1].name == "NUSCALE":
            NUSCALElist.append(varobject[index].value)
        if index[1].name == "P_HOBpellet":
            P_HOBpelletlist.append(varobject[index].value)

    plt.plot(P_CHPCOALlist, label="P_CHPCOALlist")
    plt.plot(P_CHPGASlist, label="P_CHPGASlist")
    plt.plot(P_CHPWastelist, label="P_CHPWastelist")
    plt.plot(P_HOBCOALlist, label="P_HOBCOALlist")
    plt.plot(P_HOBGASlist, label="P_HOBGASlist")
    plt.plot(NUSCALElist, label="NUSCALE")
    plt.plot(P_HOBpelletlist, label="P_HOBpelletlist")

    plt.plot(htdemand, label="demand")
    plt.legend(loc="upper left")
    plt.savefig('foo.png')
    plt.show()

print("Thomas meugt em iphoangen")
