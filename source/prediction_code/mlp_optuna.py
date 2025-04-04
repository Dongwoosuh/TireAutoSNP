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

import optuna
from optuna import Trial
from optuna.samplers import TPESampler
from optuna.pruners import HyperbandPruner
from torch.utils.data import DataLoader, TensorDataset
from optuna.visualization.matplotlib import plot_optimization_history, plot_param_importances

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
SEED = 2025
np.random.seed(SEED)
network = "MLP"
# data path -------------------------------------------------------------------
RESOURCE_PATH = Path(__file__).parent / "resource/"
RESULT_PATH = Path(__file__).parent / "results/"
data_file = RESOURCE_PATH / "DOE_results.csv"
result_file = RESOURCE_PATH / "Total_results_new.csv"
# test_datafile = RESOURCE_PATH / "TestData.csv"

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
trials = 500
train_epoch = 1000
bestmodel_epoch = 3000
kf = KFold(n_splits=5, shuffle=True, random_state=SEED)

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

# Optuna 목적 함수 정의
def objective(trial: Trial):
    # 하이퍼파라미터의 범위를 지정
    param = {
        "lr": trial.suggest_float("lr", 1e-4, 1e-2),
        "hidden_size": trial.suggest_int("hidden_size", 16, 256),
        "num_layers": trial.suggest_int("num_layers", 1, 5),
        "batch_size": trial.suggest_categorical("batch_size", [8, 16, 32]),
        "dropout_rate": trial.suggest_float("dropout_rate", 0.0, 0.3),
        "hidden_activation": trial.suggest_categorical(
            "hidden_activation", ["ReLU", "SiLU", "LeakyReLU"]
        ),
        "output_activation": trial.suggest_categorical(
            "output_activation", ["Sigmoid"]
        ),
    }

    # 초기화된 변수
    lr = param["lr"]
    hidden_size = param["hidden_size"]
    num_layers = param["num_layers"]
    batch_size = param["batch_size"]
    hidden_activation = param["hidden_activation"]
    output_activation = param["output_activation"]
    dropout_rate = param["dropout_rate"]

    fold_val_losses = []

    # 각 폴드마다 새로운 모델 생성 및 학습
    for fold, (train_index, val_index) in enumerate(kf.split(input_data)):
        model = MLP(
            input_size=input_data.shape[1],
            node_num=hidden_size,
            num_layers=num_layers,
            hidden_activation=hidden_activation,
            output_activation=output_activation,
            output_size=output_data.shape[1],
            dropout_rate=dropout_rate,
        ).to(device)

        criterion = nn.MSELoss()
        optimizer = torch.optim.NAdam(model.parameters(), lr=lr)
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

        for epoch in range(train_epoch):
            model.train()
            for inputs, targets in train_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                optimizer.zero_grad()
                outputs = model(inputs.float())
                loss = criterion(outputs, targets.float())
                loss.backward()
                optimizer.step()
                # scheduler.step(epoch + fold * train_epoch + 1)

            model.eval()
            with torch.no_grad():
                val_losses = []
                for inputs, targets in val_loader:
                    inputs, targets = inputs.to(device), targets.to(device)
                    outputs = model(inputs.float())
                    val_loss = criterion(outputs, targets.float())
                    val_losses.append(val_loss.item())
                avg_val_loss = sum(val_losses) / len(val_losses)

            if epoch == train_epoch - 1:
                fold_val_losses.append(avg_val_loss)
                print(f"Fold {fold+1}, Avg Validation Loss: {avg_val_loss}")

    final_avg_val_loss = sum(fold_val_losses) / len(fold_val_losses)
    print(f"Final Avg Validation Loss: {final_avg_val_loss}")
    return final_avg_val_loss


# Optuna 설정 및 실행
sampler = TPESampler(seed=SEED)
pruner = HyperbandPruner()
study = optuna.create_study(sampler=sampler, pruner=pruner, direction="minimize")
study.optimize(objective, n_trials=trials, catch=(Exception,))

