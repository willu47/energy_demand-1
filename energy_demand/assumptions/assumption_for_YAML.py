energy_demand_parameters = [
    # Building stock related parameter
    {
        "name": "assump_diff_floorarea_pp",
        "description": "Difference in floor area per person in end year compared to base year",
        "absolute_range": (0.5, 2),
        "suggested_range": (0.5, 2),
        "default": 1,
        "units": "percentage"
    },

    # Temperature related parameter
    {
        "name": "climate_change_temp_diff_month",
        "description": "Change in temperatures for every month up to end year (linear)",
        "absolute_range": (-10, 10),
        "suggested_range": (-10, 10),
        "default": [0] * 12,
        "units": "degrees °C"
    },
    {
        "name": "rs_t_base_heating_ey",
        "description": "Base temperature for residential space heating in end year",
        "absolute_range": (10, 18),
        "suggested_range": (10, 18),
        "default": 15.5,
        "units": "degrees °C"
    },

    # Technology related parameters
    {
        "name": "efficiency_achieving_factor",
        "description": "How much of the potential efficiency improvements up to end year can be reaped",
        "absolute_range": (0,1),
        "suggested_range": (0,1),
        "default": 0,
        "units": "percentage"
    }
]

"""
    '''# Bool parameter (mode of running model)
    {
        "name": "mode_constrained",
        "description": "Mode definition for running the model. If unconstrained mode (False), heat demand is provided per technology. If True, heat is delievered with fueltype",
        "absolute_range": (),
        "suggested_range": (),
        "default": False,
        "units": "bool"
    },'''
"""