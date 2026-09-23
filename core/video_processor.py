"""
Video Processing Pipeline for Telegram Video Stickers (Bot API 7.0+).
- Formats: WebM container, VP9 codec (libvpx-vp9), no audio (-an).
- Dimensions: 512x512, max 2.95s duration, 30 fps.
- File size strict enforcement: <= 256 KB (262 144 байт).
- Pillow for crystal-clear meme text overlay with black outline (stroke_width=4).
- Seamless support for local files, user uploads (webapp/media/uploads/), animated GIFs, and static images.
- Asynchronous non-blocking FFmpeg execution.
"""

import os
import shutil
import asyncio
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple, List, Any
from urllib.parse import urlparse
import aiohttp
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

MAX_STICKER_SIZE_BYTES = 256 * 1024  # 262 144 байт
_FFMPEG_PATH: Optional[str] = None


def find_ffmpeg() -> str:
    """
    Автоматически находит исполняемый файл FFmpeg в системе.
    1. imageio_ffmpeg
    2. Системный PATH
    3. Стандартные системные каталоги
    """
    global _FFMPEG_PATH
    if _FFMPEG_PATH and os.path.isfile(_FFMPEG_PATH):
        return _FFMPEG_PATH

    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.isfile(exe):
            _FFMPEG_PATH = exe
            return _FFMPEG_PATH
    except Exception:
        pass

    which_ffmpeg = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if which_ffmpeg and os.path.isfile(which_ffmpeg):
        _FFMPEG_PATH = which_ffmpeg
        return _FFMPEG_PATH

    candidates = [
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\tools\ffmpeg\bin\ffmpeg.exe",
        r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\ffmpeg\bin\ffmpeg.exe"),
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
    ]

    for candidate in candidates:
        if os.path.isfile(candidate):
            _FFMPEG_PATH = candidate
            return _FFMPEG_PATH

    raise RuntimeError("FFmpeg не найден в системе. Установите imageio-ffmpeg.")


def resolve_media_path(source: str) -> Optional[str]:
    """
    Разрешает путь к локальному медиафайлу (включая webapp/media/ и webapp/media/uploads/).
    Поддерживает:
    - Абсолютные и относительные пути
    - Пути вида '/media/uploads/file.gif' или 'uploads/file.gif'
    - URL вида 'http://localhost:8080/media/uploads/file.gif'
    """
    if not source:
        return None

    # 1. Прямой путь на диске
    if os.path.isfile(source):
        return os.path.abspath(source)

    base_dir = Path(__file__).resolve().parent.parent
    webapp_media = base_dir / "webapp" / "media"
    uploads_dir = webapp_media / "uploads"

    # Очищаем URL query string, если есть (напр. ?v=123)
    clean_src = source.split("?")[0].replace("\\", "/")

    # 2. Проверяем пути, содержащие 'media/uploads/' или '/uploads/'
    if "media/uploads/" in clean_src:
        filename = clean_src.split("media/uploads/")[-1].lstrip("/")
        cand = uploads_dir / filename
        if cand.is_file():
            return str(cand)

    if "/uploads/" in clean_src or clean_src.startswith("uploads/"):
        filename = clean_src.split("uploads/")[-1].lstrip("/")
        cand = uploads_dir / filename
        if cand.is_file():
            return str(cand)

    # 3. Проверяем пути, содержащие '/media/'
    if "/media/" in clean_src or clean_src.startswith("media/"):
        rel_path = clean_src.split("media/")[-1].lstrip("/")
        cand_media = webapp_media / rel_path
        if cand_media.is_file():
            return str(cand_media)
        cand_upload = uploads_dir / rel_path
        if cand_upload.is_file():
            return str(cand_upload)

    # 4. Проверяем относительно корня проекта
    cand_base = base_dir / clean_src.lstrip("/")
    if cand_base.is_file():
        return str(cand_base)

    # 5. Поиск по имени файла в uploads и media
    fname_only = os.path.basename(clean_src)
    if fname_only:
        cand_u = uploads_dir / fname_only
        if cand_u.is_file():
            return str(cand_u)
        cand_m = webapp_media / fname_only
        if cand_m.is_file():
            return str(cand_m)

    return None


