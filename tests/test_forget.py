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
def no_message(monkeypatch):
    monkeypatch.setattr(plugin, '_show_forget_message', lambda win: None)


def press():
    return [types.SimpleNamespace(type=plugin.BUTTON_FORGET_EVENT)]


def assert_forgotten(app, savedir):
    assert not (savedir / PICTURE).exists()
    assert (savedir / 'forget' / PICTURE).exists()
    assert app.count.forgotten == 1
    assert app.previous_picture is None
    assert app.previous_picture_file is None


def test_wait_screen_forgets_the_previous_picture(cfg, app, savedir):
    plugin.state_wait_do(cfg, app, press())

    assert_forgotten(app, savedir)
    assert app.count.remaining_duplicates == 0  # The print LED and icon go off


def test_wait_screen_is_drawn_again_once(cfg, app):
    plugin.state_wait_do(cfg, app, press())

    assert plugin.state_wait_validate(app) == 'wait'
    assert plugin.state_wait_validate(app) is None


def test_print_screen_forgets_the_picture_and_prevents_printing(cfg, app, savedir):
    plugin.state_print_do(cfg, app, None, press())

    assert_forgotten(app, savedir)
    assert app.count.remaining_duplicates == 0


def test_nothing_happens_without_a_press(cfg, app, savedir):
    plugin.state_wait_do(cfg, app, [])

    assert (savedir / PICTURE).exists()
    assert app.count.forgotten == 0


def test_nothing_happens_without_a_picture(cfg, app, savedir):
    app.previous_picture_file = None

    plugin.state_wait_do(cfg, app, press())

    assert (savedir / PICTURE).exists()
    assert app.count.forgotten == 0
