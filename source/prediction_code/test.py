import os
import joblib
import torch
import numpy as np
import pandas as pd
from pathlib import Path
from model import MLP  # 모델 클래스 import

# 1. 저장된 모델 디렉토리 설정
RESULT_PATH = Path(__file__).parent / "results/"
saved_model_dir = RESULT_PATH / "[25]_MLP_    87.642935%"  # 저장된 모델 폴더 (실제 폴더명으로 변경)

# 2. 저장된 하이퍼파라미터 로드
hyperparam_file = saved_model_dir / "model_info.txt"
hyperparams = {}
with open(hyperparam_file, "r") as f:
    for line in f:
        if ": " in line:
            key, value = line.strip().split(": ")
            try:
                hyperparams[key] = float(value) if "." in value else int(value)
            except ValueError:
                hyperparams[key] = value

# 3. 모델 설정 로드
input_size = 7  # 입력 피처 개수 (데이터에 맞게 변경)
output_size = 6  # 출력 개수 (데이터에 맞게 변경)
node_num = hyperparams["Node number"]
num_layers = hyperparams["Number of layers"]
dropout_rate = hyperparams["Dropout rate"]
hidden_activation = hyperparams["Hidden activation"]
output_activation = hyperparams["Output activation"]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 4. 저장된 모델 로드
model = MLP(
    input_size=input_size,
    node_num=node_num,
    output_size=output_size,
    num_layers=num_layers,
    hidden_activation=hidden_activation,
    output_activation=output_activation,
    dropout_rate=dropout_rate,
).to(device)

model_file = saved_model_dir / "model.pt"
model.load_state_dict(torch.load(model_file, map_location=device))
model.eval()

# 5. 저장된 스케일러 로드
scaler_path = saved_model_dir / "scalers"
input_scaler_file = scaler_path / "input_scaler.pkl"
output_scaler_file = scaler_path / "output_scaler.pkl"

input_scaler = joblib.load(input_scaler_file)
output_scaler = joblib.load(output_scaler_file)

# 6. 새로운 입력 데이터 로드 (새로운 예측을 위한 데이터)
new_input_file = Path(__file__).parent / "resource/new_inference_data.csv"
new_input_data = pd.read_csv(new_input_file)

# 입력 데이터 스케일링
new_input_scaled = input_scaler.transform(new_input_data.iloc[:,:-1].values)

# 7. 모델을 사용한 Inference(예측 수행)
with torch.no_grad():
    input_tensor = torch.from_numpy(new_input_scaled).float().to(device)
    scaled_pred_output = model(input_tensor)

# 8. 예측 결과 역변환 (스케일링 해제)
predicted_output = (
    scaled_pred_output.cpu().numpy()
    * (output_scaler.data_max_ - output_scaler.data_min_)
    + output_scaler.data_min_
)

# 9. 예측 결과 저장
output_df = pd.DataFrame(predicted_output, columns=["Vertical stiffness", "Max slip angle", "Max slip distance", "Bending moment", "Torque", "Max Stress"])
output_file = saved_model_dir / "inference_results.csv"
output_df.to_csv(output_file, index=False)

print(f"✅ 새로운 예측값이 저장되었습니다: {output_file}")
