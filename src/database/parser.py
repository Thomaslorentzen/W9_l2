import csv
import logging

class DataParser:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.logger = logging.getLogger(__name__)

    def parse(self, file_path):
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file, delimiter=';')
                next(reader)  # Skip header row
                next(reader)  # Skip sub-header row

                # Establish a database connection and cursor
                with self.db_connection.get_cursor() as cursor:
                    sql = "INSERT INTO cereals (name, mfr, type, calories, protein, fat, sodium, fiber, carbo, sugars, potass, vitamins, shelf, weight, cups, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                    for row_num, row in enumerate(reader, start=1):
                        try:
                            if len(row) != 16:
                                self.logger.error("Error in row %d: Incorrect number of values", row_num)
                                continue

                            # Log the contents of the row being processed
                            self.logger.debug("Processing row %d: %s", row_num, row)

                            # Check if the cereal already exists in the database
                            cursor.execute("SELECT * FROM cereals WHERE name = %s", (row[0],))
                            existing_cereal = cursor.fetchone()

                            if existing_cereal:
                                self.logger.info("Cereal '%s' already exists. Skipping insertion.", row[0])
                                continue

                            # Convert the last value (rating) to float after removing periods
                            row[-1] = float(row[-1].replace('.', '').replace(',', ''))

                            # Execute the SQL query
                            cursor.execute(sql, row)

                            # Commit the transaction
                            self.db_connection.commit()
                        except Exception as e:
                            self.logger.error("An error occurred while inserting data: %s", e)
                            # Log the SQL query and the problematic row causing the error
                            self.logger.error("SQL Query: %s", sql)
                            self.logger.error("Problematic row: %s", row)
        except FileNotFoundError:
            self.logger.error("File not found: %s", file_path)
        except csv.Error as e:
            self.logger.error("CSV Error: %s", e)
        except Exception as e:
            self.logger.error("An error occurred: %s", e)
