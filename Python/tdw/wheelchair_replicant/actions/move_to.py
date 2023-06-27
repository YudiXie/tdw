from typing import Optional, List
import numpy as np
from tdw.type_aliases import TARGET
from tdw.tdw_utils import TDWUtils
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.actions.action import Action
from tdw.wheelchair_replicant.wheel_values import WheelValues, get_move_values
from tdw.wheelchair_replicant.actions.turn_to import TurnTo
from tdw.wheelchair_replicant.actions.move_by import MoveBy
from tdw.wheelchair_replicant.wheelchair_replicant_dynamic import WheelchairReplicantDynamic
from tdw.wheelchair_replicant.wheelchair_replicant_static import WheelchairReplicantStatic


class MoveTo(Action):
    def __init__(self, target: TARGET, turn_wheel_values: Optional[WheelValues],
                 move_wheel_values: Optional[WheelValues], dynamic: WheelchairReplicantDynamic,
                 collision_detection: CollisionDetection, previous: Optional[Action], reset_arms: bool,
                 reset_arms_duration: float, scale_reset_arms_duration: bool, aligned_at: float, arrived_at: float):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param turn_wheel_values: The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels while it's turning. If None, values will be derived from the angle.
        :param move_wheel_values: The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels while it's moving. If None, values will be derived from the distance.
        :param dynamic: The [`WheelchairReplicantDynamic`](../wheelchair_replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../../replicant/collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param aligned_at: If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """

        super().__init__()
        """:field
        If True, the wheelchair is turning. If False, the wheelchair is moving.
        """
        self.turning: bool = True
        """:field
        The current sub-action. This is first a `TurnTo`, then a `MoveBy`.
        """
        self.action = TurnTo(target=target, wheel_values=turn_wheel_values, dynamic=dynamic,
                             collision_detection=collision_detection, previous=previous, reset_arms=reset_arms,
                             reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=aligned_at)
        self._target: TARGET = target
        self._image_frequency: ImageFrequency = ImageFrequency.once
        self._collision_detection: CollisionDetection = collision_detection
        """:field
        If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """
        self.arrived_at: float = arrived_at
        self._move_wheel_values: Optional[WheelValues] = move_wheel_values

    def get_initialization_commands(self, resp: List[bytes],
                                    static: WheelchairReplicantStatic,
                                    dynamic: WheelchairReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        self._image_frequency = image_frequency
        return self.action.get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)

    def get_ongoing_commands(self, resp: List[bytes],
                             static: WheelchairReplicantStatic,
                             dynamic: WheelchairReplicantDynamic) -> List[dict]:
        commands = self.action.get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        # The sub-action is ongoing.
        if self.action.status == ActionStatus.ongoing:
            return commands
        # The sub-action ended.
        else:
            # The sub-action succeeded.
            if self.action.status == ActionStatus.success:
                # We're done turning. Start moving.
                if self.turning:
                    self.turning = False
                    # Get the distance.
                    if isinstance(self._target, int):
                        target: np.ndarray = self._get_object_position(object_id=self._target, resp=resp)
                    elif isinstance(self._target, dict):
                        target = TDWUtils.vector3_to_array(self._target)
                    elif isinstance(self._target, np.ndarray):
                        target = self._target
                    else:
                        raise Exception(f"Invalid MoveBy target: {self._target}")
                    distance = np.linalg.norm(dynamic.transform.position - target)
                    # Get the direction.
                    d0 = dynamic.transform.position + dynamic.transform.forward
                    d1 = dynamic.transform.position - dynamic.transform.forward
                    if np.linalg.norm(self._target - d1) < np.linalg.norm(self._target - d0):
                        distance *= -1
                    # Get wheel values.
                    if self._move_wheel_values is None:
                        self._move_wheel_values = get_move_values(distance)
                    self.action = MoveBy(distance=distance, wheel_values=self._move_wheel_values, dynamic=dynamic,
                                         collision_detection=self._collision_detection, previous=None,
                                         reset_arms=False, reset_arms_duration=0, scale_reset_arms_duration=False,
                                         arrived_at=self.arrived_at)
                    return self.action.get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                                   image_frequency=self._image_frequency)
                # We're done!
                else:
                    self.status = ActionStatus.success
            # The action failed.
            else:
                self.status = self.action.status
                return commands

    def get_end_commands(self, resp: List[bytes],
                         static: WheelchairReplicantStatic,
                         dynamic: WheelchairReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        return self.action.get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