def is_static_image_file(path: str) -> bool:
    """
    Проверяет, является ли файл статичным изображением (1 кадр) или анимированным/видео.
    Для статичных изображений требуется FFmpeg флаг '-loop 1'.
    Для анимированных GIF и видео используется '-stream_loop -1'.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
        try:
            with Image.open(path) as img:
                return not getattr(img, "is_animated", False)
        except Exception:
            return True
    elif ext == ".gif":
        try:
            with Image.open(path) as img:
                # Если GIF содержит только 1 кадр — он статичен
                return not getattr(img, "is_animated", False)
        except Exception:
            return False
    return False


def _parse_color(color_val: Any, default: Tuple[int, int, int, int] = (255, 255, 255, 255)) -> Tuple[int, int, int, int]:
    """Парсит HEX-цвет (#FFFFFF, #00FF88 и т.д.) или RGB кортеж в RGBA кортеж."""
    if not color_val:
        return default
    if isinstance(color_val, (tuple, list)):
        if len(color_val) == 3:
            return (int(color_val[0]), int(color_val[1]), int(color_val[2]), 255)
        elif len(color_val) >= 4:
            return (int(color_val[0]), int(color_val[1]), int(color_val[2]), int(color_val[3]))
    if isinstance(color_val, str):
        c = color_val.strip().lstrip("#")
        if len(c) == 6:
            try:
                r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
                return (r, g, b, 255)
            except ValueError:
                pass
        elif len(c) == 8:
            try:
                r, g, b, a = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16)
                return (r, g, b, a)
            except ValueError:
                pass
    return default


