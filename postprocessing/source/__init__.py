import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # 현재 경로 추가

from Score_Outlier_loop import max_stress_after_outlier_removal
from combine_all_results import combine_results
from filter_DOE import filter_doe_results
from combine_dummy_results import combine_max_stress, combine_max_velocity