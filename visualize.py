#!/usr/bin/env python3
#
# Traffic Simulation Visualizer
# Copyright (C) 2022 jonatcln
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from typing import NamedTuple, Tuple
import sys
import ast
import argparse
import contextlib
with contextlib.redirect_stdout(None):  # Hides pygame welcome message
    import pygame


# Configuration constants
INITIAL_WINDOW_WIDTH = 800
INITIAL_WINDOW_HEIGHT = 200


def main():
    cli = argparse.ArgumentParser(
        prog='visualize.py',
        description='Traffic Simulation Visualizer',
    )

    def speed(s: str):
        """Parse a valid speed int from a string."""
        speed = int(s)
        if speed < 1: raise argparse.ArgumentTypeError("speed must be >= 1")
        return speed

    cli.add_argument(
        '-s', '--speed', type=speed, default=4,
        help='set the playback rate to the given factor (>= 1)',
    )

    cli.add_argument(
        '--dark', action='store_true',
        help='use dark mode',
    )

    args = cli.parse_args()

    visualizer = Visualizer(INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT)
    visualizer.set_playback_rate(args.speed)

    if args.dark:
        # You can adjust these colors to get a custom theme
        visualizer.set_colors(Visualizer.Colors(
            background = Color(0, 0, 0),
            text = Color(255, 255, 255),
            road = Color(55, 55, 55),
            car = Color(215, 215, 215),
            generator = Color(140, 0, 140),
            deceleration_range = Color(55, 75, 113),
            stopping_range_full = Color(119, 25, 25),
            stopping_range_half = Color(113, 73, 0),
        ))

    for line in sys.stdin.readlines():
        visualizer.push_simulation_frame_data(line)

    visualizer.main_loop()


class Color:
    def __init__(self, red: int, green: int, blue: int):
        assert 0 <= red <= 255
        assert 0 <= green <= 255
        assert 0 <= blue <= 255
        self._red = red
        self._green = green
        self._blue = blue

    def as_tuple(self) -> Tuple[int, int, int]:
        return self._red, self._green, self._blue

    def get_red(self) -> int:
        return self._red

    def set_red(self, red: int):
        assert 0 <= red <= 255
        self._red = red

    def get_green(self) -> int:
        return self._green

    def set_green(self, green: int):
        assert 0 <= green <= 255
        self._green = green

    def get_blue(self) -> int:
        return self._blue

    def set_blue(self, blue: int):
        assert 0 <= blue <= 255
        self._blue = blue


