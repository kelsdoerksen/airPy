"""
Test functions in generate_config
"""
import pytest
from generate_config import GenerateConfig


class TestGenerateConfig():
    def setup_method(self):
        # setup method for GenerateConifg class to test various functions
        self.gee_data = None
        self.region = 'Canada'  # setting to excluded region to raise exception
        self.date = '1999-17-01'    # setting to excluded date to raise exception
        self.analysis_type = 'collection'
        self.add_time = 'y'
        self.buffer_size = 1
        self.configs_dir = None
        self.save_dir = None
        self.resolution = 1

    def test_check_query_date(self):
        """Test function that checks query date"""

        data_collections = [{"name": "modis", "min_date": "2001-01-01", "max_date": "2021-01-01"},
                            {"name": "pop", "min_date": "2000-01-01", "max_date": "2020-01-01"},
                            {"name": "fire", "min_date": "2001-01-01", "max_date": "2020-12-01"},
                            {"name": "nightlight", "min_date": "2012-04-01", "max_date": "2024-02-01"},
                            {"name": "human_settlement_layer_built_up", "min_date": "2018-01-01",
                             "max_date": "2018-12-31"},
                            {"name": "global_human_modification", "min_date": "2016-01-01", "max_date": "2016-12-31"}]

        for d in data_collections:
            with pytest.raises(ValueError):
                bad_date = '1999-01-01'
                generate_config = GenerateConfig(d['name'], self.region, bad_date, self.analysis_type,
                                                 self.add_time, self.buffer_size, self.configs_dir,
                                                 self.save_dir)
                generate_config.check_query_date(d)
            with pytest.raises(ValueError):
                bad_date = '2040-01-01'
                generate_config = GenerateConfig(d['name'], self.region, bad_date, self.analysis_type,
                                                 self.add_time, self.buffer_size, self.configs_dir,
                                                 self.save_dir)
                generate_config.check_query_date(d)


    def test_get_query_date(self):
        """Test function to grab query date in format YYYY-MM-DD"""
        generate_config = GenerateConfig(self.gee_data, self.region, self.date, self.analysis_type,
                                         self.add_time, self.buffer_size, self.configs_dir,
                                         self.save_dir)
        with pytest.raises(ValueError):
            generate_config.get_query_date()


    def test_get_boundary(self):
        """Test function that subsets boundary region"""
        # Test if region not within bounds
        generate_config = GenerateConfig(self.gee_data, self.region, self.date, self.analysis_type,
                                         self.add_time, self.buffer_size, self.configs_dir,
                                         self.save_dir)
        with pytest.raises(ValueError):
            generate_config.get_boundary()


    def test_get_collection_data(self):
        """Test function that grabs data collection dictionary"""
        # Test if collection file not found
        generate_config = GenerateConfig(self.gee_data, self.region, self.date, self.analysis_type,
                                         self.add_time, self.buffer_size, self.configs_dir,
                                         self.save_dir)
        with pytest.raises(ValueError):
            generate_config.get_gee_collection_data()
