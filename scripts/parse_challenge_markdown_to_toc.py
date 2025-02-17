# %%
"""
This file is an example of parsing a markdown file into a
theory of change data structure that can be plotted.

"""

import yaml
import markdown.blockparser
import json
import networkx as nx
import re
import markdown
from markdown.preprocessors import build_preprocessors
from markdown.blockprocessors import build_block_parser
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches

# %%

markdown_example = """# Green RSE

The environmental impact of RSEs through their work is a growing concern. RSEs need to consider the environmental impact of their work and adopt sustainable practices where possible.

## Evidence of the problem

 - [UK Gov Office for Science: Large-scale computing: the case for greater UK coordination](https://assets.publishing.service.gov.uk/media/654a4025e2e16a000d42aaef/UK_Computing_report_-_Final_20.09.21.pdf)
 - [Some other evidence link](https://example.com)

## Impact Targets

### Reduce the environmental impact of RSEs through their work

This impact target will be achieved by creating a set of best practices for RSEs to follow in order to reduce their environmental impact. This will be achieved by creating a Green RSE SIG.

```yaml
id: 1
```

### Raise awareness of the environmental impact of RSEs and the importance of adopting sustainable practices

```yaml
id: 2
```

## Objectives

### Develop a set of best practices for RSEs to reduce their environmental impact

This objective will be achieved by creating a set of best practices for RSEs to follow in order to reduce their environmental impact. This will be achieved by creating a Green RSE SIG.

```yaml
id: 1
Impact targets: [1]
```

### Encourage green rse champions within RSE groups to promote sustainable practices

```yaml
id: 2
Impact targets: [1, 2]
```

## Actions

### Create a Green RSE SIG

This action will be achieved by creating a Green RSE SIG.
Some more text

```yaml
id: 1
```

#### Outputs

- An SIG dedicated to the green RSE initiative `objectives: 1`
- A person to lead the Green RSE SIG `objectives: [1,2]`

## Current Active Projects and Initiatives

- [green algorithms](https://www.green-algorithms.org/)
- [Green SIG slack](https://ukrse.slack.com/archives/C07UXQEE014)

## Past work towards overcoming the challenge

## Resources

- [Alan Turing - Community Stakeholder Map](https://cassgvp.kumu.io/alan-turing-institute-environment-and-sustainability)
- [Website Carbon Calculator](https://www.websitecarbon.com)
- [green algorithms](https://www.green-algorithms.org/)


"""


markdown_example_short = """# Green RSE

## Impact Targets

### Reduce the environmental impact of RSEs through their work

This impact target will be achieved by creating a set of best practices for RSEs to follow in order to reduce their environmental impact. This will be achieved by creating a Green RSE SIG.
"""

# %%


def parse_markdown(markdown_text: str):
    md = markdown.Markdown()
    preprocessors = build_preprocessors(md)
    parser = build_block_parser(md)
    lines = markdown_text.split("\n")
    for prep in preprocessors:
        lines = prep.run(lines)

        # Parse the high-level elements.
    root = parser.parseDocument(lines)
    return root


# result = parse_markdown(markdown_example)


