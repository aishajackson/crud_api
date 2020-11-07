import flask
from flask import request, jsonify
import sqlite3 as sl

app = flask.Flask(__name__)
app.config["DEBUG"] = True


#display the key and values in the returned json
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


#connect to the sql databse
def connect_to_database(query):
    try:
        conn = sl.connect('example.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()
        result = cur.execute(query)
        conn.commit()
        return result
    except:
        raise Exception('Unable to execute query or connect to database')


# Get latest version of the object
def get_latest_version():
    query = "SELECT DISTINCT version FROM persons;"
    result = connect_to_database(query).fetchone()
    version = result['version']

    return version


LATEST_VERSION = get_latest_version()


#move old versions to history table for future reference
def transfer_data_to_history():
    query = "INSERT INTO persons_history SELECT * FROM persons;"
    connect_to_database(query)

    return 'Values are moved to the history table'


#update the version of the current table when data is changed
def update_version():
    new_version = get_latest_version() + 1
    query = f"UPDATE persons SET version = {new_version};"
    connect_to_database(query)

    return "Values are updated to the newest version"


#update the version of the current table when data is changed
def verify_inputs(id, first_name, last_name, email, age):
    if not all(isinstance(i, str)
               for i in [id, first_name, last_name, email]) and not isinstance(
                   age, int):
        raise Exception(
            "Id, first name, middle name, last name, and email have to be strings and age has to be an integer. Middle name isnt required."
        )
    else:
        return True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Noyo Coding Challenge.</p>"


# A route to create a new person in the data object
@app.route('/api/people', methods=['POST'])
def create_product():
    data = request.get_json()
    if data is None or data == {}:
        return "Error Please provide connection information"

    id = data.get('id')
    first_name = data.get('first_name')
    middle_name = data.get('middle_name')
    last_name = data.get('last_name')
    email = data.get('email')
    age = data.get('age')

    check_inputs = verify_inputs(id, first_name, last_name, email, age)

    if check_inputs:
        transfer_data_to_history()
        if middle_name:
            query = f"INSERT INTO persons (id, version, first_name, middle_name, last_name, email, age) VALUES ('{id}', {LATEST_VERSION}, '{first_name}','{middle_name}', '{last_name}', '{email}', {age});"
        else:
            query = f"INSERT INTO persons (id, version, first_name, last_name, email, age) VALUES ('{id}', {LATEST_VERSION}, '{first_name}', '{last_name}', '{email}', {age});"
    else:
        return "Missing some values - (id, first name, last name, email, age) are required"

    connect_to_database(query)
    update_version()

    return jsonify(data), 200


#Get all people in the database
@app.route('/api/people', methods=['GET'])
def get_all_persons():

    query = "SELECT * FROM persons;"
    people = connect_to_database(query)

    return jsonify(people.fetchall()), 200


#Get by id or by version and id
@app.route('/api/people/<id>', methods=['GET'])
@app.route('/api/<version>/people/<id>', methods=['GET'])
def get_person_by_id(id, version=LATEST_VERSION):

    if version is not LATEST_VERSION:
        query = "SELECT * FROM persons_history WHERE"
    else:
        query = "SELECT * FROM persons WHERE"

    if id:
        query += f" id='{id}' AND"
    if version:
        query += f' version={version} AND'

    query = query[:-4] + ';'

    results = connect_to_database(query).fetchall()

    if not results:
        return f"User ID - {id} does not exist in version {version}"
    else:
        return jsonify(results), 200


#Update the person with given id
@app.route('/api/people/<id>', methods=['PUT'])
def update_person_id(id):
    data = request.get_json()
    if data is None or data == {}:
        return "Error Please provide connection information"

    transfer_data_to_history()

    first_name = data.get('first_name')
    middle_name = data.get('middle_name')
    last_name = data.get('last_name')
    email = data.get('email')
    age = data.get('age')

    query = "UPDATE persons SET"
    where_clause = f" WHERE id='{id}';"

    if first_name:
        query += f" first_name='{first_name}', "
    if middle_name:
        query += f" middle_name='{middle_name}', "
    if last_name:
        query += f" last_name='{last_name}', "
    if email:
        query += f" email='{email}', "
    if age:
        query += f" age={age}, "

    query = query[:-2] + where_clause

    results = connect_to_database(query)

    update_version()

    return f"{results.rowcount} row was updated in the persons table for {id}", 200


#Delete person from the object
@app.route('/api/people/<id>', methods=['DELETE'])
def delete_by_id(id):
    transfer_data_to_history()
    update_version()

    query = f"DELETE FROM persons WHERE id='{id}';"

    results = connect_to_database(query)

    return f"{results.rowcount} row was deleted in the persons table for {id}", 200


app.run()