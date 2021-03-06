"""
Industry Submodel
====================

"""
import energy_demand.enduse as endusefunctions

class IndustryModel(object):
    """Industry Submodel
    """
    def __init__(self, data, region_object, enduse, sector):
        """Constructor of industry submodel

        Parameters
        ----------
        data : dict
            Data
        region_object : dict
            Object of region
        enduse : string
            Enduse
        sector : string
            Service sector
        """
        self.region_name = region_object.region_name
        self.enduse = enduse
        self.sector = sector
        self.fuels_all_enduses = data['is_fueldata_disagg'][self.region_name][self.sector]

        self.enduse_object = self.create_enduse(region_object, data)

    def create_enduse(self, region_object, data):
        """Create enduse for industry sector
        """
        industry_object = endusefunctions.Enduse(
            region_name=self.region_name,
            data=data,
            enduse=self.enduse,
            sector=self.sector,
            fuel=self.fuels_all_enduses[self.enduse],
            tech_stock=region_object.is_tech_stock,
            heating_factor_y=region_object.is_heating_factor_y,
            cooling_factor_y=region_object.is_cooling_factor_y,
            fuel_switches=data['assumptions']['is_fuel_switches'],
            service_switches=data['assumptions']['is_service_switches'],
            fuel_tech_p_by=data['assumptions']['is_fuel_tech_p_by'][self.enduse],
            tech_increased_service=data['assumptions']['is_tech_increased_service'],
            tech_decreased_share=data['assumptions']['is_tech_decreased_share'],
            tech_constant_share=data['assumptions']['is_tech_constant_share'],
            installed_tech=data['assumptions']['is_installed_tech'],
            sig_param_tech=data['assumptions']['is_sig_param_tech'],
            enduse_overall_change_ey=data['assumptions']['enduse_overall_change_ey']['is_model'],
            regional_profile_stock=region_object.is_load_profiles,
            reg_scenario_drivers=data['assumptions']['scenario_drivers']['is_submodule'],
            crit_flat_profile=True
        )

        return industry_object
