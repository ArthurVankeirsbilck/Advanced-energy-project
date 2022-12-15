import pyomo.environ as pyomo
import random
import matplotlib.pyplot as plt
import pandas as pd
from Dataclass import *
import numpy as np

plt.rcParams.update({'font.size': 11})
# rc('figure', figsize=(11.69,8.27))
plt.rcParams["figure.figsize"] = (11.69/2,8.27/2)
def graph(x, y, legende, ylabel, xlabel):
    plt.plot(x,y, label="{}".format(legende), color="blue")
    # plt.legend(loc="upper lefst")
    plt.xlabel("{}".format(xlabel), fontsize=10)
    plt.ylabel("{}".format(ylabel), fontsize=10)
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['top'].set_color('none')
    plt.show()

def Gasprice():
    df = pd.read_csv('../Data/Henry_Hub_Natural_Gas_Spot_Price.csv',sep = ',', decimal='.')

    df.columns = ['Date', 'gasprice']
    df = df[43:56]
    df = df[::-1]
    df["gasprice"] = pd.to_numeric(df["gasprice"])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date').resample('D',).bfill()
    df["gasprice"] = (df["gasprice"]/293.08323)*1000

    df = df[:-1]

    P =  list(df["gasprice"])
    return P

def Heatdemand():
    df = pd.read_csv('../Data/helen_2015_2021b.csv',sep = ';', decimal=',')

    df.columns = ['Date', 'Consumption']
    df = df.loc[26304:35063]
    print(df)
    df['Date']= pd.to_datetime(df['Date'], format='%d.%m.%Y %H:%M')
    df['Date'] = pd.to_datetime(df["Date"].dt.strftime('%Y-%m-%d %H'));
    df = df.set_index('Date').resample('D').sum()

    df["Consumption"] = pd.to_numeric(df["Consumption"])
    P =  list(df["Consumption"])
    return P

def Coalprice():
    df = pd.read_csv('../Data/Coal.csv',sep = ',', decimal='.')

    df.columns = ['Date', 'coalprice']
    df["coalprice"] = pd.to_numeric(df["coalprice"])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date').resample('D').bfill()
    df = df[:-1]
    df["coalprice"] = (df["coalprice"]/8.14)
    df["coalprice"] = pd.to_numeric(df["coalprice"])

    P =  list(df["coalprice"])
    Date = list(df.index)
    return P, Date

def Wasteprice():
    x=[0.05] * 365
    return x

def Nuclear():
    costpermwh = 1663*0.001
    x=[0.01] * 365
    return x

def Pellet():
    x=[0.01] * 365
    return x

def Spotprice():
    df = pd.read_csv('../Data/energy-charts_Daily_electricity_spot_market_prices_in_Finland_in_2018_Excel.csv',sep = ';', decimal='.')

    df.columns = ['Date', 'gasprice']
    df["gasprice"] = pd.to_numeric(df["gasprice"])
    df['Date']= pd.to_datetime(df['Date'], format='%d.%m.%Y')
    df['Date'] = pd.to_datetime(df["Date"].dt.strftime('%Y-%m-%d %H'));
    P =  list(df["gasprice"])
    Date =  list(df["Date"])

    return P, Date


Pel = Spotprice()[0]


htdemand = Heatdemand()
gasprice = Gasprice()
coalprice = Coalprice()[0]
wasteprice = Wasteprice()
Nuclearprice = Nuclear()
Pelletprice = Pellet()

y = Spotprice()[0]
x = Coalprice()[1]
# plt.subplot(3, 1, 1)
# plt.plot(x,y, color="#6392c0")
# plt.title("Spot pricing elec."+r"$\quad (\frac{EUR}{MWh})$")

# y = gasprice
# x = Coalprice()[1]
# plt.subplot(2, 1, 2)
# plt.plot(x,y)
# plt.title("Henry HUB NG Spotpricing"+r"$\quad (\frac{EUR}{MWh_{th}})$")

y = htdemand
newList = [x / 1000 for x in htdemand] 
x = Coalprice()[1]

# plt.subplot(2, 1, 2)
plt.plot(x,newList, color="#6392c0")
# plt.title("Heat demand DH Helsinki"+r"$\quad (GWh)$")
plt.ylabel("Heat demand DH Helsinki"+r"$\quad (GWh)$")

plt.show()

T = len(htdemand)
times = list(range(T))
M = 10000000

