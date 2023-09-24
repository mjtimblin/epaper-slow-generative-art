import os
import qrcode
import subprocess
import time
from os import path
from PIL import Image, ImageDraw, ImageFont
from shutil import copyfile
from typing import Tuple

from prompt_sources import get_random_prompt, FALLBACK_PROMPT

SRC_DIR = path.dirname(path.realpath(__file__))
REPO_DIR = path.abspath(path.join(SRC_DIR, '..'))
FONTS_DIR = path.join(REPO_DIR, 'fonts')
GENERATED_DIR = path.join(REPO_DIR, 'generated')
WEIGHTS_DIR = path.join(REPO_DIR, 'weights')
ONNXSTREAM_DIR = path.join(REPO_DIR, 'OnnxStream')
SD_PATH = path.join(ONNXSTREAM_DIR, 'src', 'build', 'sd')

DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 800
MAX_IMAGE_WIDTH = 512
MAX_IMAGE_HEIGHT = 512
PADDING = 10
TEXT_WIDTH = 460

NUM_SD_STEPS = 20
MAX_ARTICLE_HISTORY = 100

IS_RPI = path.isfile('/sys/firmware/devicetree/base/model')


def generate_sd_image(prompt, image_filepath) -> None:
    negative_prompt = 'ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face, blurry, draft, grainy'

    cmd = (f'{SD_PATH} \
       --models-path "{WEIGHTS_DIR}" \
       --steps {str(NUM_SD_STEPS)} \
       {"--rpi" if IS_RPI else ""} \
       --neg-prompt "{negative_prompt}" \
       --prompt "{prompt.prefix + prompt.title + prompt.suffix}" \
       --output "{image_filepath}"')

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=ONNXSTREAM_DIR)

    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print(output.strip().decode(), flush=True)

    if process.returncode != 0:
        raise Exception('Image generation failed')

    if not path.exists(image_filepath):
        raise Exception('Generated image not found')


def generate_qrcode(url, image_filepath) -> None:
    output_image = Image.new('RGB', (DISPLAY_WIDTH, MAX_IMAGE_HEIGHT), (255, 255, 255))
    qrcode_img = None

    # Double the padding around the QR code to help with scanning
    qrcode_max_width = DISPLAY_WIDTH - (4 * PADDING)

    box_size = 12
    while qrcode_img is None:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=0,
        )
        qr.add_data(url)
        qr.make()
        img = qr.make_image(fill_color='black', back_color='white').get_image()

        if img.width <= qrcode_max_width:
            qrcode_img = img
        else:
            box_size -= 1

    x_offset = int((DISPLAY_WIDTH - qrcode_img.width) / 2)
    y_offset = int((MAX_IMAGE_HEIGHT - qrcode_img.height) / 2)

    output_image.paste(qrcode_img, (x_offset, y_offset))
    output_image.save(image_filepath)


def __format_text(drawing, font_path, text) -> Tuple[str, ImageFont.FreeTypeFont]:
    formatted_text = text
    font = ImageFont.truetype(font_path, 36)

    size = 36
    while size > 9:
        font = ImageFont.truetype(font_path, size)
        lines = []
        line = ''

        for word in text.split():
            proposed_line = line
            if line:
                proposed_line += ' '

            proposed_line += word

            if font.getlength(proposed_line) <= TEXT_WIDTH:
                line = proposed_line
            else:
                # If this word was added, the line would be too long
                # Start a new line instead
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        formatted_text = "\n".join(lines)

        x1, y1, x2, y2 = drawing.multiline_textbbox((PADDING, MAX_IMAGE_HEIGHT + PADDING), formatted_text, font,
                                                    align='center', stroke_width=2)
        w, h = x2 - x1, y2 - y1

        if h <= DISPLAY_HEIGHT - MAX_IMAGE_HEIGHT - PADDING - PADDING:
            break
        else:
            # The text did not fit comfortably into the image
            # Try again at a smaller font size
            size -= 1

    return formatted_text, font


