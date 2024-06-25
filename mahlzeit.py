import tkinter as tk
from tkinter import messagebox, ttk
import json
import sqlite3


class MealPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meal Planner")
        self.root.geometry("1400x1400")  # Breite x Höhe

        self.root.configure(bg="#f0f0f0")

        self.init_db()
        self.meals = []
        self.ingredients = {}

        # Style-Definitionen
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 16), background="#f0f0f0")
        style.configure("TEntry", font=("Arial", 16))
        style.configure("TButton", font=("Arial", 16), padding=10)
        style.configure("TOptionMenu", font=("Arial", 16))
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        style.configure("Treeview", font=("Arial", 14), rowheight=30)

        # Anzahl der Personen
        self.person_count_label = ttk.Label(root, text="Anzahl der Personen:")
        self.person_count_label.pack(pady=10)
        self.person_count_entry = ttk.Entry(root)
        self.person_count_entry.pack(pady=5)

        # Anzahl der vegetarischen Personen
        self.vegetarian_count_label = ttk.Label(root, text="Anzahl der Vegetarier:")
        self.vegetarian_count_label.pack(pady=10)
        self.vegetarian_count_entry = ttk.Entry(root)
        self.vegetarian_count_entry.pack(pady=5)

        # Mahlzeiten Auswahl
        self.meal_label = ttk.Label(root, text="Wähle eine Mahlzeit:")
        self.meal_label.pack(pady=10)
        self.meal_var = tk.StringVar()
        self.meal_options = ["Frühstück", "Mittagessen", "Abendessen"]
        self.meal_menu = ttk.OptionMenu(
            root, self.meal_var, self.meal_options[0], *self.meal_options
        )
        self.meal_menu.pack(pady=5)

        # Gerichte Auswahl
        self.dish_label = ttk.Label(
            root, text="Wähle ein Gericht oder füge ein neues hinzu:"
        )
        self.dish_label.pack(pady=10)
        self.dish_var = tk.StringVar()
        self.dish_entry = ttk.Entry(root, textvariable=self.dish_var)
        self.dish_entry.pack(pady=5)

        self.dish_options = {
            "Frühstück": ["Haferschleim", "Brot"],
            "Mittagessen": ["Brotmahlzeit"],
            "Abendessen": [
                "Nudeln mit Tomatensauce",
                "Nudeln mit Pesto",
                "Reis mit Gemüse",
                "Reis mit Curry",
                "Eintopf",
                "Gemüsesuppe",
            ],
        }
        self.default_ingredients = {
            "Haferschleim": [
                ("Haferflocken", 50, "Gramm"),
                ("Milch", 200, "Milliliter"),
            ],
            "Brot": [
                ("Brot", 80, "Gramm"),
                ("Butter", 20, "Gramm"),
                ("Belag", 50, "Gramm"),
            ],
            "Brotmahlzeit": [("Brot", 80, "Gramm"), ("Käse/Wurst", 50, "Gramm")],
            "Nudeln mit Tomatensauce": [
                ("Nudeln", 80, "Gramm"),
                ("Tomatensauce", 125, "Milliliter"),
            ],
            "Nudeln mit Pesto": [("Nudeln", 80, "Gramm"), ("Pesto", 80, "Gramm")],
            "Reis mit Gemüse": [("Reis", 80, "Gramm"), ("Gemüse", 300, "Gramm")],
            "Reis mit Curry": [
                ("Reis", 80, "Gramm"),
                ("Gemüse", 300, "Gramm"),
                ("Curry-Sauce", 125, "Milliliter"),
            ],
            "Eintopf": [("Gemüse", 300, "Gramm"), ("Fleisch", 150, "Gramm")],
            "Gemüsesuppe": [("Gemüse", 300, "Gramm")],
        }
        self.meal_var.trace("w", self.update_dishes)

        # Tabelle für Zutaten
        self.ingredients_frame = ttk.Frame(root)
        self.ingredients_frame.pack(pady=10, expand=True, fill="both")

        self.tree = ttk.Treeview(
            self.ingredients_frame,
            columns=("Mahlzeit", "Gericht", "Zutat", "Menge pro Person", "Einheit"),
            show="headings",
        )
        self.tree.heading("Mahlzeit", text="Mahlzeit")
        self.tree.heading("Gericht", text="Gericht")
        self.tree.heading("Zutat", text="Zutat")
        self.tree.heading("Menge pro Person", text="Menge pro Person")
        self.tree.heading("Einheit", text="Einheit")
        self.tree.column("Mahlzeit", width=150)
        self.tree.column("Gericht", width=150)
        self.tree.column("Zutat", width=200)
        self.tree.column("Menge pro Person", width=200)
        self.tree.column("Einheit", width=150)

        self.tree.pack(side="left", expand=True, fill="both")

        self.scrollbar = ttk.Scrollbar(
            self.ingredients_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        self.add_ingredient_button = ttk.Button(
            root, text="Zutat hinzufügen", command=self.add_ingredient
        )
        self.add_ingredient_button.pack(pady=5)

        self.remove_ingredient_button = ttk.Button(
            root, text="Zutat entfernen", command=self.remove_ingredient
        )
        self.remove_ingredient_button.pack(pady=5)

        self.edit_ingredient_button = ttk.Button(
            root, text="Zutat bearbeiten", command=self.edit_ingredient
        )
        self.edit_ingredient_button.pack(pady=5)

        # Hinzufügen der Mahlzeit
        self.add_meal_button = ttk.Button(
            root, text="Mahlzeit hinzufügen", command=self.add_meal
        )
        self.add_meal_button.pack(pady=10)

        # Alle Mahlzeiten planen
        self.plan_meals_button = ttk.Button(
            root, text="Alle Mahlzeiten planen", command=self.plan_meals
        )
        self.plan_meals_button.pack(pady=10)

        # Ergebnisanzeige
        self.result_label = ttk.Label(root, text="", wraplength=1000)
        self.result_label.pack(pady=10, expand=True, fill="both")

        # Vorschläge anzeigen
        self.show_suggestions_button = ttk.Button(
            root, text="Vorschläge anzeigen", command=self.show_suggestions
        )
        self.show_suggestions_button.pack(pady=10)

        # Beenden der App
        self.quit_button = ttk.Button(root, text="Beenden", command=root.quit)
        self.quit_button.pack(pady=10)

        # Planung speichern
        self.save_button = ttk.Button(
            root, text="Planung speichern", command=self.save_plan
        )
        self.save_button.pack(pady=5)

    def init_db(self):
        self.conn = sqlite3.connect("mealplanner.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_type TEXT,
                dish TEXT,
                ingredient TEXT,
                amount_per_person REAL,
                unit TEXT
            )
        """
        )
        self.conn.commit()

    def update_dishes(self, *args):
        meal_type = self.meal_var.get()
        if meal_type in self.dish_options:
            self.dish_var.set(self.dish_options[meal_type][0])
        else:
            self.dish_var.set("")

        self.tree.delete(*self.tree.get_children())
        dish = self.dish_var.get()
        if dish in self.default_ingredients:
            for ingredient, amount, unit in self.default_ingredients[dish]:
                self.tree.insert(
                    "", "end", values=(meal_type, dish, ingredient, amount, unit)
                )

    def add_ingredient(self):
        ingredient_window = tk.Toplevel(self.root)
        ingredient_window.title("Zutat hinzufügen")

        meal_type_label = ttk.Label(ingredient_window, text="Mahlzeit:")
        meal_type_label.pack(pady=5)
        meal_type_entry = ttk.Entry(ingredient_window)
        meal_type_entry.pack(pady=5)

        dish_label = ttk.Label(ingredient_window, text="Gericht:")
        dish_label.pack(pady=5)
        dish_entry = ttk.Entry(ingredient_window)
        dish_entry.pack(pady=5)

        ingredient_label = ttk.Label(ingredient_window, text="Zutat:")
        ingredient_label.pack(pady=5)
        ingredient_entry = ttk.Entry(ingredient_window)
        ingredient_entry.pack(pady=5)

        amount_label = ttk.Label(ingredient_window, text="Menge pro Person:")
        amount_label.pack(pady=5)
        amount_entry = ttk.Entry(ingredient_window)
        amount_entry.pack(pady=5)

        unit_label = ttk.Label(ingredient_window, text="Einheit:")
        unit_label.pack(pady=5)
        unit_entry = ttk.Entry(ingredient_window)
        unit_entry.pack(pady=5)

        def add_to_tree():
            meal_type = meal_type_entry.get()
            dish = dish_entry.get()
            ingredient = ingredient_entry.get()
            amount = amount_entry.get()
            unit = unit_entry.get()
            if meal_type and dish and ingredient and amount and unit:
                self.tree.insert(
                    "", "end", values=(meal_type, dish, ingredient, amount, unit)
                )
                ingredient_window.destroy()
            else:
                messagebox.showerror("Eingabefehler", "Bitte fülle alle Felder aus.")

        add_button = ttk.Button(
            ingredient_window, text="Hinzufügen", command=add_to_tree
        )
        add_button.pack(pady=5)

    def remove_ingredient(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
        else:
            messagebox.showerror(
                "Auswahlfehler", "Bitte wähle eine Zutat aus der Liste aus."
            )

    def edit_ingredient(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror(
                "Auswahlfehler", "Bitte wähle eine Zutat aus der Liste aus."
            )
            return

        item = self.tree.item(selected_item)
        values = item["values"]

        ingredient_window = tk.Toplevel(self.root)
        ingredient_window.title("Zutat bearbeiten")

        meal_type_label = ttk.Label(ingredient_window, text="Mahlzeit:")
        meal_type_label.pack(pady=5)
        meal_type_entry = ttk.Entry(ingredient_window)
        meal_type_entry.insert(0, values[0])
        meal_type_entry.pack(pady=5)

        dish_label = ttk.Label(ingredient_window, text="Gericht:")
        dish_label.pack(pady=5)
        dish_entry = ttk.Entry(ingredient_window)
        dish_entry.insert(0, values[1])
        dish_entry.pack(pady=5)

        ingredient_label = ttk.Label(ingredient_window, text="Zutat:")
        ingredient_label.pack(pady=5)
        ingredient_entry = ttk.Entry(ingredient_window)
        ingredient_entry.insert(0, values[2])
        ingredient_entry.pack(pady=5)

        amount_label = ttk.Label(ingredient_window, text="Menge pro Person:")
        amount_label.pack(pady=5)
        amount_entry = ttk.Entry(ingredient_window)
        amount_entry.insert(0, values[3])
        amount_entry.pack(pady=5)

        unit_label = ttk.Label(ingredient_window, text="Einheit:")
        unit_label.pack(pady=5)
        unit_entry = ttk.Entry(ingredient_window)
        unit_entry.insert(0, values[4])
        unit_entry.pack(pady=5)

        def save_changes():
            meal_type = meal_type_entry.get()
            dish = dish_entry.get()
            ingredient = ingredient_entry.get()
            amount = amount_entry.get()
            unit = unit_entry.get()
            if meal_type and dish and ingredient and amount and unit:
                self.tree.item(
                    selected_item, values=(meal_type, dish, ingredient, amount, unit)
                )
                ingredient_window.destroy()
            else:
                messagebox.showerror("Eingabefehler", "Bitte fülle alle Felder aus.")

        save_button = ttk.Button(
            ingredient_window, text="Speichern", command=save_changes
        )
        save_button.pack(pady=5)

    def add_meal(self):
        try:
            person_count = int(self.person_count_entry.get())
            vegetarian_count = int(self.vegetarian_count_entry.get())
            if (
                person_count <= 0
                or vegetarian_count < 0
                or vegetarian_count > person_count
            ):
                raise ValueError

            meal_type = self.meal_var.get()
            dish = self.dish_var.get()

            for row in self.tree.get_children():
                values = self.tree.item(row)["values"]
                if values[1] == dish:
                    break
            else:
                if dish in self.default_ingredients:
                    for ingredient, amount, unit in self.default_ingredients[dish]:
                        self.tree.insert(
                            "",
                            "end",
                            values=(meal_type, dish, ingredient, amount, unit),
                        )

            messagebox.showinfo(
                "Hinzugefügt", f"{dish} für {meal_type} wurde hinzugefügt."
            )
        except ValueError:
            messagebox.showerror(
                "Eingabefehler",
                "Bitte gib eine gültige Anzahl von Personen und Vegetariern ein.",
            )

    def plan_meals(self):
        total_amounts = {}
        recipes = []

        for row in self.tree.get_children():
            meal_type, dish, ingredient, amount, unit = self.tree.item(row)["values"]
            if dish in self.default_ingredients:
                person_count = int(self.person_count_entry.get())
                vegetarian_count = int(self.vegetarian_count_entry.get())
                amounts = self.get_amounts(dish, person_count, vegetarian_count)
                recipe = self.get_recipe(dish)
                if ingredient in amounts:
                    if ingredient in total_amounts:
                        total_amounts[ingredient][0] += amounts[ingredient][0]
                    else:
                        total_amounts[ingredient] = [amounts[ingredient][0], unit]
                recipes.append((dish, recipe))

        result_text = "Einkaufsliste:\n"
        for item, (amount, unit) in total_amounts.items():
            result_text += f"{item}: {amount} {unit}\n"

        result_text += "\nRezepte:\n"
        for dish, recipe in recipes:
            result_text += f"\nRezept für {dish}:\n{recipe}\n"

        self.result_label.config(text=result_text)

    def get_amounts(self, dish, person_count, vegetarian_count):
        amounts = {}
        if dish in self.default_ingredients:
            for ingredient, amount_per_person, unit in self.default_ingredients[dish]:
                total_amount = amount_per_person * person_count
                amounts[ingredient] = (total_amount, unit)
        else:
            # Schätze typische Mengen für unbekannte Gerichte
            amounts["Nudeln"] = (80 * person_count, "Gramm")
            amounts["Tomatensauce"] = (125 * person_count, "Milliliter")
        return amounts

    def get_recipe(self, dish):
        recipes = {
            "Nudeln mit Tomatensauce": "1. Nudeln in Salzwasser kochen.\n2. Tomatensauce erhitzen.\n3. Nudeln mit Tomatensauce vermischen und servieren.",
            "Nudeln mit Pesto": "1. Nudeln in Salzwasser kochen.\n2. Pesto unter die Nudeln mischen.\n3. Mit Parmesan bestreuen und servieren.",
            "Reis mit Gemüse": "1. Reis kochen.\n2. Gemüse in einer Pfanne anbraten.\n3. Reis und Gemüse vermischen und servieren.",
            "Reis mit Curry": "1. Reis kochen.\n2. Gemüse in einer Pfanne anbraten.\n3. Curry-Sauce hinzufügen.\n4. Reis und Curry-Gemüse vermischen und servieren.",
            "Eintopf": "1. Gemüse klein schneiden.\n2. Fleisch anbraten.\n3. Gemüse und Wasser hinzufügen und köcheln lassen, bis alles gar ist.",
            "Gemüsesuppe": "1. Gemüse klein schneiden.\n2. In einem großen Topf Gemüse anbraten.\n3. Wasser und Gewürze hinzufügen und köcheln lassen, bis alles gar ist.",
            "Haferschleim": "1. Haferflocken mit Milch in einem Topf aufkochen.\n2. Unter Rühren köcheln lassen, bis die gewünschte Konsistenz erreicht ist.\n3. Nach Belieben süßen und servieren.",
            "Brot": "1. Brot in Scheiben schneiden.\n2. Nach Belieben mit Butter und Belag bestreichen.\n3. Servieren.",
        }
        return recipes.get(
            dish,
            "Kein Rezept verfügbar. Hier kannst du dein eigenes Rezept hinzufügen.",
        )

    def show_suggestions(self):
        suggestions_window = tk.Toplevel(self.root)
        suggestions_window.title("Mengen Vorschläge")

        suggestions_text = """
        Klare Brühe: 200 ml
        Suppe und Eintopf: 400 ml (als Hauptgang), 200–250 ml (als Beilage)
        Salat: 200 g (als Hauptgang), 50–100 g (als Beilage)
        Fleisch: 150–200 g (als Hauptgang), 50–100 g (als Beilage)
        Fisch: 150–200 g (als Hauptgang), 50–100 g (als Beilage)
        Gemüse: 300–350 g (als Hauptgang), 150–200 g (als Beilage)
        Kartoffeln: 300 g (als Hauptgang), 150–200 g (als Beilage)
        Reis und andere Getreidesorten (Trockengewicht): 80–100 g (als Hauptgang), 50–70 g (als Beilage)
        Nudeln (Trockengewicht): 80–100 g (als Hauptgang), 50–70 g (als Beilage)
        Saucen (gehaltvoll und cremig): 80 ml (als Hauptgang), 75 ml (als Beilage)
        Saucen (leicht und dünnflüssig): 125 ml (als Hauptgang), 100 ml (als Beilage)
        Brot und Brötchen: 80–100 g
        Dessert: 150–200 g
        Käse: 50 g
        Obst: 80–100 g
        Gebäck: ¼ Springform (26 cm Durchmesser) für Quiche, 1⁄12 Springform (26 cm Durchmesser) für Kuchen und Torten
        """

        suggestions_label = ttk.Label(
            suggestions_window, text=suggestions_text, font=("Arial", 14)
        )
        suggestions_label.pack(pady=10, padx=10)

    def save_plan(self):
        plan = {
            "meals": self.meals,
            "ingredients": {
                dish: ingredients for dish, ingredients in self.ingredients.items()
            },
        }

        with open("meal_plan.json", "w") as f:
            json.dump(plan, f)

        messagebox.showinfo("Gespeichert", "Planung wurde gespeichert.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MealPlannerApp(root)
    root.mainloop()
