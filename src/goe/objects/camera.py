from typing import final, override

from pygae.core import GameObject
from pygae.input import IInputService
from pygae.math import Vec2, Vec2Like
from pygame import Rect

from goe.core import Actions, make_cam_pos_event, make_cam_zoom_event
from goe.helpers import normalize_value
from goe.setting import CAM_SCALE_MIN, CAM_SCALE_MAX, CAM_MOVE_SPEED, CAM_SCALE_SPEED, SCREEN_SIZE


SCALE_DEFAULT = 30


@final
class Camera(GameObject):

    def __init__(self) -> None:
        super().__init__()
        self._input_srv: IInputService | None = None
        self._scale = SCALE_DEFAULT
        self._center = Vec2.as_vec2(SCREEN_SIZE) / 2
        self._pos = Vec2.zero()
        self._prev = Vec2.zero()
        self._bbox = Rect(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1])
        self._bbox.center = self._pos.snap()

    def _set_pos(self, v: Vec2):
        self._pos = v
        self._publish_location()

    def _set_scale(self, s: float):
        self._scale = max(min(s, CAM_SCALE_MAX), CAM_SCALE_MIN)
        self._publish_zoom()

    def _publish_location(self, force: bool = False):
        if self._prev != self._pos or force:
            event = make_cam_pos_event(self._pos)
            self.publish(event)

    def _publish_zoom(self):
        zoom = self.get_zoom()
        event = make_cam_zoom_event(zoom)
        self.publish(event)

    def get_bbox(self) -> Rect:
        width = SCREEN_SIZE[0] / self._scale
        height = SCREEN_SIZE[1] / self._scale
        x = self._pos.x - (width / 2)
        y = self._pos.y - (height / 2)
        return Rect(x, y, width, height)

    def world_to_screen(self, world: Vec2Like, alpha: float) -> Vec2:
        cam = self._prev.lerp(self._pos, alpha)
        return ((world - cam) * self._scale + self._center)

    def get_pixel_scale(self) -> float:
        return self._scale

    def get_zoom(self) -> float:
        return normalize_value(self._scale, CAM_SCALE_MIN, CAM_SCALE_MAX)

    @override
    def on_load(self) -> None:
        self._input_srv = self.get_service(IInputService)
        self._publish_location(True)
        self._publish_zoom()

    @override
    def pre_fixed_update(self, delta: float):
        if self._input_srv is None: return
        self._prev = self._pos
        direction = Vec2.zero()
        self._scale += self._input_srv.get_value(Actions.ZOOM) * CAM_SCALE_SPEED * delta
        self._scale = max(min(self._scale, CAM_SCALE_MAX), CAM_SCALE_MIN)
        if self.input_held(Actions.PAN_UP):
            direction += (0, -1)
        if self.input_held(Actions.PAN_DOWN):
            direction += (0, 1)
        if self.input_held(Actions.PAN_LEFT):
            direction += (-1, 0)
        if self.input_held(Actions.PAN_RIGHT):
            direction += (1, 0)
        if self.input_held(Actions.ZOOM_IN):
            self._set_scale(self._scale + (CAM_SCALE_SPEED * delta))
        if self.input_held(Actions.ZOOM_OUT):
            self._set_scale(self._scale - (CAM_SCALE_SPEED * delta))
        if self.input_pressed(Actions.PAN_HOME):
            self._set_scale(SCALE_DEFAULT)
            self._set_pos(Vec2.zero())
        if direction.xy != (0, 0):
            w = (CAM_MOVE_SPEED * delta) / self._scale
            self._set_pos(self._pos + direction.normalized() * w)