def parsed_markdown_to_page_data(parsed_markdown):
    active_heading = None
    # page_heading = None
    active_sub_heading = None
    active_sub_sub_heading = None
    # in_table = False
    # table_headings = []
    page_data = {}

    # class TableData:
    #     def __init__(self, headings, data):
    #         self.headings = headings
    #         self.data = data

    #     def __repr__(self):
    #         return f"TableData({self.headings}, {self.data})"

    #     def __str__(self):
    #         return f"TableData({self.headings}, {self.data})"

    #     def __iter__(self):
    #         return iter(self.data)

    #     def __getitem__(self, key):
    #         return self.data[key]

    # TODO: Can we parse yaml code blocks?
    for el in parsed_markdown.iter():
        if el.tag == "h1":
            # page_heading = el.text
            active_heading = "root"
            page_data[active_heading] = []
        if el.tag == "h2":
            active_heading = el.text
            page_data[active_heading] = []
            active_sub_heading = None  # Clear as started new section
            active_sub_sub_heading = None  # Clear as started new section
        if el.tag == "h3":
            active_sub_heading = el.text
            page_data[active_heading] = page_data[active_heading] or {}
            page_data[active_heading][active_sub_heading] = {
                "title": active_sub_heading,
            }
            active_sub_sub_heading = None  # Clear as started new section
        if el.tag == "h4":
            # TODO: Handle nested sub-sub headings
            active_sub_sub_heading = el.text
            page_data[active_heading][active_sub_heading][active_sub_sub_heading] = {
                "content": {}
            }
        if el.tag == "p" or el.tag == "li":
            if not el.text:
                continue
            # NOTE: No longer parsing tables
            # elif el.text[0:2] == "| ":
            #     table_lines = el.text.split("\n")
            #     table_headings = [
            #         heading.strip() for heading in table_lines[0].split("|")[1:-1]
            #     ]
            #     table_content = [
            #         [cell.strip() for cell in row.split("|")[1:-1]]
            #         for row in table_lines[2:]
            #     ]
            #     page_data[active_heading].append(TableData(table_headings, table_content))
            elif el.text[0:7] == "```yaml":
                yaml_content = yaml.safe_load(el.text[8:-4])
                if active_sub_heading and active_sub_sub_heading:
                    page_data[active_heading][active_sub_heading][
                        active_sub_sub_heading
                    ] |= yaml_content
                elif active_sub_heading:
                    page_data[active_heading][active_sub_heading] |= yaml_content
                else:
                    raise ValueError("YAML block found outside of sub-heading")
            else:
                if active_sub_heading and active_sub_sub_heading:
                    page_data[active_heading][active_sub_heading][
                        active_sub_sub_heading
                    ]["content"] = (
                        page_data[active_heading][active_sub_heading][
                            active_sub_sub_heading
                        ]["content"]
                        or []
                    )
                    page_data[active_heading][active_sub_heading][
                        active_sub_sub_heading
                    ]["content"].append(el.text)
                elif active_sub_heading:
                    page_data[active_heading][active_sub_heading]["content"] = (
                        page_data[active_heading][active_sub_heading].get(
                            "content", None
                        )
                        or []
                    )
                    page_data[active_heading][active_sub_heading]["content"].append(
                        el.text
                    )
                else:
                    page_data[active_heading].append(el.text)
    return page_data


# %%
# page_data = parsed_markdown_to_page_data(parse_markdown(markdown_example))
# json.dumps(page_data)
# %%


def get_targets_from_page_data(page_data):
    targets_data = page_data.get("Impact Targets", [])
    targets = []
    for i, target in enumerate(targets_data):
        target_heading = target.split("\n")[0]
        target_description = "\n".join(target.split("\n")[1:-1])
        targets.append({"name": target_heading, "description": target_description})
    return targets


# targets_data = page_data.get("Impact Targets", [])
# for i, target in enumerate(targets_data):
#     print("=====", i + 1)
#     target_heading = target.split("\n")[0]
#     print(target_heading)
#     print("---------")
#     target_description = "\n".join(target.split("\n")[1:-1])
#     print(target_description)

# targets = get_targets_from_page_data(page_data)
# %%


# objectives_dat

# %%

# Try parsing to json ==============
# %%

# example_str = """Hello example `{"action": 1}` `{"objective": 2}`"""
# # get example data using regex
# example_data = [re.findall(r"`(.+?)`", example_str)]
# example_data = [json.loads(s) for s in re.findall(r"`(.+?)`", example_str)]
# example_data_merged = {k: v for d in example_data for k, v in d.items()}
# example_data_merged


def get_inline_data(s: str):
    data_elements = re.findall(r"`(.+?)`", s)
    str_without_data = re.sub(r"`(.+?)`", "", s).strip()
    data_merged = {
        k: v for d in [json.loads(s) for s in data_elements] for k, v in d.items()
    }
    return str_without_data, data_merged


# get_inline_data(example_str)
# %%
# page_data.get("Actions, Outputs and Objectives")[0][0]
# %%
# output = "A person to lead the Green RSE SIG `objectives: [1,2]`"
# # output = "A person to lead the Green RSE SIG"
# objectives_search = re.search(r"`objectives: \[(.+?)\]`", output)
# objectives_yaml = objectives_search and objectives_search.group(1).split(',') or []
# objectives = [int(o) for o in objectives_yaml]
# objectives

