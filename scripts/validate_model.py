"""Geometry-derived checks; usable both live and after reopening the saved file.

Collision test: a 0.50 m diameter, 1.70 m tall vertical capsule against
oriented mesh bounding boxes. Sampling is 25 mm maximum, with a 12.5 mm
safety allowance. Furniture boxes are intentionally conservative.
"""

from mathutils import Matrix


def obstacle_boxes():
    obstacles = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or not obj.get("collision_source", False):
            continue
        if any(collection.name == "Collision" for collection in obj.users_collection):
            continue
        corners = [Vector(corner) for corner in obj.bound_box]
        low = Vector(tuple(min(point[axis] for point in corners) for axis in range(3)))
        high = Vector(tuple(max(point[axis] for point in corners) for axis in range(3)))
        inverse = obj.matrix_world.inverted()
        up = obj.matrix_world.to_3x3() @ Vector((0, 0, 1))
        if abs(up.normalized().z) < 0.99999:
            # Sideways appliances use conservative world bounds. Their local Z
            # cannot be treated as the vertical direction of a human capsule.
            corners = [obj.matrix_world @ point for point in corners]
            low = Vector(
                tuple(min(point[axis] for point in corners) for axis in range(3))
            )
            high = Vector(
                tuple(max(point[axis] for point in corners) for axis in range(3))
            )
            inverse = Matrix.Identity(4)
        obstacles.append((obj, low, high, inverse))
    return obstacles


def capsule_distance(x, plan_y, obstacle):
    obj, low, high, inverse = obstacle
    # Upright local coordinates, or world coordinates for tilted sources.
    foot = inverse @ Vector((x, -plan_y, 0))
    spine_low = foot.z + 0.25
    spine_high = foot.z + 1.45
    dx = max(low.x - foot.x, 0, foot.x - high.x)
    dy = max(low.y - foot.y, 0, foot.y - high.y)
    dz = max(low.z - spine_high, 0, spine_low - high.z)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def floor_supported(x, plan_y):
    return any(
        a - 1e-6 <= x <= b + 1e-6 and c - 1e-6 <= plan_y <= d + 1e-6
        for name, (a, b, c, d) in ROOMS.items()
        if name != "AC_Ledge"
    )


def validate_routes(report_name="walkthrough-validation"):
    bpy.context.view_layer.update()
    boxes = obstacle_boxes()
    # Supporting floor slabs touch the capsule bottom and are not side obstacles.
    walls_and_furniture = [
        box
        for box in boxes
        if max((box[0].matrix_world @ Vector(c)).z for c in box[0].bound_box) > 0.04
    ]
    results = []
    for route in sorted(bpy.context.scene.objects, key=lambda obj: obj.name):
        if not route.get("route_points_plan_m"):
            continue
        points = json.loads(route["route_points_plan_m"])
        minimum = float("inf")
        nearest = None
        hits = set()
        unsupported = 0
        count = 0
        length = 0.0
        for a, b in zip(points, points[1:]):
            segment_length = math.dist(a, b)
            length += segment_length
            steps = max(1, math.ceil(segment_length / 0.025))
            for step in range(steps + 1):
                x = a[0] + (b[0] - a[0]) * step / steps
                plan_y = a[1] + (b[1] - a[1]) * step / steps
                count += 1
                if not floor_supported(x, plan_y):
                    unsupported += 1
                for obstacle in walls_and_furniture:
                    distance = capsule_distance(x, plan_y, obstacle)
                    if distance < minimum:
                        minimum, nearest = distance, obstacle[0].name
                    if distance < 0.25 + 0.0125:
                        hits.add(obstacle[0].name)
        results.append(
            {
                "route": route.name,
                "length_m": round(length, 3),
                "samples": count,
                "minimum_capsule_surface_clearance_m": round(minimum - 0.25, 4),
                "centered_clear_diameter_m": round(2 * minimum, 4),
                "nearest_obstacle": nearest,
                "collisions_or_sampling_margin": sorted(hits),
                "unsupported_samples": unsupported,
                "pass": not hits and unsupported == 0,
            }
        )
    report = {
        "method": "Vertical capsule vs upright oriented source bounding boxes; max step 0.025m; safety allowance 0.0125m",
        "capsule_diameter_m": 0.50,
        "capsule_height_m": 1.70,
        "doors": "OPEN",
        "routes": results,
        "all_pass": all(row["pass"] for row in results),
        "limitations": "Conservative furniture bounds, proposed dimensions, no building compliance certification or game-engine physics test",
    }
    (ROOT / "docs" / (report_name + ".json")).write_text(json.dumps(report, indent=2))
    return report


