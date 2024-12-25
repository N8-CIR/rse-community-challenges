# %%
import markdown.blockparser
import json
import os
import markdown
from markdown.preprocessors import build_preprocessors
from markdown.blockprocessors import build_block_parser
# %%

markdown_example = """# Green RSE

The environmental impact of RSEs through their work is a growing concern. RSEs need to consider the environmental impact of their work and adopt sustainable practices where possible.

## Evidence of the problem

 - [UK Gov Office for Science: Large-scale computing: the case for greater UK coordination](https://assets.publishing.service.gov.uk/media/654a4025e2e16a000d42aaef/UK_Computing_report_-_Final_20.09.21.pdf)
 - [Some other evidence link](https://example.com)

## Objectives and Milestones for overcoming the challenge

### Impact Targets

1. Reduce the environmental impact of RSEs through their work.
2. Raise awareness of the environmental impact of RSEs and the importance of adopting sustainable practices.

### Objectives

1. Develop a set of best practices for RSEs to reduce their environmental impact.
This objective will be achieved by creating a set of best practices for RSEs to follow in order to reduce their environmental impact. This will be achieved by creating a Green RSE SIG.
**Impact target**: 1

2. Encourage green rse champions within RSE groups to promote sustainable practices.
**Impact target**: 1
**Impact target**: 2

### Actions, Outputs and Objectives

#### 1. Create a Green RSE SIG

This action will be achieved by creating a Green RSE SIG.
Some more text

**Outputs**:

- An SIG dedicated to the green RSE initiative
  **Objective**: 1
- A person to lead the Green RSE SIG
  **Objective**: 1
  **Objective**: 2

#### 2. Another one!

This action will be achieved by creating a Green RSE SIG.
Some more text

**Outputs**:

- An SIG dedicated to the green RSE initiative
  **Objective**: 1
- A person to lead the Green RSE SIG
  **Objective**: 1, 2


### Prerequisites

1. Green RSE Sig Lead  `{"action": 1}`

## Current Active Projects and Initiatives

- [green algorithms](https://www.green-algorithms.org/)
- [Green SIG slack](https://ukrse.slack.com/archives/C07UXQEE014)

## Past work towards overcoming the challenge

## Resources

- [Alan Turing - Community Stakeholder Map](https://cassgvp.kumu.io/alan-turing-institute-environment-and-sustainability)
- [Website Carbon Calculator](https://www.websitecarbon.com)
- [green algorithms](https://www.green-algorithms.org/)


"""


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


result = parse_markdown(markdown_example)

active_heading = None
page_heading = None
active_sub_heading = None
in_table = False
table_headings = []
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


for el in result.iter():
    # print(el.tag, el.text, el.tail)
    if el.tag == "h1":
        page_heading = el.text
        active_heading = "root"
        page_data[active_heading] = []
    if el.tag == "h2" or el.tag == "h3":
        active_heading = el.text
        page_data[active_heading] = []
        active_sub_heading = None
    if el.tag == "h4":
        active_sub_heading = el.text
        page_data[active_heading] = page_data[active_heading] or {}
        page_data[active_heading][active_sub_heading] = []
    if el.tag == "p" or el.tag == "li":
        if not el.text:
            continue
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
        else:
            if active_sub_heading:
                page_data[active_heading][active_sub_heading].append(el.text)
            else:
                page_data[active_heading].append(el.text)

page_data

# %%

targets_data = page_data.get("Impact Targets", [])
for i, target in enumerate(targets_data):
    print("=====", i+1)
    target_heading = target.split('\n')[0]
    print(target_heading)
    print("---------")
    target_description = "\n".join(target.split('\n')[1:-1])
    print(target_description)


# %%


objectives_data = page_data.get("Objectives")
for objective in objectives_data:
    print("=====")
    objective_heading = objective.split('\n')[0]
    print(objective_heading)
    print("---------")
    objective_description = "\n".join([line for line in objective.split('\n')[1:-1] if "**Impact target**" not in line])
    print(objective_description)
    target_impacts = [int(s) for line in objective.split('\n')[1:] for s in line.replace("**Impact target**: ", "") if "**Impact target**" in line]
    print(target_impacts)

# %%


actions_data = page_data.get("Actions, Outputs and Objectives", [])
actions_data
# %%

for action in actions_data:
    print("=====")
    action_heading = action.split('\n')[0]
    print(action_heading)
    print("---------")
    action_description = "\n".join([line for line in action.split('\n')[1:] if "**Output**:" not in line and "**Objective**:" not in line ])
    print(action_description)
    outputs = [s for line in action.split('\n')[1:] for s in line.replace("**Output**: ", "") if "**Output**:" in line]
    print(outputs)



# %%

# Try parsing to json ==============
# %%

example_str = """Hello example `{"action": 1}` `{"objective": 2}`"""
# get example data using regex
import re
import json
example_data = [re.findall(r"`(.+?)`", example_str)]
example_data = [json.loads(s) for s in re.findall(r"`(.+?)`", example_str)]
example_data_merged = {k: v for d in example_data for k, v in d.items()}
example_data_merged

def get_inline_data(s: str):
    data_elements = re.findall(r"`(.+?)`", s)
    str_without_data = re.sub(r"`(.+?)`", "", s).strip()
    data_merged = {k: v for d in [json.loads(s) for s in data_elements] for k, v in d.items()}
    return str_without_data, data_merged

get_inline_data(example_str)
# %%
page_data.get("Actions, Outputs and Objectives")[0][0]
# %%

toc_parsed = {
    "name": page_heading,
    "description": page_data["root"],
    "evidence": [
        {"id": i+1, "name": get_inline_data(item)[0], **get_inline_data(item)[1]}
        for i, item in enumerate(page_data.get("Evidence of the problem", []))
    ],
    "inputs": [
        {"id": i+1, "name": get_inline_data(item)[0], **get_inline_data(item)[1]}
        for i, item in enumerate(page_data.get("Prerequisites", []))
    ],
    "actions": [
        {"id": i+1, "name": get_inline_data(item)[0], **get_inline_data(item)[1]}
        for i, item in page_data.get("Actions, Outputs and Objectives", None)
    ] if page_data.get("Actions, Outputs and Objectives", None) else []
}
toc_parsed

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
