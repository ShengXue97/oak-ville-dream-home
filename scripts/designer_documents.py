"""Derive designer schedules and an annotated orthographic SVG from the scene.

The SVG is a coordination drawing, not an issued-for-construction drawing.
Dimensions come from saved mesh locations; written reference datums and
assumed clear room spans are distinguished explicitly.
"""

import csv
import html


def write_designer_documents():
    scene = bpy.context.scene
    bpy.context.view_layer.update()
    with (ROOT / "docs/schedules/furniture-component-schedule.csv").open(
        "w", newline=""
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ["component", "width_m", "depth_m", "height_m", "x_m", "plan_y_m", "z_m"]
        )
        for obj in sorted(scene.objects, key=lambda item: item.name):
            if obj.type == "MESH" and any(
                c.name in {"Furniture", "Fixed_Joinery"} for c in obj.users_collection
            ):
                writer.writerow(
                    [
                        obj.name,
                        *[round(value, 4) for value in obj.dimensions],
                        round(obj.location.x, 4),
                        round(-obj.location.y, 4),
                        round(obj.location.z, 4),
                    ]
                )
    wall_boxes = []
    for obj in scene.objects:
        if obj.type != "MESH" or not any(
            c.name == "Architecture" for c in obj.users_collection
        ):
            continue
        corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        low = [min(point[axis] for point in corners) for axis in range(3)]
        high = [max(point[axis] for point in corners) for axis in range(3)]
        if low[2] <= 0.80 <= high[2]:
            wall_boxes.append((low[0], high[0], -high[1], -low[1], obj.name))
    room_rows = []
    resolution = 0.025
    for name, (left, right, top, bottom) in ROOMS.items():
        columns = math.ceil((right - left) / resolution)
        rows = math.ceil((bottom - top) / resolution)
        dx = (right - left) / columns
        dy = (bottom - top) / rows
        available = 0
        relevant = [
            box
            for box in wall_boxes
            if box[0] < right and box[1] > left and box[2] < bottom and box[3] > top
        ]
        for column in range(columns):
            x = left + (column + 0.5) * dx
            for row in range(rows):
                plan_y = top + (row + 0.5) * dy
                if not any(
                    a <= x <= b and c <= plan_y <= d for a, b, c, d, _ in relevant
                ):
                    available += 1
        room_rows.append(
            {
                "room": name,
                "reference_width_m": right - left,
                "reference_depth_m": bottom - top,
                "reference_area_m2": round((right - left) * (bottom - top), 4),
                "approx_floor_excluding_walls_m2": round(available * dx * dy, 3),
                "floor_area_method": "25mm centre-sampled grid; excludes wall footprint at z=0.8m, includes doorway floors; no furniture subtraction",
            }
        )
    with (ROOT / "docs/schedules/room-area-schedule.csv").open(
        "w", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=room_rows[0].keys())
        writer.writeheader()
        writer.writerows(room_rows)

    # Actual wall reference positions, independently checked from mesh origins.
    def wall_coordinate(prefix, axis):
        obj = next(
            obj
            for obj in scene.objects
            if obj.name.startswith(prefix)
            and obj.type == "MESH"
            and any(
                collection.name == "Architecture" for collection in obj.users_collection
            )
        )
        return obj.location.x if axis == 0 else -obj.location.y

    checks = []
    for description, prefix, axis, intended in [
        ("Bedroom 3 west partition datum", "Bedroom3_West", 0, 3.375),
        ("Bedroom 3/2 partition datum", "Bedroom3_East", 0, 6.375),
        ("Bedroom 2/main partition datum", "Bedroom2_East", 0, 9.375),
        ("Right external wall datum", "Main_East", 0, 12.675),
        ("Shelter east datum", "Shelter_East", 0, 1.750),
        ("Kitchen west datum", "Kitchen_West", 0, 3.500),
        ("Kitchen/yard divider datum", "Kitchen_Yard_0", 0, 5.775),
        ("Yard/utility divider datum", "Yard_Utility", 0, 7.150),
        ("Ensuite/ledge east datum", "Ensuite_East", 0, 11.100),
        ("Shelter north datum", "Shelter_North", 1, 4.450),
        ("Shelter south datum", "Shelter_South", 1, 7.250),
        ("Kitchen south datum", "Kitchen_Yard_South", 1, 8.950),
        ("Bath south datum", "Baths_South", 1, 6.400),
        ("Ledge south datum", "Ledge_South", 1, 7.650),
    ]:
        actual = wall_coordinate(prefix, axis)
        checks.append(
            {
                "description": description,
                "plan_reference_mm": intended * 1000,
                "actual_mesh_datum_mm": round(actual * 1000, 3),
                "error_mm": round((actual - intended) * 1000, 4),
                "pass": abs(actual - intended) < 0.00001,
            }
        )
    net_internal = sum(
        row["approx_floor_excluding_walls_m2"]
        for row in room_rows
        if row["room"] != "AC_Ledge"
    )
    report = {
        "mesh_datum_checks": checks,
        "all_mesh_datums_pass": all(row["pass"] for row in checks),
        "sampled_internal_floor_m2": round(net_internal, 3),
        "sampled_floor_including_ledge_m2": round(
            sum(row["approx_floor_excluding_walls_m2"] for row in room_rows), 3
        ),
        "secondary_plan_quoted_internal_m2": 86,
        "difference_m2": round(net_internal - 86, 3),
        "warning": "Not a statutory area calculation. Wall-face assumptions and drawing variants remain unresolved.",
    }
    (ROOT / "docs/validation/mesh-dimensions-and-areas.json").write_text(
        json.dumps(report, indent=2)
    )

    # Vector orthographic drawing: 80 screen units/m, plan orientation retained.
    scale = 80
    origin_x, origin_y = 165, 155

    def position(x, plan_y):
        return origin_x + x * scale, origin_y + plan_y * scale

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1140" viewBox="0 0 1440 1140">',
        '<rect width="1440" height="1140" fill="#fffdf8"/>',
        "<style>text{font-family:Arial,sans-serif;fill:#273538}.dim{font-size:13px}.room{font-size:14px;font-weight:bold}.note{font-size:14px}</style>",
        '<text x="70" y="40" font-size="26" font-weight="bold">OAK VILLE | DIMENSIONED DESIGN REFERENCE</text>',
        '<text x="70" y="66" class="note">Metres in Blender · written dimensions shown in mm · provisional wall-centre datum interpretation</text>',
    ]
    for room, (left, right, top, bottom) in ROOMS.items():
        x, y = position(left, top)
        color = (
            "#e8ddc7"
            if room
            not in {
                "Kitchen",
                "Common_Bath",
                "Ensuite",
                "Service_Yard",
                "Utility_Strip",
                "AC_Ledge",
            }
            else "#eeeae0"
        )
        svg.append(
            f'<rect x="{x}" y="{y}" width="{(right-left)*scale}" height="{(bottom-top)*scale}" fill="{color}" stroke="#b8af9b" stroke-width="0.6"/>'
        )
    for left, right, top, bottom, name in wall_boxes:
        x, y = position(left, top)
        svg.append(
            f'<rect x="{x}" y="{y}" width="{(right-left)*scale}" height="{(bottom-top)*scale}" fill="#454b49"/>'
        )
    # Hinged leaves and furniture are measured from actual transformed bounds.
    for obj in scene.objects:
        if obj.type != "MESH":
            continue
        is_furniture = any(
            c.name in {"Furniture", "Fixed_Joinery"} for c in obj.users_collection
        )
        if not (obj.get("hinged_component") or is_furniture):
            continue
        corners = footprint(obj)
        polygon = " ".join(
            f"{origin_x+p.x*scale:.2f},{origin_y-p.y*scale:.2f}" for p in corners
        )
        svg.append(
            f'<polygon points="{polygon}" fill="{("#dbc5a4" if is_furniture else "#b89a6c")}" fill-opacity="0.24" stroke="#a08b6b" stroke-width="0.7"/>'
        )
    for obj in scene.objects:
        if obj.get("route_points_plan_m"):
            points = json.loads(obj["route_points_plan_m"])
            points_string = " ".join(
                f"{position(x,y)[0]},{position(x,y)[1]}" for x, y in points
            )
            svg.append(
                f'<polyline points="{points_string}" fill="none" stroke="#337f82" stroke-width="2" stroke-dasharray="5 4"/>'
            )
    for room, (left, right, top, bottom) in ROOMS.items():
        x, y = position((left + right) / 2, (top + bottom) / 2)
        text_name = room.replace("_", " ")
        if room == "Utility_Strip":
            svg.append(
                f'<text transform="translate({x},{y}) rotate(-90)" text-anchor="middle" font-size="11">Utility strip*</text>'
            )
        else:
            svg.append(
                f'<text x="{x}" y="{y}" text-anchor="middle" class="room">{html.escape(text_name)}</text>'
            )

    def horizontal_dimension(values, plan_y, extension_y):
        accumulated = 0
        for millimetres in values:
            end = accumulated + millimetres / 1000
            x1, y = position(accumulated, plan_y)
            x2, _ = position(end, plan_y)
            svg.append(
                f'<path d="M{x1},{position(0,extension_y)[1]} V{y+7} M{x2},{position(0,extension_y)[1]} V{y+7} M{x1},{y} H{x2}" fill="none" stroke="#394446" stroke-width="0.8"/>'
            )
            for x in (x1, x2):
                svg.append(f'<path d="M{x-4},{y+4} l8,-8" stroke="#394446"/>')
            svg.append(
                f'<text x="{(x1+x2)/2}" y="{y-7}" text-anchor="middle" class="dim">{millimetres}</text>'
            )
            accumulated = end

    def vertical_dimension(values, plan_x, extension_x):
        accumulated = 0
        for millimetres in values:
            end = accumulated + millimetres / 1000
            x, y1 = position(plan_x, accumulated)
            _, y2 = position(plan_x, end)
            ex = position(extension_x, 0)[0]
            svg.append(
                f'<path d="M{ex},{y1} H{x+7} M{ex},{y2} H{x+7} M{x},{y1} V{y2}" fill="none" stroke="#394446" stroke-width="0.8"/>'
            )
            svg.append(
                f'<text transform="translate({x-8},{(y1+y2)/2}) rotate(-90)" text-anchor="middle" class="dim">{millimetres}</text>'
            )
            accumulated = end

    horizontal_dimension(CHAINS["upper"], -0.55, 0)
    horizontal_dimension([12675], -0.80, 0)
    horizontal_dimension(CHAINS["lower"], 9.65, 8.95)
    horizontal_dimension([11100], 10.10, 8.95)
    vertical_dimension(CHAINS["left"], -0.75, 0)
    vertical_dimension([8950], -1.25, 0)
    vertical_dimension(CHAINS["right"], 13.35, 12.675)
    vertical_dimension([7650], 13.85, 12.675)
    svg.extend(
        [
            '<text x="70" y="1004" class="note">Teal: W01–W11 routes. Interior doors open; entry closed. Ceiling removed only in this drawing.</text>',
            '<text x="70" y="1029" class="note">* Undimensioned partition positions, wall thicknesses, utility strip, fixtures and opening sizes are provisional.</text>',
            '<text x="70" y="1054" class="note">FFL Z=0.00 m · ceiling assumed 2.60 m · typical door clear head 2.12 m · corridor datum band 1.10 m</text>',
            '<text x="70" y="1079" class="note">See DESIGNER_HANDOFF.md and schedules. Verify finished faces and services on site before fabrication.</text>',
            '<text x="70" y="1110" font-size="15" font-weight="bold">NOT A SURVEY / NOT ISSUED FOR CONSTRUCTION</text>',
            "</svg>",
        ]
    )
    (ROOT / "docs/drawings/OAK_VILLE_DIMENSIONED_MODEL.svg").write_text(
        "\n".join(svg), encoding="utf-8"
    )
    return report
