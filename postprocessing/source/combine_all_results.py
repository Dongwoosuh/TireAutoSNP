import os
import pandas as pd
import re

__all__ = ['combine_results'] # 외부에서 import할 수 있는 함수 목록   

def combine_results():
    # 폴더 경로 설정
    folder_path = './results/total_results'
    # csv_files = sorted([f for f in os.listdir(folder_path) if re.match(r"Run\d+\.csv", f)],
    #                     key=lambda x: int(re.search(r"\d+", x).group()))

    csv_files = sorted(
        [f for f in os.listdir(folder_path) if f.endswith(".csv")],
        key=lambda x: (not x.startswith("Add_Run"), int(re.search(r"\d+", x).group()))
    )


    # 결과를 저장할 리스트
    last_rows = []

    # 폴더 내의 모든 CSV 파일을 처리
    for file_name in csv_files:
        file_path = os.path.join(folder_path, file_name)
        base_file_name = os.path.splitext(file_name)[0]
        # CSV 파일 읽기
        try:
            df = pd.read_csv(file_path)
            if not df.empty:  # 비어있지 않은 파일의 경우
                last_rows.append(df.iloc[-1].values)  # 마지막 행 추가
        except Exception as e:
            print(f"Error reading {file_name}: {e}")

    # 새 헤더 정의
    columns = ["ODB Name", "Vertical Stiffness", "Max Slip Angle", "Max Slip Distance", "Bending Moment", "Torque", "Center Disp Gap(subrot)", "Center Disp Gap(rot)" , 
               "Total Center Disp Gap", "Total Center Disp Std", "Max Velocity(subrot)", "Max Velocity(rot)", "Target Contact Area"]

    # 마지막 행들을 데이터프레임으로 변환
    result_df = pd.DataFrame(last_rows, columns=columns)

    # 결과를 Total_results.csv로 저장
    save_path = './results'
    output_path = os.path.join(save_path, 'Total_results_new.csv')
    result_df.to_csv(output_path, index=False)

    print(f"Total results saved to {output_path}")\
    
if __name__ == '__main__':
    combine_results()
