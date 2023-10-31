"""
Test functions in metric utils
"""
import airpy.metric_utils as mu
import numpy as np

test_array = np.array([[3,3,5], [160, 160, 3]])

true_modis_pct_cov = {
    1: {'class': 'evg_conif', 'pct_cov': 0}, 2: {'class': 'evg_broad', 'pct_cov': 0},
    3: {'class': 'dcd_needle', 'pct_cov': 0.5}, 4: {'class': 'dcd_broad', 'pct_cov': 0},
    5: {'class': 'mix_forest', 'pct_cov': 0.16666666666666666}, 6: {'class': 'cls_shrub', 'pct_cov': 0},
    7: {'class': 'open_shrub', 'pct_cov': 0}, 8: {'class': 'woody_savanna', 'pct_cov': 0},
    9: {'class': 'savanna', 'pct_cov': 0}, 10: {'class': 'grassland', 'pct_cov': 0},
    11: {'class': 'perm_wetland', 'pct_cov': 0}, 12: {'class': 'cropland', 'pct_cov': 0},
    13: {'class': 'urban', 'pct_cov': 0}, 14: {'class': 'crop_nat_veg', 'pct_cov': 0},
    15: {'class': 'perm_snow', 'pct_cov': 0}, 16: {'class': 'barren', 'pct_cov': 0},
    17: {'class': 'water_bds', 'pct_cov': 0}}

true_fire_pct_cov = {
    0: {'class': 'crop_rain', 'pct_cov': 0}, 20: {'class': 'crop_irr', 'pct_cov': 0},
    30: {'class': 'crop_veg', 'pct_cov': 0}, 40: {'class': 'veg_crop', 'pct_cov': 0},
    50: {'class': 'broad_ever', 'pct_cov': 0}, 60: {'class': 'broad_decid', 'pct_cov': 0},
    70: {'class': 'needle_ever', 'pct_cov': 0}, 80: {'class': 'needle_decid', 'pct_cov': 0},
    90: {'class': 'tree_mixed', 'pct_cov': 0}, 100: {'class': 'tree_shrub_herb', 'pct_cov': 0},
    110: {'class': 'herb_tree_shrub', 'pct_cov': 0}, 120: {'class': 'shrubland', 'pct_cov': 0},
    130: {'class': 'grassland', 'pct_cov': 0}, 140: {'class': 'lichen_moss', 'pct_cov': 0},
    150: {'class': 'sparse_veg', 'pct_cov': 0}, 170: {'class': 'tree_flooded', 'pct_cov': 0},
    180: {'class': 'shrub_herb_flood', 'pct_cov': 0}, 160: {'class': 'unburnt', 'pct_cov': 0.3333333333333333}
}

metric_utils = mu.MetricUtils(test_array)

def test_get_mode():
    """Test function to calculate mode of array"""
    true_mode = 3
    assert metric_utils.get_mode() == true_mode


def test_get_perc_cov():
    """Test function to calculate percent coverage per MODIS land cover class"""
    assert metric_utils.get_perc_cov('modis') == true_modis_pct_cov
    assert metric_utils.get_perc_cov('fire') == true_fire_pct_cov


def test_calc_burnt_pct():
    """Test function to calculate percent coverage per MODIS fire land cover class"""
    true_burnt = 0.6666666666666666
    assert metric_utils.calc_burnt_pct() == true_burnt