def _find_best_font(size: int = 38, font_family: str = "impact") -> ImageFont.FreeTypeFont:
    """Ищет подходящий жирный шрифт с поддержкой кириллицы по выбранному стилю."""
    fam = (font_family or "impact").lower()

    family_candidates = {
        "impact": [
            r"C:\Windows\Fonts\impact.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Impact.ttf",
            r"C:\Windows\Fonts\arialbd.ttf"
        ],
        "rubik": [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            r"C:\Windows\Fonts\impact.ttf"
        ],
        "montserrat": [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\tahoma.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ],
        "comic": [
            r"C:\Windows\Fonts\comicbd.ttf",
            r"C:\Windows\Fonts\comic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            r"C:\Windows\Fonts\arialbd.ttf"
        ]
    }

    candidates = list(family_candidates.get(fam, family_candidates["impact"]))
    # Общие резервные шрифты
    candidates += [
        r"C:\Windows\Fonts\impact.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]

    for path in candidates:
        if os.path.isfile(path):
            try:
                font = ImageFont.truetype(path, size)
                bbox = font.getbbox("ТЕСТ123")
                if bbox and (bbox[2] - bbox[0] > 0):
                    return font
            except Exception:
                continue

    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _wrap_text_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    stroke_width: int = 4
) -> List[str]:
    """Разбивает текст на строки под заданную максимальную ширину."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font, stroke_width=stroke_width)
        line_w = bbox[2] - bbox[0]
        if line_w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def create_text_overlay_png(
    text: str,
    output_path: Optional[str] = None,
    size: Tuple[int, int] = (512, 512),
    font_family: str = "impact",
    text_color: str = "#FFFFFF",
    stroke_color: str = "#000000",
    stroke_width: int = 4,
    font_size_scale: float = 1.0
) -> str:
    """
    Создает прозрачный PNG 512x512 с адаптивным авто-переносом строк,
    жирным мемным текстом с настраиваемыми цветами, обводкой и масштабом шрифта.
    """
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        output_path = temp_file.name
        temp_file.close()

    clean_text = text.strip().upper()
    img = Image.new("RGBA", size, (0, 0, 0, 0))

    if not clean_text:
        img.save(output_path, "PNG")
        return output_path

    draw = ImageDraw.Draw(img)
    max_text_width = size[0] - 56

    scale = max(0.65, min(float(font_size_scale or 1.0), 1.55))
    base_size = 44 if len(clean_text) < 22 else (36 if len(clean_text) < 42 else 28)
    initial_font_size = int(base_size * scale)
    font = None
    lines = []

    min_size = max(14, int(18 * scale))
    for test_size in range(initial_font_size, min_size, -2):
        font = _find_best_font(test_size, font_family=font_family)
        candidate_lines = _wrap_text_lines(draw, clean_text, font, max_text_width, stroke_width=stroke_width)
        if len(candidate_lines) <= 4:
            lines = candidate_lines
            break
    else:
        font = _find_best_font(min_size, font_family=font_family)
        lines = _wrap_text_lines(draw, clean_text, font, max_text_width, stroke_width=stroke_width)

    line_spacing = 6
    line_heights = []
    line_widths = []

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=stroke_width)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])

    total_height = sum(line_heights) + (len(lines) - 1) * line_spacing
    y_current = size[1] - total_height - 35
    if y_current < 20:
        y_current = 20

    fill_rgba = _parse_color(text_color, (255, 255, 255, 255))
    stroke_rgba = _parse_color(stroke_color, (0, 0, 0, 255))

    for i, line in enumerate(lines):
        x = (size[0] - line_widths[i]) // 2
        draw.text(
            (x, y_current),
            line,
            font=font,
            fill=fill_rgba,
            stroke_width=stroke_width,
            stroke_fill=stroke_rgba
        )
        y_current += line_heights[i] + line_spacing

    img.save(output_path, "PNG")
    return output_path


def generate_text_overlay_png(
    top_text: str,
    bottom_text: str,
    output_path: str,
    width: int = 512,
    height: int = 512,
    font_family: str = "impact",
    text_color: str = "#FFFFFF",
    stroke_color: str = "#000000",
    stroke_width: int = 4,
    font_size_scale: float = 1.0,
    text_layout: str = "both"
) -> str:
    """Создает прозрачный PNG 512x512 с настраиваемым размером, стилем и расположением текста."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    max_w = width - 50

    top_clean = (top_text or "").strip().upper()
    bottom_clean = (bottom_text or "").strip().upper()

    fill_rgba = _parse_color(text_color, (255, 255, 255, 255))
    stroke_rgba = _parse_color(stroke_color, (0, 0, 0, 255))

    scale = max(0.65, min(float(font_size_scale or 1.0), 1.55))
    layout = (text_layout or "both").lower()

    if layout == "center":
        center_text = f"{top_clean} {bottom_clean}".strip() or bottom_clean or top_clean
        if center_text:
            font_center = _find_best_font(int(42 * scale), font_family=font_family)
            center_lines = _wrap_text_lines(draw, center_text, font_center, max_w, stroke_width=stroke_width)
            line_heights = [draw.textbbox((0, 0), l, font=font_center, stroke_width=stroke_width)[3] - draw.textbbox((0, 0), l, font=font_center, stroke_width=stroke_width)[1] for l in center_lines]
            total_h = sum(line_heights) + (len(center_lines) - 1) * 6
            y_center = (height - total_h) // 2
            for i, line in enumerate(center_lines):
                bbox = draw.textbbox((0, 0), line, font=font_center, stroke_width=stroke_width)
                x = (width - (bbox[2] - bbox[0])) // 2
                draw.text((x, y_center), line, font=font_center, fill=fill_rgba, stroke_width=stroke_width, stroke_fill=stroke_rgba)
                y_center += line_heights[i] + 6
        img.save(output_path, "PNG")
        return output_path

    if layout in ("both", "top_only") and top_clean:
        font_top = _find_best_font(int(36 * scale), font_family=font_family)
        top_lines = _wrap_text_lines(draw, top_clean, font_top, max_w, stroke_width=stroke_width)
        y_top = 20
        for line in top_lines:
            bbox = draw.textbbox((0, 0), line, font=font_top, stroke_width=stroke_width)
            x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((x, y_top), line, font=font_top, fill=fill_rgba, stroke_width=stroke_width, stroke_fill=stroke_rgba)
            y_top += (bbox[3] - bbox[1]) + 6

    if layout in ("both", "bottom_only") and bottom_clean:
        font_bottom = _find_best_font(int(40 * scale), font_family=font_family)
        bot_lines = _wrap_text_lines(draw, bottom_clean, font_bottom, max_w, stroke_width=stroke_width)
        line_heights = [draw.textbbox((0, 0), l, font=font_bottom, stroke_width=stroke_width)[3] - draw.textbbox((0, 0), l, font=font_bottom, stroke_width=stroke_width)[1] for l in bot_lines]
        total_h = sum(line_heights) + (len(bot_lines) - 1) * 6
        y_bot = height - total_h - 35
        if y_bot < 20:
            y_bot = 20
        for i, line in enumerate(bot_lines):
            bbox = draw.textbbox((0, 0), line, font=font_bottom, stroke_width=stroke_width)
            x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((x, y_bot), line, font=font_bottom, fill=fill_rgba, stroke_width=stroke_width, stroke_fill=stroke_rgba)
            y_bot += line_heights[i] + 6

    img.save(output_path, "PNG")
    return output_path



