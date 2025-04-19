import cv2
import os
import numpy as np
from random import randrange
from datetime import datetime
from nova_space_armada.utilities.pygui_actions import *

import pytesseract
from nova_space_armada.containers import (system_scavenger_icon, system_ally_icon, ocr_engine_path,
                                          system_ally_flag_icon)


def object_counter(images_path, threshold=0.90, get_objects=False, screenshot=None):
    discovered_objects = list()
    if screenshot is not None:
        img_rgb = cv2.imread(screenshot)
    else:
        img_rgb = cv2.imread(take_screenshot())
    images = os.listdir(images_path)

    for image in images:
        image_path = os.path.join(images_path, image)
        template = cv2.imread(image_path)

        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        if loc[0].size > 0:
            for x, y in list(zip(loc[1], loc[0])):
                pack_cords = (x, y)
                # calculate is the picture close to other cords in list
                already_in = [(x1, y1) for x1, y1 in discovered_objects if abs(x1 - x) < 5 or abs(y1 - y) < 5]
                if not already_in:
                    discovered_objects.append(pack_cords)
    if get_objects is True:
        return discovered_objects
    return len(discovered_objects)


def click_when_ready(images_path, threshold=0.90, match=False, click=True, move=True, no_loop=False,
                     offset=(0,0), on_result=False, focus=False, timeout=None, skip=None):
    x, y = None, None
    off_x, off_y = offset
    loop_start = datetime.now()
    while match is False:
        img_rgb = cv2.imread(take_screenshot())
        images = os.listdir(images_path)
        image_loop_start = datetime.now()
        for image in images:
            image_time_elapsed = abs((image_loop_start - datetime.now()).total_seconds())
            if image_time_elapsed > 3:
                image_loop_start = datetime.now()

            if timeout is not None:
                time_elapsed = abs((loop_start - datetime.now()).total_seconds())
                if time_elapsed > timeout:
                    return f'TIMEOUT: could not match any image for {images_path}'

            image_path = os.path.join(images_path, image)
            template = cv2.imread(image_path)
            res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)

            if loc[0].size > 0 and loc[1].size > 0:
                match = True
            else:
                match = False

            if match is True:
                x = int(loc[1][0])
                y = int(loc[0][0])
                if skip is not None:
                    if (x, y) in skip:
                        continue
                    skip.update({(x, y): datetime.now()})
                if move is True:
                    pyautogui.moveTo(x+off_x, y+off_y)
                if click is True:
                    sleep(0.5)
                    pyautogui.click(x=x+off_x, y=y+off_y)
                    if focus is True:
                        # pyautogui.moveTo(50, 50)
                        pyautogui.moveTo(randrange(5, 10), randrange(5, 10))
                        sleep(2)
                if on_result is True:
                    return x, y
                break
        if no_loop is True:
            return x, y
        sleep(0.2)
    return x, y


def process_system_data():
    pytesseract.pytesseract.tesseract_cmd = ocr_engine_path
    system_scavenger_icon_dir = os.path.join(os.path.pardir, system_scavenger_icon)
    system_ally_icon_dir = os.path.join(os.path.pardir, system_ally_icon)
    system_ally_flag_dir = os.path.join(os.path.pardir, system_ally_flag_icon)

    planet_items = {'scavengers': system_scavenger_icon_dir, 'ally': system_ally_icon_dir,
                    'ally_flag': system_ally_flag_dir}
    system_data = {'scavengers': 0, 'ally': 0, 'ally_flag': 0}

    for item_name, item_path in planet_items.items():
        icon_cords = object_counter(item_path, threshold=0.90, get_objects=True)
        if len(icon_cords):
            scav_icon = icon_cords[0]
            left = scav_icon[0]
            right = left + 150
            upper = scav_icon[1]
            lower = upper + 60

            rgb_img = cv2.imread(take_screenshot())
            if item_name in ['ally_flag']:
                ally_flag_cnt = len(object_counter(system_ally_flag_dir, threshold=0.90, get_objects=True))
                system_data.update({item_name: ally_flag_cnt})
                continue

            img_crop = rgb_img[upper:lower, left:right]

            item_number = int(pytesseract.image_to_string(img_crop, config='--psm 7 -c tessedit_char_whitelist=0123456789').strip())
            system_data.update({item_name: int(item_number)})
    return system_data


def hsv_objects_search(screenshot_path, bgr_down_limit: list, bgr_upper_limit: list,
                       min_height: int = None, max_height: int = None,
                       min_width: int = None, max_width: int = None,
                       edges: list = None, proximity: int = None):
    """
    :param bgr_down_limit: darkest color to search in BGR format
    :param bgr_upper_limit: the lightest color to search in BGR format
    :param min_height: min height of object
    :param max_height: max height of object
    :param min_width: min width of object
    :param max_width: max width of object
    :param edges: list with number of edges that object should have, if not provided it will get all objects
    :param proximity: how many px should be considered as another obj
    :return:
    """
    # read iscreenshot image
    img = cv2.imread(screenshot_path)

    # convert image to hsv format
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # lower bound and upper bound for
    lower_bound = np.array(bgr_down_limit)
    upper_bound = np.array(bgr_upper_limit)

    # find the colors within the boundaries
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # define kernel size
    kernel = np.ones((1, 1), np.uint8)

    # remove unnecessary noise from mask
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # segment only the detected region
    segmented_img = cv2.bitwise_and(img, img, mask=mask)

    # find contours from the mask
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # get filtered cordinates
    coordinates = []
    filtered_contoures = dict()
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if edges is not None:
            edge_count = len(cv2.approxPolyDP(contour, 0.03 * cv2.arcLength(contour, True), True))
            if edge_count not in edges:
                continue

        # filter object by size
        size_compare = {'>': {min_width: w, min_height: h}, '<': {max_width: w, max_height: h}}

        skip = False
        for compare_type, compare_data in size_compare.items():
            for defined_size, actual_size in compare_data.items():
                if defined_size is not None:
                    eval_text = f"{actual_size} {compare_type} {defined_size}"
                    eval_result = eval(eval_text)
                    if eval_result is False and skip is False:
                        skip = True

        if skip is True:
            continue

        # proximity object skip
        if proximity is not None:
            for coordinate in coordinates:
                x_, y_ = coordinate
                if abs(x - x_) < proximity or abs(y - y_) < proximity:
                    skip = True
                    break
                else:
                    coordinates.append((x, y))

        if skip is True:
            continue

        filtered_contoures.update({(x, y): contour})
    filtered_contoures = dict(list(sorted(filtered_contoures.items())))
    return filtered_contoures