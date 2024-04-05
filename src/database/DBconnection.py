import mysql.connector

class DatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            try:
                cls._instance.conn = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='Kom12345',
                    database='cereal'
                )
                cls._instance.cursor = cls._instance.conn.cursor()
            except mysql.connector.Error as e:
                print(f"Error connecting to the database: {e}")
                # Handle the error appropriately (e.g., logging, raising custom exception)
                raise  # Reraise the exception to indicate failure
        return cls._instance
    
    def __init__(self) -> None:
        pass 

    def close(self):
        self.conn.close()  # Close the connection
    
    def commit(self):
        self.conn.commit()  # Commit the changes

    def get_cursor(self):
        return self.cursor
