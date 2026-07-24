import logging


logger = logging.getLogger(__name__)


def _load_tatr_from_pretrained(model_path: str, revision: str = None):
    """
    Load a ``TableTransformerForObjectDetection`` model, working around
    ``huggingface_hub`` strict-dataclass validation introduced in transformers 5.x.

    The ``microsoft/table-transformer-*`` checkpoints on the Hub contain
    ``"dilation": null`` in their ``config.json``, which fails ``bool``
    field validation inside ``huggingface_hub >= 1.13.0`` when loaded via
    ``from_pretrained``.

    Strategy: try the normal path first (fast, works on transformers 4.x, <5.4 and
    any future fixed 5.x).  On the specific dilation error, fall back to
    downloading the raw config, patching the field, and passing a pre-built
    config object.
    """
    from transformers import TableTransformerForObjectDetection

    try:
        return TableTransformerForObjectDetection.from_pretrained(
            model_path, revision=revision
        )
    except Exception as e:
        # Strictly match only huggingface_hub's StrictDataclassFieldValidationError
        # for the 'dilation' field — re-raise everything else untouched.
        try:
            from huggingface_hub.errors import StrictDataclassFieldValidationError

            _is_target = isinstance(
                e, StrictDataclassFieldValidationError
            ) and "dilation" in str(e)
        except ImportError:
            _is_target = False

        if not _is_target:
            raise

        logger.warning(
            "Applying compatibility workaround for transformers 5.x: "
            "fixing 'dilation' field in model config for %s",
            model_path,
        )

        import json

        from huggingface_hub import hf_hub_download
        from transformers import AutoConfig

        config_file = hf_hub_download(
            repo_id=model_path, filename="config.json", revision=revision
        )
        with open(config_file) as f:
            config_dict = json.load(f)

        if config_dict.get("dilation") is None:
            config_dict["dilation"] = False

        model_type = config_dict.pop("model_type", "detr")
        config_cls = AutoConfig.for_model(model_type)
        # transformers 5.x for_model() returns an instance, not a class
        if not isinstance(config_cls, type):
            config_cls = type(config_cls)
        config = config_cls(**config_dict)

        return TableTransformerForObjectDetection.from_pretrained(
            model_path, config=config, revision=revision
        )
