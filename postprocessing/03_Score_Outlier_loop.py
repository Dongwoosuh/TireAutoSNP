import pandas as pd
import numpy as np
import os
from scipy.stats import zscore

import re

# 분석할 모든 CSV 파일 찾기 (현재 디렉터리에서)
directory_path = "./"  # 현재 디렉터리

# 파일명에서 숫자 추출 후 정렬
csv_files = sorted([f for f in os.listdir(directory_path) if re.match(r"Run\d+\.csv", f)],
                    key=lambda x: int(re.search(r"\d+", x).group()))

# Z-Score 임계값 설정
threshold_z = 10

# 결과 저장용 리스트
results = []

# 각 CSV 파일에 대해 분석 진행
for file_name in csv_files:
    file_path = os.path.join(directory_path, file_name)
    
    print(f"\n Processing file: {file_name}")

    df = pd.read_csv(file_path, header=0)
    # 숫자가 아닌 값(문자열) 제거
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.dropna().reset_index(drop=True)

    # 이상치 제거 함수 (상위 Z-Score 기반)
    def remove_upper_outliers_zscore(data, threshold=10):
        z_scores = zscore(data)
        outliers = data[z_scores > threshold]  # 상위 이상치만 제거
        filtered_data = data[z_scores <= threshold]
        return filtered_data, outliers

    # 각 프레임에서 이상치 제거 및 이상치 저장
    filtered_df = df.copy()
    outliers_dict = {}  # 이상치 저장용 딕셔너리
    outlier_counts = {}  # 이상치 개수 저장
    max_outliers = {}  # 제거된 값 중 최대값
    min_outliers = {}  # 제거된 값 중 최소값

    for frame in df.columns[1:]:  # 첫 번째 컬럼(Element)을 제외한 나머지 프레임 데이터 처리
        filtered_values, outliers = remove_upper_outliers_zscore(df[frame])
        filtered_df[frame] = filtered_values
        outliers_dict[frame] = outliers
        outlier_counts[frame] = len(outliers.dropna())
        max_outliers[frame] = outliers.max() if not outliers.empty else None
        min_outliers[frame] = outliers.min() if not outliers.empty else None

    # 이상치 제거 후 최대 Stress 찾기
    max_stress = filtered_df.iloc[:, 1:].max().max()
    # 결과 저장
    results.append([file_name, max_stress])

    # 결과 출력
    print("Filtered Max Stress:", max_stress)
    print("\nNumber of Outliers Removed per Frame:")
    for frame, count in outlier_counts.items():
        print(f"{frame}: {count} values removed")

    print("\nExtreme Outlier Values Removed:")
    for frame in df.columns[1:]:
        print(f"{frame}: Max Removed = {max_outliers[frame]}, Min Removed = {min_outliers[frame]}")


# %%

# 결과를 DataFrame으로 변환 후 CSV 저장
results_df = pd.DataFrame(results, columns=["File Name", "Max Stress After Outlier Removal"])
output_filename = "Max_Stress_After_Outlier_Removal.csv"
results_df.to_csv(output_filename, index=False)
print("\n All CSV files have been processed successfully!")
