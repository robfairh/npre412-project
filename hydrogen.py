import numpy as np


def lte_prod_rate(P, eta):
    """
    Low temperature electrolysis energy requirements and prodution rate.
    Parameters:
    -----------
    P: thermal power [MW]
    eta: themal-to-electric conversion efficiency
    Returns:
    --------
    see: sepecific energy [kWh(th)/kg-H2]
    pr: production rate [kg/h]
    """
    see = 60  # kWh(e)/kg-H2
    see /= eta
    pr = P/see*1e3
    return see, pr


def efficiency(th):
    """
    Calculates thermal-to-electricity conversion efficiency
    from the hot temperature.
    Parameters:
    -----------
    th: hot temperature [C]
    Returns:
    --------
    eta: Thermal-to-electricity conversion efficiency.
    """
    tc = 27  # C
    tc += 273  # K
    th += 273  # K
    eta = 1-tc/th
    eta *= 0.68
    return eta


def delta_H(Tout, Tin):
    """
    Calculates H(P, Tout)-H(P, Tin), P = 3.5 MPa.
    Parameters:
    -----------
    Tout: outlet temperature [C]
    Tin: inlet temperature [C]
    """
    temp = [25, 50, 75, 100, 125, 150, 175, 200, 225, 242.56, 242.56, 250,
            275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575,
            600, 625, 650, 675, 700, 725, 750, 775, 800, 825, 850, 875, 900,
            925, 950, 975, 1000]
    ent35 = [1.9468, 3.8255, 5.7076, 7.5974, 9.5, 11.423, 13.374, 15.368,
             17.421, 18.912, 50.49, 50.977, 52.4, 53.657, 54.823, 55.935,
             57.012, 58.066, 59.106, 60.136, 61.16, 62.182, 63.203, 64.225,
             65.249, 66.276, 67.306, 68.341, 69.381, 70.426, 71.477, 72.534,
             73.597, 74.666, 75.742, 76.825, 77.914, 79.009, 80.112, 81.221,
             82.337, 83.459]
    dH = np.interp(Tout, temp, ent35) - np.interp(Tin, temp, ent35)  # [kJ/mol]
    return dH


def power_req(P, Te):
    """
    Calculates electrical and thermal needs to carry out electrolysis.
    Parameters:
    -----------
    P: pressure [atm]
    Te: electrolysis temperature [C]
    Returns:
    --------
    dg: electrial requirement [kJ/mol]
    tds: thermal requirement [kJ/mol]
    """
    R = 8.314  # [J/mol/K]
    # In theory dh doesn't change with P (I checked, this is correct)
    dg_T = [225, 222, 210, 199, 189, 175, 165]
    tds_T = [17, 25, 40, 55, 70, 84, 99]
    temp = [100, 200, 400, 600, 800, 1000, 1200]
    dh = np.interp(Te, temp, dg_T) + np.interp(Te, temp, tds_T)
    tds = np.interp(Te, temp, tds_T) - R*(Te+273)*np.log(P)/1e3
    dg = dh - tds  # [kJ/mol]
    return dg, tds


def very_simple_hte1(P, outT):
    """
    Calculates the thermal power [Pth] required to produce 1kg/h-H2,
    and gamma = Pth->e/Pth, Pth->e is the thermal power that is converted
    into electricity.
    Parameters:
    -----------
    P: pressure [atm]
    outT: reactor outlet temperature [C]
    Returns:
    --------
    Pth: reactor thermal power requirement [kWh/kgH2]
    gamma: Pe/Pth
    """
    ef = 0.97
    Tr = ef * outT  # Electrolysis temperature
    eta = efficiency(Tr)
    etagammaPth, gammacPth = power_req(P, Tr)
    # gammacPth += delta_H(Tr, 25)
    gammacPth += delta_H(243, 242)  # vaporization energy
    gammaPth = etagammaPth/eta  # Electrical power
    Pth = gammaPth + gammacPth  # P_{th} [kJ/mol] = total power
    gamma = gammaPth/Pth  # \gamma
    Pth = Pth/(2*1.008*3.6)  # [kWh/kg-H2]
    return Pth, gamma


def simple_hte1(P, outT):
    """
    Calculates the thermal power [Pth] required to produce 1kg/h-H2,
    and gamma = Pth->e/Pth, Pth->e is the thermal power that is converted
    into electricity.
    Parameters:
    -----------
    P: pressure [atm]
    outT: reactor outlet temperature [C]
    Returns:
    --------
    Pth: reactor thermal power requirement [kWh/kgH2]
    gamma: Pe/Pth
    """
    ef = 0.97
    Tr = ef * outT  # Electrolysis temperature
    eta = efficiency(Tr)
    etagammaPth, gammacPth = power_req(P, Tr)
    gammacPth += delta_H(Tr, 25)
    gammaPth = etagammaPth/eta  # Electrical power
    Pth = gammaPth + gammacPth  # P_{th} [kJ/mol] = total power
    gamma = gammaPth/Pth  # \gamma
    Pth = Pth/(2*1.008*3.6)  # [kWh/kg-H2]
    return Pth, gamma


def hte1_prod_rate(P, outT):
    """
    High temperature electrolysis energy requirement and production rate.
    Parameters:
    -----------
    P: thermal power [MW]
    outT: reactor outlet temperature [C]
    Returns:
    --------
    pth: sepecific energy [kWh(th)/kg-H2]
    pr: production rate [kg/h]
    """
    if P != 0:
        pth, gamma = very_simple_hte1(P, outT)
        pr = P/pth*1e3
    else:
        pth = 0
        pr = 0
    return pth, pr


def si_prod_rate(P, outT):
    """
    Sulfur-Iodine energy requirement and production rate.
    Parameters:
    -----------
    P: thermal power [MW]
    outT: reactor outlet temperature [C]
    Returns:
    --------
    pth: sepecific energy [kWh(th)/kg-H2]
    pr: production rate [kg/h]
    """
    Mh = 1.008
    pr = 4200  # moles/sec
    ef = [0.25, 0.38, 0.46, 0.52, 0.57, 0.6]
    temp = [750, 800, 850, 900, 950, 1000]
    sev = 2400e3/(pr*(2*Mh/1e3)*3600*np.array(ef)/0.5)
    pth = np.interp(0.97*outT, temp, sev)
    pr = P/pth*1e3
    return pth, pr


def electricity(mass):
    """
    Energy produced from H2.
    Parameters:
    -----------
    mass: hydrogen mass [kg]
    Returns:
    --------
    E: electrical energy [kWh]
    """
    # Mh = 1.008
    # m = mass*1e3/(2*Mh)  # moles
    # E = 285*m  # kJ
    # E /= 3600  # kWh
    E = 40*mass  # ~285kJ/mol = ~40kWh/kg-H2
    return E