def rectangles_overlap(first, second, tolerance=0.002):
    """Separating-axis test for upright, possibly rotated rectangle footprints."""
    for polygon in (first, second):
        for index in range(4):
            edge = polygon[(index + 1) % 4] - polygon[index]
            axis = Vector((-edge.y, edge.x))
            if axis.length < 1e-8:
                continue
            axis.normalize()
            a = [point.dot(axis) for point in first]
            b = [point.dot(axis) for point in second]
            if min(max(a), max(b)) - max(min(a), min(b)) <= tolerance:
                return False
    return True


def footprint(obj):
    up = obj.matrix_world.to_3x3() @ Vector((0, 0, 1))
    if abs(up.normalized().z) < 0.99999:
        corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        left, right = min(p.x for p in corners), max(p.x for p in corners)
        bottom, top = min(p.y for p in corners), max(p.y for p in corners)
        return [
            Vector(point)
            for point in [(left, bottom), (right, bottom), (right, top), (left, top)]
        ]
    low = [min(corner[axis] for corner in obj.bound_box) for axis in range(3)]
    high = [max(corner[axis] for corner in obj.bound_box) for axis in range(3)]
    return [
        (obj.matrix_world @ Vector((x, y, 0))).xy
        for x, y in [
            (low[0], low[1]),
            (high[0], low[1]),
            (high[0], high[1]),
            (low[0], high[1]),
        ]
    ]


def z_span(obj):
    values = [(obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box]
    return min(values), max(values)


def validate_furniture_and_swings():
    bpy.context.view_layer.update()
    sources = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "MESH" and obj.get("collision_source", False)
    ]
    architecture = [
        obj
        for obj in sources
        if any(c.name == "Architecture" for c in obj.users_collection)
        and z_span(obj)[1] > 0.10
    ]
    furnishings = [
        obj
        for obj in sources
        if any(c.name in {"Furniture", "Fixed_Joinery"} for c in obj.users_collection)
    ]
    clashes = []
    for item in furnishings:
        item_low, item_high = z_span(item)
        for wall_obj in architecture:
            wall_low, wall_high = z_span(wall_obj)
            if min(item_high, wall_high) - max(item_low, wall_low) > 0.01:
                if rectangles_overlap(footprint(item), footprint(wall_obj), 0.01):
                    clashes.append([item.name, wall_obj.name])
    swings = []
    for hinge in bpy.context.scene.objects:
        if "open_angle_degrees" not in hinge:
            continue
        leaf = next(obj for obj in hinge.children if obj.get("hinged_component"))
        original_angle = hinge.rotation_euler.z
        contacts = set()
        for step in range(91):
            hinge.rotation_euler.z = math.radians(
                hinge["open_angle_degrees"] * step / 90
            )
            bpy.context.view_layer.update()
            leaf_low, leaf_high = z_span(leaf)
            for obstacle in architecture + furnishings:
                obstacle_low, obstacle_high = z_span(obstacle)
                if min(leaf_high, obstacle_high) - max(leaf_low, obstacle_low) > 0.01:
                    if rectangles_overlap(footprint(leaf), footprint(obstacle), 0.002):
                        contacts.add(obstacle.name)
        hinge.rotation_euler.z = original_angle
        swings.append(
            {
                "hinge": hinge.name,
                "tested_angles": 91,
                "contacts": sorted(contacts),
                "pass": not contacts,
            }
        )
    bpy.context.view_layer.update()
    report = {
        "furniture_wall_clashes_over_10mm": clashes,
        "door_swings": swings,
        "all_pass": not clashes and all(row["pass"] for row in swings),
        "limitations": "1-degree swing samples, leaf bounds only; handles/hinge hardware and cabinet door operation need detailed design. Interpenetrating components within the same furniture assembly are intentional.",
    }
    (ROOT / "docs/furniture-fit-and-door-swings.json").write_text(
        json.dumps(report, indent=2)
    )
    return report
