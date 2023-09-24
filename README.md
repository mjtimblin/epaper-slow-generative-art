# ePaper Slow Generative Art

This is a self-contained image generation picture frame showing mostly on-topic news headlines and probably only tangentially related images.

The project runs Stable Diffusion on a raspberry pi, showing a image about a semi-random headline every 5 hours. It's a self-contained image generation picture frame showing mostly on-topic news headlines and probably only tangentially related images.

It could be a lot faster with less iterations, but I like images that are time-wise more "expensive". A new image every 5 hours means that there's a new image in the morning, around lunch, around dinner and during the evening.

The generated images aren't saved, it's a physical piece and I like that you have to be there to see it. If you don't want this, remove the line indicated by the comment in [bin/run.sh](bin/run.sh).

It's fun to guess what the neural nets might have latched on to; Wednesday the day or Wednesday the character? The image generation isn't very good, adding its own interesting twist.

It's a nice way to interact with the news.

Additionally, pressing any of the four buttons on the ePaper HAT will toggle the display between the generated image and a QR code linking to the headline source.

## Generation sources

Headlines are sourced from
- [CNN](https://www.cnn.com/)
- [BBC World](https://www.bbc.com/news/world)
- [The Onion](https://www.theonion.com/)
- [r/nottheonion](https://www.reddit.com/r/nottheonion/)

The sources are chosen to be a nice mix of actual news and random funny bits. They're combined with some random prefixes and suffixes to hopefully make the images interesting.

See `src/prompt_sources.py` for sources and how to add your own.

## Hardware

- Raspberry Pi Zero 2 W
- Inky Impression 7.3" (7 colour ePaper/E Ink HAT)
  - [PiShop.us product page](https://www.pishop.us/product/inky-impression-7-3-7-colour-epaper-e-ink-hat/)
- Geekworm Raspberry Pi Zero 2 W Heatsink C296
  - [Amazon product page](https://www.amazon.com/dp/B09QMBCXLB)
- Amazon Basics 5" x 7" Rectangular Photo Picture Frame
  - [Amazon product page](https://www.amazon.com/dp/B079LNFJQX)

Keep the thermals in mind, the rpi zero is kept busy and pulls a couple of watts. It needs some (passive) airflow, don't put it into the enclosure without any additional cooling. I put it on the outside and that seems to be working fine.

## Installation

### OS Setup

- Install Raspberry Pi OS Lite (**64 bit**)
- Enable I2C and SPI using `sudo raspi-config`
- Increase swap size to 1024
  - `sudo dphys-swapfile swapoff`
  - `sudo nano /etc/dphys-swapfile`
    - Set `CONF_SWAPSIZE=1024`
  - `sudo dphys-swapfile setup`
  - `sudo dphys-swapfile swapon`
- `sudo apt update && sudo apt upgrade -y`
- `sudo apt install git`

### Repository setup

- `cd ~`
- `git clone https://github.com/mjtimblin/epaper-slow-generative-art.git`
- `cd epaper-slow-generative-art`
- `sudo chmod +x bin/*`
- `./bin/install_dependencies.sh`
  - This will take a very long time (probably over an hour)
- `sudo crontab -e`
  - Add the following line
    - `55 5 * * * reboot`
- `crontab -e`
  - Add the following lines
    - `@reboot cd epaper-slow-generative-art && ./bin/handle_button_presses.sh >> /tmp/buttons.log 2>&1`
    - `0 6,11,16,21 * * * cd epaper-slow-generative-art && /usr/bin/flock -w 0 ./bin/run.sh ./bin/run.sh >> /tmp/generate.log 2>&1`
- (optional) `nano src/generate_image.py`
  - Update `NUM_SD_STEPS` with a different value to change the number of steps used during Stable Diffusion image generation
- `sudo reboot`
