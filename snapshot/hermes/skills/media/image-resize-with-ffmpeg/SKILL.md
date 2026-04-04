---
name: image-resize-with-ffmpeg
description: Resize a local image to target desktop or social dimensions using ffmpeg when Pillow/ImageMagick are unavailable.
---

Use this when a user sends or references a local image file and wants a resized output, especially in Hermes environments where PIL/Pillow is not installed but ffmpeg/ffprobe is available.

When to use
- Resize a single image to a target resolution
- Make wallpaper-sized outputs like 1920x1080
- Need a fast fallback when Python PIL is missing
- Want letterbox/blur-fill/crop behavior using only terminal tools

Steps
0. Check available tools and fall back cleanly.
   - If Pillow/PIL is unavailable, do not spend time trying to install it for a simple resize.
   - Check what is present with something like:
     which identify || which magick || which ffprobe || which ffmpeg || which convert || which python3
   - If ffprobe/ffmpeg are available, proceed entirely with ffmpeg.

1. Inspect the source image.
   - Verify file exists.
   - Get dimensions with:
     ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 INPUT

2. Choose the resize mode.
   - Preserve aspect ratio exactly inside target canvas: use pad.
   - Full-screen wallpaper without distortion: use blurred background + centered foreground.
   - Fill the frame edge-to-edge: use force_original_aspect_ratio=increase plus crop.
   - Only stretch if the user explicitly wants distortion.

3. Create the output with ffmpeg.

   A. Blurred wallpaper fill with centered original (good default for square art -> 16:9 wallpaper):
   ffmpeg -y -i INPUT -filter_complex "[0:v]scale=TARGET_W:TARGET_H:force_original_aspect_ratio=increase:flags=lanczos,crop=TARGET_W:TARGET_H,boxblur=20:10[bg];[0:v]scale=INNER_W:INNER_H:force_original_aspect_ratio=decrease:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2" -frames:v 1 -q:v 2 OUTPUT

   Example for 1024x1024 art to 1920x1080:
   ffmpeg -y -i INPUT -filter_complex "[0:v]scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,boxblur=20:10[bg];[0:v]scale=1080:1080:force_original_aspect_ratio=decrease:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2" -frames:v 1 -q:v 2 OUTPUT

   B. Fit inside frame with padding (no blur):
   ffmpeg -y -i INPUT -vf "scale=TARGET_W:TARGET_H:force_original_aspect_ratio=decrease:flags=lanczos,pad=TARGET_W:TARGET_H:(ow-iw)/2:(oh-ih)/2:black" -frames:v 1 -q:v 2 OUTPUT

   C. Fill and crop (no bars, no blur layer):
   ffmpeg -y -i INPUT -vf "scale=TARGET_W:TARGET_H:force_original_aspect_ratio=increase:flags=lanczos,crop=TARGET_W:TARGET_H" -frames:v 1 -q:v 2 OUTPUT

4. Verify the output dimensions.
   ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 OUTPUT

5. Return the file path to the user as media.
   - In Telegram-compatible Hermes responses, send:
     MEDIA:/absolute/path/to/output.jpg

Pitfalls
- Pillow may be missing; do not assume PIL is installed.
- ffmpeg may warn about image sequence patterns for single-image output. Using -frames:v 1 is usually sufficient even if the warning appears with image2 output.
- Preserve subject proportions unless the user explicitly asks for a stretched image.
- For square source art on widescreen targets, blurred-background composite usually looks better than hard crop.

Verification
- Confirm output dimensions with ffprobe.
- If the user asked for “fit laptop screen,” clarify the actual display resolution when possible.
- Mention whether the image was cropped, padded, or blur-filled so the user knows what changed.
