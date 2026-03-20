# SSGG-BE-V2
This is an api that serves as a backend for a mobile application made for a scouting group to manage attendance and member profiles. SSGG stands for Sporting Scouts and Girl Guides.

This is V2 of the repo [SSGG-BE](https://github.com/ahmed-881994/SSGG-BE)

## Technology Stack

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/) [![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/) [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-000000?style=flat&logo=sqlalchemy)](https://www.sqlalchemy.org/) [![MySQL](https://img.shields.io/badge/MySQL-000000?style=flat&logo=mysql)](https://www.mysql.com/) [![Redis](https://img.shields.io/badge/Redis-000000?style=flat&logo=redis)](https://redis.io/) [![Docker](https://img.shields.io/badge/Docker-000000?style=flat&logo=docker)](https://www.docker.com/) [![Traefik](https://img.shields.io/badge/Traefik-000000?style=flat&logo=traefikproxy)](https://traefik.io/)

For detailed information on the technology stack used in this project, please refer to the [Technology Stack Documentation](docs/TECHNOLOGY_STACK.md).

## Setup (local development)

### Application Setup

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

4. Create and configure a `.env` file or use the provided environment presets under the `env/` directory for different environments (development, staging, production).

### Database Setup
1. Install MySQL and create a database with the required charset (`utf8mb4`).
2. Update the database connection settings in the environment variables or `.env` file.
3. Run the provided SQL script [database/DB_Setup.sql](database/DB_Setup.sql) to set up the initial schema.
   ```bash
      mysql -u your_username -p your_database < database/DB_Setup.sql
   ```
4. Run the seed scripts located in the [database/seeds/](database/seeds/) directory to populate initial data:
   ```bash
   mysql -u your_username -p your_database < database/seeds/roles.sql
   mysql -u your_username -p your_database < database/seeds/users.sql
   ```
   admin user credentials:
   - Username: `su`
   - Password: `P@ssw0rd`

### Redis Setup
1. Install and run a Redis server.
2. Update the Redis connection settings in the environment variables or `.env` file.

## Documentation

- Technology Stack: [docs/TECHNOLOGY_STACK.md](docs/TECHNOLOGY_STACK.md)
- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Repository Maintenance: [docs/REPOSITORY_MAINTENANCE.md](docs/REPOSITORY_MAINTENANCE.md)
- Deployment: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)