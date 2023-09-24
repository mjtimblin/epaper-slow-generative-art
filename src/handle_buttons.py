import signal
import RPi.GPIO as GPIO
from inky import Inky_Impressions_7 as Inky
from os import path
from PIL import Image

BUTTON_PINS = [5, 6, 16, 24]  # A, B, C, and D buttons respectively

SRC_DIR = path.dirname(path.realpath(__file__))
REPO_DIR = path.abspath(path.join(SRC_DIR, '..'))
GENERATED_DIR = path.join(REPO_DIR, 'generated')
SD_IMAGE_FILEPATH = path.join(GENERATED_DIR, 'latest_sd_with_caption.png')
QR_CODE_IMAGE_FILEPATH = path.join(GENERATED_DIR, 'latest_qrcode_with_caption.png')

show_sd_image_next = True


def display_image(image_filepath):
    inky = Inky()
    img = Image.open(image_filepath)
    img = img.rotate(90, Image.NEAREST, expand=True)
    resized_img = img.resize(inky.resolution)
    inky.set_image(resized_img)
    inky.show()


def handle_button_press(pin):
    global show_sd_image_next

    if show_sd_image_next and path.exists(SD_IMAGE_FILEPATH):
        display_image(SD_IMAGE_FILEPATH)
    elif path.exists(QR_CODE_IMAGE_FILEPATH):
        display_image(QR_CODE_IMAGE_FILEPATH)

    show_sd_image_next = not show_sd_image_next


def main():
    global show_sd_image_next

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PINS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    for pin in BUTTON_PINS:
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=handle_button_press, bouncetime=250)

    # Display the Stable Diffusion image initially if it exists, otherwise display the QR code image
    if path.exists(SD_IMAGE_FILEPATH):
        display_image(SD_IMAGE_FILEPATH)
        show_sd_image_next = False
    elif path.exists(QR_CODE_IMAGE_FILEPATH):
        display_image(QR_CODE_IMAGE_FILEPATH)
        show_sd_image_next = True

    signal.pause()


if __name__ == '__main__':
    main()
