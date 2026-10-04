# pibooth-forget-button

Plugin for [pibooth](https://github.com/pibooth/pibooth) adding a third button to "forget" photos.

## Features

- Dedicated GPIO button to move photos to a "forget" folder
- LED indicator that blinks while the last photo can be forgotten
- Displays "Photo oubliee !" on screen when a photo is forgotten
- Works during both print and wait states: a forgotten photo can no longer be printed

## Installation

```bash
pip install pibooth-forget-button
```

## Configuration

In the file `~/.config/pibooth/pibooth.cfg`, add:

```ini
[FORGET_BUTTON]
# GPIO IN pin for the button (BOARD numbering, 0 to disable)
forget_btn_pin = 36

# GPIO OUT pin for the LED (0 to disable)
forget_led_pin = 37

# Button press duration in seconds
debounce_delay = 0.3
```

## Usage

1. Take a photo with pibooth
2. On the print or wait screen (when the LED blinks), hold the forget button
   for `debounce_delay` seconds
3. The photo is moved to the `forget/` subfolder, "Photo oubliee !" is
   displayed, then the wait screen comes back without the photo and the print
   LED goes off

## License

MIT

## Boards

The plugin drives its button and its LED through `app.board`, the GPIO layer of
[pibooth-ceeeeb](https://github.com/ceeeeb/pibooth), so it works on a Raspberry
Pi and on any board exposing its GPIO through `/dev/gpiochipN`, a Khadas VIM4
for instance. Pin numbers stay the physical ones of the 40 pins header.
