import pandas as pd

# 파일 경로 설정
total_results_path = './results/Updated_Total_results_250203.csv'
doe_results_path = './postprocessing/result/Total_0203.csv'

# 파일 읽기
total_results = pd.read_csv(total_results_path)
doe_results = pd.read_csv(doe_results_path)

# Total_results의 첫 번째 열 값 추출 (e.g., "Run03", "Run04" 등)
total_results_runs = total_results.iloc[:, 0].unique()

# DOE_results에서 첫 번째 열의 값이 Total_results의 값과 일치하는 행만 필터링
filtered_doe_results = doe_results[doe_results.iloc[:, -1].isin(total_results_runs)]

# 결과 저장
filtered_doe_results_path = './postprocessing/result/DOE_results.csv'
filtered_doe_results.to_csv(filtered_doe_results_path, index=False)

print(f"Filtered results saved to {filtered_doe_results_path}")
