import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import hydrogen as h2
from datetime import datetime


def get_prediction(syear, stime, elec, fut, plotflag, title, name=0):
    """
    Parameters:
    -----------
    - syear: [int]
    data used for prediction starts at syear and
    ends at last year.
    - stime: [list]
    list of years of the electricity generation data.
    - elec: [list]
    list of electricity generation data.
    - fut: [int]
    number of years to do the prediction for.
    - plotflag: [bool]
    False: no plotting.
    Returns:
    --------
    - future: [list]
    years of the prediction.
    - ytf: [list]
    prediction of electricity generation.
    """
    sstime = stime[stime.index(syear):]
    yt = elec[stime.index(syear):]
    sstime = np.array(sstime).reshape(len(sstime), 1)
    yt = np.array(yt)
    lin = LinearRegression()
    lin.fit(sstime, yt)
    print(r'R$^2$ score: ', lin.score(sstime, yt))
    pt = lin.predict(sstime)
    future = np.arange(fut).reshape(fut, 1) + stime[-1]
    ytf = lin.predict(future)
    if plotflag is True:
        plt.figure()
        plt.plot(stime, elec, label='data')
        plt.plot(sstime, pt, label='regression')
        plt.plot(future, ytf, label='prediction')
        plt.legend(loc='upper left')
        plt.xlabel('year')
        plt.ylabel('Million [kWh]')
        plt.title(title+' electricity net generation.')
        plt.savefig("figures/"+name, dpi=300, bbox_inches="tight")
        # plt.show()
        plt.close()
    return future, ytf


def us_year():
    df = pd.read_csv('electricity-year.csv')
    time = df['Annual Total'].tolist()
    solar = df["Electricity Net Generation From Solar, " +
               "All Sectors (Million Kilowatthours)"].tolist()
    nuclear = df["Electricity Net Generation From Nuclear Electric Power, " +
                 "All Sectors (Million Kilowatthours)"].tolist()
    total = df["Electricity Net Generation Total (including from sources " +
               "not shown), All Sectors (Million Kilowatthours)"].tolist()

    for i in range(len(solar)):
        if solar[i] == 'Not Available':
            solar[i] = 0
        else:
            solar[i] = float(solar[i])

    zyear = 1980
    ztime = time[time.index(zyear):]
    ztotal = total[time.index(zyear):]
    zsolar = solar[time.index(zyear):]
    znuclear = nuclear[time.index(zyear):]

    predict = 31
    future1, ytf1 = get_prediction(2006, ztime, ztotal, predict, True, 'Total',
                                   'us-prediction1')
    print(ytf1[-1])
    future2, ytf2 = get_prediction(2015, ztime, zsolar, predict, True, 'Solar',
                                   'us-prediction2')
    future3, ytf3 = get_prediction(2012, ztime, znuclear, predict, False,
                                   'nuclear')

    plt.figure()
    plt.plot(ztime, ztotal, label='total')
    plt.plot(future1, ytf1, label='total prediction')
    plt.plot(ztime, zsolar, label='solar')
    plt.plot(future2, ytf2, label='solar prediction')
    plt.plot(ztime, znuclear, label='nuclear')
    plt.plot(future3, ytf3, label='nuclear prediction')
    # plt.legend(loc='upper left')
    plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1.0), fancybox=True)
    plt.xlabel('year')
    plt.ylabel('Million [kWh]')
    plt.savefig("figures/us-prediction", dpi=300, bbox_inches="tight")

    ustg = ytf1[-1]/ztotal[-1]
    print('ustg:', ustg)
    print('ustg %:', (ustg-1)/predict)

    ussg = ytf2[-1]/zsolar[-1]
    print('ussg:', ussg)
    print('ussg %:', (ussg-1)/predict)

    return predict, ustg, ussg


def us_hour():
    predict, ustg, ussg = us_year()
    df = pd.read_csv('us-hourly3.csv')
    time = df['Timestamp (Hour Ending)'].tolist()
    solar = df['Solar Generation (MWh)'].tolist()
    total = df['Total Generation (MWh)'].tolist()

    time_max = time[solar.index(max(solar))]
    print(time_max)

    # choose date and time
    sdate = '4/17/2019'
    stime = '12 a.m. EDT'
    edate = '4/18/2019'
    etime = '12 a.m. EDT'

    s = time.index(sdate+' '+stime)
    e = time.index(edate+' '+etime)

    ntime = time[s:e]
    nsolar = np.array(solar[s:e])
    ntotal = np.array(total[s:e])

    ntime = [str(i)+':00' for i in range(24)]
    print(ntime)

    plt.figure()
    nntotal = ustg*ntotal
    plt.plot(ntime, nsolar, label='solar 2019')
    nnsolar = ussg*nsolar
    plt.plot(ntime, nnsolar, label='solar {0}'.format(2019+predict))
    plt.plot(ntime, ntotal-nsolar, label='total-solar 2019')
    plt.plot(ntime, nntotal-nnsolar,
             label='total-solar {0}'.format(2019+predict))

    plt.xticks(np.arange(0, 24, step=3), rotation=45)
    plt.legend(loc="lower left")
    plt.ylabel('[MWh]')
    plt.xlabel('Time')
    plt.savefig("figures/duck-curve4", dpi=300, bbox_inches="tight")


