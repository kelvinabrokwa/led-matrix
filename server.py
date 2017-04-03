""" ultra fuego web service for playing with an RGB led matrix
"""

import argparse
import base64
import datetime
import logging
import os
import re
import sys
import time

from color_quant.get_colors import get_colors
from color_quant.utils import get_image
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from io import BytesIO
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from time import sleep
from threading import Thread, Timer, Event
from urllib.request import urlopen


DIR = os.path.dirname(os.path.realpath(__file__))
FONT_DIR = os.path.join(DIR, "rpi-rgb-led-matrix", "fonts")


# Set up logging
logger = logging.getLogger(__name__)
loggingHandler = logging.StreamHandler(sys.stdout)
loggingHandler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s %(message)s"))
logger.addHandler(loggingHandler)
logger.setLevel(logging.INFO)


# Set up matrix
options = RGBMatrixOptions()
options.rows = 32
options.hardware_mapping = "adafruit-hat"
matrix = RGBMatrix(options=options)


# Set up threading
gif = False
clock = False
funky = False
matrix_clear_event = Event()
# mark as clear, this means no threads are currently rendering on a loop
matrix_clear_event.set()


# HTTP API
app = Flask(__name__)
CORS(app)


@app.before_request
def before_request():
    """
    """
    global gif
    global clock
    global funky
    if not matrix_clear_event.is_set():
        gif = False
        clock = False
        funky = False
        logger.info("Waiting for matrix clear")
        matrix_clear_event.wait()


@app.route("/")
def home():
    """Heartbeat
    """
    return ";)"


@app.route("/text", methods=["POST"])
def text_message():
    """Receive a text message
    """
    msg = request.json["message"]
    logger.info("New message: " + msg)
    render_text(msg)

    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/img/<format>", methods=["POST"])
def image(format):
    """Receive a text message
    """
    if format == "png":
        img_b64 = request.json["img"]
        img_formatted = re.sub("^data:image/.+;base64,", "", img_b64)
        img = Image.open(BytesIO(base64.b64decode(img_formatted))).convert("RGB")
    elif format == "url":
        data = BytesIO(urlopen(request.json["url"]).read())
        img = Image.open(data)
    else:
        return make_response(jsonify({"message": "unsupported format"}), 415)

    try:
        render_image(img)
    except:
        return make_response(jsonify({"message": "could not render image"}), 500)

    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/gif", methods=["POST"])
def gif_():
    """Display GIF from URL
    """
    global gif
    gif = True
    url = request.json["url"]
    data = BytesIO(urlopen(url).read())
    gif = Image.open(data)
    Thread(target=render_gif, args=(gif,)).start()
    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/clock", methods=["POST"])
def clock_():
    """Display the time
    """
    global clock

    clock = True
    Thread(target=render_clock).start()

    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/funky", methods=["POST"])
def funky_():
    """
    """
    global funky

    funky = True
    Thread(target=render_funky).start()

    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/color-match", methods=["POST"])
def color_match_():
    """
    """
    color_match()
    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/clear", methods=["POST"])
def clear():
    """Clear the matrix
    """
    render_clear()
    return make_response(jsonify({"message": "ok"}), 200)


#
# Rendering functions
#


def loop_renderer(renderer):
    """Decorator for renderers that need to grab the display lock and release it
    when they're done
    """
    def f(*args):
        matrix_clear_event.clear()  # Lock matrix
        renderer(*args)
        render_clear()  # Clear matrix and release lock
    return f


def render_text(text):
    """Render a text message
    """
    global matrix

    fonts = {
        "small": {
            "name": "5x8.bdf",
            "n": 7
        },
        "medium": {
            "name": "6x10.bdf",
            "n": 5
        },
        "large": {
            "name": "7x13.bdf",
            "n": 3
        }
    }
    canvas = matrix.CreateFrameCanvas()
    font = graphics.Font()
    text_color = graphics.Color(255, 255, 0)
    if len(text) < 9:
        font_size = "large"
    elif len(text) < 13:
        font_size = "medium"
    else:
        font_size = "small"
    font.LoadFont(os.path.join(FONT_DIR, fonts[font_size]["name"]))
    lines = []
    line = ""
    for word in text.split(" "):
        if line == "":
            line += word
        else:
            if len(line + " " + word) < fonts[font_size]["n"]:
                line += " " + word
            else:
                lines.append(line)
                line = word
    lines.append(line)  # add the last line
    for i, line in enumerate(lines):
        x = 0
        y = i * font.baseline
        pos = {"x": x, "y": y + font.baseline}
        graphics.DrawText(canvas, font, pos["x"], pos["y"], text_color, line)

    matrix.SwapOnVSync(canvas)