# %%
# output = "A person to lead the Green RSE SIG"
# output = "A person to lead the Green RSE SIG `objectives: [1,2]`"
# # objectives_search = re.search(r"(.+?) `objectives: \[(.+?)\]`", output)
# # objectives_yaml = objectives_search and objectives_search.group(1) or ""
# # objectives_yaml
# # output.replace(/`objectives: \[(.+?)\]`/g, "")
# re.sub(r"`objectives: \[(.+?)\]`", "", output)

# %%


def parse_actions(actions_data: dict):
    actions = []
    outputs_all = []
    output_i = 1  # Start at 1 to match markdown ordered list
    action_i = 1  # Start at 1 to match markdown ordered list
    for action_name, action_data in actions_data.items():
        description = "\n".join(action_data["content"])
        outputs = action_data.get("Outputs", {}).get("content", [])
        action = {
            "id": action_data["id"],
            "name": action_name,
            "description": description,
            "outputs": [i for i in range(output_i, output_i + len(outputs))],
        }
        # TODO: Handle duplicate outputs
        outputs_all += [output.strip() for output in outputs]
        output_i += len(outputs)
        action_i += 1

        actions.append(action)
    outputs_parsed = []
    for i, output in enumerate(outputs_all):
        print(output)
        output_search = re.search(r"`objectives: \[(.+?)\]`", output)
        print(output_search)
        print("Hello")
        objectives_yaml = output_search and output_search.group(1).split(",") or []
        objectives = [int(o) for o in objectives_yaml]
        title = re.sub(r"`objectives: \[(.+?)\]`", "", output)
        output_parsed = {
            "id": i + 1,
            "name": title,
            "objectives": objectives,
        }
        outputs_parsed.append(output_parsed)
    return actions, outputs_parsed


# parse_actions(page_data.get("Actions"))
# %%

# page_data["Objectives"]
# %%


# TODO: Up to here. Need to update parsing objectives
def parse_objectives(objectives_data: dict):
    objectives = []
    objective_i = 1  # Start at 1 to match markdown ordered list
    for objective_name, objective_data in objectives_data.items():
        # print(objective_data)
        description = "\n".join(
            [o for o in objective_data if "**Impact targets**" not in o]
        )
        impacts = objective_data.get("Impact targets", [])
        # impacts = [
        #     [int(oo.strip()) for oo in o.replace("**Impact targets**: ", "").split(",")]
        #     for o in objective_data
        #     if "**Impact targets**" in o
        # ]
        # impacts_flat = [i for sublist in impacts for i in sublist]
        objective = {
            "id": objective_i,
            "name": objective_name,
            "description": description,
            "impacts": impacts,
        }
        objective_i += 1

        objectives.append(objective)
    return objectives


# print(page_data.get("Objectives", {}))
# objectives_parsed = parse_objectives(page_data.get("Objectives", {}))
# objectives_parsed
# %%
# actions, outputs = (
#     parse_actions(page_data.get("Actions"))
#     if page_data.get("Actions", None)
#     else [None, None]
# )
# objectives = (
#     parse_objectives(page_data.get("Objectives", {}))
#     if page_data.get("Objectives", None)
#     else None
# )
def get_toc_data(page_data: dict, heading: str, actions, outputs, objectives):
    toc_parsed = {
        "name": heading,
        "description": page_data["root"],
        "evidence": [
            {"id": i + 1, "name": get_inline_data(item)[0], **get_inline_data(item)[1]}
            for i, item in enumerate(page_data.get("Evidence of the problem", []))
        ],
        "inputs": [
            {"id": i + 1, "name": get_inline_data(item)[0], **get_inline_data(item)[1]}
            for i, item in enumerate(page_data.get("Prerequisites", []))
        ],
        "actions": actions,
        "outputs": outputs,
        "objectives": objectives,
        "impacts": [
            {"id": i + 1, "name": get_inline_data(item)[0], **get_inline_data(item)[1]}
            for i, item in enumerate(page_data.get("Impact Targets", []))
        ],
    }  #
    return toc_parsed


# toc_parsed = get_toc_data(page_data, "Green RSE", actions, outputs, objectives)

