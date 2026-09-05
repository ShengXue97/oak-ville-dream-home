"""Editor Play controls: grounded character, doors and optional inspection flight.

Loaded automatically by Content/Python/init_unreal.py. CharacterMovement owns
gravity, floor contact and collision. This module supplies interaction input and
door animation in editor Play; it is not a packaged-game Python runtime.
"""

import gzip
import json
import math
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
STATE = None
HANDLE = None
BUSY = False
WALK_SPEED_CM_S = 180.0
RUN_SPEED_CM_S = 320.0


def message(world, text, key="OakVilleControls", duration=0.2):
    unreal.SystemLibrary.print_string(
        world,
        text,
        True,
        False,
        unreal.LinearColor(1, 0.9, 0.7, 1),
        duration,
        unreal.Name(key),
    )


def rotate_xy(vector, degrees):
    angle = math.radians(degrees)
    return unreal.Vector(
        vector.x * math.cos(angle) - vector.y * math.sin(angle),
        vector.x * math.sin(angle) + vector.y * math.cos(angle),
        vector.z,
    )


class Door:
    def __init__(self, record, children, records):
        self.name = record["name"]
        self.hinge = unreal.Vector(*record["location_cm"])
        self.open_angle = record["open_angle"]
        self.export_angle = record.get("export_angle", self.open_angle)
        self.closed_angle = record["closed_angle"]
        self.locked = self.name == "Entry_Door_Hinge"
        self.parts = [
            (actor, actor.get_actor_location(), actor.get_actor_rotation())
            for actor in children
        ]
        self.leaf = next(
            actor for actor in children if records[actor]["name"].endswith("_Leaf")
        )
        self.leaf_size = records[self.leaf]["bounds_size_cm"]
        self.current = self.closed_angle
        self.target = self.closed_angle
        for actor in children:
            actor.get_component_by_class(unreal.StaticMeshComponent).set_mobility(
                unreal.ComponentMobility.MOVABLE
            )
        self.apply(self.current)

    def apply(self, angle):
        # Mesh geometry is baked at its recorded Blender export angle. Y is
        # reflected on export, so Unreal's incremental yaw has the opposite sign.
        yaw = self.export_angle - angle
        for actor, position, rotation in self.parts:
            actor.set_actor_location(
                self.hinge + rotate_xy(position - self.hinge, yaw), False, False
            )
            actor.set_actor_rotation(
                unreal.Rotator(
                    pitch=rotation.pitch, yaw=rotation.yaw + yaw, roll=rotation.roll
                ),
                False,
            )

    def blocked_by(self, pawn, angle):
        yaw = self.export_angle - angle
        original = next(
            position for actor, position, _ in self.parts if actor == self.leaf
        )
        centre = self.hinge + rotate_xy(original - self.hinge, yaw)
        local = rotate_xy(pawn.get_actor_location() - centre, -yaw)
        radius = pawn.get_editor_property(
            "capsule_component"
        ).get_scaled_capsule_radius()
        half_height = pawn.get_editor_property(
            "capsule_component"
        ).get_scaled_capsule_half_height()
        x = max(abs(local.x) - self.leaf_size[0] / 2, 0)
        y = max(abs(local.y) - self.leaf_size[1] / 2, 0)
        return (
            x * x + y * y < (radius + 2) ** 2
            and abs(local.z) < self.leaf_size[2] / 2 + half_height
        )

    def toggle(self):
        if self.locked:
            return False
        self.target = (
            self.closed_angle if self.target == self.open_angle else self.open_angle
        )
        return True

    def tick(self, delta, pawn, creative):
        distance = self.target - self.current
        if abs(distance) < 0.001:
            return
        step = max(-100 * delta, min(100 * delta, distance))
        subdivisions = max(1, math.ceil(abs(step) / 3))
        for _ in range(subdivisions):
            angle = self.current + step / subdivisions
            if not creative and self.blocked_by(pawn, angle):
                self.target = self.current
                return
            self.current = angle
            self.apply(angle)


