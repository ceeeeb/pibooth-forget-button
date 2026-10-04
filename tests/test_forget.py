# -*- coding: utf-8 -*-

import types

import pytest

import pibooth_forget_button as plugin

PICTURE = '2026-10-04-17-26-22_pibooth.jpg'


@pytest.fixture
def savedir(tmp_path):
    (tmp_path / PICTURE).write_bytes(b'jpeg')
    return tmp_path


@pytest.fixture
def cfg(savedir):
    return types.SimpleNamespace(gettuple=lambda section, option, types_: (str(savedir),))


@pytest.fixture
def app(savedir):
    return types.SimpleNamespace(
        forget_button=object(), forget_led=None,
        previous_picture=object(), previous_animated=None,
        previous_picture_file=str(savedir / PICTURE),
        count=types.SimpleNamespace(forgotten=0, remaining_duplicates=3))


@pytest.fixture(autouse=True)
def messages(monkeypatch):
    shown = []
    monkeypatch.setattr(plugin, '_show_forget_message', shown.append)
    return shown


def press():
    return [types.SimpleNamespace(type=plugin.BUTTON_FORGET_EVENT)]


def assert_forgotten(app, savedir):
    assert not (savedir / PICTURE).exists()
    assert (savedir / 'forget' / PICTURE).exists()
    assert app.count.forgotten == 1
    assert app.previous_picture is None
    assert app.previous_picture_file is None


def test_wait_screen_forgets_the_previous_picture(cfg, app, savedir):
    plugin.state_wait_do(cfg, app, None, press())

    assert_forgotten(app, savedir)
    assert app.count.remaining_duplicates == 0  # The print LED and icon go off


def test_wait_screen_confirms_the_forget(cfg, app, messages):
    win = object()

    plugin.state_wait_do(cfg, app, win, press())

    assert messages == [win]


def test_wait_screen_is_drawn_again_once(cfg, app):
    plugin.state_wait_do(cfg, app, None, press())

    assert plugin.state_wait_validate(app) == 'wait'
    assert plugin.state_wait_validate(app) is None


def test_print_screen_forgets_the_picture_and_prevents_printing(cfg, app, savedir):
    plugin.state_print_do(cfg, app, None, press())

    assert_forgotten(app, savedir)
    assert app.count.remaining_duplicates == 0


def test_nothing_happens_without_a_press(cfg, app, savedir):
    plugin.state_wait_do(cfg, app, None, [])

    assert (savedir / PICTURE).exists()
    assert app.count.forgotten == 0


def test_nothing_happens_without_a_picture(cfg, app, savedir):
    app.previous_picture_file = None

    plugin.state_wait_do(cfg, app, None, press())

    assert (savedir / PICTURE).exists()
    assert app.count.forgotten == 0


class FakeLed(object):

    def __init__(self):
        self.state = 'off'

    def blink(self, on_time=1, off_time=1, n=None):
        self.state = 'blinking'

    def off(self):
        self.state = 'off'


def test_forget_led_blinks_on_the_wait_screen_while_a_picture_exists(app):
    app.forget_led = FakeLed()

    plugin.state_wait_enter(app)
    assert app.forget_led.state == 'blinking'

    plugin.state_wait_exit(app)
    assert app.forget_led.state == 'off'


def test_forget_led_is_off_on_the_wait_screen_without_picture(app):
    app.forget_led = FakeLed()
    app.forget_led.state = 'blinking'
    app.previous_picture_file = None

    plugin.state_wait_enter(app)

    assert app.forget_led.state == 'off'
