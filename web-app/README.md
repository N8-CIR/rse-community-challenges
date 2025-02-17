# RSE Challenges Web App

The RSE Challenges web app is an interactive web based interface to the RSE Challenges book. It allows users to view and interact with the challenges in the book, and to contribute to the challenges by submitting new evidence, impact targets, objectives, actions, and outputs.

## Installation

## Development

### Environment Setup (First time)

- Setup python virtual environment with UV
- Install dependencies with `uv sync --group=dev`
- Run database migrations with `python manage.py migrate`
- Add initial data with `python manage.py loaddata web-app/rse_challenges_app/fixtures/challenges.json`

### Running Development Server

`python manage.py runserver`

### Testing