async def _download_video(url: str, dest_path: str, timeout_sec: float = 12.0) -> None:
    """Скачивает медиафайл по внешнему URL."""
    timeout = aiohttp.ClientTimeout(total=timeout_sec)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Не удалось скачать видео {url}: HTTP {resp.status}")
            with open(dest_path, "wb") as f:
                while True:
                    chunk = await resp.content.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)


async def _execute_ffmpeg(cmd: List[str]) -> None:
    """Запускает FFmpeg подпроцесс и логирует вывод."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        err_msg = stderr.decode(errors="replace")[-500:]
        raise RuntimeError(f"FFmpeg error (code {proc.returncode}): {err_msg}")


async def process_sticker(
    video_source: Optional[str] = None,
    text: str = "",
    output_path: Optional[str] = None,
    video_url: Optional[str] = None,
    caption: str = "",
    top_text: str = "",
    bottom_text: str = "",
    font_family: str = "impact",
    text_color: str = "#FFFFFF",
    stroke_color: str = "#000000",
    font_size_scale: float = 1.0,
    text_layout: str = "both"
) -> bytes:
    """
    Основной пайплайн сборки Telegram Video Sticker:
    - WebM VP9, 512x512, <= 2.95s, <= 256 КБ, 30 FPS, без аудио (-an).
    - Корректная обработка видео, анимированных GIF и статичных картинок (PNG/JPG).
    - Корректное разрешение путей пользовательских загрузок (webapp/media/uploads/).
    - Наложение прозрачного PNG через Pillow и -filter_complex overlay.
    - Поддержка шрифтов, цветов, масштаба размера и расположения текста.
    - Автоматический контроль размера файла.
    """
    source = video_source or video_url
    if not source:
        raise ValueError("Источник видео не указан ('video_source' или 'video_url').")

    combined_text = (text or caption or "").strip()
    clean_top = top_text.strip()
    clean_bottom = bottom_text.strip()

    if not clean_top and not clean_bottom and combined_text:
        if "\n" in combined_text:
            parts = combined_text.split("\n", 1)
            clean_top, clean_bottom = parts[0].strip(), parts[1].strip()
        else:
            clean_bottom = combined_text

    ffmpeg_exe = find_ffmpeg()
    temp_files = []

    try:
        input_video_path = None
        webapp_media = Path(__file__).resolve().parent.parent / "webapp" / "media"
        fallback_video = webapp_media / "fine_dog.mp4"

        # 1. Попытка локального разрешения пути (webapp/media, webapp/media/uploads, прямой путь на диске)
        resolved_local = resolve_media_path(source)
        if resolved_local and os.path.isfile(resolved_local):
            input_video_path = resolved_local
            logger.info(f"Локальный медиафайл успешно разрешен: {input_video_path}")

        # 2. Если файл не локальный, проверяем, является ли он сетевым URL
        if not input_video_path:
            is_url = bool(urlparse(source).scheme in ("http", "https"))
            if is_url:
                try:
                    # Извлекаем расширение из URL если возможно
                    parsed_path = urlparse(source).path
                    ext = os.path.splitext(parsed_path)[1].lower() or ".mp4"
                    t_in = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
                    input_video_path = t_in.name
                    t_in.close()
                    temp_files.append(input_video_path)
                    logger.info(f"Скачивание внешнего видео с {source}...")
                    await _download_video(source, input_video_path)
                except Exception as e:
                    logger.warning(f"Не удалось скачать видео {source}: {e}. Используем fallback.")
                    if fallback_video.is_file():
                        input_video_path = str(fallback_video)
                    else:
                        raise
            else:
                if fallback_video.is_file():
                    logger.warning(f"Файл {source} не найден. Используем fallback.")
                    input_video_path = str(fallback_video)
                else:
                    raise FileNotFoundError(f"Медиафайл не найден: {source}")

        # 3. Определение флагов зацикливания входного потока
        # Статичные изображения требуют -loop 1 для непрерывного потока кадров
        # Анимированные GIF и видео требуют -stream_loop -1 для зацикливания коротких клипов до 2.95s
        if is_static_image_file(input_video_path):
            input_flags = ["-loop", "1"]
            logger.debug(f"Входной файл определен как статичное изображение. Применяем -loop 1.")
        else:
            input_flags = ["-stream_loop", "-1"]
            logger.debug(f"Входной файл определен как анимация/видео. Применяем -stream_loop -1.")

        # 4. Создание PNG-оверлея
        t_overlay = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        overlay_path = t_overlay.name
        t_overlay.close()
        temp_files.append(overlay_path)

        if clean_top or clean_bottom or text_layout == "center":
            generate_text_overlay_png(
                clean_top, clean_bottom, overlay_path, 512, 512,
                font_family=font_family, text_color=text_color, stroke_color=stroke_color,
                font_size_scale=font_size_scale, text_layout=text_layout
            )
        else:
            final_punchline = clean_bottom or clean_top or combined_text
            create_text_overlay_png(
                final_punchline, overlay_path, (512, 512),
                font_family=font_family, text_color=text_color, stroke_color=stroke_color,
                font_size_scale=font_size_scale
            )

        # 5. Выходной файл
        target_path = output_path
        if not target_path:
            t_out = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
            target_path = t_out.name
            t_out.close()
            temp_files.append(target_path)

        filter_complex = (
            "[0:v]scale=512:512:force_original_aspect_ratio=increase,"
            "crop=512:512,fps=30[bg];"
            "[bg][1:v]overlay=0:0:format=auto[v]"
        )

        cmd = [
            ffmpeg_exe,
            "-y"
        ] + input_flags + [
            "-i", input_video_path,
            "-i", overlay_path,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libvpx-vp9",
            "-b:v", "450k",
            "-maxrate", "550k",
            "-bufsize", "900k",
            "-crf", "32",
            "-deadline", "realtime",
            "-cpu-used", "4",
            "-row-mt", "1",
            "-pix_fmt", "yuv420p",
            "-an",
            "-t", "2.95",
            target_path
        ]

        logger.info("Запуск кодирования FFmpeg (VP9, 512x512, <=2.95s, 30fps)...")
        await _execute_ffmpeg(cmd)

        size_bytes = os.path.getsize(target_path)
        logger.info(f"Стикер скомпилирован: {size_bytes} байт ({size_bytes / 1024:.1f} КБ)")

        # Адаптивное дожатие при превышении лимита 256 КБ
        if size_bytes > MAX_STICKER_SIZE_BYTES:
            logger.warning(
                f"Размер стикера ({size_bytes} байт) превысил 256 КБ. Запуск адаптивного дожатия..."
            )
            strict_cmd = [
                ffmpeg_exe,
                "-y"
            ] + input_flags + [
                "-i", input_video_path,
                "-i", overlay_path,
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-c:v", "libvpx-vp9",
                "-b:v", "320k",
                "-maxrate", "390k",
                "-bufsize", "600k",
                "-crf", "38",
                "-deadline", "realtime",
                "-cpu-used", "5",
                "-row-mt", "1",
                "-pix_fmt", "yuv420p",
                "-an",
                "-t", "2.95",
                target_path
            ]
            await _execute_ffmpeg(strict_cmd)
            size_bytes = os.path.getsize(target_path)
            logger.info(f"Размер после дожатия: {size_bytes} байт ({size_bytes / 1024:.1f} КБ)")

            if size_bytes > MAX_STICKER_SIZE_BYTES:
                raise ValueError(
                    f"Размер видео ({size_bytes} байт) превышает лимит Telegram 256 КБ."
                )

        with open(target_path, "rb") as f:
            result_bytes = f.read()

        return result_bytes

    finally:
        for p in temp_files:
            if output_path and p == output_path:
                continue
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception as e:
                    logger.debug(f"Ошибка удаления временного файла {p}: {e}")
