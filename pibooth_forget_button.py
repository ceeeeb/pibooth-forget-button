# -*- coding: utf-8 -*-

"""Pibooth plugin to add a third button for forgetting/deleting photos.

This plugin adds a dedicated "forget" button that moves the current photo
to the forget folder, separate from the capture and print buttons.
"""

import os
import os.path as osp

import pygame

import pibooth
from pibooth.utils import LOGGER

__version__ = "1.2.0"

# Custom event for forget button
BUTTON_FORGET_EVENT = pygame.USEREVENT + 10


@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options."""
    cfg.add_option('FORGET_BUTTON', 'forget_btn_pin', 0,
                   "Physical GPIO IN pin for forget button (BOARD numbering, 0 to disable)",
                   "Forget Button Pin", "0")

    cfg.add_option('FORGET_BUTTON', 'forget_led_pin', 0,
                   "Physical GPIO OUT pin to light LED when forget button is pressed (0 to disable)",
                   "Forget LED Pin", "0")

    cfg.add_option('FORGET_BUTTON', 'debounce_delay', 0.3,
                   "How long to press the forget button in seconds",
                   "Debounce Delay", "0.3")


@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Initialize the forget button."""
    pin = cfg.getint('FORGET_BUTTON', 'forget_btn_pin')

    if not pin:
        LOGGER.info("Forget button plugin: disabled (pin = 0)")
        app.forget_button = None
        return

    try:
        debounce = cfg.getfloat('FORGET_BUTTON', 'debounce_delay')
        # app.board knows which GPIO backend the running machine needs, the pin
        # stays the physical one whatever the board.
        app.forget_button = app.board.create_button(pin, hold_time=debounce)

        def on_forget_held():
            """Called when forget button is held."""
            LOGGER.debug("Forget button pressed")
            event = pygame.event.Event(BUTTON_FORGET_EVENT)
            pygame.event.post(event)

        app.forget_button.when_held = on_forget_held

        LOGGER.info("Forget button initialized on pin %s", pin)

        # Initialize LED if configured
        led_pin = cfg.getint('FORGET_BUTTON', 'forget_led_pin')
        if led_pin:
            app.forget_led = app.board.create_led(led_pin)
            LOGGER.info("Forget LED initialized on pin %s", led_pin)
        else:
            app.forget_led = None

    except Exception as e:
        LOGGER.error("Failed to initialize forget button: %s", str(e))
        app.forget_button = None


@pibooth.hookimpl
def pibooth_cleanup(app):
    """Cleanup GPIO resources."""
    if hasattr(app, 'forget_button') and app.forget_button:
        app.forget_button.close()
    if hasattr(app, 'forget_led') and app.forget_led:
        app.forget_led.close()


def find_forget_event(events):
    """Check if forget button was pressed."""
    for event in events:
        if event.type == BUTTON_FORGET_EVENT:
            return event
    return None


def _show_forget_message(win):
    """Display 'Photo oubliée!' message on screen."""
    import time
    from pibooth import fonts

    # Get window dimensions
    rect = win.get_rect()

    # Create font
    font = pygame.font.Font(fonts.get_filename(fonts.CURRENT), rect.height // 8)

    # Render text
    text = font.render("Photo oubliee !", True, (255, 255, 255))
    text_rect = text.get_rect(center=(rect.width * 3 // 4, rect.height // 2))

    # Fill screen with dark background
    win.surface.fill((50, 50, 50))

    # Draw text
    win.surface.blit(text, text_rect)

    # Update display
    pygame.display.update()

    # Wait 2 seconds
    time.sleep(2)


@pibooth.hookimpl
def state_wait_enter(app):
    """Blink the forget LED while the previous picture can be forgotten."""
    if not getattr(app, 'forget_led', None):
        return
    if app.previous_picture_file:
        app.forget_led.blink(on_time=0.5, off_time=0.5)
    else:
        app.forget_led.off()


@pibooth.hookimpl
def state_wait_exit(app):
    if getattr(app, 'forget_led', None):
        app.forget_led.off()


@pibooth.hookimpl
def state_print_enter(app):
    """Turn on forget LED when entering print state."""
    if hasattr(app, 'forget_led') and app.forget_led:
        app.forget_led.blink(on_time=0.5, off_time=0.5)
        LOGGER.debug("Forget LED blinking")


@pibooth.hookimpl
def state_print_exit(app):
    """Turn off forget LED when exiting print state."""
    if hasattr(app, 'forget_led') and app.forget_led:
        app.forget_led.off()
        LOGGER.debug("Forget LED off")


def forget_previous_picture(cfg, app):
    """Move the previous picture to the forget folder of each save directory,
    stop showing it and prevent printing it."""
    for savedir in cfg.gettuple('GENERAL', 'directory', 'path'):
        forgetdir = osp.join(savedir, "forget")
        if not osp.isdir(forgetdir):
            os.makedirs(forgetdir)

        src = osp.join(savedir, osp.basename(app.previous_picture_file))
        dst = osp.join(forgetdir, osp.basename(app.previous_picture_file))

        if osp.exists(src):
            os.rename(src, dst)
            LOGGER.info("Moved %s to forget folder", osp.basename(src))

    app.count.forgotten += 1

    app.previous_picture = None
    app.previous_animated = None
    app.previous_picture_file = None

    app.count.remaining_duplicates = 0


@pibooth.hookimpl
def state_print_do(cfg, app, win, events):
    """Handle forget button press during print state."""
    if not hasattr(app, 'forget_button') or not app.forget_button:
        return

    if find_forget_event(events) and app.previous_picture_file:
        LOGGER.info("Forget button: Moving picture to forget folder")

        # Turn off LED when action is taken
        if hasattr(app, 'forget_led') and app.forget_led:
            app.forget_led.off()

        forget_previous_picture(cfg, app)

        # Display "Photo oubliée!" message
        _show_forget_message(win)


@pibooth.hookimpl
def state_wait_do(cfg, app, win, events):
    """Handle forget button press during wait state (to delete previous photo)."""
    if not hasattr(app, 'forget_button') or not app.forget_button:
        return

    if find_forget_event(events) and app.previous_picture_file:
        LOGGER.info("Forget button: Moving previous picture to forget folder")

        # Flash LED if available
        if hasattr(app, 'forget_led') and app.forget_led:
            app.forget_led.blink(on_time=0.1, n=3)

        forget_previous_picture(cfg, app)
        _show_forget_message(win)
        # Draw the wait screen and set the LEDs again, without the picture
        app.forget_redraw = True


@pibooth.hookimpl
def state_wait_validate(app):
    """Enter the wait state again once the previous picture is forgotten."""
    if getattr(app, 'forget_redraw', False):
        app.forget_redraw = False
        return 'wait'
