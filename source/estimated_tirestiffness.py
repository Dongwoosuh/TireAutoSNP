import math

Kz=0.00028
Inflation_pressure=2.2 #bar (2.0~2.4)
tire_footprint=60 #mm
# OD=302.73 #mm
OD=250 #mm

estimated_tirestiffness=(Kz*100*Inflation_pressure*math.sqrt(tire_footprint*OD)+3.45)*9.81 #stiffness
print("estimated_tirestiffness=" , estimated_tirestiffness)