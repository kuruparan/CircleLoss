import torch
from torch import nn, Tensor


class NormLinear(nn.Linear):
    def __init__(self, in_features: int, out_features: int) -> None:
        super(NormLinear, self).__init__(in_features, out_features, bias=False)

    def forward(self, inp: Tensor) -> Tensor:
        return nn.functional.linear(nn.functional.normalize(inp),
                                    nn.functional.normalize(self.weight))


# TODO: check detach
class CircleLoss(nn.Module):
    def __init__(self, m: float, gamma: float) -> None:
        super(CircleLoss, self).__init__()
        self.m = m
        self.gamma = gamma
        self.loss = nn.CrossEntropyLoss()

    def forward(self, inp: Tensor, label: Tensor) -> Tensor:
        a = torch.clamp_min(inp + self.m, min=0).detach()
        a[label] = torch.clamp_min(- inp[label] + 1 + self.m, min=0).detach()
        sigma = torch.ones_like(inp, device=inp.device, dtype=inp.dtype) * self.m
        sigma[label] = 1 - self.m
        return self.loss(a * (inp - sigma) * self.gamma, label)


if __name__ == "__main__":
    feature = torch.rand(32, 128)
    gt = torch.randint(high=10, dtype=torch.long, size=(32,))
    norm_liner = NormLinear(128, 10)
    loss = CircleLoss(0.35, 256)
    print(loss(norm_liner(feature), gt))
