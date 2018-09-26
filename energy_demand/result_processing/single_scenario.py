"""Read in model results and plot results
"""
import os
from collections import defaultdict

from energy_demand.read_write import data_loader, read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_results, result_mapping
from energy_demand.basic import logger_setup, basic_functions
from energy_demand.basic import lookup_tables
from energy_demand.plotting import fig_weather_variability_priod

def main(
        path_data_energy_demand,
        path_shapefile_input,
        plot_crit_dict,
        base_yr,
        comparison_year
    ):
    """Read in all results and plot PDFs

    Arguments
    ----------
    path_data_energy_demand : str
        Path to results
    path_shapefile_input : str
        Path to shapefile
    plot_crit_dict : dict
        Criteria to select plots to plot
    base_yr : int
        Base year
    comparison_year : int
        Year to generate comparison plots
    """
    print("...Start creating plots")

    # Get all yealy results
    all_result_folders = os.listdir(path_data_energy_demand)

    weather_yrs = []
    for result_folder in all_result_folders:
        try:
            weather_yr = int(result_folder)
            weather_yrs.append(weather_yr)
        except ValueError:
            pass


    # ------------------------------
    # Plotting weather variability results
    # ------------------------------
    if plot_crit_dict['plot_weather_day_year']:

        # Container to store all data of weather years
        weather_yr_container = defaultdict(dict)

        data = {}
        #data['local_paths'] = data_loader.get_local_paths(path_data_energy_demand_weather_yr)
        #data['result_paths'] = data_loader.get_result_paths(os.path.join(path_data_energy_demand_weather_yr))
        data['lookups'] = lookup_tables.basic_lookups()

        path_out_plots = os.path.join(path_data_energy_demand, "PDF_weather_varability")

        basic_functions.del_previous_setup(path_out_plots)
        basic_functions.create_folder(path_out_plots)

        data['enduses'], data['assumptions'], data['reg_nrs'], data['regions'] = data_loader.load_ini_param(
            os.path.join(path_data_energy_demand))

        # Other information is read in
        data['assumptions']['seasons'] = date_prop.get_season(year_to_model=2015)
        data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_yeardays_daytype(year_to_model=2015)

        for weather_yr in weather_yrs:

            path_data_energy_demand_weather_yr = os.path.join(path_data_energy_demand, str(weather_yr))

            # --------------------------------------------
            # Reading in results from different model runs
            # --------------------------------------------
            results_container = read_data.read_in_results(
                os.path.join(path_data_energy_demand_weather_yr, 'model_run_results_txt'),
                data['assumptions']['seasons'],
                data['assumptions']['model_yeardays_daytype'])

            # Store data in weather container
            aggregated_data_enduses = fig_weather_variability_priod.sum_all_enduses_fueltype(
                results_container['results_enduse_every_year'])

            weather_yr_container['tot_enduses'][weather_yr] = aggregated_data_enduses

        # plot over period of time across all weather scenario
        fig_weather_variability_priod.run(
            data_input=weather_yr_container['tot_enduses'],
            fueltype_str='electricity',
            simulation_yr_to_plot=2015, # Simulation year to plot
            #period_h=list(range(100,200)), #period to plot
            period_h=list(range(200,500)), #period to plot
            fig_name=os.path.join(
                path_out_plots, "weather_var_period.pdf"))
    else:
        pass

    # Execute script to generate PDF results
    for weather_yr in weather_yrs:

        path_data_energy_demand_weather_yr = os.path.join(path_data_energy_demand, str(weather_yr))

        # Set up logger
        #logger_setup.set_up_logger(
        #    os.path.join(
        #        path_data_energy_demand_weather_yr, "plotting.log"))
        # Simulation information is read in from .ini file for results
        data['enduses'], data['assumptions'], data['reg_nrs'], data['regions'] = data_loader.load_ini_param(
            os.path.join(path_data_energy_demand))

        # ------------------
        # Load necessary inputs for read in
        # ------------------
        data = {}
        data['local_paths'] = data_loader.get_local_paths(
            path_data_energy_demand_weather_yr)
        data['result_paths'] = data_loader.get_result_paths(
            os.path.join(path_data_energy_demand_weather_yr))
        data['lookups'] = lookup_tables.basic_lookups()

        # ---------------
        # Folder cleaning
        # ---------------
        basic_functions.del_previous_setup(data['result_paths']['data_results_PDF'])
        basic_functions.del_previous_setup(data['result_paths']['data_results_shapefiles'])
        basic_functions.create_folder(data['result_paths']['data_results_PDF'])
        basic_functions.create_folder(data['result_paths']['data_results_shapefiles'])
        basic_functions.create_folder(data['result_paths']['individual_enduse_lp'])

        # Simulation information is read in from .ini file for results
        data['enduses'], data['assumptions'], data['reg_nrs'], data['regions'] = data_loader.load_ini_param(
            os.path.join(path_data_energy_demand))

        # Other information is read in
        data['assumptions']['seasons'] = date_prop.get_season(year_to_model=2015)
        data['assumptions']['model_yeardays_daytype'], data['assumptions']['yeardays_month'], data['assumptions']['yeardays_month_days'] = date_prop.get_yeardays_daytype(year_to_model=2015)

        # Read scenario data
        data['scenario_data'] = {}

        data['scenario_data']['population'] = read_data.read_scenaric_population_data(
            os.path.join(path_data_energy_demand, 'model_run_pop'))

        # --------------------------------------------
        # Reading in results from different model runs
        # --------------------------------------------
        results_container = read_data.read_in_results(
            data['result_paths']['data_results_model_runs'],
            data['assumptions']['seasons'],
            data['assumptions']['model_yeardays_daytype'])

        # ------------------------------
        # Plotting other results
        # ------------------------------
        plotting_results.run_all_plot_functions(
            results_container,
            data['reg_nrs'],
            data['regions'],
            data['lookups'],
            data['result_paths'],
            data['assumptions'],
            data['enduses'],
            plot_crit=plot_crit_dict,
            base_yr=base_yr,
            comparison_year=comparison_year)

        # ------------------------------
        # Plotting spatial results
        # ------------------------------
        if plot_crit_dict['spatial_results']:
            result_mapping.create_geopanda_files(
                data,
                results_container,
                data['result_paths']['data_results_shapefiles'],
                data['regions'],
                data['lookups']['fueltypes_nr'],
                data['lookups']['fueltypes'],
                path_shapefile_input,
                plot_crit_dict,
                base_yr=base_yr)

    print("===================================")
    print("... finished reading and plotting results")
    print("===================================")
