import logging
import os
import threading
import requests
from endpoints.get_requests import get_cereal, get_cereals, delete_cereal, create_or_update_cereals
from database import DBconnection, parser
from database.DBconnection import DatabaseConnection
import uvicorn
from fastapi import FastAPI


# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

class MainForm:
    def __init__(self):
        self.query_input = None
        self.results_display = None

    def create(self):
        logging.info("Database Search")
        print("Select an option:")
        print("1. Search for cereals")
        print("2. Insert or update a cereal")
        print("3. Delete a cereal")
        print("4. Exit")
        self.query_input = input("> ")

    def search(self):
        try:
            while True:
                if self.query_input == "1":
                    query = input("Search Query:\n> ")
                    if not query:
                        break
                    # Perform GET request to search for cereals by name
                    response = requests.get(f"http://localhost:80/cereals", params={"column": "name", "value": query})
                    if response.status_code == 200:
                        # Display search results if available
                        results = response.json()
                        if results:
                            print("Search Results:")
                            for result in results:
                                print(result)
                        else:
                            print("No results found.")
                    else:
                        print(f"Error: HTTP {response.status_code} - Failed to fetch search results.")
                elif self.query_input == "2":
                    cereal_name = input("Enter cereal name: ")
                    cereal_mfr = input("Enter cereal manufacturer: ")
                    cereal_type = input("Enter cereal type: ")
                    cereal_calories = input("Enter cereal calories: ")
                    cereal_protein = input("Enter cereal protein: ")
                    cereal_fat = input("Enter cereal fat: ")
                    cereal_sodium = input("Enter cereal sodium: ")
                    cereal_fiber = input("Enter cereal fiber: ")
                    cereal_carbo = input("Enter cereal carbo: ")
                    cereal_sugars = input("Enter cereal sugars: ")
                    cereal_potass = input("Enter cereal potass: ")
                    cereal_vitamins = input("Enter cereal vitamins: ")
                    cereal_shelf = input("Enter cereal shelf: ")
                    cereal_weight = input("Enter cereal weight: ")
                    cereal_cups = input("Enter cereal cups: ")
                    cereal_rating = input("Enter cereal rating: ")

                    cereal = {
                        "name": cereal_name,
                        "mfr": cereal_mfr,
                        "type": cereal_type,
                        "calories": cereal_calories,
                        "protein": cereal_protein,
                        "fat": cereal_fat,
                        "sodium": cereal_sodium,
                        "fiber": cereal_fiber,
                        "carbo": cereal_carbo,
                        "sugars": cereal_sugars,
                        "potass": cereal_potass,
                        "vitamins": cereal_vitamins,
                        "shelf": cereal_shelf,
                        "weight": cereal_weight,
                        "cups": cereal_cups,
                        "rating": cereal_rating
                    }        

                    response = requests.post("http://localhost:80/cereals", json=cereal)
                    if response.status_code == 200:
                        print("Cereal inserted/updated successfully!")
                    else:
                        print(f"Error: HTTP {response.status_code} - Failed to insert/update cereal.")       

                elif self.query_input == "3":
                     # Delete a cereal
                    cereal_id = input("Enter cereal ID to delete: ")
                    response = requests.delete(f"http://localhost:80/cereals/{cereal_id}")
                    if response.status_code == 200:
                        print("Cereal deleted successfully!")
                    else:
                        print(f"Error: HTTP {response.status_code} - Failed to delete cereal.")
                elif self.query_input == "4":
                    # Exit
                    break
                else:
                    print("Invalid option. Please select a valid option (1, 2, 3, or 4).")
                self.create()  # Prompt the user for another option
        except Exception as e:
            logging.error("An error occurred: %s", e)

class MenuApp:
    def __init__(self):
        self.db = DBconnection.DatabaseConnection()


    def start(self):
        # Check if data parsing is required
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM cereals")
            count = cursor.fetchone()[0]
            if count == 0:
                # Get the directory of the current script
                current_dir = os.path.dirname(os.path.abspath(__file__))

                # Construct the file path to the CSV file in the data directory
                csv_file_path = os.path.join(current_dir, 'data', 'Cereal.csv')

                # Parse the data
                parser = parser.DataParser(self.db)
                parser.parse(csv_file_path)
                logging.info("Data parsing completed successfully.")
            else:
                logging.info("Data already exists in the database. Skipping data parsing.")
        
        # Start the main form
        main_form = MainForm()
        main_form.create()
        main_form.search()
    
def run_server():
    uvicorn.run(app, host="127.0.0.1", port=80)

def start_menu():
    # Instantiate and run the menu interface
    menu = MenuApp()
    menu.start()

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Start the menu interface in the main thread
    start_menu()

