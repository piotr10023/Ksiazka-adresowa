import json
import os
from collections import Counter
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QLineEdit, QPushButton, QLabel, QMessageBox, QComboBox
)


class PhoneBook(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Książka adresowa")
        self.setGeometry(100, 100, 600, 600)

        self.contacts = []

        self.layout = QVBoxLayout()

        self.contact_list = QListWidget()
        self.layout.addWidget(self.contact_list)

        form_layout = QVBoxLayout()

        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Imię")
        form_layout.addWidget(self.first_name_input)

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Nazwisko")
        form_layout.addWidget(self.last_name_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Numer telefonu")
        form_layout.addWidget(self.phone_input)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Miejscowość")
        form_layout.addWidget(self.city_input)

        self.street_input = QLineEdit()
        self.street_input.setPlaceholderText("Ulica")
        form_layout.addWidget(self.street_input)

        self.house_number_input = QLineEdit()
        self.house_number_input.setPlaceholderText("Numer domu")
        form_layout.addWidget(self.house_number_input)

        self.save_button = QPushButton("Zapisz kontakt do książki adresowej")
        form_layout.addWidget(self.save_button)

        self.load_button = QPushButton("Wczytaj kontakt z książki adresowej")
        form_layout.addWidget(self.load_button)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Wpisz tekst do wyszukania")
        search_layout.addWidget(self.search_input)

        self.search_field = QComboBox()
        self.search_field.addItems(["imię", "nazwisko", "telefon", "miejscowość", "ulica", "numer domu"])
        search_layout.addWidget(self.search_field)

        self.search_button = QPushButton("Szukaj")
        search_layout.addWidget(self.search_button)

        self.clear_search_button = QPushButton("Wyczyść wyszukiwanie")
        search_layout.addWidget(self.clear_search_button)

        form_layout.addLayout(search_layout)

        self.stats_button = QPushButton("Statystyka miast")
        form_layout.addWidget(self.stats_button)

        self.layout.addLayout(form_layout)
        self.setLayout(self.layout)

        self.save_button.clicked.connect(self.save_contacts)
        self.load_button.clicked.connect(self.load_contacts)
        self.search_button.clicked.connect(self.search_contacts)
        self.clear_search_button.clicked.connect(self.load_contacts)
        self.stats_button.clicked.connect(self.show_city_stats)

        self.load_contacts()

    def refresh_contact_list(self, filtered=None):
        self.contact_list.clear()
        data = filtered if filtered is not None else self.contacts
        for c in data:
            display_text = (
                f"{c['first_name']} {c['last_name']}, tel: {c['phone']}, "
                f"{c['city']}, ul. {c['street']} {c['house_number']}"
            )
            self.contact_list.addItem(display_text)

    def clear_inputs(self):
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.phone_input.clear()
        self.city_input.clear()
        self.street_input.clear()
        self.house_number_input.clear()

    def save_contacts(self):
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        phone = self.phone_input.text().strip()
        city = self.city_input.text().strip()
        street = self.street_input.text().strip()
        house_number = self.house_number_input.text().strip()

        if all([first_name, last_name, phone, city, street, house_number]):
            contact = {
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "city": city,
                "street": street,
                "house_number": house_number
            }
            self.contacts.append(contact)
            self.clear_inputs()
            self.refresh_contact_list()

            try:
                with open("kontakty.json", "w", encoding="utf-8") as f:
                    json.dump(self.contacts, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Sukces", "Kontakt został zapisany w książce adresowej!")
                self.load_contacts()
            except IOError:
                QMessageBox.critical(self, "Błąd zapisu", "Nie udało się zapisać danych do pliku.")
        else:
            QMessageBox.warning(self, "Błąd", "Proszę wypełnić wszystkie pola przed zapisem!")

    def load_contacts(self):
        try:
            if os.path.exists("kontakty.json"):
                with open("kontakty.json", "r", encoding="utf-8") as f:
                    self.contacts = json.load(f)
            else:
                self.contacts = []
            self.refresh_contact_list()
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Błąd odczytu", "Błąd podczas odczytu pliku danych JSON. Plik może być uszkodzony lub pusty.")
            self.contacts = []
            self.refresh_contact_list()
        except IOError:
            QMessageBox.critical(self, "Błąd odczytu", "Nie udało się odczytać danych z pliku.")
            self.contacts = []
            self.refresh_contact_list()

    def search_contacts(self):
        text = self.search_input.text().strip().lower()
        field_map = {
            "imię": "first_name",
            "nazwisko": "last_name",
            "telefon": "phone",
            "miejscowość": "city",
            "ulica": "street",
            "numer domu": "house_number"
        }
        if not text:
            QMessageBox.warning(self, "Błąd", "Wpisz tekst do wyszukania.")
            return

        selected_field_name = self.search_field.currentText()
        field = field_map[selected_field_name]
        filtered = [c for c in self.contacts if text in c.get(field, "").lower()]
        if filtered:
            self.refresh_contact_list(filtered)
        else:
            QMessageBox.information(self, "Brak wyników", "Nie znaleziono pasujących kontaktów.")

    def show_city_stats(self):
        if not self.contacts:
            QMessageBox.information(self, "Brak danych", "Brak kontaktów do analizy.")
            return
        cities = [c["city"] for c in self.contacts if "city" in c and c["city"].strip()]
        counts = Counter(cities)
        if not counts:
            QMessageBox.information(self, "Brak danych", "Brak miast w kontaktach do analizy.")
            return
        stats_text = "\n".join(f"{city}: {count}" for city, count in counts.items())
        QMessageBox.information(self, "Statystyka miast", stats_text)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = PhoneBook()
    window.show()
    sys.exit(app.exec_())