plants = []
P_CHPCOAL = Powerplants("P_CHPCOAL", "CHP", 0, 2.80,0,3.47,(1036)*24, coalprice, 0.01*60*24, (0.25*1036)*24,58)
P_HOBCOAL = Powerplants("P_HOBCOAL", "HOB", 0, 2.80,0,3.47,420*24, coalprice, 0.01*60*24, (0.25*420)*24,58)
P_CHPGAs = Powerplants("P_CHPGAS", "CHP", 0,4.20,0,3.17,970*24, gasprice, 0.04*60*24, (0.16*970)*24, 22)
P_HOBGAs = Powerplants("P_HOBGAS", "HOB", 0,4.20,0,3.17,1970*24, gasprice, 0.04*60*24, (0.16*(1970/3))*24, 22)
NUSCALE = Powerplants("NUSCALE", "HOB", 0,1.26,0,3.17,250*24, Nuclearprice, 0.1*60*24, (0.6*250)*24, 100)
P_CHPWaste = Powerplants("P_CHPWaste", "CHP", 0,45.15,0,0,120*24, wasteprice, 0.03*60*24, (0.4*120)*24, 58)
P_HOBpellet = Powerplants("P_HOBpellet", "HOB", 0,1.85,0,0,170*24, Pelletprice, 0.03*60*24, (0.4*170)*24, 58)
# HEATPUMP = Powerplants("HEATPUMP", "HOB", 0,0,0,0,200, Pel, 1, 0.1*200, 0)

plants.append(P_CHPCOAL)
plants.append(P_HOBCOAL)
plants.append(P_CHPGAs) 
plants.append(P_HOBGAs)
plants.append(P_CHPWaste)
plants.append(NUSCALE)
plants.append(P_HOBpellet)
# plants.append(HEATPUMP)

m = pyomo.ConcreteModel()


m.time = pyomo.Set(initialize=times)
m.plants = pyomo.Set(initialize=plants)
m.Cramp = pyomo.Var(m.time, m.plants, domain=pyomo.Reals)
m.P_CHPCOALht = pyomo.Var(m.time, m.plants, domain=pyomo.Reals)
m.P_CHPCOALel = pyomo.Var(m.time, m.plants, domain=pyomo.Reals)
m.I = pyomo.Var(m.time, m.plants, domain=pyomo.Binary)
m.z = pyomo.Var(m.time, m.plants, domain=pyomo.Binary)

m.cons = pyomo.ConstraintList()

cost = sum(sum((g.variable_costs_el+g.fuelpricing[t])*(m.P_CHPCOALht[t,g]+m.P_CHPCOALel[t,g]) - m.P_CHPCOALel[t,g]*Pel[t] +m.Cramp[t,g]*g.rampcost for g in m.plants) for t in m.time)

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
                m.cons.add(g.CHP_feasible_area()[6]*m.I[t,g] <= m.P_CHPCOALel[t,g])
                m.cons.add(m.P_CHPCOALel[t,g] <= g.yA*m.I[t,g])
                m.cons.add(0 <= m.P_CHPCOALht[t,g])
                m.cons.add(m.P_CHPCOALht[t,g] <= g.CHP_feasible_area()[1]*m.I[t,g])
                m.cons.add(m.Cramp[t,g] == m.P_CHPCOALht[t,g])
            else:
                m.cons.add(m.P_CHPCOALel[t,g] - g.yA - ((g.yA-g.CHP_feasible_area()[2])/(g.CHP_feasible_area()[0]-g.CHP_feasible_area()[1])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[0]) <= 0)
                m.cons.add(m.P_CHPCOALel[t,g] - g.CHP_feasible_area()[2] - ((g.CHP_feasible_area()[2]-g.CHP_feasible_area()[4])/(g.CHP_feasible_area()[1]-g.CHP_feasible_area()[3])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[1]) >= M*(m.I[t,g] - 1))
                m.cons.add(m.P_CHPCOALel[t,g] - g.CHP_feasible_area()[4] - ((g.CHP_feasible_area()[4]-g.CHP_feasible_area()[6])/(g.CHP_feasible_area()[3]-g.CHP_feasible_area()[5])) * (m.P_CHPCOALht[t,g] - g.CHP_feasible_area()[3]) >= M*(m.I[t,g] - 1))
                m.cons.add(g.CHP_feasible_area()[6]*m.I[t,g] <= m.P_CHPCOALel[t,g])
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
                m.cons.add(m.P_CHPCOALht[t,g] <= g.yA*m.I[t,g])
                m.cons.add(m.P_CHPCOALht[t,g] >= g.minload*m.I[t,g]) 
            else:
                m.cons.add(m.P_CHPCOALel[t,g] == 0)
                m.cons.add(-g.ramprate*g.yA <= m.P_CHPCOALht[t,g] - m.P_CHPCOALht[t-1,g])
                m.cons.add(m.P_CHPCOALht[t,g] - m.P_CHPCOALht[t-1,g] <= g.ramprate*g.yA)
                m.cons.add(0 <= m.Cramp[t,g] -  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]))
                m.cons.add(m.Cramp[t,g] -  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]) <= (2*g.ramprate*g.yA) * m.z[t,g])
                m.cons.add(0 <= m.Cramp[t,g] +  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]))
                m.cons.add(m.Cramp[t,g] +  (m.P_CHPCOALht[t,g] -  m.P_CHPCOALht[t-1,g]) <= (2*g.ramprate*g.yA) * (1-m.z[t,g]))
                m.cons.add(m.P_CHPCOALht[t,g] <= g.yA*m.I[t,g])
                m.cons.add(m.P_CHPCOALht[t,g] >= g.minload*m.I[t,g])
        # if g.name == "NUSCALE":
        #     if 200 <= t <= 245:
        #         m.cons.add(m.P_CHPCOALht[t,g] <= 200)

        #     else:
        #         pass