def uiuc_hour():
    predict, ustg, ussg = us_year()
    df = pd.read_csv('2015-2019-uiuc-solar.csv')

    timeh = df['time'].tolist()
    solarh = df['measured'].tolist()

    s = timeh.index('2018-10-03 00:00:00')
    e = timeh.index('2019-10-03 23:45:00')
    timev = timeh[s:e+1]
    solarv = solarh[s:e+1]
    time_max = timev[solarv.index(max(solarv))]
    day = datetime.fromisoformat(time_max)
    s = timev.index(str(day.date())+' 00:00:00')
    e = timev.index(str(day.date())+' 23:45:00')
    timed = timev[s:e+1]
    valsol = solarv[s:e+1]

    plt.figure()
    df = pd.read_csv('2014-2019-uiuc-electricity-demand.csv')

    timeh = df['time'].tolist()
    totalh = df['kw'].tolist()

    s = timeh.index(str(day.date())+' 00:00:00')
    e = timeh.index(str(day.date())+' 23:00:00')
    timed = timeh[s:e+1]
    valtot = totalh[s:e+1]

    A = np.zeros((len(valtot), len(valsol)))
    for i in range(A.shape[0]):
        A[i, 4*i:4*(i+1)] = 0.25*np.ones(4)
    nvalsol = A @ np.array(valsol)

    timep = [str(datetime.fromisoformat(timed[i]).time()) for i in range(len(timed))]

    plt.plot(timep, nvalsol, label='solar 2019')
    nnvalsol = ussg*nvalsol
    plt.plot(timep, nnvalsol, label='solar {0}'.format(2019+predict))

    valtot = np.array(valtot)
    totmsol = valtot-nvalsol
    nvaltot = ustg*valtot
    plt.plot(timep, totmsol, label='total-solar')
    ntotmsol = nvaltot-nnvalsol
    plt.plot(timep, ntotmsol, label='total-solar {0}'.format(2019+predict))
    plt.xticks(np.arange(0, 24, step=3), rotation=45)
    plt.ylabel('[kWh]')
    plt.xlabel('Time')
    plt.legend(loc="lower left")
    plt.savefig("figures/uiuc-duck2", dpi=300, bbox_inches="tight")

    return predict, timep, nvalsol, ntotmsol


