from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.vray_exporter import VRayExporter


class DynamicObjects(Controller):
    """
    Create a typical TDW scene. Apply a force to the chair, then export using V-Ray add-on for maximum photorealism.
    """

    def __init__(self, output_path: str, render_host: str = "localhost", port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.frame_range = 150
        self.chair_id = self.get_unique_id()
        self.table_id = self.get_unique_id()
        self.render_host = render_host
        self.output_path = output_path

    def run(self):
        # Add a camera and enable export.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": 2.5, "y": 1.0, "z": 2},
                                   look_at={"x": 0, "y": 0.5, "z": 0.5},
                                   field_of_view=55)
        exporter = VRayExporter(image_width=1280,
                                image_height=720,
                                scene_name="tdw_room",
                                animate=True)
        self.add_ons.append(camera)
        # Load the scene.
        # Add the objects.
        # Adjust post-processing parameters to achieve a suitable depth of field and exposure.
        # Also adjust the ambient occlusion parameters for realistic shadowing in corners and under furniture objects.
        # Set shadow strength to near-full.
        self.communicate([{"$type": "set_render_quality",
                           "render_quality": 5},
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
                           "strength": 0.85},
                          self.get_add_scene(scene_name="tdw_room"),
                          self.get_add_object(model_name="coffee_table_glass_round",
                                              object_id=self.table_id,
                                              position={"x":0.125, "y": 0, "z": 0.37},
                                              rotation={"x": 0, "y": 45, "z": 0}),
                         self.get_add_object(model_name="live_edge_coffee_table",
                                             object_id=self.get_unique_id(),
                                             position={"x": 1.81, "y": 0, "z": -0.47},
                                             rotation={"x": 0, "y": -90, "z": 0}),
                         self.get_add_object(model_name="bastone_floor_lamp",
                                             object_id=self.get_unique_id(),
                                             position={"x": 2.35, "y": 0, "z": 1},
                                             rotation={"x": 0, "y": 35, "z": 0}),
                         self.get_add_object(model_name="chair_eames_plastic_armchair",
                                             object_id=self.chair_id,
                                             position={"x": 0.1, "y": 0, "z": 1.85},
                                             rotation={"x": 0, "y": 63.25, "z": 0}),
                         self.get_add_object(model_name="vase_05",
                                             object_id=self.get_unique_id(),
                                             position={"x": 0.125, "y": 0.3960, "z": 0.37},
                                             rotation={"x": 0, "y": 63.25, "z": 0}),
                         self.get_add_object(model_name="zenblocks",
                                             object_id=self.get_unique_id(),
                                             position={"x": 1.8, "y": 0.303, "z": -0.517},
                                             rotation={"x": 0, "y": 70, "z": 0})])
        # Let physics settle.       
        for step in range(15):
            self.communicate([])
        self.add_ons.append(exporter)
        # Ten frame hold before moving chair.
        for step in range(10):
            self.communicate([])
        # Apply a force and run simulation for 150 frames.
        self.communicate({"$type": "apply_force_to_object",
                          "id": self.chair_id,
                          "force": {"x": 0, "y": 0.5, "z": -35}})
        for step in range(self.frame_range):
            self.communicate([])
        # Launch Vantage render in headless mode; it will run to completion and automatically close.
        exporter.launch_renderer(output_directory=self.output_path,
                                 render_host=self.render_host)
        

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--render_host", type=str, default="localhost", help="Host to render on.")
    parser.add_argument("--output_path", type=str, help="Folder location to output rendered images.")
    args = parser.parse_args()
    DynamicObjects(render_host=args.render_host, output_path=args.output_path).run()
