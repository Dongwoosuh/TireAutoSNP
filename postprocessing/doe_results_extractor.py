import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from source import *

combine_results()
max_stress_after_outlier_removal()
combine_max_stress()
# combine_max_velocity()
filter_doe_results()

