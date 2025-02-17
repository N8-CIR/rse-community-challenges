# %%
"""
An example of visualising a theory of change using a Sankey diagram.
"""

from matplotlib import pyplot as plt
import plotly.graph_objects as go
import networkx as nx
import matplotlib.patches as mpatches

# %%
toc_example = {
    "name": "Green RSE",
    "description": "The environmental impact of RSEs through their work is a growing concern. RSEs need to consider the environmental impact of their work and adopt sustainable practices where possible.",
    "evidence": [
        {
            "id": 1,
            "name": "Example evidence",
        },
    ],
    "inputs": [
        {
            "id": 1,
            "name": "Green RSE Sig Lead",
            "description": "A person to lead the Green RSE SIG",
            "actions": [1],
        },
    ],
    "actions": [
        {"id": 1, "name": "Create a Green RSE SIG", "outputs": [1]},
    ],
    "outputs": [
        {
            "id": 1,
            "name": "An SIG dedicated to the green RSE initiative",
            "objectives": [1, 2],
        },
    ],
    "objectives": [
        {
            "id": 1,
            "name": "Develop a set of best practices for RSEs to reduce their environmental impact.",
            "impacts": [1],
        },
        {
            "id": 2,
            "name": "Encourage green rse champions within RSE groups to promote sustainable practices.",
            "impacts": [1],
        },
    ],
    "impacts": [
        {
            "id": 1,
            "name": "Reduce the environmental impact of RSEs through their work.",
            "evidences": [1],
        },
    ],
}


# %%

# source = [0, 1, 2, 2, 3, 4]
# target = [1, 2, 3, 4, 5, 5]
# value = [2, 2, 1, 1, 1, 1]

# link = dict(source=source, target=target, value=value)
# data = go.Sankey(
#     node=dict(
#         pad=15,
#         thickness=20,
#         line=dict(color="black", width=0.5),
#         label=["A1", "A2", "B1", "B2", "C1", "C2"],
#         color=["blue", "red", "red", "blue", "blue", "red"],
#     ),
#     link=link,
# )

# fig = go.Figure(data)

# fig.show()

# %%


nodes_id_map = {
    k: i
    for i, k in enumerate(
        [
            *[f"evidence_{item['id']}" for item in toc_example["evidence"]],
            *[f"inputs_{item['id']}" for item in toc_example["inputs"]],
            *[f"actions_{item['id']}" for item in toc_example["actions"]],
            *[f"outputs_{item['id']}" for item in toc_example["outputs"]],
            *[f"objectives_{item['id']}" for item in toc_example["objectives"]],
            *[f"impacts_{item['id']}" for item in toc_example["impacts"]],
        ]
    )
}
nodes_id_map

# %%
# source_ids = list(nodes_id_map.values())
# source_ids

# %%

nodes = [
    *[item for item in toc_example["evidence"]],
    *[item for item in toc_example["inputs"]],
    *[item for item in toc_example["actions"]],
    *[item for item in toc_example["outputs"]],
    *[item for item in toc_example["objectives"]],
    *[item for item in toc_example["impacts"]],
]
nodes


# %%
node_positions = [
    *[
        [0, (i + 1) / len(toc_example["evidence"])]
        for i, item in enumerate(toc_example["evidence"])
    ],
    *[
        [1, (i + 1) / len(toc_example["inputs"])]
        for i, item in enumerate(toc_example["inputs"])
    ],
    *[
        [2, (i + 1) / len(toc_example["actions"])]
        for i, item in enumerate(toc_example["actions"])
    ],
    *[
        [3, (i + 1) / len(toc_example["outputs"])]
        for i, item in enumerate(toc_example["outputs"])
    ],
    *[
        [4, (i + 1) / len(toc_example["objectives"])]
        for i, item in enumerate(toc_example["objectives"])
    ],
    *[
        [5, (i + 1) / len(toc_example["impacts"])]
        for i, item in enumerate(toc_example["impacts"])
    ],
]
node_positions
# %%

node_names = [f"{node['name']}" for node in nodes]
node_names

# %%
node_ids = [f"{node['id']}" for node in nodes]


# %%
color_map = {
    "evidence": "blue",
    "inputs": "red",
    "actions": "green",
    "outputs": "purple",
    "objectives": "orange",
    "impacts": "yellow",
}
node_colors = [
    *[color_map["evidence"] for item in toc_example["evidence"]],
    *[color_map["inputs"] for item in toc_example["inputs"]],
    *[color_map["actions"] for item in toc_example["actions"]],
    *[color_map["outputs"] for item in toc_example["outputs"]],
    *[color_map["objectives"] for item in toc_example["objectives"]],
    *[color_map["impacts"] for item in toc_example["impacts"]],
]
node_colors


