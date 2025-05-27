import pytest
import torch

from gmft.detectors.tatr import TATRDetector, TATRDetectorConfig
from gmft.formatters.tatr import TATRFormatConfig, TATRFormatter


def test_cuda(doc_tiny):
    if not torch.cuda.is_available():
        pytest.skip("cannot test device settings without cuda")

    page = doc_tiny[0]
    detector = TATRDetector(TATRDetectorConfig(torch_device="cuda"))
    formatter = TATRFormatter(TATRFormatConfig(torch_device="cuda"))
    table = detector.extract(page)[0]
    ft = formatter.extract(table)

    # make sure serialization works - or that it doesn't throw
    y = ft.to_dict()
    # 'config': {'torch_device': device(type='cpu')}
    import json

    js = json.dumps(y)
    from gmft.formatters.tatr import TATRFormattedTable

    ft_redux = TATRFormattedTable.from_dict(json.loads(js), page)


if __name__ == "__main__":
    pytest.main(["-s", __file__])