plot_optimization_history(study)
plt.tight_layout()
plot_param_importances(study)
plt.tight_layout()

# 최적의 하이퍼파라미터를 출력
print("Best trial:")
trial = study.best_trial
print("  Value: ", trial.value)
print("  Params: ")
for key, value in trial.params.items():
    print("    {}: {}".format(key, value))

# 최적의 하이퍼파라미터를 사용하여 모델을 다시 학습시킵니다.
best_params = study.best_trial.params
best_lr = best_params["lr"]
best_hidden_size = best_params["hidden_size"]
best_batch_size = best_params["batch_size"]
best_num_layers = best_params["num_layers"]
best_hidden_activation = best_params["hidden_activation"]
best_output_activation = best_params["output_activation"]
best_dropout_rate = best_params["dropout_rate"]

last_val_losses = []
model = MLP(
    input_size=input_data.shape[1],
    node_num=best_hidden_size,
    num_layers=best_num_layers,
    hidden_activation=best_hidden_activation,
    output_activation=best_output_activation,
    output_size=output_data.shape[1],
    dropout_rate=best_dropout_rate,
).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.NAdam(model.parameters(), lr=best_lr)
# scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=200, T_mult=1)

for fold, (train_index, val_index) in enumerate(kf.split(input_data)):
    train_inputs, val_inputs = input_data[train_index], input_data[val_index]
    train_targets, val_targets = output_data[train_index], output_data[val_index]

    train_dataset = TensorDataset(
        torch.from_numpy(train_inputs), torch.from_numpy(train_targets)
    )
    val_dataset = TensorDataset(
        torch.from_numpy(val_inputs), torch.from_numpy(val_targets)
    )

    train_loader = DataLoader(train_dataset, batch_size=best_batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=len(val_dataset), shuffle=False)

    for epoch in range(bestmodel_epoch):
        model.train()
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs.float())
            loss = criterion(outputs, targets.float())
            loss.backward()
            optimizer.step()
            # scheduler.step(epoch + fold * bestmodel_epoch + 1)

        model.eval()
        with torch.no_grad():
            val_losses = []
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs.float())
                val_loss = criterion(outputs, targets.float())
                val_losses.append(val_loss.item())
            avg_val_loss = sum(val_losses) / len(val_losses)
        if epoch == bestmodel_epoch - 1:
            last_val_losses.append(avg_val_loss)
            print(f"Fold {fold+1}, Avg Validation Loss: {avg_val_loss}")

# 테스트 세트로 예측 수행
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

mape = np.mean(np.abs((output_test - output_pred) / output_test), axis=1) * 100
acc = 100 - mape
acc = np.where((acc > 100.0), 0.0, acc)
acc = np.where((acc < 0.0), 0.0, acc)

print(f"\t - accuracy [%] : {np.round(np.mean(acc),6)} ± {np.round(np.std(acc),6)}")

# 결과 저장 경로 생성
dir_count = len([name for name in Path(RESULT_PATH).iterdir() if name.is_dir()])
new_dir_name = f"[{dir_count+1}]_{network}_{np.round(np.mean(acc),6)}%"
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
    f.write(f"Batch size: {best_batch_size}\n")
    f.write(f"Number of layers: {best_num_layers}\n")
    f.write(f"Node number: {best_hidden_size}\n")
    f.write(f"Dropout rate: {best_dropout_rate}\n")
    f.write(f"Hidden activation: {best_hidden_activation}\n")
    f.write(f"Output activation: {best_output_activation}\n")
    f.write(f"Learning rate: {best_lr}\n")
    f.write(f"Epoch: {bestmodel_epoch}\n")
    f.write(f"\nAccuracy: {np.round(np.mean(acc), 6)}±{np.round(np.std(acc), 6)}\n")

torch.save(model.state_dict(), str((new_dir_path / "model.pt").resolve()))

print("Execution time: ", time.time() - start_time, "s")