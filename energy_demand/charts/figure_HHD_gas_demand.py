"""Create chart of correlating HDD with gas demand

Calculate HDD with weather data from a asingle weather station for the whole of the UK.abs
Correlate HDD with national gas data.

National gas data source: National Grid (2015) Seasonal Normal Demand Forecasts¨

http://www2.nationalgrid.com/UK/Industry-information/Gas-transmission-operational-data/Supplementary-Reports/

"""
import logging
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from energy_demand.plotting import plotting_program
from energy_demand.geography.weather_station_location import get_closest_station
from energy_demand.basic import conversions

def main(region_names, weather_regions, data):
    """Plot weighted HDD (HDD per Region & region pop)
    with national gas demand
    Note
    ----
    Comparison with national demand is not perfect
    because not all electricity use depends on hdd
    """
    base_yr = 2015
    # ----------------------------------
    # Read temp data and weather station
    # ----------------------------------
    weighted_daily_hdd = np.zeros((365))
    #weighted_daily_hdd_pop = np.zeros((365))

    for region_name in region_names:
        #logging.warning("==============reg_array " + str(region_name))

        # Get closest weather station to `Region`
        closest_weather_station = get_closest_station(
            data['reg_coord'][region_name]['longitude'],
            data['reg_coord'][region_name]['latitude'],
            data['weather_stations'])

        #closest_weather_station = '593' # Birmingham station
        closest_weather_region = weather_regions[closest_weather_station]

        reg_pop = data['scenario_data']['population'][base_yr][region_name]

        ##logging.warning("REGPOP: " + str(reg_pop))
        #logging.warning(closest_weather_region.weather_region_name)
        #logging.warning(closest_weather_region.rs_hdd_by)
        #logging.warning(np.sum(closest_weather_region.rs_hdd_by))

        for day in range(365):
            reg_hdd_day = closest_weather_region.rs_hdd_by[day]

            # ----------------------------
            # Weighted HDD with population
            # ----------------------------
            # WEIGHT WITH POP / TWO OPTIONS
            weighted_daily_hdd[day] += reg_hdd_day * reg_pop
            #weighted_daily_hdd_pop[day] += reg_hdd_day * reg_pop

    # -------------------------------
    # Calculate sum of HDD across all regions for every day [reg][day] --> [day]
    # -------------------------------

    # Convert to list
    weighted_daily_hdd = list(weighted_daily_hdd)
    #weighted_daily_hdd_pop = list(weighted_daily_hdd_pop)
    # -- Non daily metered gas demand in mcm == Residential heating gas
    # demand for year 2015 (Jan - Dez --> Across two excel in orig file)
    # gas demand for 365 days

    # Unit: GWh per day
    gas_demand_NDM_2015_2016_gwh = [
        2059.3346672,
        2170.0185108,
        2098.5700609,
        2129.0042078,
        2183.3908583,
        2183.3755211,
        2181.77478289999,
        2180.2661608,
        2171.9539465,
        2093.1630535,
        2123.4248103,
        2177.2511151,
        2177.4395409,
        2177.4392085,
        2175.2222323,
        2166.6139387,
        2087.285658,
        2115.1954239,
        2167.4317226,
        2166.5545797,
        2164.694753,
        2163.4837384,
        2157.386435,
        2080.9887003,
        2111.8947958,
        2166.0717924,
        2162.6456414,
        2159.295252,
        2155.8334129,
        2145.8472366,
        2061.1717803,
        2082.3903686,
        2127.0822845,
        2118.2712922,
        2113.193853,
        2107.8898595,
        2095.8412092,
        2014.9440596,
        2049.2258347,
        2107.0791469,
        2112.1583269,
        2117.2396604,
        2123.0313351,
        2122.1358234,
        2051.7066905,
        2087.3670451,
        2136.4535688,
        2132.1460485,
        2128.3906968,
        2124.2843977,
        2105.6629196,
        2019.1113801,
        2036.5569675,
        2077.2039557,
        2061.8101344,
        2046.7869234,
        2031.4318873,
        2005.2602169,
        1914.0892568,
        1922.9069295,
        1954.9594171,
        1933.6480271,
        1912.3061523,
        1890.5476499,
        1862.3706414,
        1775.6671805,
        1783.4502818,
        1814.9200643,
        1796.8545889,
        1784.4710306,
        1771.6500082,
        1752.3369114,
        1674.0247522,
        1687.99816,
        1726.2909774,
        1715.8915875,
        1705.7032311,
        1692.0716697,
        1671.1552101,
        1594.1241588,
        1603.713891,
        1636.247885,
        1620.6947572,
        1605.2659081,
        1590.0104955,
        1569.4656755,
        1494.5719877,
        1502.5278704,
        1535.2362037,
        1526.2747126,
        1513.4608687,
        1504.8484041,
        1490.7666095,
        1325.9250159,
        1316.9165572,
        1462.4932465,
        1458.1802196,
        1442.6262542,
        1426.8417784,
        1411.3589019,
        1335.8538668,
        1333.6755582,
        1356.6697705,
        1334.994619,
        1313.3468669,
        1291.2764263,
        1261.7044342,
        1187.3254679,
        1182.7090036,
        1206.201116,
        1187.9607269,
        1169.0975458,
        1150.8622665,
        1125.7570188,
        1059.6150794,
        1057.5077396,
        1081.4643041,
        1065.2552632,
        1049.0529795,
        1032.9539024,
        1007.1793016,
        914.58361712,
        897.87864486,
        880.61178046,
        909.11557166,
        890.86945346,
        871.96514751,
        853.8612021,
        791.8538562,
        775.11686001,
        832.03363633,
        814.21901615,
        799.58233329,
        784.71165334,
        761.63725303,
        707.19260431,
        704.66692408,
        729.32567359,
        716.8394616,
        704.16329367,
        692.60720982,
        673.62744381,
        625.16539826,
        616.31467523,
        606.17192685,
        636.72436643,
        625.93400599,
        615.10886486,
        605.22026297,
        557.46992056,
        551.34168138,
        578.47909485,
        570.13253752,
        561.78823047,
        553.3654021,
        538.91778989,
        498.94506464,
        500.61103512,
        529.17638846,
        522.76561207,
        516.42800386,
        510.56638091,
        496.03207692,
        456.62523814,
        456.93248186,
        484.57825041,
        478.35283027,
        472.67018165,
        467.07413108,
        452.94073995,
        415.61047941,
        417.54936646,
        447.87992936,
        444.32552312,
        440.34388174,
        436.93497309,
        425.39778941,
        390.98147195,
        393.27803263,
        422.2499116,
        418.01587597,
        413.61939995,
        409.40057065,
        397.24314025,
        362.84744615,
        363.93696426,
        393.56430501,
        390.46598983,
        387.50245828,
        384.08572436,
        373.79849944,
        341.87745791,
        344.96303388,
        375.65480602,
        374.49215286,
        372.75648874,
        371.74226978,
        361.8690835,
        331.52439876,
        335.15290392,
        366.77742567,
        365.12052235,
        364.02193295,
        362.52261752,
        352.52451205,
        322.45011946,
        326.07034766,
        357.85885375,
        357.46873061,
        356.17585959,
        356.18529447,
        347.76795445,
        318.87093053,
        323.44991194,
        357.14307241,
        358.48343406,
        359.41495,
        360.13619174,
        352.30573134,
        323.75524954,
        328.47959503,
        361.26301948,
        361.91381511,
        362.52822042,
        363.04084256,
        354.83105903,
        327.4003489,
        333.7913569,
        367.75844026,
        369.11519087,
        372.6949059,
        375.8462941,
        371.01068634,
        344.6986732,
        353.4825506,
        390.13714534,
        393.84951909,
        397.83499025,
        401.57927692,
        396.97028525,
        370.21486247,
        379.29129941,
        416.16743945,
        420.07485221,
        423.97519461,
        429.74321627,
        427.2986801,
        401.46194542,
        413.22870233,
        456.07775396,
        465.3295712,
        474.21723331,
        483.12391875,
        484.18266475,
        461.009664,
        476.92695202,
        521.59453157,
        530.84505032,
        540.18546168,
        549.72258375,
        551.25306059,
        525.45532919,
        542.29079386,
        587.07994975,
        596.34233521,
        607.50869098,
        618.97893781,
        622.86393906,
        597.19837803,
        621.39030489,
        674.41691171,
        690.65537739,
        706.66602486,
        750.44401705,
        761.5020047,
        735.3577927,
        758.94313283,
        820.97761046,
        841.64549132,
        862.82785312,
        882.73942176,
        895.8174329,
        867.22285798,
        895.86950089,
        962.4264397,
        986.21496809,
        1010.5025124,
        1034.947993,
        1049.36376,
        1016.2553526,
        1045.7292098,
        1113.1746337,
        1125.8164178,
        1141.3139762,
        1159.7889682,
        1167.2284687,
        1125.5987857,
        1158.1749163,
        1228.6271493,
        1250.8619219,
        1276.6254017,
        1300.3160004,
        1317.8170358,
        1282.8879339,
        1320.3942354,
        1394.2587548,
        1416.5190559,
        1438.5435458,
        1461.7634807,
        1479.7562971,
        1438.8539543,
        1478.9216764,
        1557.1207719,
        1573.4090718,
        1587.6655331,
        1603.6341589,
        1613.333634,
        1562.3586478,
        1600.277806,
        1679.9344601,
        1697.4619665,
        1712.8552817,
        1724.7516139,
        1724.0138982,
        1657.0594241,
        1682.3440925,
        1748.5809406,
        1752.9203251,
        1763.9782637,
        1775.1642524,
        1782.4227695,
        1722.1387718,
        1761.2175743,
        1843.516748,
        1861.6814774,
        1873.721509,
        1884.7695907,
        1889.1761128,
        1820.2893554,
        1849.3759024,
        1927.6865797,
        1941.1637845,
        1949.9179591,
        1955.9424808,
        1956.9521671,
        1880.0208367,
        1906.0644726,
        1980.6623416,
        1988.0433795,
        1992.2170495,
        2003.9919664,
        2009.5777063,
        1937.9896745,
        1964.8414739,
        2036.894857,
        2044.9981179,
        2053.3450878,
        1974.8040044,
        1814.6135915,
        1904.8874509,
        1909.229843,
        1911.2513971,
        1995.545462,
        1995.3479943,
        1997.4328038
        ]

    # Total SND (includes IUK exports and storage injection)
    gas_demand_TOTALSND_2015_2016 = [
        3017,
        3218,
        3093,
        3105,
        3281,
        3281,
        3280,
        3279,
        3246,
        3089,
        3101,
        3277,
        3278,
        3278,
        3276,
        3242,
        3085,
        3095,
        3270,
        3269,
        3267,
        3267,
        3235,
        3081,
        3093,
        3270,
        3267,
        3264,
        3261,
        3226,
        3063,
        3066,
        3234,
        3226,
        3221,
        3216,
        3179,
        3020,
        3035,
        3217,
        3222,
        3227,
        3233,
        3207,
        3056,
        3073,
        3246,
        3241,
        3237,
        3233,
        3188,
        3023,
        3022,
        3185,
        3170,
        3155,
        3139,
        3088,
        2919,
        2904,
        3058,
        3037,
        3016,
        2994,
        2941,
        2773,
        2764,
        2915,
        2897,
        2885,
        2872,
        2828,
        2673,
        2669,
        2826,
        2816,
        2805,
        2792,
        2746,
        2594,
        2586,
        2736,
        2720,
        2705,
        2690,
        2645,
        2496,
        2486,
        2635,
        2626,
        2597,
        2588,
        2537,
        2311,
        2300,
        2527,
        2541,
        2526,
        2510,
        2476,
        2340,
        2321,
        2458,
        2436,
        2413,
        2391,
        2339,
        2193,
        2175,
        2315,
        2302,
        2287,
        2274,
        2230,
        2098,
        2084,
        2223,
        2211,
        2200,
        2190,
        2142,
        1975,
        1961,
        2009,
        2064,
        2050,
        2036,
        2006,
        1885,
        1871,
        2035,
        2022,
        2012,
        2002,
        1967,
        1848,
        1834,
        1969,
        1961,
        1952,
        1945,
        1908,
        1795,
        1778,
        1848,
        1888,
        1881,
        1874,
        1850,
        1746,
        1738,
        1872,
        1867,
        1862,
        1857,
        1825,
        1721,
        1711,
        1845,
        1842,
        1839,
        1836,
        1803,
        1700,
        1689,
        1821,
        1817,
        1814,
        1811,
        1778,
        1677,
        1667,
        1801,
        1799,
        1797,
        1796,
        1766,
        1667,
        1657,
        1788,
        1786,
        1708,
        1705,
        1674,
        1584,
        1573,
        1693,
        1691,
        1690,
        1688,
        1659,
        1571,
        1562,
        1682,
        1681,
        1679,
        1678,
        1650,
        1563,
        1553,
        1673,
        1672,
        1670,
        1669,
        1637,
        1550,
        1540,
        1660,
        1659,
        1657,
        1656,
        1628,
        1542,
        1533,
        1653,
        1653,
        1652,
        1654,
        1626,
        1541,
        1531,
        1649,
        1648,
        1647,
        1646,
        1619,
        1534,
        1526,
        1646,
        1646,
        1648,
        1650,
        1625,
        1540,
        1534,
        1657,
        1659,
        1661,
        1663,
        1638,
        1551,
        1545,
        1669,
        1670,
        1672,
        1675,
        1651,
        1564,
        1560,
        1691,
        1697,
        1703,
        1709,
        1688,
        1602,
        1601,
        1735,
        1742,
        1748,
        1754,
        1733,
        1643,
        1643,
        1779,
        1784,
        1792,
        1803,
        1783,
        1692,
        1698,
        1843,
        1855,
        1867,
        2041,
        2009,
        1868,
        1873,
        2089,
        2103,
        2119,
        2132,
        2102,
        1958,
        1968,
        2188,
        2206,
        2224,
        2242,
        2212,
        2063,
        2074,
        2296,
        2303,
        2312,
        2324,
        2288,
        2130,
        2143,
        2369,
        2385,
        2404,
        2422,
        2395,
        2243,
        2261,
        2491,
        2508,
        2524,
        2541,
        2514,
        2357,
        2376,
        2612,
        2623,
        2633,
        2649,
        2619,
        2457,
        2481,
        2725,
        2743,
        2758,
        2771,
        2731,
        2552,
        2563,
        2796,
        2801,
        2812,
        2824,
        2791,
        2618,
        2642,
        2893,
        2911,
        2923,
        2935,
        2899,
        2716,
        2730,
        2979,
        2993,
        3002,
        3008,
        2969,
        2777,
        2788,
        3035,
        3042,
        3047,
        3059,
        3024,
        2835,
        2847,
        3033,
        3041,
        3050,
        2907,
        2758,
        2710,
        2715,
        2816,
        2929,
        2930,
        2932]

    # -------------------------
    # Convert GWh per day to GW
    # -------------------------
    # Conversions
    gas_demand_NDM_2015_2016_gw = list(conversions.gewhperday_to_gw(np.array(gas_demand_NDM_2015_2016_gwh)))

    # ----------------
    # Linear regression
    # ----------------
    def lin_func(x, slope, intercept):
        y = slope * x + intercept
        return y

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        gas_demand_NDM_2015_2016_gw,
        weighted_daily_hdd)

    logging.warning("Slope:         %s", str(slope))
    logging.warning("intercept:     %s", str(intercept))
    logging.warning("r_value:       %s", str(r_value))
    logging.warning("p_value:       %s", str(p_value))
    logging.warning("std_err:       %s", str(std_err))
    logging.warning("sum:           %s", str(sum(weighted_daily_hdd)))
    logging.warning("av:            %s", str(sum(weighted_daily_hdd) / len(weighted_daily_hdd)))
    logging.warning("Nr of reg:     %s", str(len(region_names)))
    logging.warning("nr of days (gray points): " + str(len(gas_demand_NDM_2015_2016_gw)))
    logging.warning("Nr of days:    " + str(len(weighted_daily_hdd)))

    # Set figure size in cm
    plt.figure(figsize=plotting_program.cm2inch(8, 8))

    # Points are days
    plt.scatter(
        gas_demand_NDM_2015_2016_gw,
        weighted_daily_hdd,
        marker='o',
        s=2.5, #MARKERSIZE
        color='black')

    # ---------------------
    # Plot regression line
    # ---------------------
    x_plot = np.linspace(10, 90, 500)
    y_plot = []
    for x in x_plot:
        y_plot.append(lin_func(x, slope, intercept))
    plt.plot(x_plot, y_plot, color='black')

    plt.xlim(0, 100)

    # ---------------------
    # Labelling
    # ---------------------
    font_additional_info = {'family': 'arial', 'color': 'black', 'weight': 'normal', 'size': 8}
    #plt.xlabel("UK non daily metered gas demand [GW]")
    #plt.ylabel("HDD * POP [mio]")
    plt.title("slope: {}, intercept: {}, r2: {})".format(round(slope, 3), round(intercept, 3), round(r_value, 3)), fontdict=font_additional_info)
    #plt.text(10, 10, "y = {} x + {}".format(round(slope, 2), round(intercept, 2)), fontdict=font_additional_info)

    # Tight layout
    plt.tight_layout()
    plt.margins(x=0)
    plt.show()
