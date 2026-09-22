import asyncio
import os
import sys
import tempfile

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.gemini_client import generate_vibe, CATEGORIES
from core.tenor_client import search_media, search_gifs
from core.video_processor import find_ffmpeg, create_text_overlay_png, process_sticker, MAX_STICKER_SIZE_BYTES
from api.server import setup_app
from bot.config import config
from aiohttp.test_utils import TestClient, TestServer


async def test_all():
    print("=== [1/4] Testing Core: Gemini Vibe Generation ===")
    vibe = await generate_vibe("it_deadline")
    print(f"  Punchline: {vibe['punchline']}")
    print(f"  Search query: {vibe['search_query']}")
    print(f"  Emoji: {vibe['emoji']}")
    assert len(vibe["punchline"]) > 0, "Punchline should not be empty"
    assert len(vibe["search_query"]) > 0, "Search query should not be empty"
    print("  [OK] Gemini generation passed!")

    print("\n=== [2/4] Testing Core: Tenor Media Search ===")
    media = await search_media(vibe["search_query"], limit=3)
    print(f"  Found {len(media)} media items")
    assert len(media) > 0, "Should find at least 1 media item"
    print(f"  Sample URL: {media[0]['url']}")
    print("  [OK] Tenor media search passed!")

    print("\n=== [3/4] Testing Core: Video Processor & FFmpeg ===")
    ffmpeg_exe = find_ffmpeg()
    print(f"  FFmpeg: {ffmpeg_exe}")
    assert os.path.isfile(ffmpeg_exe), "FFmpeg binary must exist"

    with tempfile.TemporaryDirectory() as tmp_dir:
        input_mp4 = os.path.join(tmp_dir, "test_input.mp4")
        cmd = [
            ffmpeg_exe, "-y",
            "-f", "lavfi", "-i", "testsrc=duration=1.2:size=320x240:rate=30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", input_mp4
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await proc.communicate()
        assert os.path.isfile(input_mp4), "Test input MP4 must be generated"

        print("  Running process_sticker to WebM VP9 512x512...")
        sticker_bytes = await process_sticker(
            video_source=input_mp4,
            text=vibe["punchline"]
        )
        print(f"  Output size: {len(sticker_bytes)} bytes ({len(sticker_bytes)/1024:.1f} KB)")
        assert len(sticker_bytes) <= MAX_STICKER_SIZE_BYTES, f"Size exceeds limit: {len(sticker_bytes)}"
        assert sticker_bytes[:4] == b"\x1a\x45\xdf\xa3", "Header must be valid EBML/WebM"
        print("  [OK] Video processor passed!")

    print("\n=== [4/4] Testing API Server & Endpoints ===")
    app = await setup_app(bot=None, dp=None)
    client = TestClient(TestServer(app))
    await client.start_server()

    try:
        # Test index.html
        resp = await client.get("/")
        print(f"  GET / -> HTTP {resp.status}")
        assert resp.status == 200, "Webapp index.html should return 200"
        text = await resp.text()
        assert "Vibe Stickers" in text, "Webapp title should be in HTML"

        # Test local static media
        resp = await client.get("/media/fine_dog.mp4")
        print(f"  GET /media/fine_dog.mp4 -> HTTP {resp.status}")
        assert resp.status == 200, "Local media video should return 200"
        assert resp.content_type == "video/mp4", "Content-Type must be video/mp4"

        resp = await client.get("/api/pack-info?dev_user_id=12345")
        print(f"  GET /api/pack-info -> HTTP {resp.status}")
        assert resp.status == 200, "Pack info should return 200"
        pack_data = await resp.json()
        print(f"  Pack data: {pack_data}")
        assert "pack_name" in pack_data

        resp = await client.post("/api/generate-vibe", json={"category": "friday_evening"})
        print(f"  POST /api/generate-vibe -> HTTP {resp.status}")
        assert resp.status == 200, "Generate vibe should return 200"
        vibe_data = await resp.json()
        print(f"  Generated vibe: {vibe_data['vibe']['punchline']}")
        assert vibe_data["status"] == "ok"

        resp = await client.get("/api/search-gifs?q=cat&limit=2")
        print(f"  GET /api/search-gifs -> HTTP {resp.status}")
        assert resp.status == 200, "Search gifs should return 200"
        gifs_data = await resp.json()
        print(f"  Found GIFs: {len(gifs_data.get('gifs', []))}")
        assert gifs_data["status"] == "ok"

        # Test POST /api/commit-sticker (DEV_MODE)
        resp = await client.post("/api/commit-sticker", json={
            "video_url": gifs_data["gifs"][0]["url"],
            "caption": "ПОНЕЛ ЗРЯ БЫКАСАНУЛ",
            "emoji": "🗿"
        })
        print(f"  POST /api/commit-sticker -> HTTP {resp.status}")
        assert resp.status == 200, "Commit sticker should return 200"
        commit_data = await resp.json()
        print(f"  Commit response: {commit_data}")
        assert commit_data["success"] is True

        # Test POST /api/upload-media
        from aiohttp import FormData
        upload_form = FormData()
        test_file_bytes = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"  # Valid MP4 header sample
        upload_form.add_field("file", test_file_bytes, filename="my_custom_vibe.mp4", content_type="video/mp4")
        resp = await client.post("/api/upload-media", data=upload_form)
        print(f"  POST /api/upload-media -> HTTP {resp.status}")
        assert resp.status == 200, "Upload media should return 200"
        upload_data = await resp.json()
        print(f"  Upload response: {upload_data}")
        assert upload_data["status"] == "ok", "Upload status must be 'ok'"
        assert upload_data["url"].startswith("/media/uploads/"), "Upload URL must start with /media/uploads/"
        assert "filename" in upload_data, "Response must contain 'filename'"

        # Test GET uploaded static file
        resp = await client.get(upload_data["url"])
        print(f"  GET {upload_data['url']} -> HTTP {resp.status}")
        assert resp.status == 200, "Uploaded media should be accessible via static route"
        uploaded_bytes = await resp.read()
        assert uploaded_bytes == test_file_bytes, "Uploaded file content must match original bytes"

        # Test invalid extension rejection
        bad_form = FormData()
        bad_form.add_field("file", b"echo evil", filename="script.sh", content_type="application/x-sh")
        resp = await client.post("/api/upload-media", data=bad_form)
        print(f"  POST /api/upload-media (bad extension) -> HTTP {resp.status}")
        assert resp.status == 400, "Should reject invalid file extension with 400"

        # Test POST /api/upload-media with animated GIF
        import io
        from PIL import Image
        gif_buffer = io.BytesIO()
        frame1 = Image.new("RGBA", (128, 128), (255, 0, 0, 255))
        frame2 = Image.new("RGBA", (128, 128), (0, 0, 255, 255))
        frame1.save(gif_buffer, format="GIF", save_all=True, append_images=[frame2], duration=200, loop=0)
        gif_bytes = gif_buffer.getvalue()

        gif_form = FormData()
        gif_form.add_field("file", gif_bytes, filename="animated_meme.gif", content_type="image/gif")
        resp = await client.post("/api/upload-media", data=gif_form)
        print(f"  POST /api/upload-media (GIF) -> HTTP {resp.status}")
        assert resp.status == 200, "Upload GIF should return 200"
        gif_upload_data = await resp.json()
        assert gif_upload_data["url"].endswith(".gif"), "Uploaded GIF URL must end with .gif"

        # Test POST /api/commit-sticker with uploaded GIF
        resp = await client.post("/api/commit-sticker", json={
            "video_url": gif_upload_data["url"],
            "top_text": "КОГДА ЗАГРУЗИЛ СВОЮ ГИФКУ",
            "bottom_text": "И ВСЁ РАБОТАЕТ ИДЕАЛЬНО",
            "emoji": "🎉"
        })
        print(f"  POST /api/commit-sticker (with uploaded GIF) -> HTTP {resp.status}")
        assert resp.status == 200, "Commit sticker with GIF should return 200"
        commit_gif_data = await resp.json()
        assert commit_gif_data["success"] is True, "GIF commit sticker must succeed"

        # Test 33+ clips collection
        from core.tenor_client import FALLBACK_MEMES
        print(f"\n=== [5/6] Testing Media Library Size: {len(FALLBACK_MEMES)} memes ===")
        assert len(FALLBACK_MEMES) >= 33, f"Expected at least 33 memes in collection, got {len(FALLBACK_MEMES)}"
        print(f"  [OK] Collection contains {len(FALLBACK_MEMES)} video meme templates!")

        print("\n=== [6/6] Testing AI GIF Search Pipeline (/api/ai-search-gifs) ===")
        # Test POST /api/ai-search-gifs with Russian query
        resp = await client.post("/api/ai-search-gifs", json={
            "query": "горящий дедлайн кот",
            "limit": 4
        })
        print(f"  POST /api/ai-search-gifs (Russian query) -> HTTP {resp.status}")
        assert resp.status == 200, "AI search gifs should return 200"
        ai_search_data = await resp.json()
        print(f"  AI Search Query: '{ai_search_data.get('search_query')}'")
        print(f"  Suggested Top: '{ai_search_data.get('suggested_top')}'")
        print(f"  Suggested Bottom: '{ai_search_data.get('suggested_bottom')}'")
        print(f"  Emoji: '{ai_search_data.get('emoji')}'")
        print(f"  GIFs count: {len(ai_search_data.get('gifs', []))}")
        assert ai_search_data["status"] == "ok"
        assert len(ai_search_data["gifs"]) > 0, "AI search must return gifs"
        assert "suggested_top" in ai_search_data

        # Test GET /api/ai-search-gifs with pagination
        resp = await client.get("/api/ai-search-gifs?q=panic&limit=3&offset=3")
        print(f"  GET /api/ai-search-gifs?q=panic&limit=3&offset=3 -> HTTP {resp.status}")
        assert resp.status == 200, "GET /api/ai-search-gifs should return 200"
        ai_get_data = await resp.json()
        assert ai_get_data["status"] == "ok"
        assert len(ai_get_data["gifs"]) > 0
        assert "has_more" in ai_get_data, "Response must include 'has_more'"
        assert "offset" in ai_get_data, "Response must include 'offset'"

        # Test POST /api/ai-search-gifs with shuffle & pos
        resp = await client.post("/api/ai-search-gifs", json={
            "query": "cat",
            "limit": 4,
            "offset": 2,
            "pos": "test_token",
            "shuffle": True
        })
        assert resp.status == 200
        ai_shuffle_data = await resp.json()
        assert ai_shuffle_data["status"] == "ok"
        assert len(ai_shuffle_data["gifs"]) > 0

        # Verify HTML has Split View & Onboarding & Thumbs Pagination elements
        resp = await client.get("/")
        html_content = await resp.text()
        assert "split-viewport" in html_content, "Split View container must be present in HTML"
        assert "panel-studio" in html_content, "Studio panel must be present in HTML"
        assert "panel-feed" in html_content, "Feed panel must be present in HTML"
        assert "onboardingGuide" in html_content, "3-step onboarding guide must be present in HTML"
        assert "btnAiGenerate" in html_content, "AI generate button must be present in HTML"
        assert "thumbsPaginationBar" in html_content, "Thumbs pagination bar must be present in HTML"
        assert "btnLoadMoreGifs" in html_content, "Load more gifs button must be present in HTML"
        assert "btnShuffleGifs" in html_content, "Shuffle gifs button must be present in HTML"
        assert "thumbsCounterLabel" in html_content, "Thumbs counter label must be present in HTML"
        print("  [OK] AI GIF Search, Pagination, Shuffle, and UI controls verification passed!")

        print("  [OK] All API endpoints, Upload pipeline and AI Search passed!")
    finally:
        await client.close()

    print("\n" + "="*50)
    print(">>> SUCCESS: ALL END-TO-END TESTS PASSED! <<<")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(test_all())