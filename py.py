import mysql.connector
from mysql.connector import Error
import uuid
import os
import random
from dotenv import load_dotenv
from faker import Faker

# Load environment variables
load_dotenv()
faker = Faker()

# Connection settings
HOST = os.getenv('host')
USER = os.getenv('user')
PASSWORD = os.getenv('password')
DATABASE = os.getenv('database')


def create_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
        return connection
    except Error as e:
        print(f"The error '{e}' occurred")
        return None


def execute_query(connection, query, data=None):
    """Execute a single query"""
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def batch_execute_query(connection, query, data_batch):
    """Execute batch queries"""
    cursor = connection.cursor()
    try:
        cursor.executemany(query, data_batch)
        connection.commit()
        print("Batch query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def insert_initial_data():
    connection = create_connection()
    if connection is None:
        return

    # Insert 500,000 owners
    owners_query = """
    INSERT INTO owners (id, first_name, last_name, phone, email) 
    VALUES (%s, %s, %s, %s, %s)
    """
    owners_data = [(str(uuid.uuid4()), faker.first_name(), faker.last_name(), faker.phone_number(), faker.email())
                   for _ in range(500000)]

    # Insert in batches of 10,000 rows
    for i in range(0, len(owners_data), 10000):
        batch_execute_query(connection, owners_query, owners_data[i:i + 10000])

    # Insert pets for each owner
    pets_query = """
    INSERT INTO pets (id, owner_id, pet_name, species, breed, age) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM owners")
    owner_ids = [row[0] for row in cursor.fetchall()]

    pets_data = [(str(uuid.uuid4()), random.choice(owner_ids), faker.first_name(),
                  faker.word(ext_word_list=['Dog', 'Cat', 'Bird']),
                  faker.word(ext_word_list=['Golden Retriever', 'Siamese', 'Parakeet']),
                  random.randint(1, 15)) for _ in range(500000)]

    # Insert in batches of 10,000 rows
    for i in range(0, len(pets_data), 10000):
        batch_execute_query(connection, pets_query, pets_data[i:i + 10000])

    # Insert veterinarians
    veterinarians_query = """
    INSERT INTO veterinarians (id, first_name, last_name, phone, email, specialty) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    veterinarians_data = [(str(uuid.uuid4()), faker.first_name(), faker.last_name(), faker.phone_number(),
                           faker.email(), random.choice(['General Care', 'Surgery', 'Dentistry']))
                          for _ in range(500)]

    batch_execute_query(connection, veterinarians_query, veterinarians_data)

    connection.close()
    print("Initial data inserted into 'owners', 'pets', and 'veterinarians' tables.")


def insert_bulk_appointments():
    connection = create_connection()
    if connection is None:
        return

    # Fetch existing IDs
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM pets")
    pet_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM veterinarians")
    veterinarian_ids = [row[0] for row in cursor.fetchall()]

    # Bulk insert for appointments
    appointments_query = """
    INSERT INTO appointments (id, pet_id, veterinarian_id, appointment_date, status) 
    VALUES (%s, %s, %s, %s, %s)
    """
    appointments_data = []
    statuses = ['Scheduled', 'Completed', 'Cancelled']

    for _ in range(500000):
        appointment_id = str(uuid.uuid4())
        pet_id = random.choice(pet_ids)
        veterinarian_id = random.choice(veterinarian_ids)
        appointment_date = faker.date_this_year()
        status = random.choice(statuses)
        appointments_data.append((appointment_id, pet_id, veterinarian_id, appointment_date, status))

        # Insert in batches of 10,000 rows
        if len(appointments_data) >= 10000:
            cursor.executemany(appointments_query, appointments_data)
            connection.commit()
            print(f"Batch of 10,000 appointments inserted")
            appointments_data.clear()

    # Insert any remaining rows
    if appointments_data:
        cursor.executemany(appointments_query, appointments_data)
        connection.commit()
        print("Final batch of appointments inserted")

    connection.close()
    print("500,000 rows inserted into 'appointments' table.")


if __name__ == "__main__":
    insert_initial_data()
    insert_bulk_appointments()



