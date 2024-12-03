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

## Objectives and Milestones for overcoming the challenge

### Impact Targets

1. Reduce the environmental impact of RSEs through their work.
2. Raise awareness of the environmental impact of RSEs and the importance of adopting sustainable practices.

### Objectives

1. Develop a set of best practices for RSEs to reduce their environmental impact.
2. Encourage green rse champions within RSE groups to promote sustainable practices.

### Actions, Outputs and Objectives

| Actions                | Output                                       | Objective | Impact |
| ---------------------- | -------------------------------------------- | --------- | ------ |
| Create a Green RSE SIG | An SIG dedicated to the green RSE initiative | 1         | 1      |

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
result
# %%

first_el = next(result.iter())
first_el.tag, first_el.text, first_el.tail
# %%
[el.text for el in result.iter()]

# %%
active_heading = None
page_heading = None
in_table = False
table_headings = []
page_data = {}


class TableData:
    def __init__(self, headings, data):
        self.headings = headings
        self.data = data

    def __repr__(self):
        return f"TableData({self.headings}, {self.data})"


for el in result.iter():
    # print(el.tag, el.text, el.tail)
    if el.tag == "h1":
        page_heading = el.text
        active_heading = "root"
        page_data[active_heading] = []
    if el.tag == "h2" or el.tag == "h3":
        active_heading = el.text
        page_data[active_heading] = []
    if el.tag == "p" or el.tag == "li":
        if not el.text:
            continue
        elif el.text[0:2] == "| ":
            table_lines = el.text.split("\n")
            table_headings = [
                heading.strip() for heading in table_lines[0].split("|")[1:-1]
            ]
            table_content = [
                [cell.strip() for cell in row.split("|")[1:-1]]
                for row in table_lines[2:]
            ]
            page_data[active_heading].append(TableData(table_headings, table_content))
        else:
            page_data[active_heading].append(el.text)

page_data

# %%
# Convert this to a Django fixture to import into the database

# example_fixture
"""
[
  {
    "model": "rse_challenges_app.challenge",
    "pk": 1,
    "fields": {
      "name": "Example Challenge",
      "description": "The environmental impact of RSEs through their work is a growing concern. RSEs need to consider the environmental impact of their work and adopt sustainable practices where possible.",
      "created_date": "2024-11-28T21:57:06Z",
      "last_modified_date": "2024-11-28T21:57:08Z",
      "is_active": true,
      "is_deleted": false,
      "evidence_text": "- [UK Gov Office for Science: Large-scale computing: the case for greater UK coordination](https://assets.publishing.service.gov.uk/media/654a4025e2e16a000d42aaef/UK_Computing_report_-_Final_20.09.21.pdf)",
      "impacts_text": "1. Reduce the environmental impact of RSEs through their work.\r\n2. Raise awareness of the environmental impact of RSEs and the importance of adopting sustainable practices.",
      "objectives_text": "1. Develop a set of best practices for RSEs to reduce their environmental impact.\r\n2. Encourage green rse champions within RSE groups to promote sustainable practices.",
      "actions_and_outputs_text": "| Actions                | Output                                       | Objective | Impact |\r\n| ---------------------- | -------------------------------------------- | --------- | ------ |\r\n| Create a Green RSE SIG | An SIG dedicated to the green RSE initiative | 1         | 1      |",
      "active_projects_text": "- [green algorithms](https://www.green-algorithms.org/)\r\n- [Green SIG slack](https://ukrse.slack.com/archives/C07UXQEE014)",
      "past_work_text": "- [Hello world](http://localhost:8000)"
    }
  },
]
"""

page_fixture = {
    "model": "rse_challenges_app.challenge",
    "pk": 1,
    "fields": {
        "name": page_heading,
        "description": page_data.get("root", ""),
        "created_date": "2024-11-28T21:57:06Z",
        "last_modified_date": "2024-11-28T21:57:08Z",
        "is_active": True,
        "is_deleted": False,
        "evidence_text": page_data.get("Evidence of the problem", ""),
        "impacts_text": page_data.get(
            "Objectives and Milestones for overcoming the challenge", ""
        ),
        "objectives_text": page_data.get("Objectives", ""),
        "actions_and_outputs_text": page_data.get(
            "Actions, Outputs and Objectives", ""
        ),
        "active_projects_text": page_data.get(
            "Current Active Projects and Initiatives", ""
        ),
        "past_work_text": page_data.get(
            "Past work towards overcoming the challenge", ""
        ),
    },
}
page_fixture

# %%


def join_lines_with_break(text: list[str]):
    return ("\n").join(text)


def markdown_to_fixture(md: str, id: str):
    result = parse_markdown(md)
    active_heading = None
    page_heading = None
    table_headings = []
    page_data = {}

    class TableData:
        def __init__(self, headings, data):
            self.headings = headings
            self.data = data

        def __repr__(self):
            return f"TableData({self.headings}, {self.data})"

    for el in result.iter():
        # print(el.tag, el.text, el.tail)
        if el.tag == "h1":
            page_heading = el.text
            active_heading = "root"
            page_data[active_heading] = []
        if el.tag == "h2" or el.tag == "h3":
            active_heading = el.text
            page_data[active_heading] = []
        if el.tag == "p" or el.tag == "li":
            if not el.text:
                continue
            elif el.text[0:2] == "| ":
                table_lines = el.text.split("\n")
                table_headings = [
                    heading.strip() for heading in table_lines[0].split("|")[1:-1]
                ]
                table_content = [
                    [cell.strip() for cell in row.split("|")[1:-1]]
                    for row in table_lines[2:]
                ]
                page_data[active_heading].append(
                    TableData(table_headings, table_content)
                )
            else:
                page_data[active_heading].append(el.text)
    page_fixture = {
        "model": "rse_challenges_app.challenge",
        "pk": 1,
        "fields": {
            "name": page_heading or id,
            "description": join_lines_with_break(page_data.get("root", [""])),
            "created_date": "2024-11-28T21:57:06Z",
            "last_modified_date": "2024-11-28T21:57:08Z",
            "is_active": True,
            "is_deleted": False,
            "evidence_text": join_lines_with_break(
                page_data.get("Evidence of the problem", [""])
            ),
            "impacts_text": join_lines_with_break(
                page_data.get(
                    "Objectives and Milestones for overcoming the challenge", [""]
                )
            ),
            "objectives_text": join_lines_with_break(page_data.get("Objectives", [""])),
            "actions_and_outputs_text": page_data.get(
                "Actions, Outputs and Objectives", [""]
            ),
            "active_projects_text": join_lines_with_break(
                page_data.get("Current Active Projects and Initiatives", [""])
            ),
            "past_work_text": join_lines_with_break(
                page_data.get("Past work towards overcoming the challenge", [""])
            ),
        },
    }
    return page_fixture


# Apply to
markdown_files = [
    f
    for f in os.listdir("rse-community-challenges-book/rse-community-challenges")
    if ".md" in f
]
page_fixtures = []
for i, file in enumerate(markdown_files):
    with open(f"rse-community-challenges-book/rse-community-challenges/{file}") as f:
        markdown_text = f.read()
        page_fixtures.append({**markdown_to_fixture(markdown_text, file), "pk": i + 1})
with open("web-app/rse_challenges_app/fixtures/challenges.json", "w") as f:
    json.dump(page_fixtures, f, indent=2, default=str)

# %%