class Visualizer:
    class Colors(NamedTuple):
        background: Color = Color(255, 255, 255)
        text: Color = Color(0, 0, 0)
        road: Color = Color(200, 200, 200)
        car: Color = Color(40, 40, 40)
        traffic_light_green: Color = Color(0, 255, 0)
        traffic_light_red: Color = Color(255, 0, 0)
        generator: Color = Color(255, 100, 255)
        deceleration_range: Color = Color(155, 175, 213)
        stopping_range_full: Color = Color(219, 125, 125)
        stopping_range_half: Color = Color(213, 173, 99)

    _FPS: int = 60
    _DEFAULT_PLAYBACK_RATE: int = 1
    _DEFAULT_WINDOW_TITLE: str = 'Traffic Simulation Visualizer'
    _DEFAULT_CANVAS_MARGIN: int = 16
    _DEFAULT_ROAD_HEIGHT: int = 20
    _DEFAULT_CAR_HEIGHT: int = 10
    _DEFAULT_CAR_WIDTH: int = 4
    _DEFAULT_LIGHT_OFFSET: int = 4
    _DEFAULT_LIGHT_RADIUS: int = 5
    _DEFAULT_LIGHT_STOP_LINE_THICKNESS: int = 1
    _DEFAULT_ROAD_NAME_OFFSET: int = 3
    _DEFAULT_PAUSE_ICON_WIDTH: int = 15
    _DEFAULT_PAUSE_ICON_HEIGHT: int = 20
    _DEFAULT_FONT_FAMILY: str = 'DejaVu Sans'
    _DEFAULT_FONT_SIZE: int = 16

    def __init__(self, initial_window_width: int, initial_window_height: int):
        self._fps: int = Visualizer._FPS
        self._window_width: int = initial_window_width
        self._window_height: int = initial_window_height
        self._window_title: int = Visualizer._DEFAULT_WINDOW_TITLE
        self._canvas_margin: int = Visualizer._DEFAULT_CANVAS_MARGIN
        self._road_height: int = Visualizer._DEFAULT_ROAD_HEIGHT
        self._car_height: int = Visualizer._DEFAULT_CAR_HEIGHT
        self._car_width: int = Visualizer._DEFAULT_CAR_WIDTH
        self._light_offset: int = Visualizer._DEFAULT_LIGHT_OFFSET
        self._light_radius: int = Visualizer._DEFAULT_LIGHT_RADIUS
        self._light_stop_line_thickness: int = \
            Visualizer._DEFAULT_LIGHT_STOP_LINE_THICKNESS
        self._road_name_offset: int = Visualizer._DEFAULT_ROAD_NAME_OFFSET
        self._colors: Visualizer.Colors = Visualizer.Colors()
        self._font_family: str = Visualizer._DEFAULT_FONT_FAMILY
        self._font_size: int = Visualizer._DEFAULT_FONT_SIZE
        self._pause_icon_width: int = Visualizer._DEFAULT_PAUSE_ICON_WIDTH
        self._pause_icon_height: int = Visualizer._DEFAULT_PAUSE_ICON_HEIGHT
        self._playback_rate: int = Visualizer._DEFAULT_PLAYBACK_RATE
        self._timeline = []
        self._time_idx: int = 0
        self._paused: bool = False

    def push_simulation_frame_data(self, data: str):
        parsed_data = ast.literal_eval(data)
        self._timeline.append(parsed_data)

    def set_playback_rate(self, rate: int):
        assert rate >= 1
        self._playback_rate = rate

    def set_colors(self, colors: 'Visualizer.Colors'):
        self._colors = colors

    def main_loop(self):
        self._time_idx = 0

        pygame.init()
        fps_clock = pygame.time.Clock()
        window = pygame.display.set_mode(
            (self._window_width, self._window_height), pygame.RESIZABLE)
        pygame.display.set_caption(self._window_title)

        while True:
            for event in pygame.event.get() :
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.VIDEORESIZE:
                    self._window_width, self._window_height = event.size
                elif event.type == pygame.KEYDOWN:
                    self._handle_key_down(event.key)

            keys_pressed = pygame.key.get_pressed()
            if keys_pressed:
                self._handle_keys_pressed(keys_pressed)

            situation = self._timeline[self._time_idx]
            if not self._paused:
                self._frames_forward(self._playback_rate)

            self._render_situation(window, situation)

            pygame.display.update()

            fps_clock.tick(self._fps)

    def _handle_key_down(self, key):
        if key == pygame.K_SPACE:
            self._toggle_pause()
        if key == pygame.K_r:
            self._time_idx = 0

    def _handle_keys_pressed(self, keys_pressed):
        shift_pressed = keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]
        if keys_pressed[pygame.K_LEFT]:
            if self._paused:
                self._frames_back(self._playback_rate if shift_pressed else 1)
        if keys_pressed[pygame.K_RIGHT]:
            if self._paused:
                self._frames_forward(self._playback_rate if shift_pressed else 1)

    def _toggle_pause(self):
        self._paused = not self._paused

    def _frames_back(self, n):
        self._time_idx = max(0, self._time_idx - n)

    def _frames_forward(self, n):
        self._time_idx = self._time_idx + n
        if self._time_idx >= len(self._timeline):
            self._paused = True
            self._time_idx = len(self._timeline) - 1

    def _render_situation(self, window, situation):
        self._draw_background(window)
        self._draw_time(window, situation['time'])
        if self._paused:
            self._draw_pause_icon(window)

        roads = situation['roads']

        max_road_length = max(int(road['length']) for road in roads)
        horizontal_scale = self._get_canvas_width() / max_road_length

        for i, road in enumerate(roads):
            road_y_offset = (i+1) * self._get_canvas_height() / (len(roads)+1)
            road_y = self._get_canvas_origin_top() + int(road_y_offset)
            self._draw_full_road(window, road, road_y, horizontal_scale)

    def _draw_background(self, window):
        window.fill(self._colors.background.as_tuple())

    def _draw_pause_icon(self, window):
        width = self._pause_icon_width
        height = self._pause_icon_height
        origin_left = self._get_canvas_origin_left() \
            + self._get_canvas_width() - width
        origin_top = self._get_canvas_origin_top()
        pygame.draw.rect(
            window, self._colors.text.as_tuple(), pygame.Rect(
                origin_left, origin_top, width, height
            )
        )
        pygame.draw.rect(
            window, self._colors.background.as_tuple(), pygame.Rect(
                origin_left + width//3, origin_top, width - 2*width//3, height
            )
        )

    def _draw_full_road(
        self, window, road, road_y: int, horizontal_scale: float
    ):
        road_x = self._get_canvas_origin_left()
        road_width = int(int(road['length']) * horizontal_scale)
        self._draw_road_name(window, road['name'], road_x, road_y)
        self._draw_road(window, road_x, road_y, road_width)
        self._draw_traffic_lights(
            window, road['lights'], road_y, horizontal_scale)
        self._draw_cars(window, road['cars'], road_y, horizontal_scale)
        self._draw_generator(window, road_x, road_y, horizontal_scale)

    def _draw_cars(self, window, cars, road_y: int, horizontal_scale: float):
        for car in cars:
            car_width = max(1, int(self._get_car_width() * horizontal_scale))
            car_x_offset = int(car['x'] * horizontal_scale) - car_width
            car_x = self._get_canvas_origin_left() + int(car_x_offset)
            self._draw_car(
                window, car_x, road_y, car_width)

    def _draw_traffic_lights(
        self, window, lights, road_y: int, horizontal_scale: float
    ):
        for light in lights:
            light_x_offset = int(light['x']) * horizontal_scale
            light_x = self._get_canvas_origin_left() + int(light_x_offset)
            stop_line_thickness = max(1,
                int(self._get_light_stop_line_thickness()*horizontal_scale)
            )
            is_green = bool(light['green'])
            if 'xs' in light and 'xs0' in light and not is_green:
                deceleration_distance = int(light['xs']) * horizontal_scale
                stopping_distance = int(light['xs0']) * horizontal_scale
                self._draw_indicators(
                    window, light_x, road_y,
                    int(deceleration_distance), int(stopping_distance)
                )
            self._draw_traffic_light(
                window, light_x, road_y, stop_line_thickness, is_green)

    def _draw_time(self, window, time: float):
        font = pygame.font.SysFont(self._font_family, self._get_font_size())
        text = font.render(f'Time: {time}', True, self._colors.text.as_tuple())
        window.blit(text, self._get_canvas_origin())

    def _draw_road_name(self, window, name: str, road_x: int, road_y: int):
        font = pygame.font.SysFont(
            self._font_family, int(.8*self._get_font_size()), italic=True)
        text = font.render(name, True, self._colors.text.as_tuple())
        origin_y = \
            road_y + self._get_road_height()//2 + self._get_road_name_offset()
        window.blit(text, (road_x, origin_y))

    def _draw_generator(
        self, window, road_x: int, road_y: int, horizontal_scale: float
    ):
        width = max(1, int(self._get_car_width() * horizontal_scale))
        road_height = self._get_road_height()
        origin_x = road_x - width
        origin_y = road_y - road_height//2
        generator_shape = pygame.Rect(origin_x, origin_y, width, road_height)
        pygame.draw.rect(
            window, self._colors.generator.as_tuple(), generator_shape)

    def _draw_road(self, window, origin_x: int, center_y: int, width: int):
        road_height = self._get_road_height()
        origin_y = center_y - road_height//2
        road_shape = pygame.Rect(origin_x, origin_y, width, road_height)
        pygame.draw.rect(window, self._colors.road.as_tuple(), road_shape)

    def _draw_car(self, window, origin_x: int, center_y: int, width: int):
        car_height = self._get_car_height()
        origin_y = center_y - car_height//2
        car_shape = pygame.Rect(origin_x, origin_y, width, car_height)
        pygame.draw.rect(window, self._colors.car.as_tuple(), car_shape)

    def _draw_traffic_light(
        self, window, center_x: int, road_center_y: int,
        stop_line_thickness: int, is_green: bool
    ):
        color = (self._colors.traffic_light_green.as_tuple() if is_green
            else self._colors.traffic_light_red.as_tuple())
        road_height = self._get_road_height()
        light_offset = self._get_light_offset()
        line_top_y = road_center_y - road_height//2
        line_bottom_y = road_center_y + road_height//2 + light_offset
        pygame.draw.line(
            window, color, (center_x, line_top_y), (center_x, line_bottom_y),
            stop_line_thickness
        )
        radius = self._get_light_radius()
        center_y = road_center_y + road_height//2 + light_offset + radius
        pygame.draw.circle(window, color, (center_x, center_y), radius)

    def _draw_indicators(
        self, window, light_x: int, road_y: int, deceleration_distance: int,
        stopping_distance: int
    ):
        origin_y = road_y - self._get_road_height()//2
        pygame.draw.rect(
            window, self._colors.deceleration_range.as_tuple(),
            pygame.Rect(
                light_x - deceleration_distance, origin_y,
                deceleration_distance, self._get_road_height()
            )
        )
        pygame.draw.rect(
            window, self._colors.stopping_range_full.as_tuple(),
            pygame.Rect(
                light_x - stopping_distance, origin_y,
                stopping_distance, self._get_road_height()
            )
        )
        pygame.draw.rect(
            window, self._colors.stopping_range_half.as_tuple(),
            pygame.Rect(
                light_x - stopping_distance//2, origin_y,
                stopping_distance//2, self._get_road_height()
            )
        )

    def _get_canvas_origin(self) -> Tuple[int, int]:
        return (self._get_canvas_origin_left(), self._get_canvas_origin_top())

    def _get_canvas_origin_left(self) -> int:
        return self._get_canvas_margin()

    def _get_canvas_origin_top(self) -> int:
        return self._get_canvas_margin()

    def _get_canvas_size(self) -> int:
        return (self._get_canvas_width(), self._get_canvas_height())

    def _get_canvas_width(self) -> int:
        return self._window_width - 2*self._get_canvas_margin()

    def _get_canvas_height(self) -> int:
        return self._window_height - 2*self._get_canvas_margin()

    def _get_canvas_margin(self) -> int:
        return self._canvas_margin

    def _get_road_height(self) -> int:
        return self._road_height

    def _get_car_height(self) -> int:
        return self._car_height

    def _get_car_width(self) -> int:
        return self._car_width

    def _get_light_offset(self) -> int:
        return self._light_offset

    def _get_light_radius(self) -> int:
        return self._light_radius

    def _get_light_stop_line_thickness(self) -> int:
        return self._light_stop_line_thickness

    def _get_road_name_offset(self) -> int:
        return self._road_name_offset

    def _get_font_size(self) -> int:
        return self._font_size


if __name__ == '__main__':
    main()
