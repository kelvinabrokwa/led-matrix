# LED Matrix

A library and web app for having fun with an [Adafruit RGB LED Matrix](https://www.adafruit.com/products/1484)

Depends on [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix)

## Running

```sh
# Install dependencies, build submodules, install nginx config
make setup

# restart nginx
sudo service nginx reload

# start the server
sudo ./pyvenv/bin/python server.py
```

## Features
- Draw: draw from a web app to your display
- Text: render a text message
- GIFs: Render GIFs by URL