def create_image_with_caption(input_image_filepath, output_image_filepath, caption) -> None:
    input_image = Image.open(input_image_filepath)
    output_image = Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT), (0, 0, 0))

    if input_image.width > MAX_IMAGE_WIDTH or input_image.height > MAX_IMAGE_HEIGHT:
        raise Exception('Image is too large. Resize it to 512x512 or smaller.')

    drawing = ImageDraw.Draw(output_image)
    font_path = path.join(FONTS_DIR, 'Oswald-Light.ttf')
    formatted_text, font = __format_text(drawing, font_path, caption)

    x1, y1, x2, y2 = drawing.multiline_textbbox((PADDING, MAX_IMAGE_HEIGHT + PADDING), formatted_text, font=font,
                                                align='center', stroke_width=2)
    width, height = x2 - x1, y2 - y1
    x_offset = int((DISPLAY_WIDTH - width) / 2)
    drawing.multiline_text((x_offset, MAX_IMAGE_HEIGHT + PADDING), formatted_text, font=font, align='center',
                           stroke_width=2, stroke_fill='#000')

    # Since the SD image is 512 px wide and the display is 480 px wide, we need to offset the image by 16 px to have the
    # image centered horizontally with an equal crop on both sides.
    if input_image.width > DISPLAY_WIDTH:
        x_offset = -int((input_image.width - DISPLAY_WIDTH) / 2)
    else:
        x_offset = int((DISPLAY_WIDTH - input_image.width) / 2)

    if input_image.height < MAX_IMAGE_HEIGHT:
        y_offset = int((MAX_IMAGE_HEIGHT - input_image.height) / 2)
    else:
        y_offset = 0

    output_image.paste(input_image, (x_offset, y_offset))

    output_image.save(output_image_filepath)


def main():
    timestamp = time.strftime('%Y%m%d_%H%M%S')

    prior_titles_filepath = path.join(GENERATED_DIR, f'previous_article_titles.txt')
    sd_image_filepath = path.join(GENERATED_DIR, f'{timestamp}_sd.png')
    sd_image_with_caption_filepath = path.join(GENERATED_DIR, f'{timestamp}_sd_with_caption.png')
    latest_sd_image_with_caption_filepath = path.join(GENERATED_DIR, 'latest_sd_with_caption.png')
    qrcode_image_filepath = path.join(GENERATED_DIR, f'{timestamp}_qrcode.png')
    qrcode_image_with_caption_filepath = path.join(GENERATED_DIR, f'{timestamp}_qrcode_with_caption.png')
    latest_qrcode_image_with_caption_filepath = path.join(GENERATED_DIR, 'latest_qrcode_with_caption.png')

    os.makedirs(GENERATED_DIR, exist_ok=True)

    blacklisted_titles = []
    if path.exists(prior_titles_filepath):
        with open(prior_titles_filepath, 'r') as f:
            blacklisted_titles = [line.strip('\n') for line in f.readlines()]

    prompt = get_random_prompt(blacklisted_titles)

    if prompt.title != FALLBACK_PROMPT.title:
        blacklisted_titles.insert(0, prompt.title)

    with open(prior_titles_filepath, 'w') as f:
        for title in blacklisted_titles[:MAX_ARTICLE_HISTORY]:
            f.write(title + '\n')

    generate_sd_image(prompt, sd_image_filepath)
    create_image_with_caption(sd_image_filepath, sd_image_with_caption_filepath, prompt.title)

    generate_qrcode(prompt.url, qrcode_image_filepath)
    create_image_with_caption(qrcode_image_filepath, qrcode_image_with_caption_filepath, prompt.title)

    # Delete intermediate files
    os.remove(sd_image_filepath)
    os.remove(qrcode_image_filepath)

    # Make a copy of the SD image with the caption with a static filename
    if path.exists(latest_sd_image_with_caption_filepath):
        os.remove(latest_sd_image_with_caption_filepath)
    copyfile(sd_image_with_caption_filepath, latest_sd_image_with_caption_filepath)

    # Make a copy of the QR code image with the caption with a static filename
    if path.exists(latest_qrcode_image_with_caption_filepath):
        os.remove(latest_qrcode_image_with_caption_filepath)
    copyfile(qrcode_image_with_caption_filepath, latest_qrcode_image_with_caption_filepath)

    if IS_RPI:
        from inky import Inky_Impressions_7 as Inky
        inky = Inky()
        img = Image.open(latest_sd_image_with_caption_filepath)
        img = img.rotate(90, Image.NEAREST, expand=True)
        resized_img = img.resize(inky.resolution)
        inky.set_image(resized_img)
        inky.show()


if __name__ == '__main__':
    main()
