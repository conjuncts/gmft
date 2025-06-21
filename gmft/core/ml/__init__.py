from typing import TYPE_CHECKING, Literal, Union


def _resolve_device(device: Union[Literal["cpu", "cuda", "auto"], str]) -> Literal["cpu", "cuda"]:
    """
    Lazy resolve the device when needed (without importing torch at the top level).
    """
    if device == 'auto':
        import torch
        return 'cuda' if torch.cuda.is_available() else 'cpu'
    return device