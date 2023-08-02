"""
Module for calculating metrics from GEE data
"""

import numpy as np
import copy
from landcover_constants import MODIS_LC, FIRE_LC

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

    def get_perc_cov(self, lc_type):
        """
        Calculate percent coverage of lc per class
        :return: dictionary of pct coverage per land cover class
        """

        if lc_type == 'modis':
            feature_dict = copy.deepcopy(MODIS_LC)
        if lc_type == 'fire':
            feature_dict = copy.deepcopy(FIRE_LC)

        rows = len(self.img_arr[:, 0])
        cols = len(self.img_arr[0, :])
        total_pixels = rows * cols
        values_val, counts_val = np.unique(self.img_arr, return_counts=True)

        values = values_val.tolist()
        counts = counts_val.tolist()

        # Removing data that is not categorized/nans10think is due to bilinear interpolation
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
        :return: percent value of burnt area in image
        '''
        total_pixels = len(self.img_arr[:, 0]) * len(self.img_arr[0, :])
        unburnt = np.count_nonzero(self.img_arr == 160)
        burnt_pct = (total_pixels - unburnt) / total_pixels

        return burnt_pct