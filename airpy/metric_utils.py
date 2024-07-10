"""
Module for calculating metrics from GEE data
"""

import numpy as np
import copy
from gee_class_constants import MODIS_LC_Type1, FIRE_LC, GHSL_Built_Class

class MetricUtils():
    def __init__(self, img_arr):
        self.img_arr = img_arr

    def get_mode(self):
        """
        Get mode of array --> useful for land cover datasets
        :return: array mode
        """
        values, counts = np.unique(self.img_arr, return_counts=True)
        m = counts.argmax()
        return values[m]

    def get_nonzero_mode(self):
        """
        Get mode of array removing 0 placeholder
        :return: array mode
        """
        flat_img = self.img_arr.flatten()
        non_zero = flat_img[flat_img != 0]
        values, counts = np.unique(non_zero, return_counts=True)
        if counts.size > 0:
            m = counts.argmax()
            return values[m]
        else:
            return 0

    def get_nonzero_var(self):
        """
        Get variance of array removing 0 placeholder
        :return: array variance
        """
        flat_img = self.img_arr.flatten()
        non_zero = flat_img[flat_img != 0]
        if non_zero.size > 0:
            return np.nanvar(non_zero)
        else:
            return 0

    def get_perc_cov(self, class_dict):
        """
        Calculate percent coverage per class
        :param: class_dict: dictionary of class constants for gee dataset
        :return: dictionary of pct coverage per class
        """

        if class_dict == 'modis':
            feature_dict = copy.deepcopy(MODIS_LC_Type1)
        if class_dict == 'fire':
            feature_dict = copy.deepcopy(FIRE_LC)
        if class_dict == 'human_settlement_layer_built_up':
            feature_dict = copy.deepcopy(GHSL_Built_Class)

        if class_dict == 'human_settlement_layer_built_up':
            # calc the total non-zero pixels (this is dummy default value for processing)
            flat = self.img_arr.flatten()
            total_pixels = len(flat[flat != 0])
        else:
            rows = len(self.img_arr[:, 0])
            cols = len(self.img_arr[0, :])
            total_pixels = rows * cols
        values_val, counts_val = np.unique(self.img_arr, return_counts=True)

        values = values_val.tolist()
        counts = counts_val.tolist()

        # Removing data that is not categorized/nans - think is due to bilinear interpolation
        new_vals = []
        new_counts = []
        for i in range(len(values)):
            if feature_dict.get(values[i]):
                new_vals.append(values[i])
                new_counts.append(counts[i])

        count_dict = {}
        for j in range(len(new_vals)):
            count_dict[new_vals[j]] = new_counts[j]

        for k, v in count_dict.items():
            pct_cov = (count_dict[k] / total_pixels)
            feature_dict[k]['pct_cov'] = pct_cov

        return feature_dict

    def calc_burnt_pct(self):
        '''
        Calculate burnt percentage for fire datasets
        :return: percent value of burnt area in array
        '''
        total_pixels = len(self.img_arr[:, 0]) * len(self.img_arr[0, :])
        unburnt = np.count_nonzero(self.img_arr == 160)
        burnt_pct = (total_pixels - unburnt) / total_pixels

        return burnt_pct

    def calc_built_pct(self):
        '''
        Calculate percentage of built up area
        :return: percent value of built up area in an array
        '''
        flat = self.img_arr.flatten()
        total_pixels = len(flat[flat != 0])
        if total_pixels == 0:
            built_pct = 0
            return built_pct

        built_classes = [11, 12, 13, 14, 15, 21, 22, 23, 24, 25]
        built_count = 0
        for i in built_classes:
            built_count += flat.tolist().count(i)

        built_pct = (total_pixels - built_count) / total_pixels

        return built_pct
