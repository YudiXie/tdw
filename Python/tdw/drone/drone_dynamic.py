from io import BytesIO
from typing import List, Dict, Optional, Union
import numpy as np
from pathlib import Path
from tdw.tdw_utils import TDWUtils
from PIL import Image
from tdw.output_data import OutputData, Images, CameraMatrices
from tdw.object_data.transform import Transform



class ReplicantDynamic:
    """
    Dynamic data for a drone that can change per `communicate()` call (such as the position of the drone).
    """

    def __init__(self, resp: List[bytes], drone_id: int, frame_count: int):
        """
        :param resp: The response from the build, which we assume contains `drone` output data.
        :param drone_id: The ID of this drone.
        :param frame_count: The current frame count.
        """

        """:field
        The [`Transform`](../object_data/transform.md) of the drone.
        """
        self.transform: Transform = Transform(np.zeros(shape=3), np.zeros(shape=4), np.zeros(shape=3))
        """:field
        The images rendered by the drone as dictionary. Key = the name of the pass. Value = the pass as a numpy array.
        """
        self.images: Dict[str, np.array] = dict()
        """:field
        The [camera projection matrix](../../api/output_data.md#cameramatrices) of the drone's camera as a numpy array.
        """
        self.projection_matrix: Optional[np.array] = None
        """:field
        The [camera matrix](../../api/output_data.md#cameramatrices) of the drone's camera as a numpy array.
        """
        self.camera_matrix: Optional[np.array] = None
        # File extensions per pass.
        self.__image_extensions: Dict[str, str] = dict()
        """:field
        If True, we got images from the output data.
        """
        self.got_images: bool = False

        self._frame_count: int = frame_count
        self._drone_id: int = _drone_id
        avatar_id = str(_drone_id)
        got_data = False
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get drone's transform data.
            if r_id == "tran":
                transforms = Transforms(resp[i])
                for j in range(transforms.get_num()):
                    if transforms.get_id(j) == drone_id:
                            self.transform = transforms(j)
            # Get the images captured by the avatar's camera.
            elif r_id == "imag":
                images = Images(resp[i])
                # Get this drones's avatar and save the images.
                if images.get_avatar_id() == avatar_id:
                    self.got_images = True
                    for j in range(images.get_num_passes()):
                        image_data = images.get_image(j)
                        pass_mask = images.get_pass_mask(j)
                        if pass_mask == "_depth":
                            image_data = TDWUtils.get_shaped_depth_pass(images=images, index=j)
                        # Remove the underscore from the pass mask such as: _img -> img
                        pass_name = pass_mask[1:]
                        # Save the image data.
                        self.images[pass_name] = image_data
                        # Record the file extension.
                        self.__image_extensions[pass_name] = images.get_extension(j)
            # Get the camera matrices for the avatar's camera.
            elif r_id == "cama":
                camera_matrices = CameraMatrices(resp[i])
                if camera_matrices.get_avatar_id() == avatar_id:
                    self.projection_matrix = camera_matrices.get_projection_matrix()
                    self.camera_matrix = camera_matrices.get_camera_matrix()

    def save_images(self, output_directory: Union[str, Path]) -> None:
        """
        Save the ID pass (segmentation colors) and the depth pass to disk.
        Images will be named: `[frame_number]_[pass_name].[extension]`
        For example, the depth pass on the first frame will be named: `00000000_depth.png`

        The `img` pass is either a .jpg. The `id` and `depth` passes are .png files.

        :param output_directory: The directory that the images will be saved to.
        """

        if isinstance(output_directory, str):
            output_directory = Path(output_directory)
        if not output_directory.exists():
            output_directory.mkdir(parents=True)
        # The prefix is a zero-padded integer to ensure sequential images.
        prefix = TDWUtils.zero_padding(self._frame_count, 8)
        # Save each image.
        for pass_name in self.images:
            if self.images[pass_name] is None:
                continue
            # Get the filename, such as: `00000000_img.png`
            p = output_directory.joinpath(f"{prefix}_{pass_name}.{self.__image_extensions[pass_name]}")
            if pass_name == "depth":
                Image.fromarray(self.images[pass_name]).save(str(p.resolve()))
            else:
                with p.open("wb") as f:
                    f.write(self.images[pass_name])

    def get_pil_image(self, pass_mask: str = "img") -> Image.Image:
        """
        Convert raw image data to a PIL image.
        Use this function to read and analyze an image in memory.
        Do NOT use this function to save image data to disk; `save_image` is much faster.

        :param pass_mask: The pass mask. Options: `"img"`, `"id"`, `"depth"`.

        :return A PIL image.
        """

        if pass_mask == "depth":
            return Image.fromarray(self.images[pass_mask])
        else:
            return Image.open(BytesIO(self.images[pass_mask]))
