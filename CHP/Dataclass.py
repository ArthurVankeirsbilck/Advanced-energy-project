class Powerplants:
    def __init__(self, name, plant_type, resting_period, variable_costs_el, variable_costs_ht, fix_costs, yA, fuelpricing,ramprate,minload, rampcost):
        self.name = name
        self.plant_type = plant_type
        self.variable_costs_el = variable_costs_el
        self.variable_costs_ht = variable_costs_ht
        self.resting_period = resting_period   
        self.fix_costs = fix_costs
        self.yA = yA
        self.fuelpricing = fuelpricing
        self.ramprate = ramprate
        self.minload = minload
        self.rampcost = rampcost

    def CHP_feasible_area(self):
        # if self.plant_type == "CHP":
        xA = 0
        xB = round(self.yA*(180/247))
        yB = round(self.yA*(215/247))
        xC = round(self.yA*(104.8/247))
        yC = round(self.yA*(81/247))
        xD = 0
        yD = round(self.yA*(81/247));

        return xA, xB, yB, xC, yC, xD, yD