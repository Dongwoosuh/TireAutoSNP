import numpy as np
import pandas as pd

# CSV 파일 불러오기
max_stress_pd = pd.read_csv('./results/Total_results_tire_center.csv')
results_pd = pd.read_csv('./results/Updated_Total_results.csv')

# 컬럼명 확인 후 공백 제거
max_stress_pd.columns = max_stress_pd.columns.str.strip()
results_pd.columns = results_pd.columns.str.strip()

# 'Max Stress' 컬럼이 없으면 새로 생성 (기본값 NaN)
results_pd['Center Disp Gap(subrot)'] = np.nan
results_pd['Center Disp Gap(rot)'] = np.nan
results_pd['Total Center Disp Gap'] = np.nan
results_pd['Total Center Disp Std'] = np.nan

# 'ODB Name'을 기준으로 'Max Stress After Outlier Removal' 값을 results_pd의 'Max Stress' 컬럼에 추가
results_pd['Center Disp Gap(subrot)'] = results_pd['ODB Name'].map(
    max_stress_pd.set_index('ODB Name')['Center Disp Gap(subrot)']
)
results_pd['Center Disp Gap(rot)'] = results_pd['ODB Name'].map(
    max_stress_pd.set_index('ODB Name')['Center Disp Gap(rot)']
)
results_pd['Total Center Disp Gap'] = results_pd['ODB Name'].map(
    max_stress_pd.set_index('ODB Name')['Total Center Disp Gap']
)
results_pd['Total Center Disp Std'] = results_pd['ODB Name'].map(
    max_stress_pd.set_index('ODB Name')['Total Center Disp Std']
)


# 결과 확인
print(results_pd)

# 변경된 데이터를 저장 (필요 시)
results_pd.to_csv('./results/Updated_Total_results.csv', index=False)
