import re
import os
import json

import cv2
import pyautogui
from random import randint
from win32gui import GetWindowText, GetForegroundWindow

from nova_space_armada.containers import *
from nova_space_armada.utilities.window import *
from nova_space_armada.utilities.loop import *
from nova_space_armada.utilities.cv_actions import *
from nova_space_armada.utilities import rabbitmq
from nova_space_armada import config


class FleetStatus:
    def __init__(self):
        self.idle = 0
        self.docked = 0
        self.incombat = 0
        self.speeding = 0

class NovaSpaceArmada:
    def __init__(self):
        self.game_window_title = 'BlueStacks App Player'
        self.combat_length = 0  # how much time last battle lasted
        self.min_scavengers_for_attack = 18

        # system map clickable area
        self.screen_w, self.screen_h = pyautogui.size()
        self.upper, self.lower = 260, self.screen_h - 200
        self.left, self.right = 250, self.screen_w - 500

        # system map drag sequnece
        self.drag_seq = [('L', 2), ('R', 4), ('L', 2),
                        ('T', 3), ('L', 1), ('R', 2), ('L', 1),
                        ('C', 0),
                        ('B', 3), ('L', 1), ('R', 2), ('L', 1),
                          ]

    def switch_window(self):
        self.log([{'text': "clean log"}])
        log("checking window name")
        current_window = GetWindowText(GetForegroundWindow())
        log(f"current window {current_window}")
        if re.search(self.game_window_title, current_window) is None:
            log("switching to game window")
            win_manager = WindowMgr()
            win_manager.find_window_wildcard(f"{self.game_window_title}")
            if win_manager._handle is None:
                log(f"window title|{self.game_window_title}|doesn't exist.")
                return
            else:
                win_manager.set_foreground()
        else:
            log("selected wanted window")
            return True

    def goto_star_system(self):
        self.log([{'text': "check if star system icon is displayed"}])
        star_system_dir = os.path.join(os.path.pardir, station_icon_dir)
        star_system_cnt = object_counter(star_system_dir)
        if star_system_cnt >= 1:
            self.log([{'text': "star system detected clicking"}])
            click_when_ready(star_system_dir)

    def set_2d_view(self, wait=False):
        self.log([{'text': "check if system is in 2D display"}])
        twod_switch_dir = os.path.join(os.path.pardir, twod_icon_dir)
        twod_icon_cnt = object_counter(twod_switch_dir, threshold=0.98)
        if twod_icon_cnt >= 1:
            self.log([{'text': "switching to 2D view"}])
            if wait is False:
                click_when_ready(twod_switch_dir)
            else:
                click_when_ready(twod_switch_dir, timeout=20)
        else:
            self.log([{'text': "2D view active"}])

    def set_3d_view(self, wait=False):
        self.log([{'text': "check if system is in 3D display"}])
        treed_switch_dir = os.path.join(os.path.pardir, treed_icon_dir)
        treed_icon_cnt = object_counter(treed_switch_dir, threshold=0.98)
        if treed_icon_cnt >= 1:
            self.log([{'text': "switching to 3D view"}])
            if wait is False:
                click_when_ready(treed_switch_dir)
            else:
                click_when_ready(treed_switch_dir, click=False, move=True, timeout=120)
        else:
            self.log([{'text': "3D view active"}])

    def drag_to(self, where, length, duration=0.2):
        assert where in ['L', 'R', 'T', 'B']

        screen_w, screen_h = pyautogui.size()
        width = (screen_w / 2)
        height = (screen_h / 2)

        if where in ['L']:
            width = 150
            pyautogui.moveTo(width, height)
        if where in ['R']:
            width = screen_w-400
            height = height + 100

        if where in ['B']:
            height = screen_h - 400

        if where in ['T']:
            height = 500

        pyautogui.moveTo(width, height)

        if where == 'L':
            pyautogui.dragTo(width + length, height, duration=duration)

        if where == 'R':
            pyautogui.dragTo(width - length, height, duration=duration)

        if where == 'T':
            pyautogui.dragTo(width, height + length, duration=duration)

        if where == 'B':
            pyautogui.dragTo(width, height - length, duration=duration)

    def galaxy_scan(self):
        """ use bookmarked planets to scan planets near them"""
        self.log([{'text': "system menu icon click"}])
        system_icon_dir = os.path.join(os.path.pardir, system_menu_dir)
        click_when_ready(system_icon_dir)

        self.log([{'text': "system menu more icon click"}])
        system_more_icon_dir = os.path.join(os.path.pardir, system_more_dir)
        click_when_ready(system_more_icon_dir)

        self.log([{'text': "system menu bookmarks icon click"}])
        system_bookmarks_icon_dir = os.path.join(os.path.pardir, system_bookmarks_dir)
        click_when_ready(system_bookmarks_icon_dir)

        # BOOKMARK CORDS PATHS
        bookmarks_dirs = os.path.join(os.path.pardir, bookmark_icons_dir)
        bookmark_arrow = os.path.join(bookmarks_dirs, 'bookmark_goto_arrow')

        self.log([{'text': "gathering bookmark arrow locations"}])
        click_when_ready(bookmark_arrow, click=False)
        bookmark_arrow_cords = object_counter(bookmark_arrow, threshold=0.98, get_objects=True)
        bookmark_cords_cnt = len(bookmark_arrow_cords)
        if bookmark_cords_cnt > 0:
            self.log([{'text': f"bookmark arrow locations found {bookmark_cords_cnt}"}])
        else:
            self.log([{'text': f"bookmark arrow locations could not find"}])

        self.log([{'text': "gathering bookmark dirs"}])
        cnt = 0
        for bookmark_dir in os.listdir(bookmarks_dirs):
            if cnt >= 1:
                self.log([{'text': "system menu icon click"}])
                system_icon_dir = os.path.join(os.path.pardir, system_menu_dir)
                click_when_ready(system_icon_dir)

                self.log([{'text': "system menu more icon click"}])
                system_more_icon_dir = os.path.join(os.path.pardir, system_more_dir)
                click_when_ready(system_more_icon_dir)

                self.log([{'text': "system menu bookmarks icon click"}])
                system_bookmarks_icon_dir = os.path.join(os.path.pardir, system_bookmarks_dir)
                click_when_ready(system_bookmarks_icon_dir)

            if bookmark_dir.__contains__('arrow'):
                continue

            self.log([{'text': f"get bookmark cords for: {bookmark_dir}"}])
            bookmark_cords = object_counter(os.path.join(bookmarks_dirs, bookmark_dir), threshold=0.90, get_objects=True)

            self.log([{'text': f"selecting bookmark arrow inline with bookmark name"}])

            bc_w, bc_h = bookmark_cords[0]
            bookmark_min_cord_idx = dict()
            for idx in range(bookmark_cords_cnt):
                bac_w, bac_h = bookmark_arrow_cords[idx]
                bookmark_min_cord_idx.update({abs(bc_h - bac_h): idx})

            min_cord_diff = min(bookmark_min_cord_idx)
            min_cord_idx = bookmark_min_cord_idx.get(min_cord_diff)
            inline_arrow = bookmark_arrow_cords[min_cord_idx]

            self.log([{'text': f"opening bookmark location"}])
            pyautogui.moveTo(inline_arrow)
            sleep(1)
            pyautogui.click(inline_arrow)

            sleep(5)
            self.log([{'text': f"goto galaxy view"}])
            galaxy_icons = os.path.join(os.path.pardir, galaxy_icon_dir)
            click_when_ready(galaxy_icons)

            self.log([{'text': f"find planet with more scavengers"}])
            galaxy_planets_icon = os.path.join(os.path.pardir, galaxy_planets_dir)
            click_when_ready(galaxy_planets_icon, click=False, move=True)

            cords_checked = list()
            while True:
                self.log([{'text': f"checking planet coordinates"}])
                planets_cords = object_counter(galaxy_planets_icon, threshold=0.90, get_objects=True)
                self.log([{'text': f"found total {len(planets_cords)} planet matches"}])
                self.log([{'text': f"filtering coordinates"}])
                planets_cords = [pc for pc in planets_cords
                                 if pc not in cords_checked and pc[1] < self.lower
                                 and pc[1] > self.upper and pc[0] > self.left and pc[0] < self.right
                                 ]
                self.log([{'text': f"remaining number of planet coordinates {len(planets_cords)}"}])

                if len(planets_cords) == 0:
                    self.log([{'text': f"could not find any more planets"}])
                    break

                planet_cnt = len(planets_cords)
                planet_cord = planets_cords[randint(0, planet_cnt-1)]
                self.log([{'text': f"planet cords {planets_cords}"}])
                planet_x, planet_y = planet_cord

                self.log([{'text': f"clicking in coordinates {planet_cord}"}])

                # proximity check
                proximity_check = [cc for cc in cords_checked if abs(cc[0]-planet_x) < 10 or abs(cc[1]-planet_y) < 10]
                if len(proximity_check) > 0:
                    self.log([{'text': f"planet coordinates to close to previous one {len(proximity_check)}"}])
                    cords_checked.append(planet_cord)
                    continue

                pyautogui.click(planet_cord, duration=0.5)
                sleep(1)

                # take data
                self.log([{'text': f"process_system_data"}])
                system_data = process_system_data()
                self.log([{'text': f"system_data: {system_data}"}])

                if system_data.get('scavengers', 0) >= self.min_scavengers_for_attack and system_data.get('ally', -1) <= 1 and system_data.get('ally_flag') > 0:
                    self.log([{'text': f"entering system..."}])
                    system_enter_path = os.path.join(os.path.pardir, system_enter_icon)
                    click_when_ready(system_enter_path)

                    self.log([{'text': f"wait for galaxy icon to appear"}])
                    galaxy_icons = os.path.join(os.path.pardir, galaxy_icon_dir)
                    click_when_ready(galaxy_icons, click=False)
                    sleep(5)

                    self.jump_to_system()

                    self.system_elite_search()

                    self.workship_docking_sequence()

                    self.docking_sequence()
                    break

                else:
                    # click again to close planet details
                    pyautogui.keyDown('ESC')
                    sleep(0.5)
                    pyautogui.keyUp('ESC')
                    sleep(5)
                    cords_checked.append(planet_cord)
            cnt += 1

    def jump_to_system(self):
        self.log([{'text': f"set to 2D if not set"}])
        # set to 2D if not set
        self.set_2d_view()
        sleep(5)

        self.log([{'text': f"click on th middle of system"}])
        screen_w, screen_h = pyautogui.size()
        width = (screen_w / 2)
        height = (screen_h / 2)
        pyautogui.click(width, height+150)

        self.log([{'text': f"jump to the middle of system map"}])
        # find jump icon
        jump_button_path = os.path.join(os.path.pardir, fleet_jump_path)
        status = click_when_ready(jump_button_path, timeout=60)
        if type(status) is str:
            self.log([{'text': f"{status}. checking possible scenarios"}])
            # todo scenarios when on click location is something
            # scenario click on scavenger attack
            # scenario click in wreck and collect
            return

        # press ok jump button
        self.log([{'text': f"confirming jump to another system"}])
        jump_ok_button = os.path.join(os.path.pardir, fleet_jump_ok_path)
        status = click_when_ready(jump_ok_button, timeout=60)
        if type(status) is str:
            self.log([{'text': f"jump confirmation failed"}])
            self.log([{'text': f"{status}. checking possible scenarios"}])
            # todo scenarios when on click location is something
            # clicked on different element
            # color behind ok button is to different

        # press ok jump button
        self.log([{'text': f"confirming jump energy usage to another system"}])
        fleet_jump_energy = os.path.join(os.path.pardir, fleet_jump_energy_path)
        status = click_when_ready(fleet_jump_energy, timeout=60)
        if type(status) is str:
            self.log([{'text': f"energy jump confirmation failed"}])
            self.log([{'text': f"{status}. checking possible scenarios"}])
            # todo scenarios when on click location is something
            # possible scenario not enough energy

    def system_elite_search(self):
        # reset map position
        self.reset_system_map_position()

        while True:
            elite_found = False
            for ds in self.drag_seq:
                direction, repeat = ds
                if direction == 'C':
                    self.reset_system_map_position()
                    continue

                for i in range(repeat):
                    # searching for elites
                    self.log([{'text': f"searching for elites"}])
                    system_elites_path = os.path.join(os.path.pardir, system_elites_icon)
                    elites = object_counter(system_elites_path, threshold=0.90, get_objects=True)
                    elite_flag = False

                    for elite in elites:
                        x, y = elite
                        # if elite is whith in clickable area
                        if x > self.left and x < self.right and y > self.upper and y < self.lower:
                            self.log([{'text': f"elites_cnt {elite}"}])
                            elite_found = True

                            # click on elite
                            self.log([{'text': f"select target"}])
                            pyautogui.click(x+3, y+5)

                            # start attack sequence
                            self.log([{'text': f"starting attack"}])
                            self.attack_sequence()

                            # track fight
                            self.log([{'text': f"starting tracking attack"}])
                            sequence_success = self.attack_tracking_sequence()
                            self.log([{'text': f"sequence_success {sequence_success}"}])

                            if sequence_success:
                                # exit quick navigation
                                sleep(3)
                                self.log([{'text': "press escape until exits quick bar"}])
                                closed_flag = False
                                for i in range(5):
                                    fleet_tab_cnt = object_counter(os.path.join(os.path.pardir, quick_actions_fleet_tab_icon))
                                    if fleet_tab_cnt > 0:
                                        pyautogui.press('esc', interval=1)
                                        sleep(2)
                                    else:
                                        closed_flag = True
                                        break
                                # todo if closed flag is False handler
                            break

                    # if elites are empty drag to left, right, top and bottom
                    if elite_flag is False:
                        self.log([{'text': f"no elites found. direction: {direction}"}])
                        drag_length = 1000
                        if direction in ['L', 'R']:
                            drag_length = 1240
                        self.drag_to(direction, drag_length)
                        continue
                    else:
                        self.wreck_collecting()
                        break

            self.log([{'text': f"starting fleet docking sequence"}])
            self.docking_sequence()

            self.log([{'text': f"starting wreck_collecting class method"}])
            self.wreck_collecting()

            if elite_found is False:
                self.log([{'text': f"no elites found. This system is now empty"}])
                break

            if elite_found is True:
                # set back to center
                self.reset_system_map_position()

    def attack_sequence(self):
        sequence_success = True
        sequences = {os.path.join(os.path.pardir, fleet_attack_path): True,
                     os.path.join(os.path.pardir, fleet_quick_repair_path): False,
                     os.path.join(os.path.pardir,admiral_select_all_path): True,
                     os.path.join(os.path.pardir,admiral_send_ok_path): True}
        for sequence, blocker in sequences.items():
            if sequence == os.path.join(os.path.pardir, fleet_quick_repair_path):
                sleep(3)
            timeout = 2
            if blocker is False:
                timeout = 1
            result = click_when_ready(sequence, timeout=timeout)
            if type(result) is str and blocker is True:
                self.log([{'text': f"attack_sequence: could not finish attack reason > {result}"}])
                sequence_success = False
                break

        return sequence_success

    def attack_tracking_sequence(self):
        sequence_success = True

        sequences = {os.path.join(os.path.pardir, quick_actions_button_icon): True,
                     os.path.join(os.path.pardir, quick_actions_fleet_tab_icon): True}
        for sequence, blocker in sequences.items():
            timeout = 5
            if blocker is False:
                timeout = 1

            offset = (0, 0)
            if sequence == os.path.join(os.path.pardir, quick_actions_button_icon):
                offset = (8, 10)
            result = click_when_ready(sequence, offset=offset, timeout=timeout)
            if type(result) is str and blocker is True:
                self.log([{'text': f"attack_tracking_sequence: could not finish attack reason > {result}"}])
                return False

        # wait until fleet available again
        curent_combat = 0
        while True:
            fleet1 = self.fleet_status()
            if fleet1.incombat > 0:
                self.combat_length += 1
                curent_combat += 1
            self.log([{'text': f"time elapsed(this combat) {curent_combat}", 'inplace': True}])
            if (fleet1.idle > 0 or fleet1.docked > 0) and fleet1.incombat == 0 and fleet1.speeding == 0:
                self.log([{'text': f"fleet fight is over", 'breakpoint': True}])
                return sequence_success
            sleep(1)

    def fleet_status(self):
        fleet_stats = FleetStatus()
        fleet_stats.idle = object_counter(os.path.join(os.path.pardir,quick_action_fleet_idle))
        fleet_stats.docked = object_counter(os.path.join(os.path.pardir,quick_action_fleet_docked))
        fleet_stats.incombat = object_counter(os.path.join(os.path.pardir,quick_action_fleet_incombat))
        fleet_stats.speeding = object_counter(os.path.join(os.path.pardir,quick_action_fleet_speeding))
        return fleet_stats

    def docking_sequence(self):
        sequence_success = True

        sequences = {os.path.join(os.path.pardir, quick_actions_button_icon): True,
                     os.path.join(os.path.pardir, quick_actions_fleet_tab_icon): True,
                     os.path.join(os.path.pardir, fleet_recall_idle_path): True}
        for sequence, blocker in sequences.items():
            timeout = 5
            if blocker is False:
                timeout = 1

            offset = (0, 0)
            if sequence == os.path.join(os.path.pardir, quick_actions_button_icon):
                offset = (8, 10)
            result = click_when_ready(sequence, offset=offset, timeout=timeout)
            if type(result) is str and blocker is True:
                self.log([{'text': f"docking_sequence: could not finish docking sequence > {result}"}])
                return False

        # wait until fleet available again
        speeding = 0
        while True:
            fleet1 = self.fleet_status()
            if fleet1.speeding > 0:
                speeding += 1
            self.log([{'text': f"time elapsed(speeding) {speeding}", 'inplace': True}])
            if fleet1.docked > 0 and fleet1.incombat == 0 and fleet1.speeding == 0:
                self.log([{'text': f"fleet is docked", 'breakpoint': True}])

                # close fleet
                pyautogui.keyDown('ESC')
                sleep(0.5)
                pyautogui.keyUp('ESC')
                sleep(5)

                return sequence_success
            sleep(1)

    def workship_docking_sequence(self):
        sequences = {os.path.join(os.path.pardir, quick_actions_button_icon): True,
                     os.path.join(os.path.pardir, quick_actions_fleet_tab_icon): True,
                     os.path.join(os.path.pardir, workships_docked_path): True}

        for sequence, blocker in sequences.items():
            if sequence == os.path.join(os.path.pardir, workships_docked_path):
                timeout = 600
            else:
                timeout = 5
            if blocker is False:
                timeout = 1

            offset = (0, 0)
            if sequence == os.path.join(os.path.pardir, quick_actions_button_icon):
                offset = (8, 10)
            result = click_when_ready(sequence, offset=offset, timeout=timeout)
            if type(result) is str and blocker is True:
                self.log([{'text': f"attack_sequence: could not finish attack reason > {result}"}])
                return False

    def unpredicted_opens(self):
        # check unwanted icon and esc if exists
        fleet_recall_icon = os.path.join(os.path.pardir, fleet_recall_path)
        fleet_move_icon = os.path.join(os.path.pardir, fleet_move_path)
        fleet_jump_icon = os.path.join(os.path.pardir, fleet_jump_path)
        quick_actions_fleet_tab = os.path.join(os.path.pardir, quick_actions_fleet_tab_icon)

        icon_checks = [fleet_recall_icon, fleet_move_icon, fleet_jump_icon, quick_actions_fleet_tab]
        for i in range(5):
            check = 0
            for icon_check in icon_checks:
                recall_icon_check = object_counter(icon_check)
                if recall_icon_check > 0:
                    check += 1
                    pyautogui.keyDown('ESC')
                    sleep(0.5)
                    pyautogui.keyUp('ESC')
                    sleep(1)
            if check == 0:
                break

    def reset_system_map_position(self):
        self.unpredicted_opens()

        # set back to center
        self.set_3d_view()
        sleep(10)
        self.set_2d_view()
        # wait for 3d view icon to appear
        self.set_3d_view(wait=True)
        sleep(10)

    def wreck_collecting(self):
        # set back to center
        self.reset_system_map_position()

        # while True:
        for i in range(1):
            wreck_found = False
            wreck_cords = []
            wreck_distance = 15

            for ds in self.drag_seq:
                direction, repeat = ds
                if direction == 'C':
                    self.reset_system_map_position()
                    continue

                for i in range(repeat):
                    # searching for wrecks
                    system_wrecks_path = os.path.join(os.path.pardir, system_wreck_icon)
                    wrecks = object_counter(system_wrecks_path, threshold=0.88, get_objects=True)
                    wreck_flag = False

                    self.log([{'text': f"wrecks element found {len(wrecks)}"}])
                    for wreck in wrecks:
                        x, y = wreck
                        # if wreck is inside clickable area
                        if x > self.left and x < self.right and y > self.upper and y < self.lower:

                            same_cord = [cord for cord in wreck_cords if abs(cord[0]-x) <= wreck_distance or abs(cord[0]-y) <= wreck_distance]
                            if same_cord:
                                self.log([{'text': f"wreck cord close to the previous one"}])
                                continue

                            wreck_cords.append([x, y])
                            self.log([{'text': f"wreck cord {wreck}"}])
                            wreck_found = True
                            wreck_flag = True

                            # click on elite
                            self.log([{'text': f"select target"}])
                            pyautogui.click(x+3, y+5)

                            # collect wreck
                            self.log([{'text': f"press collect"}])
                            click_when_ready(os.path.join(os.path.pardir, fleet_collect_path), timeout=5)

                            # check no workship available
                            self.log([{'text': f"checking work ship availability"}])
                            sleep(3)
                            no_workships = object_counter(os.path.join(os.path.pardir, no_workships_path), threshold=0.90, get_objects=True)
                            if len(no_workships) > 0:
                                self.log([{'text': f"press ok on no workship"}])
                                click_when_ready(os.path.join(os.path.pardir, ok_button_dir))

                                wait_time = 60
                                for i in range(wait_time):
                                    self.log([{'text': f"wait time elapsed(workship CD) {i}/{wait_time}s", 'inplace': True}])
                                    sleep(1)
                            break

                    # if wrecks are empty drag to left, right, top and bottom
                    if wreck_flag is False:
                        self.log([{'text': f"no wrecks found. direction: {direction}"}])
                        drag_length = 1000
                        if direction in ['L', 'R']:
                            drag_length = 1240
                        self.drag_to(direction, drag_length)
                        continue
                    else:
                        break

            if wreck_found is False:
                self.log([{'text': f"no wrecks found. This system is wreck clean"}])
                break

            if wreck_found is True:
                # set back to center
                self.reset_system_map_position()

    def log(self, message):
        message_enc = json.dumps(message).encode()
        rabbitmq.client(config.rabbit_q, config.rabbit_u, config.rabbit_p, message_enc)


if __name__ == '__main__':
    api = NovaSpaceArmada()
    execute_method(api.switch_window, api, raise_flag=True, timeout=15, wait=3)
    # api.reset_system_map_position()
    # api.goto_star_system()
    # api.set_2d_view()
    # api.galaxy_scan()
    api.reset_system_map_position()
    api.system_elite_search()
    api.wreck_collecting()
