# RSE Challenges Web App

The RSE Challenges web app is an interactive web based interface to the RSE Challenges book. It allows users to view and interact with the challenges in the book, and to contribute to the challenges by submitting new evidence, impact targets, objectives, actions, and outputs.

## Installation

## Development

### Environment Setup (First time)

- Setup python virtual environment with UV
- Install dependencies with `uv sync --group=dev`
- Run database migrations with `python manage.py migrate`
- Add initial data with `python manage.py loaddata web-app/rse_challenges_app/fixtures/challenges.json`
- Create a admin superuser to access admin panel: `python manage.py createsuperuser` and follow the instructions.

#### Updating data from markdown files

After making modifications to the markdown files run the following in the project virtual environment:
`scripts/parse_challenge_markdown_pages.py`

Then using the web app environment:
`web-app/scripts/reset_data.sh`.

### Running Development Server

`python manage.py runserver`

### Testing
