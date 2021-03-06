"""
Weather Region
===============
Depending on the number of weather stations, a ``WeatherRegion``
is generated per weather station. Within this regions,
regional load profiles are calculated.

"""
from datetime import date
import uuid
import numpy as np
from energy_demand.technologies import technological_stock
from energy_demand.basic import date_handling
from energy_demand.profiles import load_profile
from energy_demand.profiles import hdd_cdd
'''# pylint: disable=I0011,C0321,C0301,C0103,C0325,no-member'''

class WeatherRegion(object):
    """WeaterRegion

    Parameters
    ----------
    weather_region_name : str
        Unique identifyer of region_name
    data : dict
        Dictionary containing data
    modeltype : str
        Model type

    Note
    ----
    - For each region_name, a technology stock is defined with help of
      regional temperature data technology specific
    - regional specific fuel shapes are assigned to technologies
    """
    def __init__(self, weather_region_name, data, modeltype):
        """Constructor
        """
        self.weather_region_name = weather_region_name

        # Temperatures
        temp_by = data['temperature_data'][weather_region_name][data['sim_param']['base_yr']]
        temp_cy = data['temperature_data'][weather_region_name][data['sim_param']['curr_yr']]

        rs_t_base_heating_cy = hdd_cdd.sigm_temp(
            data['sim_param'], data['assumptions'], 'rs_t_base_heating')
        rs_t_base_cooling_cy = hdd_cdd.sigm_temp(
            data['sim_param'], data['assumptions'], 'rs_t_base_cooling')
        rs_t_base_heating_by = hdd_cdd.sigm_temp(
            data['sim_param'], data['assumptions'], 'rs_t_base_heating')
        rs_t_base_cooling_by = hdd_cdd.sigm_temp(
            data['sim_param'], data['assumptions'], 'rs_t_base_cooling')
        ss_t_base_heating_cy = hdd_cdd.sigm_temp(
            data['sim_param'], data['assumptions'], 'ss_t_base_heating')
        ss_t_base_cooling_cy = hdd_cdd.sigm_temp(
            data['sim_param'], data['assumptions'], 'ss_t_base_cooling')
        ss_t_base_heating_by = hdd_cdd.sigm_temp(
            data['sim_param'], data['assumptions'], 'ss_t_base_heating')
        ss_t_base_cooling_by = hdd_cdd.sigm_temp(
            data['sim_param'], data['assumptions'], 'ss_t_base_cooling')

        # -------------------
        # Technology stock
        # -------------------
        if modeltype == 'is_submodel':
            self.is_tech_stock = technological_stock.TechStock(
                'is_tech_stock',
                data,
                temp_by,
                temp_cy,
                data['assumptions']['ss_t_base_heating']['base_yr'],
                data['is_all_enduses'],
                ss_t_base_heating_cy,
                data['assumptions']['is_specified_tech_enduse_by']
                )
        elif modeltype == 'rs_submodel':
            self.rs_tech_stock = technological_stock.TechStock(
                'rs_tech_stock',
                data,
                temp_by,
                temp_cy,
                data['assumptions']['rs_t_base_heating']['base_yr'],
                data['rs_all_enduses'],
                rs_t_base_heating_cy,
                data['assumptions']['rs_specified_tech_enduse_by']
                )
        elif modeltype == 'ss_submodel':
            self.ss_tech_stock = technological_stock.TechStock(
                'ss_tech_stock',
                data,
                temp_by,
                temp_cy,
                data['assumptions']['ss_t_base_heating']['base_yr'],
                data['ss_all_enduses'],
                ss_t_base_heating_cy,
                data['assumptions']['ss_specified_tech_enduse_by']
                )

        # -------------------
        # Load profiles
        # -------------------
        if modeltype == 'rs_submodel':

            # --------Profiles
            self.rs_load_profiles = load_profile.LoadProfileStock("rs_load_profiles")

            # --------HDD/CDD
            rs_hdd_by, _ = hdd_cdd.get_reg_hdd(temp_by, rs_t_base_heating_by)
            rs_cdd_by, _ = hdd_cdd.get_reg_cdd(temp_by, rs_t_base_cooling_by)
            rs_hdd_cy, rs_fuel_shape_heating_yd = hdd_cdd.get_reg_hdd(temp_cy, rs_t_base_heating_cy)
            rs_cdd_cy, _ = hdd_cdd.get_reg_cdd(temp_cy, rs_t_base_cooling_cy)

            # Climate change correction factors
            # (Assumption: Demand for heat correlates directly with fuel)
            try:
                self.rs_heating_factor_y = np.nan_to_num(
                    1.0 / float(np.sum(rs_hdd_by))) * np.sum(rs_hdd_cy)
                self.rs_cooling_factor_y = np.nan_to_num(
                    1.0 / float(np.sum(rs_cdd_by))) * np.sum(rs_cdd_cy)
            except ZeroDivisionError:
                self.rs_heating_factor_y = 1
                self.rs_cooling_factor_y = 1

            # yd peak factors for heating and cooling
            rs_peak_yd_heating_factor = self.get_shape_peak_yd_factor(rs_hdd_cy)
            #rs_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(rs_cdd_cy)

            # --Specific heating technologies for residential sector
            rs_profile_storage_heater_yh, _ = self.get_shape_heating_boilers_yh(
                data, rs_fuel_shape_heating_yd, 'rs_profile_heating_storage_dh')
            rs_profile_elec_heater_yh, _ = self.get_shape_heating_boilers_yh(
                data, rs_fuel_shape_heating_yd, 'rs_profile_heating_second_heating_dh')
            # boiler, non-peak
            rs_profile_boilers_yh, rs_profile_boilers_y_dh = self.get_shape_heating_boilers_yh(
                data, rs_fuel_shape_heating_yd, 'rs_shapes_heating_boilers_dh')
            # heat pumps, non-peak
            rs_fuel_shape_hp_yh, rs_fuel_shape_hp_y_dh = self.get_fuel_shape_heating_hp_yh(
                data, self.rs_tech_stock, rs_hdd_cy, 'rs_shapes_heating_heat_pump_dh')

            rs_fuel_shape_hybrid_tech_yh = self.get_shape_heating_hybrid_yh(
                self.rs_tech_stock,
                'rs_space_heating',
                rs_profile_boilers_y_dh,
                rs_fuel_shape_hp_y_dh,
                rs_fuel_shape_heating_yd,
                'hybrid_gas_electricity'
                )

            # Cooling residential
            #rs_fuel_shape_cooling_yh = self.get_shape_cooling_yh(
            # data, rs_fuel_shape_cooling_yd, 'rs_shapes_cooling_dh')

            # Heating boiler
            self.rs_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_const'],
                enduses=['rs_space_heating', 'rs_water_heating'],
                shape_yd=rs_fuel_shape_heating_yd,
                shape_yh=rs_profile_boilers_yh,
                enduse_peak_yd_factor=rs_peak_yd_heating_factor,
                shape_peak_dh=data['rs_shapes_heating_boilers_dh']['peakday']
                )

            # Electric heating, primary...(storage)
            self.rs_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['primary_heating_electricity'],
                enduses=['rs_space_heating'],
                shape_yd=rs_fuel_shape_heating_yd,
                shape_yh=rs_profile_storage_heater_yh,
                enduse_peak_yd_factor=rs_peak_yd_heating_factor,
                shape_peak_dh=data['rs_profile_heating_storage_dh']['peakday']
                )

            # Electric heating, secondary...
            self.rs_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['secondary_heating_electricity'],
                enduses=['rs_space_heating', 'rs_water_heating'],
                shape_yd=rs_fuel_shape_heating_yd,
                shape_yh=rs_profile_elec_heater_yh,
                enduse_peak_yd_factor=rs_peak_yd_heating_factor,
                shape_peak_dh=data['rs_profile_heating_second_heating_dh']['peakday']
                )

            # Hybrid heating
            self.rs_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_hybrid'],
                enduses=['rs_space_heating', 'rs_water_heating'],
                shape_yd=rs_fuel_shape_heating_yd,
                shape_yh=rs_fuel_shape_hybrid_tech_yh,
                enduse_peak_yd_factor=rs_peak_yd_heating_factor
                )

            # Heat pump heating
            self.rs_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_temp_dep'],
                enduses=['rs_space_heating', 'rs_water_heating'],
                shape_yd=rs_fuel_shape_heating_yd,
                shape_yh=rs_fuel_shape_hp_yh,
                enduse_peak_yd_factor=rs_peak_yd_heating_factor,
                shape_peak_dh=data['rs_shapes_heating_heat_pump_dh']['peakday']
                )

        elif modeltype == 'ss_submodel':

            # --------Profiles
            self.ss_load_profiles = load_profile.LoadProfileStock("ss_load_profiles")

            # --------HDD/CDD
            ss_hdd_by, _ = hdd_cdd.get_reg_hdd(temp_by, ss_t_base_heating_by)
            ss_cdd_by, _ = hdd_cdd.get_reg_cdd(temp_by, ss_t_base_cooling_by)

            ss_hdd_cy, ss_fuel_shape_heating_yd = hdd_cdd.get_reg_hdd(temp_cy, rs_t_base_heating_cy)
            ss_cdd_cy, _ = hdd_cdd.get_reg_cdd(temp_cy, ss_t_base_cooling_cy)

            try:
                self.ss_heating_factor_y = np.nan_to_num(
                    1.0 / float(np.sum(ss_hdd_by))) * np.sum(ss_hdd_cy)
                self.ss_cooling_factor_y = np.nan_to_num(
                    1.0 / float(np.sum(ss_cdd_by))) * np.sum(ss_cdd_cy)
            except ZeroDivisionError:
                self.ss_heating_factor_y = 1
                self.ss_cooling_factor_y = 1

            ss_peak_yd_heating_factor = self.get_shape_peak_yd_factor(ss_hdd_cy)
            #ss_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(ss_cdd_cy)

            # --Heating technologies for service sector
            # (the heating shape follows the gas shape of aggregated sectors)
            ss_fuel_shape_any_tech, ss_fuel_shape = self.ss_get_sector_enduse_shape(
                data, ss_fuel_shape_heating_yd, 'ss_space_heating')

            # Cooling service
            #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, ss_fuel_shape_cooling_yd, 'ss_shapes_cooling_dh') # Service cooling
            #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, ss_fuel_shape_heating_yd, 'ss_shapes_cooling_dh') # Service cooling #USE HEAT YD BUT COOLING SHAPE
            #ss_fuel_shape_cooling_yh = self.get_shape_cooling_yh(data, load_profile.absolute_to_relative(ss_hdd_cy + ss_cdd_cy), 'ss_shapes_cooling_dh') # hdd & cdd

            # Hybrid
            ss_profile_hybrid_gas_elec_yh = self.get_shape_heating_hybrid_yh(
                self.ss_tech_stock,
                'ss_space_heating',
                ss_fuel_shape,
                ss_fuel_shape,
                ss_fuel_shape_heating_yd,
                'hybrid_gas_electricity')

            self.ss_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_const'],
                enduses=['ss_space_heating', 'ss_water_heating'],
                sectors=data['ss_sectors'],
                shape_yd=ss_fuel_shape_heating_yd,
                shape_yh=ss_fuel_shape_any_tech,
                enduse_peak_yd_factor=ss_peak_yd_heating_factor,
                shape_peak_dh=data['ss_shapes_dh']
                )

            self.ss_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['primary_heating_electricity'],
                enduses=['ss_space_heating'],
                sectors=data['ss_sectors'],
                shape_yd=ss_fuel_shape_heating_yd,
                shape_yh=ss_fuel_shape_any_tech,
                enduse_peak_yd_factor=ss_peak_yd_heating_factor,
                shape_peak_dh=data['rs_profile_heating_storage_dh']['peakday']
                )

            self.ss_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['secondary_heating_electricity'],
                enduses=['rs_space_heating', 'rs_water_heating'],
                sectors=data['ss_sectors'],
                shape_yd=ss_fuel_shape_heating_yd,
                shape_yh=ss_fuel_shape_any_tech,
                enduse_peak_yd_factor=ss_peak_yd_heating_factor
                )

            self.ss_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_hybrid'],
                enduses=['ss_space_heating', 'ss_water_heating'],
                sectors=data['ss_sectors'],
                shape_yd=ss_fuel_shape_heating_yd,
                shape_yh=ss_profile_hybrid_gas_elec_yh,
                enduse_peak_yd_factor=ss_peak_yd_heating_factor,
                )

            self.ss_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_temp_dep'],
                enduses=['ss_space_heating', 'ss_water_heating'],
                sectors=data['ss_sectors'],
                shape_yd=ss_fuel_shape_heating_yd,
                shape_yh=ss_fuel_shape_any_tech,
                enduse_peak_yd_factor=ss_peak_yd_heating_factor
                )

        elif modeltype == 'is_submodel':

            # --------Profiles
            self.is_load_profiles = load_profile.LoadProfileStock("is_load_profiles")

            # --------HDD/CDD
            is_hdd_by, _ = hdd_cdd.get_reg_hdd(temp_by, ss_t_base_heating_by)
            is_cdd_by, _ = hdd_cdd.get_reg_cdd(temp_by, ss_t_base_cooling_by)

            # Take same base temperature as for service sector
            is_hdd_cy, is_fuel_shape_heating_yd = hdd_cdd.get_reg_hdd(temp_cy, ss_t_base_heating_cy)
            is_cdd_cy, _ = hdd_cdd.get_reg_cdd(temp_cy, ss_t_base_cooling_cy)

            try:
                self.is_heating_factor_y = np.nan_to_num(1.0 / float(np.sum(is_hdd_by))) * np.sum(is_hdd_cy)
                self.is_cooling_factor_y = np.nan_to_num(1.0 / float(np.sum(is_cdd_by))) * np.sum(is_cdd_cy)
            except ZeroDivisionError:
                self.is_heating_factor_y = 1
                self.is_cooling_factor_y = 1

            is_peak_yd_heating_factor = self.get_shape_peak_yd_factor(is_hdd_cy)
            #is_peak_yd_cooling_factor = self.get_shape_peak_yd_factor(is_cdd_cy)

            # --Heating technologies for service sector (the heating shape follows
            # the gas shape of aggregated sectors)
            #Take from service sector
            is_fuel_shape_any_tech, _ = self.ss_get_sector_enduse_shape(
                data, is_fuel_shape_heating_yd, 'ss_space_heating')

            self.is_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_const'],
                enduses=['is_space_heating'],
                sectors=data['is_sectors'],
                shape_yd=is_fuel_shape_heating_yd,
                shape_yh=is_fuel_shape_any_tech,
                enduse_peak_yd_factor=is_peak_yd_heating_factor
                )

            self.is_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['primary_heating_electricity'],
                enduses=['is_space_heating'],
                sectors=data['is_sectors'],
                shape_yd=is_fuel_shape_heating_yd,
                enduse_peak_yd_factor=is_peak_yd_heating_factor,
                shape_yh=is_fuel_shape_any_tech
                )

            self.is_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['secondary_heating_electricity'],
                enduses=['is_space_heating'],
                sectors=data['is_sectors'],
                shape_yd=is_fuel_shape_heating_yd,
                shape_yh=is_fuel_shape_any_tech,
                enduse_peak_yd_factor=is_peak_yd_heating_factor,
                )

            self.is_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_hybrid'],
                enduses=['is_space_heating'],
                sectors=data['is_sectors'],
                shape_yd=is_fuel_shape_heating_yd,
                shape_yh=is_fuel_shape_any_tech,
                enduse_peak_yd_factor=is_peak_yd_heating_factor,
                )

            self.is_load_profiles.add_load_profile(
                unique_identifier=uuid.uuid4(),
                technologies=data['assumptions']['technology_list']['tech_heating_temp_dep'],
                enduses=['is_space_heating'],
                sectors=data['is_sectors'],
                shape_yd=is_fuel_shape_heating_yd,
                shape_yh=is_fuel_shape_any_tech,
                enduse_peak_yd_factor=is_peak_yd_heating_factor
                )

    @classmethod
    def get_shape_heating_hybrid_yh(cls, tech_stock, enduse, fuel_shape_boilers_y_dh, fuel_shape_hp_y_dh, fuel_shape_heating_yd, hybrid_tech):
        """Use yd shapes and dh shapes of hybrid technologies to generate yh shape

        Parameters
        ----------
        tech_stock : TODO
        enduse :
        fuel_shape_boilers_y_dh : array
            Fuel shape of boilers (dh) for evey day in a year
        fuel_shape_hp_y_dh : array
            Fuel shape of heat pumps (dh) for every day in a year
        fuel_shape_heating_yd : array
            Fuel shape for assign demand to day in a year (yd)
        tech_low_temp : string
            Low temperature technology
        tech_high_temp : string
            High temperature technology

        Return
        -------
        fuel_shape_yh : array
            Share of yearly fuel for hybrid technology

        Note
        -----
        This is for hybrid_gas_elec technology

        The shapes are the same for any hybrid technology with boiler and heat pump
        """
        # Create dh shapes for every day from relative dh shape of hybrid technologies
        fuel_shape_hybrid_y_dh = load_profile.get_hybrid_fuel_shapes_y_dh(
            fuel_shape_boilers_y_dh=fuel_shape_boilers_y_dh,
            fuel_shape_hp_y_dh=fuel_shape_hp_y_dh,
            tech_low_high_p=tech_stock.get_tech_attr(
                enduse, hybrid_tech, 'service_distr_hybrid_h_p')
            )

        # Calculate yh fuel shape
        fuel_shape_yh = fuel_shape_hybrid_y_dh * fuel_shape_heating_yd[:, np.newaxis]

        return fuel_shape_yh

    @classmethod
    def get_shape_peak_yd_factor(cls, demand_yd):
        """From yd shape calculate maximum relative yearly service demand which is provided in a day

        Parameters
        ----------
        demand_yd : shape
            Demand for energy service for every day in year

        Return
        ------
        max_factor_yd : float
            yd maximum factor

        Note
        -----
        If the shape is taken from heat and cooling demand the assumption is made that
        HDD and CDD are directly proportional to fuel usage
        """
        tot_demand_y = np.sum(demand_yd) # Total yearly demand
        max_demand_d = np.max(demand_yd) # Maximum daily demand
        max_factor_yd = (1.0 / tot_demand_y) * max_demand_d

        return max_factor_yd

    @classmethod
    def get_fuel_shape_heating_hp_yh(cls, data, tech_stock, rs_hdd_cy, tech):
        """Convert daily shapes to houly based on robert sansom daily load for heatpump TODO

        This is for non-peak.

        Parameters
        ---------
        data : dict
            data
        tech_stock : object
            Technology stock
        rs_hdd_cy : array
            Heating Degree Days (365, 1)
        tech : str
            Technology to get profile

        Returns
        -------
        hp_shape : array
            Daily shape how yearly fuel can be distributed to hourly
        shape_y_dh : array
            Shape of fuel shape for every day in a year (total sum = 365)

        Note
        ----
        The service is calculated based on the efficiency of gas
        heat pumps ``av_heat_pump_gas``

        The daily heat demand is converted to daily fuel depending on efficiency of
        heatpumps (assume if 100% heat pumps). In a final step the hourly fuel
        is converted to percentage of yearly fuel demand.

        Furthermore the assumption is made that the shape is the same for all fueltypes.

        The daily fuel demand curve for heat pumps taken from:
        *Sansom, R. (2014). Decarbonising low grade heat for low carbon future.
        Dissertation, Imperial College London.*
        """
        shape_yh_hp = np.zeros((365, 24))
        shape_y_dh = np.zeros((365, 24))

        daily_fuel_profile_holiday = data[tech]['holiday'] / np.sum(data[tech]['holiday'])
        daily_fuel_profile_workday = data[tech]['workday'] / np.sum(data[tech]['workday'])

        tech_eff = tech_stock.get_tech_attr('rs_space_heating', 'heat_pumps_gas', 'eff_cy')

        for day, date_gasday in enumerate(data['sim_param']['list_dates']):

            # Take respectve daily fuel curve depending on weekday or weekend
            # from Robert Sansom for heat pumps
            if date_handling.get_weekday_type(date_gasday) == 'holiday':
                daily_fuel_profile = daily_fuel_profile_holiday
            else:
                daily_fuel_profile = daily_fuel_profile_workday

            # Calculate weighted average daily efficiency of heat pump
            average_eff_d = 0
            for hour, heat_share_h in enumerate(daily_fuel_profile):
                # Hourly heat demand * heat pump efficiency
                average_eff_d += heat_share_h * tech_eff[day][hour]

            # Convert daily service demand to fuel (Heat demand / efficiency = fuel)
            hp_daily_fuel = rs_hdd_cy[day] / average_eff_d

            # Fuel distribution within day
            fuel_shape_d = hp_daily_fuel * daily_fuel_profile

            # Distribute fuel of day according to fuel load curve
            shape_yh_hp[day] = fuel_shape_d

            # Add normalised daily fuel curve
            shape_y_dh[day] = load_profile.absolute_to_relative_without_nan(fuel_shape_d)

        # Convert absolute hourly fuel demand to relative fuel demand within a year
        shape_yh = load_profile.absolute_to_relative(shape_yh_hp)

        return shape_yh, shape_y_dh

    @classmethod
    def get_shape_cooling_yh(cls, data, cooling_shape, tech):
        """Convert daily shape to hourly based on robert sansom daily load for boilers

        Parameters
        ---------
        data : dict
            data
        cooling_shape : array
            Cooling profile
        tech : str
            Technology to get profile

        Returns
        -------
        shape_yd_cooling_tech : array
            Shape of cooling devices

        Note
        ----
        The daily cooling demand (calculated with cdd) is distributed within the day
        fuel demand curve from:

        - **Residential**: Taken from *Denholm, P., Ong, S., & Booten, C. (2012).
          Using Utility Load Data to Estimate Demand for Space Cooling and
          Potential for Shiftable Loads, (May), 23.
          Retrieved from http://www.nrel.gov/docs/fy12osti/54509.pdf*

        - **Service**: *Knight, Dunn, Environments Carbon and Cooling in
          Uk Office Environments*
        """
        shape_yd_cooling_tech = data[tech] * cooling_shape[:, np.newaxis]

        return shape_yd_cooling_tech

    @classmethod
    def ss_get_sector_enduse_shape(cls, data, heating_shape, enduse):
        """Read generic shape for all technologies in a service sector enduse

        Parameters
        ---------
        data : dict
            data
        heating_shape : array
            Daily (yd) service demand shape for heat (percentage of yearly
            heat demand for every day)
        enduse : str
            Enduse where technology is used

        Returns
        -------
        shape_boilers_yh : array
            Shape how yearly fuel can be distributed to hourly (yh) (total sum == 1)
        shape_boilers_y_dh : array
            Shape of distribution of fuel within every day of a year (total sum == 365)
        """
        shape_yh_generic_tech = np.zeros((365, 24))

        if enduse not in data['ss_all_tech_shapes_dh']:
            pass
        else:
            shape_non_peak_y_dh = data['ss_all_tech_shapes_dh'][enduse]['shape_non_peak_y_dh']

            shape_yh_generic_tech = heating_shape[:, np.newaxis] * shape_non_peak_y_dh
            shape_y_dh_generic_tech = shape_non_peak_y_dh

        return shape_yh_generic_tech, shape_y_dh_generic_tech

    @classmethod
    def get_shape_heating_boilers_yh(cls, data, heating_shape, tech_to_get_shape):
        """Convert daily fuel shape to hourly based on robert sansom daily load for boilers

        Parameters
        ---------
        data : dict
            data
        heating_shape : array
            Profile (yh) for heat (percentage of yearly heat demand for every day)
        tech_to_get_shape : str
            Technology

        Returns
        -------
        shape_boilers_yh : array
            Shape how yearly fuel can be distributed to hourly (yh) (total sum == 1)
        shape_boilers_y_dh : array
            Shape of distribution of fuel within every day of a year (total sum == 365)

        Note
        ----
        - The assumption is made that boilers have constant efficiency for every hour in a year.
          Therefore the fuel demand correlates directly with the heat service demand.

        -  Furthermore the assumption is made that the profile is the same for all fueltypes.

        The daily heat demand (calculated with hdd) is distributed within the day
        fuel demand curve for boilers from:

        *Sansom, R. (2014). Decarbonising low grade heat for low carbon
        future. Dissertation, Imperial College London.*
        """
        shape_boilers_yh = np.zeros((365, 24))
        shape_boilers_y_dh = np.zeros((365, 24))

        list_dates = date_handling.fullyear_dates(
            start=date(data['sim_param']['base_yr'], 1, 1),
            end=date(data['sim_param']['base_yr'], 12, 31)
            )

        for day, date_gasday in enumerate(list_dates):
            weekday_type = date_handling.get_weekday_type(date_gasday)

            # Take respectve daily fuel curve depending on weekday or weekend
            if weekday_type == 'holiday': # Wkend Hourly gas shape.
                shape_boilers_yh[day] = heating_shape[day] * data[tech_to_get_shape]['holiday']
                shape_boilers_y_dh[day] = data[tech_to_get_shape]['holiday']
            else: # Wkday Hourly gas shape.
                shape_boilers_yh[day] = heating_shape[day] * data[tech_to_get_shape]['workday'] #yd
                shape_boilers_y_dh[day] = data[tech_to_get_shape]['workday'] #dh

        return shape_boilers_yh, shape_boilers_y_dh
