# Crud API

CRUD API on a person object using python

## Installation

Set up virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

## Usage

```python
python api.py
Base URL: http://127.0.0.1:5000/

```

## Database

```python
Person Object = {
id: string variable,
version: integer (increase by 1 numerically starting with 1)
first_name: string variable,
middle_name: string variable,
last_name: string variable,
email: string variable,
age: integer
}

Database: SQLite database - can load file into database viewer like dbeaver or use command line to view
```

## API Calls

```python
Some values are already stored in the database to test - for the POST/PUT

To Create a new person: http://127.0.0.1:5000/api/people POST

{
"id": "aajay",
"first_name": "ariana",
"middle_name": "ais",
"last_name": "jay",
"email": "aajay@abc.com",
"age": 20
}

To update a person: http://127.0.0.1:5000/api/people/<id> PUT

{
"email": "aajay@abc.com",
"age": 30
}
```