# %%
# toc_example = {
#     "name": "Green RSE",
#     "description": "The environmental impact of RSEs through their work is a growing concern. RSEs need to consider the environmental impact of their work and adopt sustainable practices where possible.",
#     "evidence": [
#         {
#             "id": 1,
#             "name": "Example evidence",
#         },
#     ],
#     "inputs": [
#         {
#             "id": 1,
#             "name": "Green RSE Sig Lead",
#             "description": "A person to lead the Green RSE SIG",
#             "actions": [1],
#         },
#     ],
#     "actions": [
#         {"id": 1, "name": "Create a Green RSE SIG", "outputs": [1]},
#     ],
#     "outputs": [
#         {
#             "id": 1,
#             "name": "An SIG dedicated to the green RSE initiative",
#             "objectives": [1, 2],
#         },
#     ],
#     "objectives": [
#         {
#             "id": 1,
#             "name": "Develop a set of best practices for RSEs to reduce their environmental impact.",
#             "impacts": [1],
#         },
#         {
#             "id": 2,
#             "name": "Encourage green rse champions within RSE groups to promote sustainable practices.",
#             "impacts": [1],
#         },
#     ],
#     "impacts": [
#         {
#             "id": 1,
#             "name": "Reduce the environmental impact of RSEs through their work.",
#             "evidences": [1],
#         },
#     ],
# }

# %%


def create_toc_graph(toc_data):
    nodes_id_map = {
        k: i
        for i, k in enumerate(
            [
                *[f"evidence_{item['id']}" for item in toc_data["evidence"]],
                *[f"inputs_{item['id']}" for item in toc_data["inputs"]],
                *[f"actions_{item['id']}" for item in toc_data["actions"]],
                *[f"outputs_{item['id']}" for item in toc_data["outputs"]],
                *[f"objectives_{item['id']}" for item in toc_data["objectives"]],
                *[f"impacts_{item['id']}" for item in toc_data["impacts"]],
            ]
        )
    }
    nodes = [
        *[item for item in toc_data["evidence"]],
        *[item for item in toc_data["inputs"]],
        *[item for item in toc_data["actions"]],
        *[item for item in toc_data["outputs"]],
        *[item for item in toc_data["objectives"]],
        *[item for item in toc_data["impacts"]],
    ]

    node_positions = [
        *[
            [0, (i + 1) / len(toc_data["evidence"])]
            for i, item in enumerate(toc_data["evidence"])
        ],
        *[
            [1, (i + 1) / len(toc_data["inputs"])]
            for i, item in enumerate(toc_data["inputs"])
        ],
        *[
            [2, (i + 1) / len(toc_data["actions"])]
            for i, item in enumerate(toc_data["actions"])
        ],
        *[
            [3, (i + 1) / len(toc_data["outputs"])]
            for i, item in enumerate(toc_data["outputs"])
        ],
        *[
            [4, (i + 1) / len(toc_data["objectives"])]
            for i, item in enumerate(toc_data["objectives"])
        ],
        *[
            [5, (i + 1) / len(toc_data["impacts"])]
            for i, item in enumerate(toc_data["impacts"])
        ],
    ]

    node_names = [f"{node['name']}" for node in nodes]
    color_map = {
        "evidence": "blue",
        "inputs": "red",
        "actions": "green",
        "outputs": "purple",
        "objectives": "orange",
        "impacts": "yellow",
    }
    node_colors = [
        *[color_map["evidence"] for item in toc_data["evidence"]],
        *[color_map["inputs"] for item in toc_data["inputs"]],
        *[color_map["actions"] for item in toc_data["actions"]],
        *[color_map["outputs"] for item in toc_data["outputs"]],
        *[color_map["objectives"] for item in toc_data["objectives"]],
        *[color_map["impacts"] for item in toc_data["impacts"]],
    ]

    target_indexes = [
        *[
            nodes_id_map[f"actions_{v}"]
            for d in toc_data["inputs"]
            for v in d["actions"]
        ],
        *[
            nodes_id_map[f"outputs_{v}"]
            for d in toc_data["actions"]
            for v in d["outputs"]
        ],
        *[
            nodes_id_map[f"objectives_{v}"]
            for d in toc_data["outputs"]
            for v in d["objectives"]
        ],
        *[
            nodes_id_map[f"impacts_{v}"]
            for d in toc_data["objectives"]
            for v in d["impacts"]
        ],
    ]

    source_indexes = [
        *[
            nodes_id_map[f"inputs_{d['id']}"]
            for d in toc_data["inputs"]
            for v in d["actions"]
        ],
        *[
            nodes_id_map[f"actions_{d['id']}"]
            for d in toc_data["actions"]
            for v in d["outputs"]
        ],
        *[
            nodes_id_map[f"outputs_{d['id']}"]
            for d in toc_data["outputs"]
            for v in d["objectives"]
        ],
        *[
            nodes_id_map[f"objectives_{d['id']}"]
            for d in toc_data["objectives"]
            for v in d["impacts"]
        ],
    ]
    node_ids = [i for i, n in enumerate(node_names)]

    G = nx.DiGraph()
    G.add_edges_from(zip(source_indexes, target_indexes))
    G.add_nodes_from(node_ids, name=node_names)
    pos = {i: node_positions[i] for i in range(len(node_positions))}
    return G, pos, node_colors, node_names


