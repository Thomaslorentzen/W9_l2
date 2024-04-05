from fastapi import FastAPI, HTTPException
import uvicorn
from database.DBconnection import DatabaseConnection
from typing import Optional
from pydantic import BaseModel

app = FastAPI()
db = DatabaseConnection()

class QueryStrategy:
    def execute(self, cursor, column, value):
        pass

class EqualStrategy(QueryStrategy):
    def execute(self, cursor, column, value):
        cursor.execute(f"SELECT * FROM cereals WHERE {column} = %s", (value,))
        return cursor.fetchall()

class GreaterThanStrategy(QueryStrategy):
    def execute(self, cursor, column, value):
        cursor.execute(f"SELECT * FROM cereals WHERE {column} > %s", (value,))
        return cursor.fetchall()

class LEQstrategy(QueryStrategy):
    def execute(self, cursor, column, value):
        cursor.execute(f"SELECT * FROM cereals WHERE {column} <= %s", (value,))
        return cursor.fetchall()

class GEQstrategy(QueryStrategy):
    def execute(self, cursor, column, value):
        cursor.execute(f"SELECT * FROM cereals WHERE {column} >= %s", (value,))
        return cursor.fetchall()

class NEQstrategy(QueryStrategy):
    def execute(self, cursor, column, value):
        cursor.execute(f"SELECT * FROM cereals WHERE {column} != %s", (value,))
        return cursor.fetchall()

@app.get("/cereals")
async def get_cereals(
    column: Optional[str] = None,
    value: Optional[str] = None,
    sort_by: Optional[str] = None,
    operator: Optional[str] = None
):
    with db.get_cursor() as cursor:
        # Apply filtering
        if column and value:
            strategy_map = {
                "=": EqualStrategy(),
                ">": GreaterThanStrategy(),
                "<=": LEQstrategy(),
                ">=": GEQstrategy(),
                "!=": NEQstrategy()
            }
            strategy = strategy_map.get(operator, EqualStrategy())
            cereals = strategy.execute(cursor, column, value)
        else:
            cursor.execute("SELECT * FROM cereals")
            cereals = cursor.fetchall()

        # Apply sorting
        if sort_by:
            if sort_by in ['name', 'mfr', 'type']:
                cereals.sort(key=lambda x: x[sort_by])
            elif sort_by in ['calories', 'protein', 'fat', 'sodium', 'fiber', 'carbo', 'sugars', 'potass', 'vitamins', 'shelf', 'weight', 'cups', 'rating']:
                cereals.sort(key=lambda x: x[sort_by], reverse=True)
            else:
                raise HTTPException(status_code=400, detail="Invalid sort_by parameter")

    return cereals

@app.get("/cereals/{cereal_id}")
async def get_cereal(cereal_id: int):
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM cereals WHERE ID = %s", (cereal_id,))
        cereal = cursor.fetchone()
    if not cereal:
        raise HTTPException(status_code=404, detail="Cereal not found")
    return cereal

@app.delete("/cereals/{cereal_name}")
async def delete_cereal(cereal_name: str):
    with db.get_cursor() as cursor:
        try:
            cursor.execute("DELETE FROM cereals WHERE name = %s", (cereal_name,))
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete cereal: {e}")

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Cereal '{cereal_name}' not found")

        return {"message": f"Cereal '{cereal_name}' deleted successfully"}

class Cereal(BaseModel):
    name: str
    mfr: str
    type: str
    calories: int
    protein: int
    fat: int
    sodium: int
    fiber: float
    carbo: float
    sugars: int
    potass: int
    vitamins: int
    shelf: int
    weight: float
    cups: float
    rating: float

@app.post("/cereals")
async def create_or_update_cereals(cereal: Cereal):
    with db.get_cursor() as cursor:
        if hasattr(cereal, 'ID'):
            cursor.execute('select * from Cereal where ID = %s', (cereal.ID))
            existing_cereal = cursor.fetchone()
            if not existing_cereal:
                raise HTTPException(status_code=404, detail="Cereal not found")
            
            update_query = """
            UPDATE cereals
            SET name = %s, mfr = %s, type = %s, calories = %s, protein = %s, fat = %s, sodium = %s,
            fiber = %s, carbo = %s, sugars = %s, potass = %s, vitamins = %s, shelf = %s, weight = %s, cups = %s, rating = %s
            WHERE ID = %s
            """

            cursor.execute(update_query, (
                cereal.name,
                cereal.mfr,
                cereal.type,
                cereal.calories,
                cereal.protein,
                cereal.fat,
                cereal.sodium,
                cereal.fiber,
                cereal.carbo,
                cereal.sugars,
                cereal.potass,
                cereal.vitamins,
                cereal.shelf,
                cereal.weight,
                cereal.cups,
                cereal.rating,
                cereal.ID,
            ))
            db.commit()
            return {"message": "cereal update succeeded!"}
        else:
            insert_query = """
            INSERT INTO cereals (name, mfr, type, calories, protein, fat, sodium, fiber, carbo, sugars, potass, vitamins, shelf, weight, cups, rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                cereal.name,
                cereal.mfr,
                cereal.type,
                cereal.calories,
                cereal.protein,
                cereal.fat,
                cereal.sodium,
                cereal.fiber,
                cereal.carbo,
                cereal.sugars,
                cereal.potass,
                cereal.vitamins,
                cereal.shelf,
                cereal.weight,
                cereal.cups,
                cereal.rating,
            ))
            db.commit()
            return {"message": "cereal insert succeeded!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)