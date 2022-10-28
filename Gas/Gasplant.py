import pandas as pd
import numpy as np
from pyomo.environ import *
#from pyomo.core import *   # not needed
import matplotlib.pyplot as plt

# Import file
df = pd.read_csv('raw_prices_full.csv', sep = ';')
df.columns = ['local_time', 'rrp']

# New Index
df['period'] = df.reset_index().index

print(df.head())
print(df.info())

# get current Year
first_model_period = 0
last_model_period = df['period'].iloc[-1]

# Gas Inputs
gunits = 1 # No units
gnet = 20 # MW/unit
#srmc = 115.49 # $/MWh
#vom = 6.18 # $/MWh
gprice = 10 # $/GJ
startup_gas_rate = 8 # GJ/unit/5mins
min_running = 5 # GJ/unit/5mins   <--- assumed minimal output...  or plant could "run" at zero
hr = 10 # GJ/MWh
sys_use = 0.10 # % overhead in GJ of gas
max_gas = 100 # GJ/30 minutes (6 periods), cut down for testing

# Filter the data
df = df.loc[first_model_period:last_model_period, :]

model = ConcreteModel()

# Define model parameters
model.T = Set(initialize=df.period.tolist(), doc='periods of year', ordered=True)
# P needs to be indexed by T, and should be init by dictionary
model.P = Param(model.T, initialize=df.rrp.to_dict(), doc='price for each period', within=NonNegativeReals)  
model.MaxGas = Param(initialize=max_gas, doc='Max gas usage (GJ) in 24 hour period', within=NonNegativeReals)

# variables
model.turn_on = Var(model.T, domain=Binary)         # decision to turn the plant on in period t, making it available at t+2
model.plant_running = Var(model.T, domain=Binary)   # plant is running (able to produce heat) in period t.  init is not necessary
model.total_gas = Var(model.T, bounds=(0, gunits*gnet / 12 * hr * (1+sys_use)))  # the total gas flow in any period [GJ/5min]
model.gas_for_power = Var(model.T, domain=NonNegativeReals )  # the gas flow for power conversion at any period [GJ/5min]
model.profit = Var(model.T)  # non-essential variable, just used for bookeeping

# *********************
# GAS CONSTRAINTS
# *********************

# logic for the plant_running control variable
def running(model, t):
    # plant cannot be running in first 2 periods
    if t < 2:
        return model.plant_running[t] == 0
    else:
        # plant can be running if it was running in last period or started 2 periods ago.
        return model.plant_running[t] <= model.plant_running[t-1] + model.turn_on[t-2]
model.running_constraint = Constraint(model.T, rule=running)

# charge the warmup gas after a start decision.  Note the conditions in this constraint are all
# mutually exclusive, so there shouldn't be any double counting
# this will constrain the minimum gas flow to either the startup flow for 2 periods, 
# the minimum running flow, or zero if neither condition is met
def gas_mins(model, t):
    # figure out the time periods to inspect to see if a start event occurred...
    if t==0:
        possible_starts = model.turn_on[t]
    else:
        possible_starts = model.turn_on[t] + model.turn_on[t-1]
    return model.total_gas[t] >= \
            startup_gas_rate * gunits * (1 + sys_use) * possible_starts + \
            min_running * gunits * (1 + sys_use) * model.plant_running[t]
model.gas_mins = Constraint(model.T, rule=gas_mins)

# constrain the gas used for power to zero if not running, or the period max
def max_flow(model, t):
    return model.gas_for_power[t] <= model.plant_running[t] * gunits * gnet / 12 * hr
model.running_max_gas = Constraint(model.T, rule=max_flow)

# add the overhead to running gas to capture total gas by when running
def tot_gas_for_conversion(model, t):
    return model.total_gas[t] >=  model.gas_for_power[t] * (1 + sys_use)
model.tot_gas_for_conversion = Constraint(model.T, rule=tot_gas_for_conversion)

# constraint to limit consumption to max per 24hr rolling period.  Note, this is *rolling* constraint,
# if a "daily" constraint tied to particular time of day is needed, more work will need to be done
# on the index to identify the indices of interest
window_size = 6  # for testing on small data, normally would be: 24hrs * 12intervals/hr
def rolling_max(model, t):
    preceding_periods = {t_prime for t_prime in model.T if t - window_size <= t_prime < t}
    return sum(model.total_gas[t_prime] for t_prime in preceding_periods) <= model.MaxGas
eval_periods = {t for t in model.T if t >= window_size}
model.rolling_max = Constraint(eval_periods, rule=rolling_max)

# Define the income, expenses, and profit
gas_income = sum(df.loc[t, 'rrp'] * model.gas_for_power[t] / hr  for t in model.T)
gas_expenses = sum(model.total_gas[t] * gprice for t in model.T)  # removed the "vom" computation
profit = gas_income - gas_expenses
model.objective = Objective(expr=profit, sense=maximize)

# Solve the model
solver = SolverFactory('ipopt')
results = solver.solve(model)
print(results)
# model.display()
# model.pprint()

cols = []
cols.append(pd.Series(model.P.extract_values(), name='energy price'))
cols.append(pd.Series(model.total_gas.extract_values(), name='total gas'))
cols.append(pd.Series(model.gas_for_power.extract_values(), name='converted gas'))
df_results = pd.concat(cols, axis=1)

fig, ax1 = plt.subplots()
width = 0.25
ax1.bar(np.array(df.index)-width, df_results['energy price'], width, color='g', label='price of power')
ax1.set_ylabel('price')
ax2 = ax1.twinx()
ax2.set_ylabel('gas')
ax2.bar(df.index, df_results['total gas'], width, color='b', label='tot gas')
ax2.bar(np.array(df.index)+width, df_results['converted gas'], width, color='xkcd:orange', label='converted gas')
fig.legend()
fig.tight_layout()
plt.show()