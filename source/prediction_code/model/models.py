import torch
import torch.nn as nn
import torch.nn.functional as F


__all__ = ["MLP", "MLP_OPTUNA", "VAE", "CVAE"]

class BaseMLP(nn.Module):
    def __init__(self):
        super(BaseMLP, self).__init__()

    def get_activation(self, name):
        activations = {
            "SiLU": nn.SiLU(),
            "Sigmoid": nn.Sigmoid(),
            "Tanh": nn.Tanh(),
            "ELU": nn.ELU(),
            "LeakyReLU": nn.LeakyReLU(),
            "Mish": nn.Mish(),
            "SeLU": nn.SELU(),
            "ReLU": nn.ReLU(),
            "ReLU6": nn.ReLU6(),
            "None": nn.Identity(),
        }
        if name in activations:
            return activations[name]
        raise ValueError(f"Invalid activation: {name}")


class MLP_OPTUNA(BaseMLP):
    def __init__(
        self,
        input_size,
        hidden_size,
        output_size,
        num_layers,
        hidden_activation,
        output_activation,
        dropout_rate,
    ):
        super(MLP_OPTUNA, self).__init__()
        self.layers = nn.ModuleList()

        self.layers.append(nn.Linear(input_size, hidden_size))
        self.layers.append(self.get_activation(hidden_activation))
        self.layers.append(nn.Dropout(dropout_rate))

        for _ in range(num_layers - 1):
            self.layers.append(nn.Linear(hidden_size, hidden_size))
            self.layers.append(self.get_activation(hidden_activation))
            self.layers.append(nn.Dropout(dropout_rate))

        self.layers.append(nn.Linear(hidden_size, output_size))
        self.layers.append(self.get_activation(output_activation))

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


class MLP(BaseMLP):
    def __init__(
        self,
        input_size,
        node_num,
        output_size,
        num_layers,
        hidden_activation,
        output_activation,
        dropout_rate,
    ):
        super(MLP, self).__init__()
        self.layers = nn.ModuleList()

        self.layers.append(nn.Linear(input_size, node_num))
        self.layers.append(self.get_activation(hidden_activation))
        self.layers.append(nn.Dropout(dropout_rate))

        for _ in range(num_layers - 1):
            self.layers.append(nn.Linear(node_num, node_num))
            self.layers.append(self.get_activation(hidden_activation))
            self.layers.append(nn.Dropout(dropout_rate))

        self.layers.append(nn.Linear(node_num, output_size))
        self.layers.append(self.get_activation(output_activation))

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


class VAE(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, latent_size):
        super(VAE, self).__init__()
        self.encoder = MLP(
            input_size, hidden_size, hidden_size, num_layers, "LeakyReLU", "None", 0.0
        )
        self.fc_mu = nn.Linear(hidden_size, latent_size)
        self.fc_logvar = nn.Linear(hidden_size, latent_size)
        self.decoder = MLP(
            latent_size, hidden_size, input_size, num_layers, "LeakyReLU", "None", 0.0
        )

    def encode(self, x):
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        return self.decoder(z)

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar
    

class CVAE(nn.Module):
    def __init__(self, input_size, condition_size, hidden_size, num_layers, latent_size):
        super(CVAE, self).__init__()
        self.encoder = MLP(input_size + condition_size, hidden_size, hidden_size, num_layers, "LeakyReLU", "None", 0.0)
        self.fc_mu = nn.Linear(hidden_size, latent_size)
        self.fc_logvar = nn.Linear(hidden_size, latent_size)
        self.decoder = MLP(latent_size + condition_size, hidden_size, input_size, num_layers, "LeakyReLU", "Sigmoid", 0.0)

    def encode(self, x, c):
        h = self.encoder(torch.cat([x, c], dim=1))
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z, c):
        return self.decoder(torch.cat([z, c], dim=1))

    def forward(self, x, c):
        mu, logvar = self.encode(x, c)
        z = self.reparameterize(mu, logvar)
        return self.decode(z, c), mu, logvar

