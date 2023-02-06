from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.vray_export import VRayExport



class Photoreal(Controller):
    """
    Create a photorealistic scene, focusing on post-processing and other effects.
    The "archviz_house" environment is used due to its maximal photorealistic lighting.
    """
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)

    def run(self):
        # Add a camera and enable image capture.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": -1, "y": 2.5, "z": -1},
                                   look_at={"x": 2, "y": 1, "z": 2},
                                   field_of_view=55)
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("photoreal")
        print(f"Image will be saved to: {path}")
        table_id = self.get_unique_id()
        statue_id = self.get_unique_id()
        lamp_id = self.get_unique_id()
        capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([camera, capture])
        export = VRayExport(image_width=1920, image_height=1080, scene_name="tdw_room", output_path="D:/VE2020_output/")
        self.add_ons.append(export)
        # Set the resolution to 1080p.
        # Set render quality to maximum.
        # Load the scene.
        # Add the objects.
        # Adjust post-processing parameters to achieve a suitable depth of field and exposure.
        # Also adjust the ambient occlusion parameters for realistic shadowing in corners and under furniture objects.
        # Set shadow strength to near-full.
        # Immediately end the simulation.
        commands =[{"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                          self.get_add_scene(scene_name="tdw_room"),
                         self.get_add_object(model_name="buddah",
                                              object_id=statue_id,
                                              position={"x": 2, "y": 0, "z": 2},
                                              rotation={"x": 0, "y": 0, "z": 0}),
                          {"$type": "set_aperture",
                           "aperture": 4.0},
                          {"$type": "set_focus_distance",
                           "focus_distance": 2.25},
                          {"$type": "set_post_exposure",
                           "post_exposure": 0.4},
                          {"$type": "set_ambient_occlusion_intensity",
                           "intensity": 0.175},
                          {"$type": "set_ambient_occlusion_thickness_modifier",
                           "thickness": 3.5},
                          {"$type": "set_shadow_strength",
                           "strength": 0.85}]
        self.communicate(commands)
        self.communicate([])
        #self.communicate({"$type": "terminate"})
        

if __name__ == "__main__":
    Photoreal(launch_build=False).run()
