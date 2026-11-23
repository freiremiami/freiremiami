import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))

from video_generator import generate_video  # noqa: E402


def _response(json_data=None, content=None, status=200):
    mock = MagicMock()
    mock.status_code = status
    mock.raise_for_status = MagicMock()
    if json_data is not None:
        mock.json.return_value = json_data
    if content is not None:
        mock.content = content
    return mock


def test_generate_video_polls_until_complete_and_downloads():
    generate_response = _response(json_data={"data": {"video_id": "vid_123"}})
    processing_response = _response(json_data={"data": {"status": "processing"}})
    completed_response = _response(
        json_data={
            "data": {
                "status": "completed",
                "video_url": "https://cdn.heygen.com/vid_123.mp4",
                "captioned_video_url": "https://cdn.heygen.com/vid_123_captioned.mp4",
            }
        }
    )
    download_response = _response(content=b"fake-mp4-bytes")

    env = {"HEYGEN_API_KEY": "fake-key", "HEYGEN_VOICE_ID": "voice_abc"}
    with patch.dict("os.environ", env), patch("video_generator.requests.post") as mock_post, patch(
        "video_generator.requests.get"
    ) as mock_get, patch("video_generator.time.sleep"):
        mock_post.return_value = generate_response
        mock_get.side_effect = [processing_response, completed_response, download_response]

        output_path = Path("/tmp/test_output/AAPL.mp4")
        result = generate_video("Apple shares closed up today.", "avatar_xyz", output_path)

    # POST body used the right avatar_id, voice_id, script, and burned-in captions
    post_kwargs = mock_post.call_args.kwargs
    assert mock_post.call_args.args[0] == "https://api.heygen.com/v3/videos"
    body = post_kwargs["json"]
    assert body["type"] == "avatar"
    assert body["avatar_id"] == "avatar_xyz"
    assert body["voice_id"] == "voice_abc"
    assert body["script"] == "Apple shares closed up today."
    assert body["aspect_ratio"] == "9:16"
    assert body["caption"]["file_format"] == "srt"

    # polled with the returned video_id until completed, then downloaded the captioned copy
    assert mock_get.call_args_list[0].args[0] == "https://api.heygen.com/v3/videos/vid_123"
    assert mock_get.call_args_list[2].args[0] == "https://cdn.heygen.com/vid_123_captioned.mp4"
    assert result == output_path
    assert output_path.read_bytes() == b"fake-mp4-bytes"
    output_path.unlink()
    output_path.parent.rmdir()


def test_generate_video_raises_on_failed_status():
    generate_response = _response(json_data={"data": {"video_id": "vid_456"}})
    failed_response = _response(
        json_data={"data": {"status": "failed", "failure_message": "avatar not found"}}
    )

    env = {"HEYGEN_API_KEY": "fake-key", "HEYGEN_VOICE_ID": "voice_abc"}
    with patch.dict("os.environ", env), patch("video_generator.requests.post") as mock_post, patch(
        "video_generator.requests.get"
    ) as mock_get:
        mock_post.return_value = generate_response
        mock_get.return_value = failed_response
        try:
            generate_video("script", "avatar_xyz", Path("/tmp/test_output/FAIL.mp4"))
            assert False, "expected RuntimeError"
        except RuntimeError as e:
            assert "avatar not found" in str(e)


def test_generate_video_refuses_placeholder_avatar():
    with patch.dict("os.environ", {"HEYGEN_API_KEY": "fake-key", "HEYGEN_VOICE_ID": "voice_abc"}), patch(
        "video_generator.requests.post"
    ) as mock_post:
        try:
            generate_video("script", "PLACEHOLDER", Path("/tmp/test_output/X.mp4"))
            assert False, "expected RuntimeError"
        except RuntimeError as e:
            assert "HEYGEN_AVATAR_ID" in str(e)
    mock_post.assert_not_called()


def test_generate_video_raises_when_captioned_copy_missing():
    generate_response = _response(json_data={"data": {"video_id": "vid_789"}})
    completed_no_captions = _response(
        json_data={"data": {"status": "completed", "video_url": "https://cdn.heygen.com/vid_789.mp4"}}
    )
    env = {"HEYGEN_API_KEY": "fake-key", "HEYGEN_VOICE_ID": "voice_abc"}
    with patch.dict("os.environ", env), patch("video_generator.requests.post") as mock_post, patch(
        "video_generator.requests.get"
    ) as mock_get:
        mock_post.return_value = generate_response
        mock_get.return_value = completed_no_captions
        try:
            generate_video("script", "avatar_xyz", Path("/tmp/test_output/NOCAP.mp4"))
            assert False, "expected RuntimeError"
        except RuntimeError as e:
            assert "captioned" in str(e)


if __name__ == "__main__":
    test_generate_video_polls_until_complete_and_downloads()
    test_generate_video_raises_on_failed_status()
    test_generate_video_refuses_placeholder_avatar()
    test_generate_video_raises_when_captioned_copy_missing()
    print("OK: generate_video polls, downloads, and surfaces failures correctly")
