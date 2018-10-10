"""Function to generate plots based on simulation results stored in a folder
"""
import os
import sys

from energy_demand.basic import basic_functions
from energy_demand.plotting import figs_p2
from energy_demand.plotting import fig_spatial_distribution_of_peak

def paper_II_plots(
        #path_to_folder_with_scenarios="C:/Users/cenv0553/ed/results/_multiple_TEST_two_scenarios",
        path_to_folder_with_scenarios="C:/Users/cenv0553/ed/results/_multiple_TWO",
        path_shapefile_input="C:/Users/cenv0553/ED/data/region_definitions/lad_2016_uk_simplified.shp"
    ):
    """Iterate the folders with scenario
    runs and generate PDF results of individual
    simulation runs

    Arguments
    ----------
    path_to_folder_with_scenarios : str
        Path to folders with stored results
    """

    # Chose which plots should be generated
    plot_crit_dict = {

        # Spatial map of distribution of peak and contribution in 
        # terms of overall variability
        "plot_spatial_distribution_of_peak" : True,

        # Needs to have weatehryr_stationid files in folder
        "plot_national_regional_hdd_disaggregation": False,

        # Plot weather variability for every weather station
        # of demand generated with regional HDD calculation
        "plot_weather_day_year": False,

        # Plot spatial distribution of differences in
        # variability of demand by weather variability
        # normed by population
        "plot_spatial_weather_var_peak": False,

        # Plot scenario years sorted with weather variability
        "plot_scenarios_sorted": True}

    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_folder_with_scenarios)

    scenario_names_ignored = [
        '__results_multiple_scenarios',
        '_FigII_non_regional_2015',
        '_results_PDF_figs']

    only_scenarios = []
    for scenario in scenarios:
        if scenario in scenario_names_ignored:
            pass
        else:
            only_scenarios.append(scenario)

    path_out_plots = os.path.join(path_to_folder_with_scenarios, '_results_PDF_figs')
    basic_functions.del_previous_setup(path_out_plots)
    basic_functions.create_folder(path_out_plots)

    ####################################################################
    # Plot weather station availability map
    ####################################################################


    ####################################################################
    # Plot regional vs national spatio-temporal validation
    ####################################################################
    path_regional_calculations = "C:/Users/cenv0553/ed/results/_Fig2_multiple_2015_weather_stations/_regional_calculations"
    path_non_regional_elec_2015 = os.path.abspath(
        os.path.join(path_regional_calculations, '..', "_all_stations_wy_2015"))
    path_rolling_elec_demand = os.path.join(
        "C:/Users/cenv0553/ed/energy_demand/energy_demand/config_data",
        '01-validation_datasets', '01_national_elec_2015', 'elec_demand_2015.csv')
    path_temporal_elec_validation = os.path.join(
        "C:/Users/cenv0553/ed/energy_demand/energy_demand/config_data",
        '01-validation_datasets', '02_subnational_elec', 'data_2015_elec.csv') #_domestic.csv')
    path_temporal_gas_validation = os.path.join(
        "C:/Users/cenv0553/ed/energy_demand/energy_demand/config_data",
        '01-validation_datasets', '03_subnational_gas', 'data_2015_gas.csv') #_domestic.csv')
    path_results = os.path.abspath(
        os.path.join(path_regional_calculations, '..'))
    path_out_plots = os.path.join(path_results, '_results_PDF_figs')
    basic_functions.del_previous_setup(path_out_plots)
    basic_functions.create_folder(path_out_plots)

    # Plot figure national an regional validation comparison
    figs_p2.plot_fig_spatio_temporal_validation(
        path_regional_calculations=path_regional_calculations,
        path_rolling_elec_demand=path_rolling_elec_demand,
        path_temporal_elec_validation=path_temporal_elec_validation,
        path_temporal_gas_validation=path_temporal_gas_validation,
        path_non_regional_elec_2015=path_non_regional_elec_2015,
        path_out_plots=path_out_plots)

    raise Exception
    
    ####################################################################
    # Plot spatial distribution of variability depending on weather year
    # Plot the variability of the contribution of regional peak demand
    # to national peak demand
    ####################################################################
    if plot_crit_dict['plot_spatial_distribution_of_peak']:

        # Select simulation years
        simulation_yrs = [2015, 2050]

        # Select field to plot
        field_to_plot = "std_deviation_p_demand_peak_h"
        #field_to_plot = "std_deviation_abs_demand_peak_h"

        fig_spatial_distribution_of_peak.run(
            only_scenarios,
            path_to_folder_with_scenarios,
            path_shapefile_input,
            simulation_yrs=simulation_yrs,
            field_to_plot=field_to_plot,
            fig_path=path_out_plots)


    ####################################################################
    # 
    ####################################################################
    for scenario in only_scenarios:

        # -----------
        # plot where spatio-temporal comparison between national and regional
        # -----------
        path_regional_calculations = "C:/Users/cenv0553/ed/results/_for_FIG2a/_regional_calculations"
        path_rolling_elec_demand = os.path.join(
            "C:/Users/cenv0553/ed/energy_demand/energy_demand/config_data",
            '01-validation_datasets', '01_national_elec_2015', 'elec_demand_2015.csv')
        path_temporal_elec_validation = os.path.join(
            "C:/Users/cenv0553/ed/energy_demand/energy_demand/config_data",
            '01-validation_datasets', '02_subnational_elec', 'data_2015_elec_domestic.csv')
        path_temporal_gas_validation = os.path.join(
            "C:/Users/cenv0553/ed/energy_demand/energy_demand/config_data",
            '01-validation_datasets', '03_subnational_gas', 'data_2015_gas_domestic.csv')
        path_non_regional_elec_2015 = os.path.abspath(
            os.path.join(path_regional_calculations, '..', "_non_regional_calculations_2015"))

        # Plot figure national an regional validation comparison
        '''figs_p2.plot_fig_spatio_temporal_validation(
            path_regional_calculations=path_regional_calculations,
            path_rolling_elec_demand=path_rolling_elec_demand,
            path_temporal_elec_validation=path_temporal_elec_validation,
            path_temporal_gas_validation=path_temporal_gas_validation,
            path_non_regional_elec_2015=path_non_regional_elec_2015)'''

        # -----------
        # Other plots
        # -----------
        figs_p2.main(
            os.path.join(path_to_folder_with_scenarios, scenario),
            path_shapefile_input,
            path_out_plots,
            plot_crit_dict)

    return

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    paper_II_plots(*sys.argv[1:])