def uiuc_hydro():
    predict, timep, nvalsol, ntotmsol = uiuc_hour()
    reactor_size = 25e3  # kW
    reactor = reactor_size*np.ones(len(nvalsol))
    h2energy = reactor-ntotmsol
    h2energy[h2energy < 0] = 0
    print(sum(h2energy))

    plt.figure()
    plt.plot(timep, ntotmsol, label='Total-Solar {0}'.format(2019+predict))
    plt.plot(timep, reactor, label='Nuclear')
    plt.plot(timep, h2energy, label='Excess')
    plt.legend(loc="upper right", bbox_to_anchor=(1.4, 1.0))
    plt.xticks(np.arange(0, 24, step=3), rotation=45)
    plt.ylabel('[kWh]')
    plt.xlabel('Time')
    plt.title('Excess of electricity')
    plt.savefig("figures/uiuc-hydro1", dpi=300, bbox_inches="tight")

    PE = reactor-h2energy  # [kWh]
    beta = PE/reactor_size  # \eta \beta P_{th} / \eta P_{th}

    eta1 = 0.33
    Pth1 = reactor_size/eta1/1e3  # [MW_{th}h]
    # print(Pth1)
    h2prod1 = h2.lte_prod_rate((1-beta)*Pth1, eta1)[1]

    tout = 850
    eta2 = h2.efficiency(tout)
    # print(eta2)
    Pth2 = reactor_size/eta2/1e3  # [MW_{th}h]
    # print(Pth2)
    h2prod2 = []
    h2prod2 = [h2.hte1_prod_rate((1-be)*Pth2, tout)[1] for be in beta]

    plt.figure()
    fig, ax1 = plt.subplots()
    ax1.plot(timep, ntotmsol, label='Total-Solar {0}'.format(2019+predict))
    ax1.plot(timep, PE, label='Nuclear')
    # ax1.legend(loc="lower right")
    # ax1.legend(loc="upper right", bbox_to_anchor=(1.4, 1.0))
    ax1.legend(loc="upper left")
    ax1.set_title("Hydrogen production", color="black")
    ax1.set_ylabel('[kWh]', color="black")
    ax1.set_ylim(0, 50e3)

    ax2 = ax1.twinx()
    ax2.plot(timep, h2prod1, label='LTE', color='red')
    ax2.plot(timep, h2prod2, '--', label='HTE', color='red')
    ax2.legend(loc="lower left")

    ax2.set_ylabel('H$_2$ [kg]', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    fig.tight_layout()

    timelabel = []
    for i in range(0, 24, 3):
        timelabel.append(timep[i])

    ax1.set_xticklabels(timelabel)
    ax1.set_xticks(timelabel)
    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    ax1.set_xlabel('Time')
    plt.savefig("figures/uiuc-hydro2", dpi=300, bbox_inches="tight")

    print(h2prod1)
    print(h2prod2)
    total1 = sum(h2prod1)
    total2 = sum(h2prod2)
    print(round(total1, 2), 'kg/day')
    print(round(total2, 2), 'kg/day')
    print(h2.electricity(1))
    elect1 = 0.6*h2.electricity(total1)
    elect2 = 0.6*h2.electricity(total2)
    print(round(elect1, 2), 'kWh/day')
    print(round(elect2, 2), 'kWh/day')

    sdistribute = '16:00:00'
    s = timep.index(sdistribute)
    distribute = 6

    level1 = (sum(ntotmsol[s:s+distribute])-elect1)/distribute
    print("level1: ", level1)
    level2 = (sum(ntotmsol[s:s+distribute])-elect2)/distribute
    print("level2: ", level2)

    new_tot_sol1 = ntotmsol.copy()
    new_tot_sol2 = ntotmsol.copy()
    new_hydro_elect1 = np.zeros(len(ntotmsol))
    new_hydro_elect2 = np.zeros(len(ntotmsol))
    for i in range(s, s+distribute):
        if new_tot_sol1[i] >= level1*1.01:
            new_tot_sol1[i] = level1*1.01
            new_hydro_elect1[i] = ntotmsol[i]-new_tot_sol1[i]
        if new_tot_sol2[i] >= level2*1.01:
            new_tot_sol2[i] = level2*1.01
            new_hydro_elect2[i] = ntotmsol[i]-new_tot_sol2[i]

    print('sanity check 1: ', sum(new_hydro_elect1))
    print('sanity check 2: ', sum(new_hydro_elect2))

    opeak = max(ntotmsol)
    print('old peak:', opeak)
    find = ntotmsol.tolist().index(max(ntotmsol))
    print('new peak1:', level1)
    print('peak reduction 1:', opeak-level1, 'kW')
    print('new peak2:', level2)
    print('peak reduction 2:', opeak-level2, 'kW')

    plt.figure()
    plt.plot(timep, ntotmsol, label='Total-Solar')
    plt.plot(timep, new_tot_sol1, label='Total-Solar-E1$_{H_2}$')
    plt.plot(timep, new_tot_sol2, label='Total-Solar-E2$_{H_2}$')
    plt.plot(timep, new_hydro_elect1, label='E1$_{H_2}$')
    plt.plot(timep, new_hydro_elect2, label='E2$_{H_2}$')
    plt.xticks(np.arange(0, 24, step=3), rotation=45)
    # plt.legend(loc="upper right", bbox_to_anchor=(1.4, 1.0), fancybox=True)
    plt.legend(loc="lower left")
    plt.annotate('old peak', xy=(find, opeak), xytext=(find+2, opeak+1e3),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    plt.ylim(0, 50e3)
    plt.ylabel('[kWh]')
    plt.xlabel('Time')
    plt.title('Peak reduction with H$_2$')
    plt.savefig("figures/uiuc-hydro3", dpi=300, bbox_inches="tight")


# Uncomment following line to plot Figure 5 and 6.
# us_year()
# Uncomment following line to plot Figure 7.
# us_hour()
# Uncomment following line to plot Figure 8.
# uiuc_hour()
# Uncomment following line to plot Figure 9 and 10.
# uiuc_hydro()
