from core.metagraph import Metagraph
from PIL import Image, ImageDraw


def draw_circle(draw, x, y, r):
    draw.ellipse((x - r, y - r, x + r, y + r), outline="blue")


def draw_vertex(draw, v, x, y, r):
    draw_circle(draw, x, y, r)
    draw.text((x - r, y - r), v.name, fill="black")


def visualize(mg: Metagraph, path: str):
    vertices = mg.vertices

    leaf_vertices = list(filter(lambda x: x.is_leaf, vertices.values()))

    image = Image.new("RGBA", (1000, 1000), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    drawn_nodes = {}

    direct_parents = []

    for i, v in enumerate(leaf_vertices):
        r = 30
        x, y = 100 + i * 2 * r * 1.5, 100

        draw_vertex(draw, v, x, y, r)

        direct_parents.extend(v.parents)

        drawn_nodes[v.id] = (x, y, r)

    print(list(set(direct_parents)))

    for i, v in enumerate(direct_parents):
        coords = [drawn_nodes[x.id] for x in v.children]

        x0, y0 = min(c[0] for c in coords), min(c[1] for c in coords)
        x1, y1 = max(c[0] for c in coords), max(c[1] for c in coords)

        print(x0, y0, x1, y1)

        draw.ellipse((x0 - 30, y0 - 100, x1 + 30, y1 + 100), outline='red')

    image.show()
    # image.save(path, "PNG")
