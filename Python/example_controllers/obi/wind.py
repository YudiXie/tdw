from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.fluids.cube_emitter import CubeEmitter
from tdw.obi_data.fluids.fluid import Fluid
from tdw.obi_data.wind_source import WindSource
from tdw.obi_data.cloth.sheet_type import SheetType
from tdw.obi_data.cloth.tether_particle_group import TetherParticleGroup
from tdw.obi_data.cloth.tether_type import TetherType
from tdw.tdw_utils import TDWUtils


"""
Add a custom fluid to the scene.
"""

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
# Add some blocks.
y = 0
x = -1
cube_scale = {"x": 0.2, "y": 0.2, "z": 0.4}
while y < 1:
    z = 0
    while z < 1:
        commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": x, "y": y, "z": z},
                                                          library="models_flex.json",
                                                          default_physics_values=False,
                                                          scale_factor=cube_scale,
                                                          scale_mass=False,
                                                          mass=0.5))
        z += cube_scale["z"]
    y += cube_scale["y"]
commands.extend(Controller.get_add_physics_object(model_name="chair_billiani_doll",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": -0.38, "y": 0, "z": -0.34},
                                                  library="models_core.json"))
c.communicate(commands)
wind_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": 1.1, "y": 1.32, "z": -1.9},
                           look_at={"x": -2, "y": 0, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
# Add a wind source.
wind_source = WindSource(wind_id=wind_id,
                         position={"x": -0.1, "y": 0, "z": 0.25},
                         rotation={"x": 0, "y": -90, "z": 0},
                         emitter_radius=1,
                         capacity=5000,
                         speed=0.1)
obi.wind_sources[wind_id] = wind_source
# Create a tethered cloth.
cloth_id = Controller.get_unique_id()
obi.create_cloth_sheet(cloth_material="canvas",
                       object_id=cloth_id,
                       position={"x": -4, "y": 1.6, "z": 0.2},
                       rotation={"x": -90, "y": 90, "z": 0},
                       sheet_type=SheetType.cloth,
                       tether_positions={TetherParticleGroup.north_edge: TetherType(object_id=cloth_id, is_static=True)})
c.communicate([])
# Start to increase the speed.
wind_source.set_speed(speed=30, ds=0.1)
for i in range(200):
    c.communicate([])
# Decrease the speed.
wind_source.set_speed(speed=0.1, ds=0.1)
for i in range(400):
    c.communicate([])
c.communicate({"$type": "terminate"})
