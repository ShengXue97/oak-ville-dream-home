"""Geometry-derived checks; usable both live and after reopening the saved file.

Collision test: a 0.50 m diameter, 1.70 m tall vertical capsule against
oriented mesh bounding boxes. Sampling is 25 mm maximum, with a 12.5 mm
safety allowance. Furniture boxes are intentionally conservative.
"""


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
        obstacles.append((obj, low, high, obj.matrix_world.inverted()))
    return obstacles


def capsule_distance(x, plan_y, obstacle):
    obj, low, high, inverse = obstacle
    # All collision sources have upright local Z, including hinged doors.
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