# %%
weighting_map = {
    k: count
    for k, count in [
        *[[f"evidence_{item['id']}", 1] for item in toc_example["evidence"]],
        *[
            [f"inputs_{item['id']}", len(item["actions"])]
            for item in toc_example["inputs"]
        ],
        *[
            [f"actions_{item['id']}", len(item["outputs"])]
            for item in toc_example["actions"]
        ],
        *[
            [f"outputs_{item['id']}", len(item["objectives"])]
            for item in toc_example["outputs"]
        ],
        *[
            [f"objectives_{item['id']}", len(item["impacts"])]
            for item in toc_example["objectives"]
        ],
        *[
            [f"impacts_{item['id']}", len(item["evidences"])]
            for item in toc_example["impacts"]
        ],
    ]
}
weighting_map
# %%

target_indexes = [
    *[
        nodes_id_map[f"actions_{v}"]
        for d in toc_example["inputs"]
        for v in d["actions"]
    ],
    *[
        nodes_id_map[f"outputs_{v}"]
        for d in toc_example["actions"]
        for v in d["outputs"]
    ],
    *[
        nodes_id_map[f"objectives_{v}"]
        for d in toc_example["outputs"]
        for v in d["objectives"]
    ],
    *[
        nodes_id_map[f"impacts_{v}"]
        for d in toc_example["objectives"]
        for v in d["impacts"]
    ],
]

target_ids = [
    *[f"actions_{v}" for d in toc_example["inputs"] for v in d["actions"]],
    *[f"outputs_{v}" for d in toc_example["actions"] for v in d["outputs"]],
    *[f"objectives_{v}" for d in toc_example["outputs"] for v in d["objectives"]],
    *[f"impacts_{v}" for d in toc_example["objectives"] for v in d["impacts"]],
]
source_indexes = [
    *[
        nodes_id_map[f"inputs_{d['id']}"]
        for d in toc_example["inputs"]
        for v in d["actions"]
    ],
    *[
        nodes_id_map[f"actions_{d['id']}"]
        for d in toc_example["actions"]
        for v in d["outputs"]
    ],
    *[
        nodes_id_map[f"outputs_{d['id']}"]
        for d in toc_example["outputs"]
        for v in d["objectives"]
    ],
    *[
        nodes_id_map[f"objectives_{d['id']}"]
        for d in toc_example["objectives"]
        for v in d["impacts"]
    ],
]
target_ids, target_indexes, source_indexes
# %%
node_ids = [i for i, n in enumerate(node_names)]
# %%

weightings = [weighting_map[k] for k in target_ids]
weightings
# %%


link = dict(source=source_indexes, target=target_indexes, value=weightings)
data = go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=node_names,
        color=node_colors,
    ),
    link=link,
)

fig = go.Figure(data)

fig.show()

# %%

G = nx.path_graph(20)  # An example graph
G

# %%
G = nx.DiGraph()
G.add_edges_from(zip(source_indexes, target_indexes))
G.add_nodes_from(node_ids, name=node_names)
options = {
    "font_size": 36,
    "node_size": 3000,
    "node_color": "white",
    "edgecolors": "black",
    "linewidths": 5,
    "width": 5,
}
pos = {i: node_positions[i] for i in range(len(node_positions))}
nx.draw(G, pos, **options)
# ax = plt.gca()
# ax.margins(0.20)
# plt.axis("off")
# plt.show()


# %%
pos
# %%


fig, ax = plt.subplots(figsize=(40, 20))

ax.set_xlim(0, len(nodes))
ax.set_ylim(0, 2)
ax.set_aspect("equal")

scale = 1
node_width = scale * 0.5
node_height = scale * 0.2
fontsize = 10

for node in G.nodes:
    position = [scale * v for v in pos[node]]
    position_text = [scale * (v + 0.07) for v in pos[node]]
    color = node_colors[node]
    rect = mpatches.Rectangle(position, node_width, node_height, color=color)
    ax.add_artist(rect)
    txt = ax.annotate(node_names[node], position_text, fontsize=fontsize)
    txt.set_clip_path(rect)


for edge in G.edges:
    # print(edge)
    ax.plot(
        [pos[edge[0]][0] + node_width, pos[edge[1]][0]],
        [pos[edge[0]][1] + 0.1, pos[edge[1]][1] + 0.1],
        "k-",
        lw=1,
    )
ax.set_axis_off()
plt.show()
#
# %%
