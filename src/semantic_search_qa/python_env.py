import os

import torch

print(100 * "-" + "\nPython Env\n" + 100 * "-")
for name, value in os.environ.items():
    print(f"{name}: {value}")
print(f"CUDA: {torch.cuda.is_available()}")