# create_toc_graph(toc_parsed)
# toc_parsed
# %%


def plot_toc_graph(G, pos, node_colors, node_names, ax=None, fig=None):
    if fig is None:
        fig, ax = plt.subplots()
    assert ax is not None
    ax.set_aspect("equal")

    scale = 1
    node_width = scale * 0.7
    node_height = scale * 0.3
    fontsize = 5
    text_padding = 0.05
    ax.set_xlim(0, 6 * scale)
    ax.set_ylim(0, 2 * scale)

    for node in G.nodes:
        print(pos[node])
        position = [scale * v for v in pos[node]]
        position_text = [scale * (v) for v in pos[node]]
        position_text[0] = position_text[0] + text_padding
        position_text[1] = position_text[1] + node_height - text_padding
        color = node_colors[node]
        rect = mpatches.Rectangle(position, node_width, node_height, color=color)
        ax.add_artist(rect)
        txt = ax.annotate(
            node_names[node],
            position_text,
            fontsize=fontsize,
            wrap=True,
            verticalalignment="top",
        )
        txt._get_wrap_line_width = (
            lambda: ((node_width * 2) - text_padding * 2) * fig.dpi
        )
        txt.set_clip_path(rect)

    for edge in G.edges:
        ax.plot(
            [pos[edge[0]][0] * scale + node_width, pos[edge[1]][0] * scale],
            [pos[edge[0]][1] * scale + 0.1, pos[edge[1]][1] * scale + 0.1],
            "k-",
            lw=1,
        )
    ax.set_axis_off()

    (plt.plot([], [], color="blue", label="evidence"),)
    (plt.plot([], [], color="red", label="inputs"),)
    (plt.plot([], [], color="green", label="actions"),)
    (plt.plot([], [], color="purple", label="outputs"),)
    (plt.plot([], [], color="orange", label="objectives"),)
    (plt.plot([], [], color="yellow", label="impacts"),)
    ax.legend()


fig, ax = plt.subplots(figsize=(20, 5))

# plot_toc_graph(*create_toc_graph(toc_parsed), ax=ax, fig=fig)
# %%

