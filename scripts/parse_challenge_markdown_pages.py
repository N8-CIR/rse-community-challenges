# %%
"""
# Parse Challenge Markdown Pages

This file parses the markdown files into the DJANGO database fixtures.

# Setup

To get the example fixture from the database run
`python manage.py dumpdata rse_challenges_app --indent 4 > challenge_b.json`

To push the new fixture to the database run

`python manage.py loaddata rse_challenges_app/fixtures/challenges.json`

## Indexing

Note that indexing is a bit fidly as we need to keep track of the global index for each object type.

`

"""

# %%

import markdown
import os
import yaml
import markdown.blockparser
import json
import re
from pprint import pprint
import markdown
from markdown.preprocessors import build_preprocessors
from markdown.blockprocessors import build_block_parser

# We need to keep track of global Id so each item has a unique ID
OUTPUTS_ID = 0
OBJECTIVES_ID = 0
IMPACTS_ID = 0


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
            page_data[active_heading] = None # This is set below now
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
                    page_data[active_heading] = page_data[active_heading] or []
                    page_data[active_heading].append(el.text)
    return page_data


def get_targets_from_page_data(page_data):
    targets_data = page_data.get("Impact Targets", []) or []
    targets = []
    for i, target in enumerate(targets_data):
        target_heading = target.split("\n")[0]
        target_description = "\n".join(target.split("\n")[1:-1])
        targets.append({"name": target_heading, "description": target_description})
        global IMPACTS_ID
        IMPACTS_ID += 1
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
            "outputs": [OUTPUTS_ID + i for i in range(output_i, output_i + len(outputs))],
        }
        # TODO: Handle duplicate outputs
        outputs_all += [output.strip() for output in outputs]
        output_i += len(outputs)
        action_i += 1

        actions.append(action)
    outputs_parsed = []
    for i, output in enumerate(outputs_all):
        global OUTPUTS_ID
        output_search = re.search(r"`objectives: \[(.+?)\]`", output)
        objectives_yaml = output_search and output_search.group(1).split(",") or []
        objectives = [OBJECTIVES_ID + int(o) for o in objectives_yaml]
        title = re.sub(r"`objectives: \[(.+?)\]`", "", output)
        output_parsed = {
            # "id": i + 1,
            "id": OUTPUTS_ID,
            "name": title,
            "objectives": objectives,
        }
        OUTPUTS_ID += 1

        outputs_parsed.append(output_parsed)
    return actions, outputs_parsed


def parse_objectives(objectives_data: dict):
    objectives = []
    objective_i = 1  # Start at 1 to match markdown ordered list
    for objective_name, objective_data in objectives_data.items():
        description = "\n".join(
            [o for o in objective_data.get('content', []) if "**Impact targets**" not in o]
        )
        impacts = objective_data.get("Impact targets", [])
        objective = {
            "id": objective_i,
            "name": objective_name,
            "description": description,
            "impacts": [IMPACTS_ID + int(i) for i in impacts],
        }
        objective_i += 1

        objectives.append(objective)
        global OBJECTIVES_ID
        OBJECTIVES_ID += 1
    return objectives


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


# %%

# Index counters ensure that we create unique indexes for each object type
# but can still reference them in challenge object
index_counters = {
    "challenge": 1,
    "actions": 1,
    "inputs": 1,
    "objective": 1,
    "outputs": 1,
    "impacts": 1,
    "evidences": 1,
    "resources": 1,
}


