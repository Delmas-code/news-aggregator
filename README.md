# Newsfeed Aggregator

## Description
News aggregator application.

## Prerequisites
- Python 3.9+
- [Poetry](https://python-poetry.org/docs/#installation)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/n529joker/news-aggregator.git
   cd newsfeed-aggregator
   ```
2. Install Poetry:
    ```
    pip install poetry
    ```

3. Activate the poetry virtual environment
   ```
   poetry shell
   ```

4. Install dependencies using Poetry:
   ```
   poetry install
   ```

5. Set up environment variables:
   ```
   Add and Edit `.env` with your specific configuration.
         Ensuring you add 
      API_KEY=6e5a0a50f3a547419708dd55fd3e8bad -> For assemblyAI
               DEV_DATABASE_URL=postgresql+asyncpg://postgres:*Your pswd*@127.0.0.1:5432/*db_name*
      PRODUCTION=FALSE
      RABBITMQ_URL=amqp://guest:guest@127.0.0.1/
      INTERVAL_TYPE = minutes  # change to days, hours etc in env
      INTERVAL_DURATION = 5

## Usage

1. Run the application:
   ```
   poetry run uvicorn app.main:app --reload
   ```

2. Access the API at `http://localhost:8000`

## Development

- Install new packages (Add packages):
```
poetry add <package-name>
```

## Project Structure
```
news-aggregator/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── content.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── content.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── content.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── content.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── nlp/
│   │   │   ├── __init__.py
│   │   │   ├── core.py
│   │   │   ├── main.py
├── .env
├── pyproject.toml
├── poetry.lock
└── README.md
```
