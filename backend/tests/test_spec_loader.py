from pathlib import Path

from app.decoder.spec_loader import SpecValidationError, load_decoder_spec


def test_spec_loads_and_validates() -> None:
    spec_path = Path("app/specs/dali_decoder.json")
    schema_path = Path("app/specs/dali_decoder.schema.json")

    spec = load_decoder_spec(spec_path, schema_path)
    assert spec.raw["version"]
    assert "forward16" in spec.raw


def test_spec_semantic_validation_catches_overlap(tmp_path: Path) -> None:
    broken_spec = {
        "version": "x",
        "frame_types": ["rx_forward16", "rx_forward24", "rx_backward"],
        "forward16": {
            "special_commands": [],
            "opcode_table": [
                {"opcode": {"type": "range", "start": "0x10", "end": "0x1F"}, "name": "A", "status": "decoded"},
                {"opcode": {"type": "exact", "value": "0x10"}, "name": "B", "status": "decoded"},
            ],
        },
        "forward24": {"special_c1": [], "device_level_opcode_table": []},
        "correlation": {"backward_directions": ["rx_backward"]},
    }

    spec_file = tmp_path / "broken.json"
    schema_file = tmp_path / "schema.json"
    spec_file.write_text(__import__("json").dumps(broken_spec), encoding="utf-8")
    schema_file.write_text("{}", encoding="utf-8")

    try:
        load_decoder_spec(spec_file, schema_file)
    except SpecValidationError as exc:
        assert "overlaps" in str(exc)
    else:
        raise AssertionError("Expected SpecValidationError")