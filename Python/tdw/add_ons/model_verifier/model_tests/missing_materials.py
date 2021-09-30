from collections import Counter
from typing import List
from io import BytesIO
from PIL import Image
from tdw.add_ons.model_verifier.model_tests.rotate_object_test import RotateObjectTest
from tdw.output_data import Images


class MissingMaterials(RotateObjectTest):
    """
    Check if any materials are missing.
    """

    """:class_var
    The Unity pink color.
    """
    PINK = (255, 0, 255)

    def start(self) -> List[dict]:
        commands = super().start()
        commands.insert(0, {"$type": "set_pass_masks",
                            "pass_masks": ["_img"]})
        return commands

    def _read_images(self, images: Images) -> None:
        image = Image.open(BytesIO(images.get_image(0)))
        # Source: https://stackoverflow.com/a/59709420
        colors = Counter(image.getdata())
        unique_colors = set(colors)
        if MissingMaterials.PINK in unique_colors:
            self.reports.append("Missing materials")
            self.done = True

    def on_send(self, resp: List[bytes]) -> List[dict]:
        commands = super().on_send(resp=resp)
        if self.done:
            commands.extend(RotateObjectTest._get_end_commands())
        return commands
