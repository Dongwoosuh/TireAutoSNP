import os
import pandas as pd
import re

# 폴더 경로 설정
folder_path = './results/Total_results'

# 결과를 저장할 리스트
last_rows = []

# 폴더 내의 모든 CSV 파일을 처리
for file_name in os.listdir(folder_path):
    # 파일명이 "Run"으로 시작하고, 뒤에 숫자가 오는 형식인지 확인 (숫자 앞 0 허용)
    if re.match(r'^Run\d{1,}\.csv$', file_name):  
        file_path = os.path.join(folder_path, file_name)
        
        # CSV 파일 읽기
        try:
            df = pd.read_csv(file_path)
            if not df.empty:  # 비어있지 않은 파일의 경우
                last_rows.append(df.iloc[-1].values)  # 마지막 행 추가
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

# 새 헤더 정의
columns = ["ODB Name", "Max Avg Stress", "Vertical Stiffness", "Max Slip Angle", "Max Slip Distance", "Bending Moment", "Torque"]

# 마지막 행들을 데이터프레임으로 변환
result_df = pd.DataFrame(last_rows, columns=columns)

# 결과를 Total_results.csv로 저장
save_path = './results'
output_path = os.path.join(save_path, 'Total_results.csv')
result_df.to_csv(output_path, index=False)

print(f"Total results saved to {output_path}")
