from tdw.controller import Controller
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.floorplan_flood import FloorplanFlood
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
Generate a floorplan scene and populate it with a layout of objects.
Flood a small set of rooms, and allow two objects to float in the water.
"""

c = Controller()

# Initialize the FloorplanFlood add-on.
floorplan_flood = FloorplanFlood()
# Scene 1, visual variant a, object layout 0.
floorplan_flood.init_scene(scene="1a", layout=0)

# Add a camera and enable image capture.
camera = ThirdPersonCamera(position={"x":-5, "y": 6.4, "z": -2.6},
                           look_at={"x": -2.25, "y": 0.05, "z": 2.5},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("floorplan_controller")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], pass_masks=["_img"], path=path)

c.add_ons.extend([floorplan_flood, camera, capture])
# Initialize the scene.
c.communicate([])
bowl_id = c.get_unique_id()
chair_id = c.get_unique_id()
# Make the image 720p and hide the roof.
c.communicate([{"$type": "set_screen_size",
                "width": 1280,
                "height": 720},
               {"$type": "set_field_of_view",
                "field_of_view": 82,
                "avatar_id": "a"},
               {"$type": "set_floorplan_roof",
                "show": False},
               # Add two objects that will float about in the water.
               c.get_add_object(model_name="elephant_bowl",
                                object_id=bowl_id,
                                position={"x": -4.0, "y": 0, "z": 3.36},
                                rotation={"x": 0, "y": 0, "z": 0}),
               c.get_add_object(model_name="chair_billiani_doll",
                                object_id=chair_id,
                                position={"x": -7.0, "y": 0, "z": 3.8},
                                rotation={"x": 0, "y": 0, "z": 0})])
# Start the flood at floor ID # 4, then use the adjacent floor info to propagate
# to adjacent rooms.  This is a very simple example; a real application would use 
# a more robust model for flood propagation.
flood_start_floor = 4
for i in range(50):
    floorplan_flood.set_flood_height(flood_start_floor, 0.0125)
    c.communicate([])
adjacent_floors = floorplan_flood.get_adjacent_floors(flood_start_floor)
for f in adjacent_floors:
    for i in range(50):
        floorplan_flood.set_flood_height(f, 0.0125)
        c.communicate([])
# Start to make the objects float.
c.communicate([{"$type": "add_floorplan_flood_buoyancy",
                "id": bowl_id},
               {"$type": "add_floorplan_flood_buoyancy",
                "id": chair_id}])
# Let the flood water undulate, and the objects bob about, for a while before quitting.
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
