from urllib.parse import urlparse

from scraper import Scraper

COLORS = [
    "#a8dadc",
    "#b5e2fa",
    "#c8b6ff",
    "#ffc8dd",
    "#ffafcc",
    "#bde0fe",
    "#a2d2ff",
    "#cdb4db",
    "#ffd6a5",
    "#caffbf",
    "#9bf6ff",
    "#fdffb6",
    "#e0aaff",
    "#98f5e1",
    "#f1c0e8",
    "#cfbaf0",
]

path_colors: dict[str, str] = {}
color_counter = 0


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def lerp(c1: str, c2: str, t: float) -> str:
    t = smoothstep(t)
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def get_color(url: str) -> str:
    global color_counter
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    key = parsed.netloc + ("/" + parts[0] if parts and parts[0] else "")

    if key not in path_colors:
        t = (color_counter * 0.09) % 1.0
        i = int(t * (len(COLORS) - 1))
        local_t = (t * (len(COLORS) - 1)) - i
        color = lerp(COLORS[i], COLORS[min(i + 1, len(COLORS) - 1)], local_t)
        path_colors[key] = color + "cc"
        color_counter += 1

    return path_colors[key]


GRAPH_ATTRS = {
    "layout": "neato",
    "mode": "KK",
    "model": "subset",
    "splines": "spline",
    "overlap": "prism",
    "overlap_scaling": "-4",
    "sep": "+25",
    "esep": "+12",
    "K": "1.5",
    "bgcolor": "#000000",
    "pad": "0.5",
    "margin": "0",
    "outputorder": "edgesfirst",
    "normalize": "true",
    "smoothing": "triangle",
    "forcelabels": "true",
    "nslimit": "5.0",
    "mclimit": "5.0",
    "ratio": "compress",
    "beautify": "true",
}

NODE_ATTRS = {
    "shape": "box",
    "style": "filled,rounded",
    "fillcolor": "#ff6b6bcc",
    "fontcolor": "#ffffff",
    "fontname": "Helvetica-Bold",
    "fontsize": "14",
    "penwidth": "0",
    "margin": "0.20,0.12",
    "height": "0.5",
    "width": "1.0",
}

EDGE_ATTRS = {
    "color": "#ffffffaa",
    "penwidth": "1.8",
    "arrowsize": "0.7",
    "arrowhead": "vee",
    "style": "solid",
    "weight": "1.0",
    "len": "2.5",
}

RENDER_OPTS = {
    "format": "svg",
    "cleanup": True,
    "view": False,
}


def main() -> None:
    roots = {
        "https://example.com/": 2,
        "https://www.iana.org/": 1,
    }

    scraper = Scraper(
        name="iana_example",
        roots=roots,
        delay=0.5,
        retries=3,
        timeout=5.0,
        get_color=get_color,
        shorten_labels=True,
    )

    scraper.customize_appearance(
        graph=GRAPH_ATTRS,
        nodes=NODE_ATTRS,
        edges=EDGE_ATTRS,
    )

    scraper.run()

    scraper.render(
        filename="iana_example_graph",
        directory="output",
        **RENDER_OPTS,
    )


if __name__ == "__main__":
    main()