class PlaySession:
    def __init__(self, world, pawn, controller):
        if not isinstance(pawn, unreal.Character):
            raise RuntimeError(
                "Play did not spawn the First Person character; refusing to disguise a flying pawn as walking"
            )
        self.world, self.pawn, self.controller = world, pawn, controller
        self.creative = False
        self.keys = {}
        self.last_safe = unreal.Vector(270, 655, 88)
        self.movement = pawn.get_editor_property("character_movement")
        self.ensure_human_collision()
        pawn.set_actor_location(self.last_safe, False, True)
        pawn.set_actor_rotation(unreal.Rotator(pitch=0, yaw=-60, roll=0), False)
        controller.set_control_rotation(unreal.Rotator(pitch=0, yaw=-60, roll=0))
        self.initial_pitch = controller.get_control_rotation().pitch
        capsule = pawn.get_editor_property("capsule_component")
        for camera in pawn.get_components_by_class(unreal.CameraComponent):
            camera.attach_to_component(
                capsule,
                unreal.Name("None"),
                unreal.AttachmentRule.KEEP_RELATIVE,
                unreal.AttachmentRule.KEEP_RELATIVE,
                unreal.AttachmentRule.KEEP_RELATIVE,
                False,
            )
            camera.set_relative_location(unreal.Vector(0, 0, 72), False, False)
            camera.set_relative_rotation(
                unreal.Rotator(pitch=0, yaw=0, roll=0), False, False
            )
            camera.set_field_of_view(65.0)
        for mesh in pawn.get_components_by_class(unreal.SkeletalMeshComponent):
            mesh.set_hidden_in_game(True)
            mesh.set_component_tick_enabled(False)
        self.movement.set_editor_property("gravity_scale", 1.0)
        self.movement.set_editor_property("jump_z_velocity", 260.0)
        self.movement.set_editor_property("max_fly_speed", 250.0)
        self.movement.set_movement_mode(unreal.MovementMode.MOVE_WALKING)
        with gzip.open(
            ROOT / "assets/unreal-export/scene.json.gz", "rt", encoding="utf-8"
        ) as stream:
            data = json.load(stream)
        records = {r["name"]: r for r in data["objects"]}
        actors = unreal.GameplayStatics.get_all_actors_of_class(
            world, unreal.StaticMeshActor
        )
        by_id = {
            str(tag).removeprefix("BlenderID:"): actor
            for actor in actors
            for tag in actor.tags
            if str(tag).startswith("BlenderID:")
        }
        records = {
            by_id[r["source_id"]]: r for r in data["objects"] if r["source_id"] in by_id
        }
        self.doors = []
        for record in data["doors"]:
            children = [
                by_id[r["source_id"]]
                for r in data["objects"]
                if r["parent"] == record["name"] and r["source_id"] in by_id
            ]
            if children:
                self.doors.append(Door(record, children, records))
        message(
            world,
            "Human mode | WASD walk | Hold Shift run | Space jump | E door | G creative",
            duration=6,
        )

    def down(self, name):
        key = unreal.Key()
        key.set_editor_property("key_name", name)
        return self.controller.is_input_key_down(key)

    def pressed(self, name):
        down = self.down(name)
        previous = self.keys.get(name, False)
        self.keys[name] = down
        return down and not previous

    def update_walk_speed(self):
        """Hold either Shift to run; release it to resume normal walking."""
        running = not self.creative and (
            self.down("LeftShift") or self.down("RightShift")
        )
        speed = RUN_SPEED_CM_S if running else WALK_SPEED_CM_S
        if self.movement.get_editor_property("max_walk_speed") != speed:
            self.movement.set_editor_property("max_walk_speed", speed)

    def set_creative(self, enabled):
        self.creative = enabled
        self.movement.stop_movement_immediately()
        self.pawn.set_actor_enable_collision(not enabled)
        if enabled:
            self.movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
        else:
            self.ensure_human_collision()
            # Resume at the last grounded location, never trapped inside a wall
            # or falling from outside the apartment after a noclip inspection.
            self.pawn.set_actor_location(self.last_safe, False, True)
            self.movement.set_movement_mode(unreal.MovementMode.MOVE_FALLING)
        message(
            self.world,
            (
                "Creative: Space up, Ctrl down; G returns to your last safe floor position"
                if enabled
                else "Human mode: gravity and collision enabled"
            ),
            duration=5,
        )

    def ensure_human_collision(self):
        """Recover safely if an editor reload or other code leaves noclip on."""
        if self.creative:
            return
        capsule = self.pawn.get_editor_property("capsule_component")
        broken = (
            not self.pawn.get_actor_enable_collision()
            or capsule.get_collision_enabled()
            != unreal.CollisionEnabled.QUERY_AND_PHYSICS
            or capsule.get_collision_response_to_channel(
                unreal.CollisionChannel.ECC_WORLD_STATIC
            )
            != unreal.CollisionResponseType.ECR_BLOCK
            or capsule.get_collision_response_to_channel(
                unreal.CollisionChannel.ECC_WORLD_DYNAMIC
            )
            != unreal.CollisionResponseType.ECR_BLOCK
        )
        if broken:
            self.pawn.set_actor_enable_collision(True)
            capsule.set_collision_profile_name("Pawn")
            capsule.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            capsule.set_collision_response_to_channel(
                unreal.CollisionChannel.ECC_WORLD_STATIC,
                unreal.CollisionResponseType.ECR_BLOCK,
            )
            capsule.set_collision_response_to_channel(
                unreal.CollisionChannel.ECC_WORLD_DYNAMIC,
                unreal.CollisionResponseType.ECR_BLOCK,
            )
            self.pawn.set_actor_location(self.last_safe, False, True)
            self.movement.stop_movement_immediately()
            self.movement.set_movement_mode(unreal.MovementMode.MOVE_FALLING)
            unreal.log_warning(
                "OakVille restored human capsule collision at the last safe position"
            )

    def aimed_door(self):
        eye, rotation = self.controller.get_player_view_point()
        forward = unreal.MathLibrary.get_forward_vector(rotation)
        candidates = []
        for door in self.doors:
            offset = door.leaf.get_actor_location() - eye
            distance = offset.length()
            if not 0.01 < distance < 210 or offset.dot(forward) / distance < 0.55:
                continue
            ignored = [self.pawn] + [a for a, _, _ in door.parts]
            hit = unreal.SystemLibrary.line_trace_single(
                self.world,
                eye,
                eye + offset,
                unreal.TraceTypeQuery.ECC_VISIBILITY,
                False,
                ignored,
                unreal.DrawDebugTrace.NONE,
            )
            if not hit:
                candidates.append((distance, door))
        return min(candidates, key=lambda pair: pair[0])[1] if candidates else None

    def tick(self, delta):
        delta = min(delta, 0.5)
        if self.pressed("G"):
            self.set_creative(not self.creative)
        self.ensure_human_collision()
        message(
            self.world,
            (
                "CREATIVE | collision OFF | G: return to human"
                if self.creative
                else "HUMAN | collision ON | Shift: run | G: creative"
            ),
            key="OakVilleMovementMode",
            duration=0.5,
        )
        self.update_walk_speed()
        if self.creative:
            vertical = int(self.down("SpaceBar")) - int(self.down("LeftControl"))
            self.pawn.add_movement_input(unreal.Vector(0, 0, 1), vertical)
        if not self.creative and self.movement.is_moving_on_ground():
            self.last_safe = self.pawn.get_actor_location()
        door = self.aimed_door()
        if door:
            message(
                self.world,
                "Front door locked" if door.locked else "E - open / close door",
                key="OakVilleDoor",
            )
        if self.pressed("E") and door:
            door.toggle()
        for door in self.doors:
            door.tick(delta, self.pawn, self.creative)


def tick(delta):
    global STATE, BUSY
    if BUSY:
        return
    BUSY = True
    try:
        world = unreal.get_editor_subsystem(
            unreal.UnrealEditorSubsystem
        ).get_game_world()
        if world is None:
            STATE = None
            return
        controller = unreal.GameplayStatics.get_player_controller(world, 0)
        pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
        if not controller or not pawn:
            return
        if STATE is None or STATE.world != world:
            STATE = PlaySession(world, pawn, controller)
        STATE.tick(delta)
    except Exception as error:
        import traceback

        unreal.log_error("OakVille Play controls: " + traceback.format_exc())
        uninstall()
    finally:
        BUSY = False


def uninstall():
    global HANDLE, STATE
    # Unloading the editor helper must never strand a character in noclip.
    if STATE is not None:
        try:
            if STATE.creative:
                STATE.set_creative(False)
            STATE.ensure_human_collision()
        except Exception:
            # The Play world may already have been destroyed during shutdown.
            pass
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
    HANDLE, STATE = None, None


def install():
    global HANDLE
    uninstall()
    HANDLE = unreal.register_slate_post_tick_callback(tick)
    unreal.log("OakVille grounded walkthrough and door controls ready")
