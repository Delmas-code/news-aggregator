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

## Usage

1. Run the application:
   ```
   poetry run uvicorn app.main:app --reload
   ```

2. Access the API at `http://localhost:8000`

## Development

- Run tests:
  ```
  poetry run pytest
  ```

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
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py
│   ├── routers/
│   │   ├── __init__.py
|   |   ├── source.py
│   ├── crud/
│   │   ├── __init__.py
|   |   ├── source.py
│   ├── schemas/
│   │   ├── __init__.py
|   |   ├── source.py
│   ├── models/
│   │   ├── __init__.py
|   |   ├── source.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── notification.py
│   ├── utils/
│   │   ├── __init__.py
│   ├── tests/
│       ├── __init__.py
├── logs
|  |  ├── app.log
├── .env
├── README.md
├── .gitignore
├── pyproject.toml
└── poetry.lock
```