# out = [
#     *[
#         {
#             "model": "rse_challenges_app.evidence",
#             "pk": evidence["id"],
#             "fields": {
#                 "name": evidence["name"],
#                 "description": evidence.get("description", ""),
#             },
#         }
#         for i, evidence in enumerate(toc_parsed["evidence"])
#     ],
#     *[
#         {
#             "model": "rse_challenges_app.input",
#             "pk": input["id"],
#             "fields": {
#                 "name": input["name"],
#                 "description": input.get("description", ""),
#                 "actions": input.get("actions", []),
#             },
#         }
#         for i, input in enumerate(toc_parsed["inputs"])
#     ],
#     *[
#         {
#             "model": "rse_challenges_app.action",
#             "pk": action["id"],
#             "fields": {
#                 "name": action["name"],
#                 "description": action.get("description", ""),
#                 "outputs": action.get("outputs", []),
#             },
#         }
#         for i, action in enumerate(toc_parsed["actions"])
#     ],
#     *[
#         {
#             "model": "rse_challenges_app.output",
#             "pk": output["id"],
#             "fields": {
#                 "name": output["name"],
#                 "description": output.get("description", ""),
#                 "objectives": output.get("objectives", []),
#             },
#         }
#         for i, output in enumerate(toc_parsed["outputs"])
#     ],
#     *[
#         {
#             "model": "rse_challenges_app.objective",
#             "pk": objective["id"],
#             "fields": {
#                 "name": objective["name"],
#                 "description": objective.get("description", ""),
#                 "impacts": objective.get("impacts", []),
#             },
#         }
#         for i, objective in enumerate(toc_parsed["objectives"])
#     ],
#     *[
#         {
#             "model": "rse_challenges_app.impact",
#             "pk": impact["id"],
#             "fields": {
#                 "name": impact["name"],
#                 "description": impact.get("description", ""),
#                 "evidences": impact.get("evidences", []),
#             },
#         }
#         for i, impact in enumerate(toc_parsed["impacts"])
#     ],
#     {
#         "model": "rse_challenges_app.challenge",
#         "pk": 1,
#         "fields": {
#             "name": toc_parsed["name"],
#             "description": toc_parsed["description"],
#             "created_date": "2024-11-28T21:57:06Z",
#             "last_modified_date": "2024-11-28T21:57:08Z",
#             "is_active": True,
#             "is_deleted": False,
#             "inputs": [input["id"] for input in toc_parsed["inputs"]],
#             "actions": [action["id"] for action in toc_parsed["actions"]],
#             "outputs": [output["id"] for output in toc_parsed["outputs"]],
#             "objectives": [objective["id"] for objective in toc_parsed["objectives"]],
#             "impacts": [impact["id"] for impact in toc_parsed["impacts"]],
#             "evidences": [evidence["id"] for evidence in toc_parsed["evidence"]],
#         },
#     },
# ]
# out
# %%
# with open("web-app/rse_challenges_app/fixtures/challenges.json", "w") as f:
#     json.dump(out, f, indent=2, default=str)

# %%
# Try with functions
result = parse_markdown(markdown_example)
page_data = parsed_markdown_to_page_data(result)
# targets = get_targets_from_page_data(page_data)
actions, outputs = parse_actions(page_data.get("Actions"))
objectives = parse_objectives(page_data.get("Objectives"))
# toc_data = get_toc_data(page_data, "Green RSE")
toc_parsed = get_toc_data(page_data, "Green RSE", actions, outputs, objectives)

fig, ax = plt.subplots(figsize=(20, 5))

plot_toc_graph(*create_toc_graph(toc_parsed), ax=ax, fig=fig)

# %%
# Try with bigger example
markdown_loaded = None
with open("rse-community-challenges-book/rse-community-challenges/green-rse.md") as f:
    markdown_loaded = f.read()

result = parse_markdown(markdown_loaded)
page_data = parsed_markdown_to_page_data(result)
targets = get_targets_from_page_data(page_data)
actions, outputs = parse_actions(page_data.get("Actions"))
objectives = parse_objectives(page_data.get("Objectives"))
toc_data = get_toc_data(page_data, "Green RSE", actions, outputs, objectives)

fig, ax = plt.subplots(figsize=(20, 5))

plot_toc_graph(*create_toc_graph(toc_data), ax=ax, fig=fig)
# %%
# %%
# Try with bigger example 2
markdown_loaded = None
with open("rse-community-challenges-book/rse-community-challenges/careers.md") as f:
    markdown_loaded = f.read()

result = parse_markdown(markdown_loaded)
page_data = parsed_markdown_to_page_data(result)
targets = get_targets_from_page_data(page_data)
actions, outputs = parse_actions(page_data.get("Actions"))
objectives = parse_objectives(page_data.get("Objectives"))
toc_data = get_toc_data(page_data, "Green RSE", actions, outputs, objectives)

fig, ax = plt.subplots(figsize=(20, 5))

plot_toc_graph(*create_toc_graph(toc_data), ax=ax, fig=fig)
# %%
actions, outputs = parse_actions(page_data.get("Actions"))
outputs
# %%
output_search = re.search(
    r"`objectives: \[(.+?)\]`",
    "Improve availability of career paths to RSEs `objectives: [1]`",
)
output_search.group(1)
