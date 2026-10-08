import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))

import orchestrator  # noqa: E402
from bots.publisher.publisher import PublishResult  # noqa: E402

# Real AAPL responses from Massive on 2026-10-08, trimmed to the fields intake reads.
SNAPSHOT = {
    "ticker": {
        "todaysChangePerc": 0.5420738408530574,
        "day": {"c": 338.4901, "v": 13947783.0},
        "min": {"c": 338.4901},
        "prevDay": {"c": 336.67},
    }
}
NEWS = {"results": [{"title": "Meet the Super Semiconductor Stock Crushing Nvidia in 2026"}]}


def _fake_claude_response(text):
    block = MagicMock(type="text", text=text)
    return MagicMock(content=[block])


def _run(tmp_dir, publish, massive_get=None):
    fake_publish = MagicMock(return_value=[PublishResult("tiktok", "p1", ""), PublishResult("youtube", "y1", "u")])
    with patch.object(orchestrator, "OUTPUT_DIR", tmp_dir), patch(
        "bots.ticker_intake.ticker_intake._massive_get",
        massive_get or (lambda path, params=None: SNAPSHOT if "snapshot" in path else NEWS),
    ), patch("bots.script_character.script_character.anthropic.Anthropic") as anthropic_cls, patch.object(
        orchestrator, "generate_video", side_effect=lambda script, avatar, path: path
    ) as fake_video, patch.object(orchestrator, "publish_daily_video", fake_publish):
        anthropic_cls.return_value.messages.create.return_value = _fake_claude_response(
            "Apple closed at $338.49 today, up about half a percent."
        )
        failed = orchestrator.run_daily_pipeline(["AAPL"], held_positions=["AAPL"], publish=publish)
    return failed, fake_video, fake_publish


def test_full_pipeline_runs_aapl_end_to_end(tmp_path=Path("/tmp/test_orchestrator")):
    tmp_path.mkdir(exist_ok=True)
    failed, fake_video, fake_publish = _run(tmp_path, publish=True)

    assert failed == []
    script = fake_video.call_args.args[0]
    assert script.startswith("Apple closed at $338.49")
    assert "Not financial advice" in script
    assert "the creator holds a position in AAPL" in script
    assert (tmp_path / "AAPL.txt").read_text() == script
    caption = fake_publish.call_args.kwargs["caption"]
    assert "Not financial advice." in caption
    assert "#aapl" in caption


def test_no_publish_renders_but_does_not_post(tmp_path=Path("/tmp/test_orchestrator")):
    tmp_path.mkdir(exist_ok=True)
    failed, fake_video, fake_publish = _run(tmp_path, publish=False)

    assert failed == []
    fake_video.assert_called_once()
    fake_publish.assert_not_called()


def test_one_failing_ticker_is_reported_not_raised(tmp_path=Path("/tmp/test_orchestrator")):
    tmp_path.mkdir(exist_ok=True)

    def broken_get(path, params=None):
        raise RuntimeError("Massive is down")

    failed, fake_video, _ = _run(tmp_path, publish=False, massive_get=broken_get)
    assert failed == ["AAPL"]
    fake_video.assert_not_called()


if __name__ == "__main__":
    test_full_pipeline_runs_aapl_end_to_end()
    test_no_publish_renders_but_does_not_post()
    test_one_failing_ticker_is_reported_not_raised()
    print("OK: orchestrator runs AAPL end to end, honors --no-publish, and isolates failures")