def render_image(img):
    """Render a base64 encoded png
    """
    img.thumbnail((32, 32), Image.ANTIALIAS)
    canvas = matrix.CreateFrameCanvas()
    canvas.SetImage(img, (32 - img.size[0]) / 2, (32 - img.size[1]) / 2)
    matrix.SwapOnVSync(canvas)


@loop_renderer
def render_clock():
    """Render the time on a 1 second loop
    """
    global clock
    global matrix

    hour_color = graphics.Color(255, 255, 0)
    hour_font = graphics.Font()
    hour_font.LoadFont(os.path.join(FONT_DIR, "9x15B.bdf"))
    min_color = graphics.Color(255, 0, 255)
    min_font = hour_font
    sec_color = graphics.Color(0, 255, 255)
    sec_font = graphics.Font()
    sec_font.LoadFont(os.path.join(FONT_DIR, "6x9.bdf"))

    while clock:
        rn = datetime.now()
        canvas = matrix.CreateFrameCanvas()

        hour = str(rn.hour)
        if rn.hour < 10:
            hour = "0" + hour
        graphics.DrawText(canvas, hour_font, 0, 2 + hour_font.baseline, hour_color, hour)

        minute = str(rn.minute)
        if rn.minute < 10:
            minute = "0" + minute
        graphics.DrawText(canvas, min_font, 0, 2 + hour_font.baseline + min_font.baseline, min_color, minute)

        sec = str(rn.second)
        if rn.second < 10:
            sec = "0" + sec
        graphics.DrawText(canvas, sec_font, 20, 2 + hour_font.baseline + min_font.baseline, sec_color, sec)

        matrix.SwapOnVSync(canvas)

        time.sleep(0.9)


@loop_renderer
def render_gif(jif):
    """Play a GIF
    """
    global gif

    # Create an array of frames
    frames = []
    palette = None
    try:
        while True:
            if palette is None:
                palette = jif.getpalette()
            frame = jif.copy()
            frame.putpalette(palette)
            frame = frame.convert("RGB")
            frame.thumbnail((32, 32), Image.ANTIALIAS)
            frames.append(frame)
            jif.seek(jif.tell() + 1)
    except EOFError:
        pass

    nframes = len(frames)
    idx = 0

    while gif:
        canvas = matrix.CreateFrameCanvas()
        frame = frames[idx]
        canvas.SetImage(frame, (32 - frame.size[0]) / 2, (32 - frame.size[1]) / 2)
        matrix.SwapOnVSync(canvas)
        idx = (idx + 1) % nframes
        sleep(0.05)


colors = [
    (209, 0, 0),     # red
    (255, 102, 34),  # orange
    (255, 218, 33),  # yellow
    (51, 221, 0),    # green
    (17, 51, 204),   # blue
    (34, 0, 102),    # indigo
    (51, 0, 68),     # violet
]


@loop_renderer
def render_funky():
    """Alternate ROYGBIV
    """
    global funky

    canvas = matrix.CreateFrameCanvas()
    idx = 0
    while funky:
        for x in range(0, matrix.width):
            for y in range(0, matrix.height):
                canvas.SetPixel(x, y, *colors[idx])
        matrix.SwapOnVSync(canvas)
        idx = (idx + 1) % len(colors)
        sleep(0.3)


def color_match():
    """
    """
    canvas = matrix.CreateFrameCanvas()
    img = get_image()
    colors = get_colors(img, 4)
    print(colors)
    matrix.SwapOnVSync(canvas)


def render_clear():
    """Clear the matrix
    """
    logger.info("Clearing matrix")
    canvas = matrix.CreateFrameCanvas()
    matrix.SwapOnVSync(canvas)
    matrix_clear_event.set()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", dest="port", type=int, default=3000)
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port)
