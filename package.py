
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random


# ==========================================
# 1. OVERLAP DETECTION
# ==========================================

def check_overlap(x, y, w, h, placements):

    for p in placements:

        if not (
            x + w <= p["x"] or
            p["x"] + p["w"] <= x or
            y + h <= p["y"] or
            p["y"] + p["h"] <= y
        ):
            return True

    return False


# ==========================================
# 2. VALIDITY CHECK
# ==========================================

def is_valid(x, y, w, h, placements,
             container_width, container_height):

    if x < 0 or y < 0:
        return False

    if x + w > container_width:
        return False

    if y + h > container_height:
        return False

    if check_overlap(x, y, w, h, placements):
        return False

    return True


# ==========================================
# 3. PACKAGE PLACEMENT
# ==========================================

def place_packages(order, packages,
                   container_width, container_height):

    placements = []
    unplaced = []

    for package_id in order:

        original_w, original_h = packages[package_id]

        orientations = [(original_w, original_h)]

        if original_w != original_h:
            orientations.append((original_h, original_w))

        x_positions = {0}
        y_positions = {0}

        for p in placements:
            x_positions.add(p["x"] + p["w"])
            y_positions.add(p["y"] + p["h"])

        candidates = [
            (x, y)
            for y in sorted(y_positions)
            for x in sorted(x_positions)
        ]

        possible = []

        for w, h in orientations:

            for x, y in candidates:

                if is_valid(
                    x, y, w, h, placements,
                    container_width, container_height
                ):

                    possible.append((y, x, w, h))

        if possible:

            y, x, w, h = min(possible)

            placements.append({
                "id": package_id,
                "x": x,
                "y": y,
                "w": w,
                "h": h
            })

        else:
            unplaced.append(package_id)

    return placements, unplaced


# ==========================================
# 4. SPACE UTILIZATION
# ==========================================

def calculate_utilization(placements,
                          container_width, container_height):

    used_area = sum(
        p["w"] * p["h"] for p in placements
    )

    if container_width <= 0 or container_height <= 0:
        raise ValueError("Container dimensions must be positive.")

    total_area = container_width * container_height

    utilization = (used_area / total_area) * 100

    return used_area, total_area, utilization


# ==========================================
# 5. ARRANGEMENT SCORING
# ==========================================

def evaluate_arrangement(placements, unplaced,
                         container_width, container_height):

    used_area, _, _ = calculate_utilization(
        placements, container_width, container_height
    )

    if placements:

        max_width = max(
            p["x"] + p["w"] for p in placements
        )

        max_height = max(
            p["y"] + p["h"] for p in placements
        )

        bounding_area = max_width * max_height

    else:
        bounding_area = container_width * container_height

    return (
        len(placements),
        used_area,
        -bounding_area
    )


# ==========================================
# 6. OPTIMIZATION
# ==========================================


def optimize_loading(packages, container_width,
                     container_height, attempts=500):
    
    if container_width <= 0 or container_height <= 0:
        raise ValueError("Container dimensions must be positive.")

    if attempts < 0:
        raise ValueError("Optimization attempts cannot be negative.")

    for package_id, dimensions in packages.items():
        if len(dimensions) != 2:
            raise ValueError(
                f"Package {package_id} must have a width and height."
            )
        width, height = dimensions
        if width <= 0 or height <= 0:
            raise ValueError(
                f"Package dimensions must be positive for {package_id}."
            )

    package_ids = list(packages.keys())

    if not package_ids:
        return [], list(package_ids)

    orders = [
        sorted(
            package_ids,
            key=lambda p: packages[p][0] * packages[p][1],
            reverse=True
        ),

        sorted(
            package_ids,
            key=lambda p: max(packages[p]),
            reverse=True
        ),

        sorted(
            package_ids,
            key=lambda p: packages[p][1],
            reverse=True
        ),

        sorted(
            package_ids,
            key=lambda p: packages[p][0],
            reverse=True
        ),

        package_ids,
        list(reversed(package_ids))
    ]

    rng = random.Random(42)

    for _ in range(attempts):

        new_order = package_ids.copy()
        rng.shuffle(new_order)
        orders.append(new_order)

    best_placements = []
    best_unplaced = package_ids.copy()
    best_score = (-1, -1, float("-inf"))

    for order in orders:

        placements, unplaced = place_packages(
            order,
            packages,
            container_width,
            container_height
        )

        score = evaluate_arrangement(
            placements,
            unplaced,
            container_width,
            container_height
        )

        if score > best_score:

            best_score = score
            best_placements = placements
            best_unplaced = unplaced

    return best_placements, best_unplaced


# ==========================================
# 7. VISUALIZATION
# ==========================================

def visualize_container(placements,
                         container_width, container_height):

    fig, ax = plt.subplots(figsize=(10, 7))

    container = patches.Rectangle(
        (0, 0),
        container_width,
        container_height,
        linewidth=3,
        edgecolor="black",
        facecolor="white"
    )

    ax.add_patch(container)

    colors = [
        "skyblue", "lightgreen", "salmon",
        "orange", "plum", "khaki", "lightcoral"
    ]

    for i, p in enumerate(placements):

        rect = patches.Rectangle(
            (p["x"], p["y"]),
            p["w"],
            p["h"],
            linewidth=2,
            edgecolor="black",
            facecolor=colors[i % len(colors)]
        )

        ax.add_patch(rect)

        ax.text(
            p["x"] + p["w"] / 2,
            p["y"] + p["h"] / 2,
            f'{p["id"]}\n{p["w"]} x {p["h"]}',
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold"
        )

    ax.set_xlim(0, container_width)
    ax.set_ylim(0, container_height)

    ax.set_xticks(range(container_width + 1))
    ax.set_yticks(range(container_height + 1))

    ax.set_aspect("equal")
    ax.set_xlabel("Container Width")
    ax.set_ylabel("Container Height")
    ax.set_title("Optimized Container Loading Layout")

    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    return fig
