from typing import List, Dict, NamedTuple, Union
from tdw.add_ons.add_on import AddOn
from pathlib import Path
from tdw.output_data import OutputData, TransformMatrices, SegmentationColors, AvatarTransformMatrices
from requests import get
import os
import re
import zipfile
import subprocess
import numpy as np


class matrix_data_struct(NamedTuple):
    column_one: str
    column_two: str
    column_three: str
    column_four: str


class VRayExport(AddOn):

    def __init__(self, image_width: int, image_height: int, scene_name: str, output_path: str):
        super().__init__()
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)
        self.S3_ROOT = "https://tdw-public.s3.amazonaws.com/"
        self.VRAY_EXPORT_RESOURCES_PATH = Path.home().joinpath("vray_export_resources")
        if not self.VRAY_EXPORT_RESOURCES_PATH.exists():
            self.VRAY_EXPORT_RESOURCES_PATH.mkdir(parents=True)
        self.image_width: int = image_width
        self.image_height: int = image_height
        self.scene_name = scene_name
        # Conversion matrix from left-hand to right-hand.
        self.handedness = np.array([[1, 0, 0, 0],
                                    [0, 0, 1, 0],
                                    [0, 1, 0, 0],
                                    [0, 0, 0, 1]])
        # Conversion matrix for camera.
        self.camera_handedness = np.array([[1, 0, 0, 0],
                                           [0, 0, 1, 0],
                                           [0, -1, 0, 0],
                                           [0, 0, 0, 1]])
        # Dictionary of model names by ID
        self.object_names: Dict[int, str] = dict()
        # Dictionary of node IDs by model name
        self.node_ids: Dict[str, str] = dict()


    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "send_transform_matrices",
                       "frequency": "always"},
                    {"$type": "send_segmentation_colors",
                       "frequency": "once"},
                    {"$type": "send_camera_matrices",
                       "frequency": "always"},
                    {"$type": "send_avatar_transform_matrices",
                      "frequency": "always"}]
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get segmentation color output data.
            if r_id == "segm":
                segm = SegmentationColors(resp[i])
                for j in range(segm.get_num()):
                    # Cache the object names and IDs.
                    object_id = segm.get_object_id(j)
                    object_name = segm.get_object_name(j)
                    self.object_names[object_id] = object_name

    def download_model(self, model_name: str):
        """
        Download the zip file of a model from Amazon S3, and unpack the contents into the general "resources" folder.
        :param model_name: The name of the model.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name.lower())
        # Check if we have already downloaded this model. If so, just cache the node ID string for later use.
        # Otherwise download, unzip and cache the node ID string.
        if os.path.exists(path + ".vrscene"):
            node_id = self.fetch_node_id_string(model_name)
            self.node_ids[model_name] = node_id
        else:
            path = path + ".zip"
            url = os.path.join(self.S3_ROOT + "vray_models/", model_name.lower()) + ".zip"
            with open(path, "wb") as f:
                f.write(get(url).content)
            # Unzip in place.
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(self.VRAY_EXPORT_RESOURCES_PATH)
            # Delete the zip file.
            os.remove(path)
            # Cache the node ID string.
            node_id = self.fetch_node_id_string(model_name)
            self.node_ids[model_name] = node_id

    def download_scene_models(self):
        """
        Download all models in the scene.
        """
        for model_name in self.object_names.values():
            self.download_model(model_name)

            print(model_name + ", " + node_id)

    def download_scene(self):
        """
        Download the zip file of a streamed scene from Amazon S3, and unpack the contents into the general "resources" folder.
        :param model_name: The name of the scene.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".zip"
        url = os.path.join(self.S3_ROOT + "vray_scenes/", self.scene_name) + ".zip"
        with open(path, "wb") as f:
            f.write(get(url).content)
        # Unzip in place.
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(self.VRAY_EXPORT_RESOURCES_PATH)
        # Delete the zip file.
        os.remove(path)

    def fetch_node_id_string(self, model_name: str) -> str:
        """
        For a given model (name), fetch the Node ID associated with that model.
        :param model_name: The name of the model.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name)  + ".vrscene"
        with open(path, "r") as filename:  
            # Look for Node structure and output node ID.
            src_str = model_name + "@node_"
            pattern = re.compile(src_str, re.IGNORECASE)
            for line in filename:
                if pattern.search(line):
                    return line


    def write_node_data(self, model_name: str, mat: matrix_data_struct):
        """
        Append the scene position and orientation of a model to its .vrscene file, as Node data.
        NOTE: This could be called once, for a static scene, or every frame if capturing physics motion.
        :param model_name: The name of the model.
        """
        # Fetch node ID from cached dictionary.
        node_id_string = self.node_ids[model_name]
        # Open model .vrscene file to append node data
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, model_name)  + ".vrscene"
        node_string = (node_id_string + 
                      "transform=Transform(Matrix" + 
                      "(Vector(" + mat.column_one + "), " +
                      "Vector(" + mat.column_two + "), " +
                      "Vector(" + mat.column_three + ")), " +
                      "Vector(" + mat.column_four + "));\n}")
        with open(path, "a") as f:  
            f.write(node_string)

    def get_renderview_line_number(self) -> int:
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name)  + ".vrscene"
        line_number = 0
        num = 0
        with open(path, "r", encoding="utf-8") as in_file:
            pattern = re.compile("RenderView")
            for line in in_file:
                if pattern.search(line):
                    # We will want to replace the line following the "RenderView" line, with the transform data
                    line_number = num + 1
                    return line_number
                else:
                    num = num + 1

    def write_renderview_data(self, mat: matrix_data_struct):
        """
        Replace the camera transform line in the scene file with the converted TDW camera pos/ori data.
        """
        # Open model .vrscene file to append node data
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name)  + ".vrscene"
        node_string = ("transform=Transform(Matrix" + 
                       "(Vector(" + mat.column_one + "), " +
                       "Vector(" + mat.column_two + "), " +
                       "Vector(" + mat.column_three + ")), " +
                       "Vector(" + mat.column_four + "));\n")
        line_number = self.get_renderview_line_number()
        with open(path, 'r', encoding="utf-8") as in_file:
            # Read a list of lines into data
            data = in_file.readlines()
            # Now change the Renderview line
            data[line_number] = node_string
        # Write everything back
        with open(path, 'w', encoding="utf-8") as out_file:
           out_file.writelines(data)

    def export_static_node_data(self, resp: List[bytes]):
        """
        For each model in the scene, export the position and orientation data to the model's .vrscene file as Node data.
        Then append an #include reference to the model file at the end of the main scene file.
        """
        path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".vrscene"
        with open(path, "a") as f: 
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "trma":
                    transform_matrices = TransformMatrices(resp[i])
                    # Iterate through the objects.
                    for j in range(transform_matrices.get_num()):
                        # Get the object ID.
                        object_id = transform_matrices.get_id(j)
                        # Get the matrix and convert it.
                        # Equivalent to: handedness * object_matrix * handedness.
                        matrix = np.matmul(self.handedness, np.matmul(transform_matrices.get_matrix(j), self.handedness))
                        # Note that V-Ray units are in centimeters while Unity's are in meters, so we need to multiply the position values by 100.
                        # We also need to negate the X and Y value, to complete the handedness conversion.
                        pos_x = -(matrix[3][0] * 100)
                        pos_y = -(matrix[3][1] * 100)
                        pos_z = matrix[3][2] * 100
                        mat_struct = matrix_data_struct(column_one = str(matrix[0][0]) + "," + str(matrix[0][1]) + "," + str(matrix[0][2]), 
                                                        column_two = str(matrix[1][0]) + "," + str(matrix[1][1]) + "," + str(matrix[1][2]), 
                                                        column_three = str(matrix[2][0]) + "," + str(matrix[2][1]) + "," + str(matrix[2][2]),  
                                                        column_four = str(pos_x) + "," + str(pos_y) + "," + str(pos_z))
                        # Get the model name for this ID
                        model_name = self.object_names[object_id]
                        self.write_node_data(model_name, mat_struct)
                        f.write("#include \"" + model_name + ".vrscene\"\n")

    def export_static_camera_view_data(self, resp: List[bytes]):
        """
        Export the position and orientation of the camera to the scene .vrscene file as Transform data.
        """	
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "atrm":
                avatar_transform_matrices = AvatarTransformMatrices(resp[i])
                for j in range(avatar_transform_matrices.get_num()):
                    avatar_id = avatar_transform_matrices.get_id(j)
                    avatar_matrix = avatar_transform_matrices.get_avatar_matrix(j)
                    sensor_matrix = avatar_transform_matrices.get_sensor_matrix(j)
                    # Get the matrix and convert it.
                    # Equivalent to: handedness * object_matrix * handedness.
                    pos_matrix = np.matmul(self.handedness, np.matmul(avatar_matrix, self.handedness))
                    #rot_matrix = np.matmul(self.camera_handedness, np.matmul(sensor_matrix, self.camera_handedness))
                    rot_matrix = np.matmul(sensor_matrix, self.camera_handedness)
                    # Note that V-Ray units are in centimeters while Unity's are in meters, so we need to multiply the position values by 100.
                    # We also need to negate the X and Y value, to complete the handedness conversion.
                    pos_x = -(pos_matrix[3][0] * 100)
                    pos_y = -(pos_matrix[3][1] * 100)
                    pos_z = pos_matrix[3][2] * 100
                    mat_struct = matrix_data_struct(column_one = str(rot_matrix[0][0]) + "," + str(rot_matrix[0][1]) + "," + str(rot_matrix[0][2]), 
                                                    column_two = str(rot_matrix[1][0]) + "," + str(rot_matrix[1][1]) + "," + str(rot_matrix[1][2]), 
                                                    column_three = str(rot_matrix[2][0]) + "," + str(rot_matrix[2][1]) + "," + str(rot_matrix[2][2]),  
                                                    column_four = str(pos_x) + "," + str(pos_y) + "," + str(pos_z))
        self.write_renderview_data(mat_struct)

    def assemble_render_file(self):
        """
        If Node and/or Lights dynamic data was exported, append to the end of the master scene file.
        """
        scene_path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".vrscene"
        with open(scene_path, "a") as f:  
            #f.write("#include models.vrscene\n")
            #f.write("#include views.vrscene\n")
            # Append nodes and lights files also, if either one exists
            if os.path.exists("nodes.vrscene"):
                f.write("#include nodes.vrscene\n")
            if os.path.exists("lights.vrscene"):
                f.write("#include lights.vrscene\n")

    def launch_vantage_render(self):
        """
        Launch Vantage in headless mode and render scene file.
        """
        scene_path = os.path.join(self.VRAY_EXPORT_RESOURCES_PATH, self.scene_name) + ".vrscene"
        output_path = str(self.output_path) + self.scene_name + ".png"
        os.chmod("C://Program Files//Chaos Group//Vantage//vantage_console.exe", 0o777)
        subprocess.run(["C:/Program Files/Chaos Group/Vantage/vantage.exe", 
                        "-sceneFile=" + scene_path, 
                        "-outputFile=" + output_path,  
                        "-outputWidth=" + str(self.image_width), 
                        "-outputHeight=" + str(self.image_height),
                        "-quiet",
                        "-autoClose=true"])

	