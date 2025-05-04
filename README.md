# SSGG-BE-V2
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

This is an api that serves as a backend for a mobile application made for a scouting group to manage attendance and member profiles. SSGG stands for Sporting Scouts and Girl Guides.

The API is deployed on AWS API Gateway with AWS Lambda as it's integration. The Lambdas are written in python and deployed using GitHub workflows to allow for fast and smooth updates.

This is V2 of the repo [SSGG-BE](https://github.com/ahmed-881994/SSGG-BE)

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Endpoints