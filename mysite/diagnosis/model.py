import torch
import torch.nn as nn
import torch.nn.functional as F


class AttentionPool(nn.Module):
    def __init__(self, hidden_size: int) -> None:
        super().__init__()
        self.proj = nn.Linear(hidden_size, hidden_size)
        self.score = nn.Linear(hidden_size, 1, bias=False)

    def forward(self, hidden_states: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        scores = self.score(torch.tanh(self.proj(hidden_states))).squeeze(-1)
        scores = scores.masked_fill(~mask, -1e4)
        weights = torch.softmax(scores, dim=-1).unsqueeze(-1)
        return torch.sum(hidden_states * weights, dim=1)


class CharHybridDiagnosisModel(nn.Module):
    def __init__(
        self,
        vocab_size,
        num_classes,
        embed_dim=128,
        rnn_hidden_size=128,
        cnn_channels=96,
        dropout=0.35,
        kernel_sizes=(2, 3, 4, 5),
    ):
        super().__init__()
        if not isinstance(kernel_sizes, tuple):
            kernel_sizes = tuple(kernel_sizes)
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.embedding_dropout = nn.Dropout(dropout * 0.5)
        self.convs = nn.ModuleList(
            nn.Conv1d(embed_dim, cnn_channels, kernel_size=kernel_size)
            for kernel_size in kernel_sizes
        )
        self.encoder = nn.GRU(
            input_size=embed_dim,
            hidden_size=rnn_hidden_size,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout * 0.5,
        )
        self.attention = AttentionPool(rnn_hidden_size * 2)
        self.cnn_projection = nn.Linear(cnn_channels * len(kernel_sizes), rnn_hidden_size * 2)
        self.gate = nn.Sequential(
            nn.Linear(rnn_hidden_size * 4, rnn_hidden_size * 2),
            nn.Sigmoid(),
        )
        self.activation = nn.GELU() if hasattr(nn, "GELU") else nn.ReLU()
        self.classifier = nn.Sequential(
            nn.LayerNorm(rnn_hidden_size * 2),
            nn.Linear(rnn_hidden_size * 2, rnn_hidden_size * 2),
            self.activation,
            nn.Dropout(dropout),
            nn.Linear(rnn_hidden_size * 2, num_classes),
        )

    def forward(self, input_ids):
        mask = input_ids.ne(0)
        embedded = self.embedding_dropout(self.embedding(input_ids))

        conv_input = embedded.transpose(1, 2)
        cnn_features = []
        for conv in self.convs:
            if hasattr(F, "gelu"):
                conv_output = F.gelu(conv(conv_input))
            else:
                conv_output = F.relu(conv(conv_input))
            pooled, _ = torch.max(conv_output, dim=-1)
            cnn_features.append(pooled)
        cnn_feature = torch.cat(cnn_features, dim=-1)
        cnn_feature = self.cnn_projection(cnn_feature)

        rnn_output, _ = self.encoder(embedded)
        rnn_feature = self.attention(rnn_output, mask)

        gate = self.gate(torch.cat([cnn_feature, rnn_feature], dim=-1))
        fused = gate * cnn_feature + (1.0 - gate) * rnn_feature
        return self.classifier(fused)
