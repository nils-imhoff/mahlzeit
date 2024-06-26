import tkinter as tk
from tkinter import messagebox, ttk
import json
import sqlite3
import pandas as pd
from fpdf import FPDF


class MealPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meal Planner")
        self.root.geometry("1000x800")  # Breite x Höhe

        self.root.configure(bg="#f0f0f0")

        self.init_db()
        self.default_ingredients = {}
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
        self.meals = []
        self.ingredients = {}

        # Style-Definitionen
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 14), background="#f0f0f0")
        style.configure("TEntry", font=("Arial", 14))
        style.configure("TButton", font=("Arial", 14), padding=10)
        style.configure("TOptionMenu", font=("Arial", 14))
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
        style.configure("Treeview", font=("Arial", 12), rowheight=30)

        # Frames für die Abschnitte
        top_frame = ttk.Frame(root)
        top_frame.pack(pady=10)

        middle_frame = ttk.Frame(root)
        middle_frame.pack(pady=10, fill='x')

        bottom_frame = ttk.Frame(root)
        bottom_frame.pack(pady=10, expand=True, fill='both')

        # Anzahl der Personen
        self.person_count_label = ttk.Label(top_frame, text="Anzahl der Personen:")
        self.person_count_label.grid(row=0, column=0, padx=5)
        self.person_count_entry = ttk.Entry(top_frame)
        self.person_count_entry.grid(row=0, column=1, padx=5)
        self.person_count_entry.insert(0, "1")  # Default value
        self.person_count_entry.bind("<KeyRelease>", self.update_totals)

        # Anzahl der vegetarischen Personen
        self.vegetarian_count_label = ttk.Label(top_frame, text="Anzahl der Vegetarier:")
        self.vegetarian_count_label.grid(row=0, column=2, padx=5)
        self.vegetarian_count_entry = ttk.Entry(top_frame)
        self.vegetarian_count_entry.grid(row=0, column=3, padx=5)
        self.vegetarian_count_entry.insert(0, "0")  # Default value

        # Mahlzeiten Auswahl
        self.meal_label = ttk.Label(top_frame, text="Wähle eine Mahlzeit:")
        self.meal_label.grid(row=1, column=0, padx=5)
        self.meal_var = tk.StringVar()
        self.meal_options = ["Frühstück", "Mittagessen", "Abendessen"]
        self.meal_menu = ttk.OptionMenu(
            top_frame, self.meal_var, self.meal_options[0], *self.meal_options, command=self.update_dishes
        )
        self.meal_menu.grid(row=1, column=1, padx=5)

        # Gerichte Auswahl
        self.dish_label = ttk.Label(top_frame, text="Wähle ein Gericht oder füge ein neues hinzu:")
        self.dish_label.grid(row=1, column=2, padx=5)
        self.dish_var = tk.StringVar()
        self.dish_entry = ttk.Entry(top_frame, textvariable=self.dish_var)
        self.dish_entry.grid(row=1, column=3, padx=5)

        # Buttons zum Hinzufügen und Planen von Mahlzeiten
        self.add_meal_button = ttk.Button(top_frame, text="Mahlzeit hinzufügen", command=self.add_meal)
        self.add_meal_button.grid(row=2, column=1, pady=10)

        self.plan_meals_button = ttk.Button(top_frame, text="Alle Mahlzeiten planen", command=self.plan_all_meals)
        self.plan_meals_button.grid(row=2, column=2, pady=10)

        self.plan_selected_meals_button = ttk.Button(top_frame, text="Ausgewählte Mahlzeiten planen", command=self.plan_selected_meals)
        self.plan_selected_meals_button.grid(row=2, column=3, pady=10)

        # Tabelle für Zutaten
        self.ingredients_frame = ttk.Frame(middle_frame)
        self.ingredients_frame.pack(pady=10, expand=True, fill="both")

        self.tree = ttk.Treeview(
            self.ingredients_frame,
            columns=("Mahlzeit", "Gericht", "Zutat", "Menge pro Person", "Einheit", "Gesamtmenge"),
            show="headings",
        )
        self.tree.heading("Mahlzeit", text="Mahlzeit")
        self.tree.heading("Gericht", text="Gericht")
        self.tree.heading("Zutat", text="Zutat")
        self.tree.heading("Menge pro Person", text="Menge pro Person")
        self.tree.heading("Einheit", text="Einheit")
        self.tree.heading("Gesamtmenge", text="Gesamtmenge")
        self.tree.column("Mahlzeit", width=100)
        self.tree.column("Gericht", width=100)
        self.tree.column("Zutat", width=150)
        self.tree.column("Menge pro Person", width=150)
        self.tree.column("Einheit", width=100)
        self.tree.column("Gesamtmenge", width=150)

        self.tree.pack(side="left", expand=True, fill="both")

        self.scrollbar = ttk.Scrollbar(
            self.ingredients_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        # Buttons zum Bearbeiten und Entfernen von Zutaten
        self.add_ingredient_button = ttk.Button(bottom_frame, text="Zutat hinzufügen", command=self.add_ingredient)
        self.add_ingredient_button.grid(row=0, column=0, padx=5)

        self.remove_ingredient_button = ttk.Button(bottom_frame, text="Zutat entfernen", command=self.remove_ingredient)
        self.remove_ingredient_button.grid(row=0, column=1, padx=5)

        self.edit_ingredient_button = ttk.Button(bottom_frame, text="Zutat bearbeiten", command=self.edit_ingredient)
        self.edit_ingredient_button.grid(row=0, column=2, padx=5)

        # Vorschläge anzeigen
        self.show_suggestions_button = ttk.Button(bottom_frame, text="Vorschläge anzeigen", command=self.show_suggestions)
        self.show_suggestions_button.grid(row=0, column=3, padx=5)

        # Planung speichern
        self.save_button = ttk.Button(bottom_frame, text="Planung speichern", command=self.save_plan_to_db)
        self.save_button.grid(row=1, column=0, pady=5)

        # Planung laden
        self.load_button = ttk.Button(bottom_frame, text="Planung laden", command=self.load_plan_from_db)
        self.load_button.grid(row=1, column=1, pady=5)

        # PDF speichern
        self.save_pdf_button = ttk.Button(bottom_frame, text="Rezepte und Einkaufsliste als PDF speichern", command=self.save_as_pdf)
        self.save_pdf_button.grid(row=1, column=2, pady=5)

        # CSV speichern
        self.save_csv_button = ttk.Button(bottom_frame, text="Planung als CSV speichern", command=self.save_as_csv)
        self.save_csv_button.grid(row=1, column=3, pady=5)

        # Ergebnisanzeige
        self.result_label = ttk.Label(bottom_frame, text="", wraplength=800)
        self.result_label.grid(row=2, column=0, columnspan=4, pady=10)

        # Laden der gespeicherten Planungen
        self.load_dishes_from_db()
        self.load_plan_from_db()

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
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_type TEXT,
                dish TEXT,
                ingredient TEXT,
                amount REAL,
                unit TEXT
            )
        """
        )
        self.conn.commit()

    def load_dishes_from_db(self):
        self.cursor.execute("SELECT DISTINCT dish, meal_type FROM dishes")
        dishes = self.cursor.fetchall()
        for dish, meal_type in dishes:
            if meal_type not in self.dish_options:
                self.dish_options[meal_type] = []
            self.dish_options[meal_type].append(dish)

        self.cursor.execute("SELECT dish, ingredient, amount, unit FROM dishes")
        rows = self.cursor.fetchall()
        for dish, ingredient, amount, unit in rows:
            if dish not in self.default_ingredients:
                self.default_ingredients[dish] = []
            self.default_ingredients[dish].append((ingredient, amount, unit))

    def load_plan_from_db(self):
        self.cursor.execute("SELECT * FROM meals")
        meals = self.cursor.fetchall()
        self.tree.delete(*self.tree.get_children())
        try:
            person_count = int(self.person_count_entry.get())
        except ValueError:
            person_count = 1
            self.person_count_entry.insert(0, "1")
        for meal in meals:
            meal_type, dish, ingredient, amount_per_person, unit = meal[1:]
            total_amount = amount_per_person * person_count
            self.tree.insert("", "end", values=(meal_type, dish, ingredient, amount_per_person, unit, total_amount))

    def update_dishes(self, *args):
        meal_type = self.meal_var.get()
        if meal_type in self.dish_options:
            self.dish_var.set(self.dish_options[meal_type][0])
        else:
            self.dish_var.set("")

        self.tree.delete(*self.tree.get_children())
        dish = self.dish_var.get()
        if dish in self.default_ingredients:
            try:
                person_count = int(self.person_count_entry.get())
            except ValueError:
                person_count = 1
                self.person_count_entry.insert(0, "1")
            for ingredient, amount, unit in self.default_ingredients[dish]:
                total_amount = amount * person_count
                self.tree.insert(
                    "", "end", values=(meal_type, dish, ingredient, amount, unit, total_amount)
                )

    def update_totals(self, *args):
        try:
            person_count = int(self.person_count_entry.get())
        except ValueError:
            person_count = 1
            self.person_count_entry.insert(0, "1")

        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            amount_per_person = values[3]
            total_amount = amount_per_person * person_count
            self.tree.item(item, values=(values[0], values[1], values[2], values[3], values[4], total_amount))

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
                try:
                    person_count = int(self.person_count_entry.get())
                except ValueError:
                    person_count = 1
                total_amount = float(amount) * person_count
                self.tree.insert(
                    "", "end", values=(meal_type, dish, ingredient, amount, unit, total_amount)
                )
                self.cursor.execute(
                    "INSERT INTO dishes (meal_type, dish, ingredient, amount, unit) VALUES (?, ?, ?, ?, ?)",
                    (meal_type, dish, ingredient, amount, unit)
                )
                self.conn.commit()
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
            item = self.tree.item(selected_item)
            meal_type, dish, ingredient, amount, unit, total_amount = item['values']
            self.cursor.execute(
                "DELETE FROM dishes WHERE meal_type = ? AND dish = ? AND ingredient = ?",
                (meal_type, dish, ingredient)
            )
            self.conn.commit()
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
                try:
                    person_count = int(self.person_count_entry.get())
                except ValueError:
                    person_count = 1
                total_amount = float(amount) * person_count
                self.tree.item(
                    selected_item, values=(meal_type, dish, ingredient, amount, unit, total_amount)
                )
                self.cursor.execute(
                    "UPDATE dishes SET meal_type = ?, dish = ?, ingredient = ?, amount = ?, unit = ? WHERE meal_type = ? AND dish = ? AND ingredient = ?",
                    (meal_type, dish, ingredient, amount, unit, values[0], values[1], values[2])
                )
                self.conn.commit()
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
                        total_amount = amount * person_count
                        self.tree.insert(
                            "",
                            "end",
                            values=(meal_type, dish, ingredient, amount, unit, total_amount),
                        )
                        self.cursor.execute(
                            "INSERT INTO meals (meal_type, dish, ingredient, amount_per_person, unit) VALUES (?, ?, ?, ?, ?)",
                            (meal_type, dish, ingredient, amount, unit)
                        )
                        self.conn.commit()

            messagebox.showinfo(
                "Hinzugefügt", f"{dish} für {meal_type} wurde hinzugefügt."
            )
        except ValueError:
            messagebox.showerror(
                "Eingabefehler",
                "Bitte gib eine gültige Anzahl von Personen und Vegetariern ein.",
            )

    def plan_all_meals(self):
        self.plan_meals(self.tree.get_children())

    def plan_selected_meals(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror(
                "Auswahlfehler", "Bitte wähle eine oder mehrere Mahlzeiten aus der Liste aus."
            )
            return
        self.plan_meals(selected_items)

    def plan_meals(self, items):
        total_amounts = {}
        recipes = []

        for item in items:
            meal_type, dish, ingredient, amount, unit, total_amount = self.tree.item(item)["values"]
            if dish in self.default_ingredients:
                person_count = int(self.person_count_entry.get())
                amounts = self.get_amounts(dish, person_count)
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

    def get_amounts(self, dish, person_count):
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

    def save_plan_to_db(self):
        self.cursor.execute("DELETE FROM meals")
        self.conn.commit()

        for item in self.tree.get_children():
            meal_type, dish, ingredient, amount, unit, total_amount = self.tree.item(item)["values"]
            self.cursor.execute(
                "INSERT INTO meals (meal_type, dish, ingredient, amount_per_person, unit) VALUES (?, ?, ?, ?, ?)",
                (meal_type, dish, ingredient, amount, unit)
            )
        self.conn.commit()
        messagebox.showinfo("Gespeichert", "Planung wurde gespeichert.")

    def save_as_pdf(self):
        total_amounts = {}
        recipes = []

        for row in self.tree.get_children():
            meal_type, dish, ingredient, amount, unit, total_amount = self.tree.item(row)["values"]
            if dish in self.default_ingredients:
                person_count = int(self.person_count_entry.get())
                amounts = self.get_amounts(dish, person_count)
                recipe = self.get_recipe(dish)
                if ingredient in amounts:
                    if ingredient in total_amounts:
                        total_amounts[ingredient][0] += amounts[ingredient][0]
                    else:
                        total_amounts[ingredient] = [amounts[ingredient][0], unit]
                recipes.append((dish, recipe))

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Einkaufsliste", ln=True, align="C")
        for item, (amount, unit) in total_amounts.items():
            pdf.cell(200, 10, txt=f"{item}: {amount} {unit}", ln=True)

        pdf.add_page()
        pdf.cell(200, 10, txt="Rezepte", ln=True, align="C")
        for dish, recipe in recipes:
            pdf.cell(200, 10, txt=f"\nRezept für {dish}:", ln=True)
            pdf.multi_cell(0, 10, txt=recipe)

        pdf.output("meal_plan.pdf")
        messagebox.showinfo("Gespeichert", "PDF wurde gespeichert.")

    def save_as_csv(self):
        data = []
        for row in self.tree.get_children():
            meal_type, dish, ingredient, amount, unit, total_amount = self.tree.item(row)["values"]
            data.append((meal_type, dish, ingredient, amount, unit, total_amount))
        
        df = pd.DataFrame(data, columns=["Mahlzeit", "Gericht", "Zutat", "Menge pro Person", "Einheit", "Gesamtmenge"])
        df.to_csv("meal_plan.csv", index=False)
        messagebox.showinfo("Gespeichert", "CSV wurde gespeichert.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MealPlannerApp(root)
    root.mainloop()
