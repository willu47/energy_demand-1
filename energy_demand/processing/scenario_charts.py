"""Generate charts from multiple scenarios
"""
import os
import logging
from energy_demand.read_write import read_data
from energy_demand.basic import date_prop
from energy_demand.plotting import plotting_multiple_scenarios
from energy_demand.basic import basic_functions

def process_scenarios(path_to_scenarios, year_to_model=2015):
    """Iterate folder with scenario results and plot charts

    Arguments
    ----------
    path_to_scenarios : str
        Path to folders with stored results
    year_to_model : int, default=2015
        Year of base year
    """
    # Delete folder results if existing
    path_result_folder = os.path.join(
        path_to_scenarios, "_results_multiple_scenarios")

    basic_functions.delete_folder(path_result_folder)

    seasons = date_prop.get_season(
        year_to_model=year_to_model)

    model_yeardays_daytype, _, _ = date_prop.get_model_yeardays_daytype(
        year_to_model=year_to_model)

    # Get all folders with scenario run results (name of folder is scenario)
    scenarios = os.listdir(path_to_scenarios)

    # -------------------------------
    # Iterate folders and get results
    # -------------------------------
    scenario_data = {}
    for scenario in scenarios:

        # Add scenario name to folder
        scenario_data[scenario] = {}

        path_to_result_files = os.path.join(
            path_to_scenarios,
            scenario,
            '_result_data',
            'model_run_results_txt')

        scenario_data[scenario] = read_data.read_in_results(
            path_runs=path_to_result_files,
            seasons=seasons,
            model_yeardays_daytype=model_yeardays_daytype)

    # -----------------------
    # Generate result folder
    # -----------------------
    basic_functions.create_folder(path_result_folder)

    # ------------
    # Create plots
    # ------------

    # -------------------------------
    # Generate plot with heat pump ranges
    # -------------------------------
    heat_pump_range_plot = False
    if heat_pump_range_plot:
        plotting_multiple_scenarios.plot_heat_pump_chart(
            scenario_data,
            fig_name=os.path.join(path_result_folder, "tot_y_multiple.pdf"),
            fueltype_str_input='electricity',
            plotshow=True)

    # -------------------------------
    # Plot total demand for every year in line plot
    # -------------------------------
    plotting_multiple_scenarios.plot_tot_y_over_time(
        scenario_data,
        fig_name=os.path.join(path_result_folder, "tot_y_multiple.pdf"),
        plotshow=False)

    # -------------------------------
    # Plot for all regions demand for every year in line plot
    # -------------------------------
    plotting_multiple_scenarios.plot_reg_y_over_time(
        scenario_data,
        fig_name=os.path.join(path_result_folder, "reg_y_multiple.pdf"),
        plotshow=False)

    # -------------------------------
    # Plot comparison of total demand for a year for all LADs (scatter plot)
    # -------------------------------
    plotting_multiple_scenarios.plot_LAD_comparison_scenarios(
        scenario_data,
        year_to_plot=2050,
        fig_name=os.path.join(path_result_folder, "LAD_multiple.pdf"),
        plotshow=False)

    # -------------------------------
    # Plot different profiles in radar plot (spider plot)
    # -------------------------------
    plotting_multiple_scenarios.plot_radar_plots_average_peak_day(
        scenario_data,
        year_to_plot=2050,
        fig_name=os.path.join(path_result_folder),
        plotshow=False)

    # ----------------------
    # Plot peak hour of all fueltypes for different scenario
    # ----------------------
    plotting_multiple_scenarios.plot_tot_y_peak_hour(
        scenario_data,
        fig_name=os.path.join(path_result_folder, "tot_y_peak_h_electricity.pdf"),
        fueltype_str_input='electricity',
        plotshow=False)
    print("Finished processing multiple scenario")
    return

# Generate plots across all scenarios
process_scenarios(os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_eff_factor_example"))
#process_scenarios(os.path.abspath("C:/Users/cenv0553/ED/_multiple_results_hp_example"))