solver = pyomo.SolverFactory('gurobi')
# solver.options['mipgap'] = 0.01
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
    HEATPUMPlist = []
    print ("Variable component object",v)
    print ("Type of component object: ", str(type(v))[1:-1]) # Stripping <> for nbconvert
    varobject = getattr(m, str(v))
    print ("Type of object accessed via getattr: ", str(type(varobject))[1:-1])
    for index in varobject:
        # print ("   ", index, round(varobject[index].value, 3))
        if index[1].name == "P_CHPCOAL":
            P_CHPCOALlist.append(varobject[index].value/1000)
        if index[1].name == "P_CHPGAS":
            P_CHPGASlist.append(varobject[index].value/1000)
        if index[1].name == "P_CHPWaste":
            P_CHPWastelist.append(varobject[index].value/1000)
        if index[1].name == "P_HOBCOAL":
            P_HOBCOALlist.append(varobject[index].value/1000)
        if index[1].name == "P_HOBGAS":
            P_HOBGASlist.append(varobject[index].value/1000)
        if index[1].name == "NUSCALE":
            NUSCALElist.append(varobject[index].value/1000)
        if index[1].name == "P_HOBpellet":
            P_HOBpelletlist.append(varobject[index].value/1000)
        if index[1].name == "HEATPUMP":
            HEATPUMPlist.append(varobject[index].value/1000)
    newList = [x / 1000 for x in htdemand]  
    plt.plot(newList, label=r"$Q_t$", color='#808080')
    plt.plot(P_CHPCOALlist, label=r"$q_{CHP - Coal}$", color="blue")
    plt.plot(P_CHPGASlist, label=r"$q_{CHP - Gas}$", color="purple")
    plt.plot(P_CHPWastelist, label=r"$q_{CHP - Waste}$",color="brown")
    plt.plot(P_HOBCOALlist, label=r"$q_{HOB - Coal}$", color="tomato")
    plt.plot(P_HOBGASlist, label=r"$q_{HOB - Gas}$", color="indigo")
    plt.plot(NUSCALElist, label=r"$q_{SMR}$", color="red")
    df = pd.DataFrame (NUSCALElist, columns = ['P_HOBGASlist'])
    df.to_csv('GFG.csv') 

    plt.plot(P_HOBpelletlist, label=r"$q_{HOB - Pellet}$", color="green")
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['top'].set_color('none')
    plt.xlabel("Time (days)")
    plt.ylabel("Production"+r"($\frac{GWh}{day})$")
    plt.legend(loc="upper right")
    plt.savefig('foo.png')
    plt.show()

    CO2COAL = sum(P_CHPCOALlist+P_HOBCOALlist)*340
    CO2GAS = sum(P_CHPGASlist+P_HOBGASlist)*202
    CO2WASTE = sum(P_CHPWastelist)*252
    CO2PELLET = sum(P_HOBpelletlist)*403
    SMR = sum(NUSCALElist)*3.71
    total=CO2COAL+CO2GAS+CO2WASTE+CO2PELLET+SMR
    print("Total emission:{}".format(total))
    print("Coal emission:{}".format(CO2COAL/total))
    print("Gas emission:{}".format(CO2GAS/total))
    print("Waste emission:{}".format(CO2WASTE/total))
    print("Pellet emission:{}".format(CO2PELLET/total))
    print("SMR emission:{}".format(SMR/total))

    CO2COALprod = sum(P_CHPCOALlist+P_HOBCOALlist)
    CO2GASprod  = sum(P_CHPGASlist+P_HOBGASlist)
    CO2WASTEprod  = sum(P_CHPWastelist)
    CO2PELLETprod  = sum(P_HOBpelletlist)
    SMRprod = sum(NUSCALElist)

    totalprod = CO2COALprod+CO2GASprod+CO2WASTEprod+CO2PELLETprod+SMRprod

    print("Total production:{}".format(totalprod))
    print("Coal production:{}".format(CO2COALprod/totalprod))
    print("Gas production:{}".format(CO2GASprod/totalprod))
    print("Waste production:{}".format(CO2WASTEprod/totalprod))
    print("Pellet production:{}".format(CO2PELLETprod/totalprod))
    print("SMR production:{}".format(SMRprod/totalprod))