import pandas as pd
import re

__all__ = ['filter_doe_results']    

def filter_doe_results():
    # 파일 경로 설정
    total_results_path = './results/Total_results_new.csv'
    doe_results_path = './postprocessing/result/Total_0203.csv'

    # 파일 읽기
    total_results = pd.read_csv(total_results_path)
    doe_results = pd.read_csv(doe_results_path)

    # Total_results의 첫 번째 열 값 추출 (e.g., "Run03", "Run04" 등)
    total_results_runs = total_results.iloc[:, 0].unique()

    # DOE_results에서 첫 번째 열의 값이 Total_results의 값과 일치하는 행만 필터링
    filtered_doe_results = doe_results[doe_results.iloc[:, -1].isin(total_results_runs)]

    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    filtered_doe_results = filtered_doe_results.sort_values(
        by=filtered_doe_results.columns[-1], 
        key=lambda x: x.map(natural_sort_key),  # 문자열과 숫자 분리하여 정렬
        ascending=True
    )


    # 결과 저장
    filtered_doe_results_path = './source/prediction_code/resource/DOE_results.csv'
    filtered_doe_results_path2 = './results/DOE_results.csv'
    filtered_doe_results.to_csv(filtered_doe_results_path, index=False)
    filtered_doe_results.to_csv(filtered_doe_results_path2, index=False)

    print(f"Filtered results saved to {filtered_doe_results_path}")
    
if __name__ == '__main__':
    filter_doe_results()