def markdown_to_fixture(markdown_text: str, name: str, pk: int) -> list[dict]:
    result = parse_markdown(markdown_text)
    page_data = parsed_markdown_to_page_data(result)
    # NOTE: Order of these is currently important so as to match ids
    actions, outputs = parse_actions(page_data.get("Actions", {}) or {})
    objectives = parse_objectives(page_data.get("Objectives", {}) or {})
    targets = get_targets_from_page_data(page_data)
    evidences = page_data.get("Evidence of the problem", []) or []

    impacts_ids = [
        i
        for i in range(
            index_counters["impacts"], index_counters["impacts"] + len(targets)
        )
    ]
    index_counters["impacts"] += len(targets)
    actions_ids = [
        i
        for i in range(
            index_counters["actions"], index_counters["actions"] + len(actions)
        )
    ]
    index_counters["actions"] += len(actions)
    outputs_ids = [
        i
        for i in range(
            index_counters["outputs"], index_counters["outputs"] + len(outputs)
        )
    ]
    index_counters["outputs"] += len(outputs)
    objectives_ids = [
        i
        for i in range(
            index_counters["objective"], index_counters["objective"] + len(objectives)
        )
    ]
    index_counters["objective"] += len(objectives)
    evidences_ids = [
        i
        for i in range(
            index_counters["evidences"], index_counters["evidences"] + len(evidences)
        )
    ]
    index_counters["evidences"] += len(evidences)

    impacts_fixtures = [
        {
            "model": "rse_challenges_app.impact",
            "pk": i,
            "fields": {
                "name": target.get("name", ""),
                "description": target.get("description", ""),
                "evidences": [],  # TODO: Implement evidences
            },
        }
        for i, target in zip(impacts_ids, targets)
    ]
    actions_fixtures = [
        {
            "model": "rse_challenges_app.action",
            "pk": i,
            "fields": {
                "name": action["name"],
                "description": action.get("description", ""),
                "outputs": action["outputs"],
                "status": "TODO",
            },
        }
        for i, action in zip(actions_ids, actions)
    ]
    outputs_fixtures = [
        {
            "model": "rse_challenges_app.output",
            "pk": i,
            "fields": {
                "name": output["name"],
                "description": output.get("description", ""),
                "objectives": output["objectives"],
            },
        }
        for i, output in zip(outputs_ids, outputs)
    ]
    objectives_fixtures = [
        {
            "model": "rse_challenges_app.objective",
            "pk": i,
            "fields": {
                "name": objective["name"],
                "description": objective.get("description", ""),
                "impacts": objective["impacts"],
            },
        }
        for i, objective in zip(objectives_ids, objectives)
    ]
    evidences_fixtures = [
        {
            "model": "rse_challenges_app.evidence",
            "pk": i,
            "fields": {
                "name": f"Evidence {i}",
                "description": evidence,
            },
        }
        for i, evidence in zip(evidences_ids, evidences)
    ]
    description_text = "\n".join(page_data.get("root", []))

    challenge_fixture = {
        "model": "rse_challenges_app.challenge",
        "pk": pk,
        "fields": {
            # Change this to match new challenge shape and other object types
            "name": name,
            "description": description_text,
            "created_date": "2024-11-28T21:57:06Z",
            "last_modified_date": "2024-11-28T21:57:08Z",
            "is_active": True,
            "is_deleted": False,
            "inputs": [],
            "actions": actions_ids,
            "outputs": outputs_ids,
            "objectives": objectives_ids,
            "impacts": impacts_ids,
            "evidences": evidences_ids,
            "resources": [],
            # "active_projects_text": join_lines_with_break(
            #     page_data.get("Current Active Projects and Initiatives", [""])
            # ),
            # "past_work_text": join_lines_with_break(
            #     page_data.get("Past work towards overcoming the challenge", [""])
            # ),
        },
    }
    fixtures = [
        *impacts_fixtures,
        *actions_fixtures,
        *outputs_fixtures,
        *objectives_fixtures,
        *evidences_fixtures,
        challenge_fixture,
    ]
    return fixtures


# Apply to
markdown_files = reversed(sorted([
    f
    for f in os.listdir("rse-community-challenges-book/rse-community-challenges")
    if ".md" in f
]))
page_fixtures = []
for i, file in enumerate(markdown_files):
    # if file != "green-rse.md":
    #     continue
    with open(f"rse-community-challenges-book/rse-community-challenges/{file}") as f:
        markdown_text = f.read()
        try:
            page_fixtures += [*markdown_to_fixture(markdown_text, file, i + 1)]
            print(f"Successfully parsed {file}")
        except Exception as e:
            print(f"Error parsing {file}: {e}")
            print(e)
            raise e

with open("web-app/rse_challenges_app/fixtures/challenges.json", "w") as f:
    json.dump(page_fixtures, f, indent=2, default=str)

# %%
