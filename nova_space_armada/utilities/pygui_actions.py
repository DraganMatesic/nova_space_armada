import os
import pyautogui
from time import sleep
from nova_space_armada.containers import screenshot_path
pyautogui.FAILSAFE = False


def take_screenshot():
    full_path = os.path.join(os.path.pardir, screenshot_path)
    pyautogui.screenshot(full_path)
    return full_path


