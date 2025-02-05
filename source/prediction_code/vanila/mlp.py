import os
import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from model import MLP  # noqa: E402

# In[1. Setting] ##############################################################
start_time = time.time()
# device setting --------------------------------------------------------------
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print("Current device: ", device)

# seed -----------------------------------------------------------------------
SEED = 2024
np.random.seed(SEED)
network = "MLP"
# data path -------------------------------------------------------------------
RESOURCE_PATH = Path(__file__).parent / "../resource/"
RESULT_PATH = Path(__file__).parent / "../results/"
data_file = RESOURCE_PATH / "DOE_results_0203.csv"
result_file = RESOURCE_PATH / "Updated_Total_results_250204.csv"

# 데이터 로드
input_dataset = pd.read_csv(data_file)
output_dataset = pd.read_csv(result_file)
# test_dataset = pd.read_csv(test_datafile)
input_data = input_dataset.iloc[:, :-1].values  # 왼쪽 11열
output_data = output_dataset.iloc[:, 1:].values # 오른쪽 하나
# input_test_data = test_dataset.iloc[:, :-1].values
# output_test_data = test_dataset.iloc[:, -1].values.reshape(-1, 1)

input_data, input_test_data, output_data, output_test_data = train_test_split(input_data, output_data, test_size=0.1, random_state=SEED)

# 모델 설정 -------------------------------------------------------------------
batch_size = 64
num_layers = 2
node_num = 43
dropout_rate = 0.23209045967503736
hidden_activation = "ELU"
output_activation = "Sigmoid"
lr = 0.0018959950656424502
n_epochs = 1000
bestmodel_epoch = 5000
kf = KFold(n_splits=7, shuffle=True, random_state=SEED)


# 데이터 정규화
input_scaler = MinMaxScaler()
output_scaler = MinMaxScaler()

input_data = input_scaler.fit_transform(input_data)
input_test_data = input_scaler.transform(input_test_data)
output_data = output_scaler.fit_transform(output_data)
output_test_data = output_scaler.transform(output_test_data)
input_data = input_data.astype(np.float32)
input_test_data = input_test_data.astype(np.float32)
output_data = output_data.astype(np.float32)
output_test_data = output_test_data.astype(np.float32)

# 모델 생성 및 학습 설정
criterion = nn.MSELoss()
fold_val_losses = []
best_model_state = None
best_fold_idx = None

for fold, (train_index, val_index) in enumerate(kf.split(input_data)):
    model = MLP(
        input_size=input_data.shape[1],
        node_num=node_num,
        output_size=output_data.shape[1],
        num_layers=num_layers,
        hidden_activation=hidden_activation,
        output_activation=output_activation,
        dropout_rate=dropout_rate,
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    # scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=200, T_mult=1)

    train_inputs, val_inputs = input_data[train_index], input_data[val_index]
    train_targets, val_targets = output_data[train_index], output_data[val_index]

    train_dataset = TensorDataset(
        torch.from_numpy(train_inputs), torch.from_numpy(train_targets)
    )
    val_dataset = TensorDataset(
        torch.from_numpy(val_inputs), torch.from_numpy(val_targets)
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=len(val_dataset), shuffle=False)

    for epoch in range(n_epochs):
        model.train()
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs.float())
            loss = criterion(outputs, targets.float())
            loss.backward()
            optimizer.step()
            # scheduler.step(epoch + fold * n_epochs + 1)

        model.eval()
        with torch.no_grad():
            val_losses = []
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs.float())
                val_loss = criterion(outputs, targets.float())
                val_losses.append(val_loss.item())
            avg_val_loss = sum(val_losses) / len(val_losses)
        if epoch == n_epochs - 1:
            fold_val_losses.append((avg_val_loss, model.state_dict()))
            print(f"Fold {fold+1}, Avg Validation Loss: {avg_val_loss}")

# 가장 낮은 validation loss를 가진 모델 선택
best_fold_idx = np.argmin([loss for loss, _ in fold_val_losses])
best_model_state = fold_val_losses[best_fold_idx][1]

# 선택된 모델을 test set에 대해 5000 에포크 학습
model = MLP(
    input_size=input_data.shape[1],
    node_num=node_num,
    output_size=output_data.shape[1],
    num_layers=num_layers,
    hidden_activation=hidden_activation,
    output_activation=output_activation,
    dropout_rate=dropout_rate,
).to(device)

model.load_state_dict(best_model_state)

optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
# scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=200, T_mult=1)

train_dataset = TensorDataset(
    torch.from_numpy(input_data), torch.from_numpy(output_data)
)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

