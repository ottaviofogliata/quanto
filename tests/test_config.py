from quanto.config import load_config


def test_load_config(tmp_path):
    sample = tmp_path / "c.yaml"
    sample.write_text("experiment: {}\n")
    cfg = load_config(sample)
    assert cfg.experiment == {}
