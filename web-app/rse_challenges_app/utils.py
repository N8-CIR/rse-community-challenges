import markdown
import matplotlib.pyplot as plt
from io import StringIO
import yaml
import networkx as nx
import markdown.blockparser
import json
import re
import markdown
from markdown.preprocessors import build_preprocessors
from markdown.blockprocessors import build_block_parser
import matplotlib.patches as mpatches

from .models import Challenge


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


def parsed_markdown_to_page_data(parsed_markdown):
    active_heading = None
    active_sub_heading = None
    active_sub_sub_heading = None
    page_data = {}

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


def get_targets_from_page_data(page_data):
    targets_data = page_data.get("Impact Targets", [])
    targets = []
    for i, target in enumerate(targets_data):
        target_heading = target.split("\n")[0]
        target_description = "\n".join(target.split("\n")[1:-1])
        targets.append({"name": target_heading, "description": target_description})
    return targets


def get_inline_data(s: str):
    data_elements = re.findall(r"`(.+?)`", s)
    str_without_data = re.sub(r"`(.+?)`", "", s).strip()
    data_merged = {
        k: v for d in [json.loads(s) for s in data_elements] for k, v in d.items()
    }
    return str_without_data, data_merged


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
        output_search = re.search(r"`objectives: \[(.+?)\]`", output)
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


def parse_objectives(objectives_data: dict):
    objectives = []
    objective_i = 1  # Start at 1 to match markdown ordered list
    for objective_name, objective_data in objectives_data.items():
        # print(objective_data)
        description = "\n".join(
            [o for o in objective_data if "**Impact targets**" not in o]
        )
        impacts = objective_data.get("Impact targets", [])
        objective = {
            "id": objective_i,
            "name": objective_name,
            "description": description,
            "impacts": impacts,
        }
        objective_i += 1

        objectives.append(objective)
    return objectives


def create_toc_graph(challenge: Challenge):
    inputs = challenge.inputs.all()
    actions = challenge.actions.all()
    outputs = challenge.outputs.all()
    objectives = challenge.objectives.all()
    impacts = challenge.impacts.all()

    nodes_id_map = {
        k: i
        for i, k in enumerate(
            [
                # *[f"evidence_{item['id']}" for item in challenge.evidence],
                *[f"inputs_{item.id}" for item in inputs],
                *[f"actions_{item.id}" for item in actions],
                *[f"outputs_{item.id}" for item in outputs],
                *[f"objectives_{item.id}" for item in objectives],
                *[f"impacts_{item.id}" for item in impacts],
            ]
        )
    }
    nodes = [
        # *[item for item in evidence], # Not currently implemented
        *[item for item in inputs],
        *[item for item in actions],
        *[item for item in outputs],
        *[item for item in objectives],
        *[item for item in impacts],
    ]

    node_positions = [
        *[[1, (i + 1) / len(inputs)] for i, item in enumerate(inputs)],
        *[[2, (i + 1) / len(actions)] for i, item in enumerate(actions)],
        *[[3, (i + 1) / len(outputs)] for i, item in enumerate(outputs)],
        *[[4, (i + 1) / len(objectives)] for i, item in enumerate(objectives)],
        *[[5, (i + 1) / len(impacts)] for i, item in enumerate(impacts)],
    ]

    node_names = [f"{node.name}" for node in nodes]
    color_map = {
        "evidence": "blue",
        "inputs": "red",
        "actions": "green",
        "outputs": "purple",
        "objectives": "orange",
        "impacts": "yellow",
    }
    node_colors = [
        # *[color_map["evidence"] for item in evidence],
        *[color_map["inputs"] for _ in inputs],
        *[color_map["actions"] for _ in actions],
        *[color_map["outputs"] for _ in outputs],
        *[color_map["objectives"] for _ in objectives],
        *[color_map["impacts"] for _ in impacts],
    ]
    target_indexes = [
        *[nodes_id_map[f"actions_{v.id}"] for d in inputs for v in d.actions.all()],
        *[nodes_id_map[f"outputs_{v.id}"] for d in actions for v in d.outputs.all()],
        *[
            nodes_id_map[f"objectives_{v.id}"]
            for d in outputs
            for v in d.objectives.all()
        ],
        *[nodes_id_map[f"impacts_{v.id}"] for d in objectives for v in d.impacts.all()],
    ]

    source_indexes = [
        *[nodes_id_map[f"inputs_{d.id}"] for d in inputs for v in d.actions.all()],
        *[nodes_id_map[f"actions_{d.id}"] for d in actions for v in d.outputs.all()],
        *[nodes_id_map[f"outputs_{d.id}"] for d in outputs for v in d.objectives.all()],
        *[
            nodes_id_map[f"objectives_{d.id}"]
            for d in objectives
            for v in d.impacts.all()
        ],
    ]
    node_ids = [i for i, n in enumerate(node_names)]

    G = nx.DiGraph()
    G.add_edges_from(zip(source_indexes, target_indexes))
    G.add_nodes_from(node_ids, name=node_names)
    pos = {i: node_positions[i] for i in range(len(node_positions))}
    return G, pos, node_colors, node_names


def plot_toc_graph(
    G, pos: tuple[float, float], node_colors, node_names, ax=None, fig=None
):
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
        position: tuple[float, float] = [scale * v for v in pos[node]]  # type: ignore
        position_text: tuple[float, float] = [scale * (v) for v in pos[node]]  # type: ignore
        position_text[0] = position_text[0] + text_padding  # type: ignore
        position_text[1] = position_text[1] + node_height - text_padding  # type: ignore
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
        )  # type: ignore
        txt.set_clip_path(rect)

    for edge in G.edges:
        ax.plot(
            [pos[edge[0]][0] * scale + node_width, pos[edge[1]][0] * scale],
            [pos[edge[0]][1] * scale + 0.1, pos[edge[1]][1] * scale + 0.1],
            "k-",
            lw=1,
        )
    ax.set_axis_off()

    plt.plot([], [], color="blue", label="evidence")
    plt.plot([], [], color="red", label="inputs")
    plt.plot([], [], color="green", label="actions")
    plt.plot([], [], color="purple", label="outputs")
    plt.plot([], [], color="orange", label="objectives")
    plt.plot([], [], color="yellow", label="impacts")
    ax.legend()


def get_toc_plot_html(challenge: Challenge):
    fig, ax = plt.subplots(figsize=(20, 5))
    plot_toc_graph(*create_toc_graph(challenge), ax=ax, fig=fig)  # type: ignore
    imgdata = StringIO()
    fig.savefig(imgdata, format="svg")
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data


def create_challenge_context(challenge: Challenge):
    return {
        **challenge.__dict__,
        "likes": 999,
        "name": challenge.name,
        "description": markdown.markdown(challenge.description),
        "created_date": challenge.created_date,
        "last_modified_date": challenge.last_modified_date,
        "is_active": challenge.is_active,
        "is_deleted": challenge.is_deleted,
        "evidence_text": "\n".join(
            markdown.markdown(e.name) for e in challenge.evidences.all()
        ),
        "impacts_text": "\n".join(
            markdown.markdown(e.name) for e in challenge.impacts.all()
        ),
        "objectives_text": "\n".join(
            markdown.markdown(e.name) for e in challenge.objectives.all()
        ),
        "actions_and_outputs_text": "\n".join(
            markdown.markdown(e.name) for e in challenge.actions.all()
        ),
        "toc": get_toc_plot_html(challenge),
        # "active_projects_text": markdown.markdown(challenge.active_projects_text),
        # "past_work_text": markdown.markdown(challenge.past_work_text),
    }