for epoch in range(bestmodel_epoch):
    model.train()
    for inputs, targets in train_loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        outputs = model(inputs.float())
        loss = criterion(outputs, targets.float())
        loss.backward()
        optimizer.step()
        # scheduler.step(epoch + 1)

# In[4. Test] #################################################################
test_dataset = TensorDataset(
    torch.from_numpy(input_test_data), torch.from_numpy(output_test_data)
)
test_loader = DataLoader(test_dataset, batch_size=len(input_test_data), shuffle=False)

model.eval()
with torch.no_grad():
    for inputs, targets in test_loader:
        inputs, targets = inputs.to(device), targets.to(device)
        outputs = model(inputs.float())
        test_loss = criterion(outputs, targets.float())

print(f"Test Loss: {test_loss.item()}")

new_output_pred_scaled = outputs.cpu().numpy()
output_pred = (
    new_output_pred_scaled * (output_scaler.data_max_ - output_scaler.data_min_)
    + output_scaler.data_min_
)
new_output_orig_scaled = targets.cpu().numpy()
output_test = (
    new_output_orig_scaled * (output_scaler.data_max_ - output_scaler.data_min_)
    + output_scaler.data_min_
)

mape_all = np.mean(np.abs((output_test - output_pred) / output_test), axis=1) * 100
acc_all = 100 - mape_all
acc_all = np.where((acc_all > 100.0), 0.0, acc_all)
acc_all = np.where((acc_all < 0.0), 0.0, acc_all)

# MAPE (Mean Absolute Percentage Error) 계산
mape = np.abs(output_pred - output_test) / np.abs(output_test)
acc_mape = (1 - mape) * 100  # MAPE 기반 정확도
acc_mape = np.where((acc_mape > 100.0), 0.0, acc_mape)
acc_mape = np.where((acc_mape < 0.0), 0.0, acc_mape)

# RMSE (Root Mean Squared Error) 계산
rmse = np.sqrt(np.mean((output_pred - output_test) ** 2, axis=0))

# R² Score (Coefficient of Determination) 계산
ss_res = np.sum((output_pred - output_test) ** 2, axis=0)
ss_tot = np.sum((output_test - np.mean(output_test, axis=0)) ** 2, axis=0)
r2_score = 1 - (ss_res / ss_tot)

# 결과 출력
result_df = pd.DataFrame({
    "Output": [f"Output_{i+1}" for i in range(output_data.shape[1])],
    "Mean Accuracy (MAPE %)": np.mean(acc_mape, axis=0),
    "Std Dev Accuracy (MAPE %)": np.std(acc_mape, axis=0),
    "RMSE": rmse,
    "R² Score": r2_score
})

print("\nLOOCV Results:")
print(result_df)

print(f"\t - accuracy [%] : {np.round(np.mean(acc_all),6)} ± {np.round(np.std(acc_all),6)}")

# In[5. Save] #################################################################

dir_count = len([name for name in Path(RESULT_PATH).iterdir() if name.is_dir()])
new_dir_name = (
    f"[{dir_count+1}]_{network}_\
    "
    f"{np.round(np.mean(acc_all),6)}%"
)
new_dir_path = Path(RESULT_PATH) / new_dir_name
new_dir_path.mkdir(parents=True, exist_ok=True)

# 결과 그래프 저장
for i in range(output_test.shape[1]):
    plt.figure(figsize=(10, 5))
    plt.plot(output_test[:, i], label="Actual")
    plt.plot(output_pred[:, i], label="Predicted")
    plt.title(f"Output variable {i+1}")
    plt.legend()
    plt.savefig(str(new_dir_path / f"Output_variable_{i+1}.png"))
    plt.close()

# 모델 정보 저장
with open(new_dir_path / "model_info.txt", "w") as f:
    f.write("MLP Hyperparameters:\n")
    f.write(f"Batch size: {batch_size}\n")
    f.write(f"Number of layers: {num_layers}\n")
    f.write(f"Node number: {node_num}\n")
    f.write(f"Dropout rate: {dropout_rate}\n")
    f.write(f"Hidden activation: {hidden_activation}\n")
    f.write(f"Output activation: {output_activation}\n")
    f.write(f"Learning rate: {lr}\n")
    f.write(f"Epoch: {epoch}\n")
    f.write(f"\nAccuracy: {np.round(np.mean(acc_all),6)}\n")

torch.save(model.state_dict(), str((new_dir_path / "model.pt").resolve()))

print("Execution time: ", time.time() - start_time, "s")