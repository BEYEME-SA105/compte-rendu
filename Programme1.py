import re
from datetime import datetime

def parse_ics(file_path):
    """
    Parse un fichier ICS et retourne les événements sous la forme d'un tableau.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    events = []
    event_data = {}

    for line in lines:
        line = line.strip()

        # Lorsque nous rencontrons BEGIN:VEVENT, cela signifie le début d'un événement
        if line.startswith("BEGIN:VEVENT"):
            event_data = {
                "UID": "vide",
                "DTSTART": "vide",
                "DTEND": "vide",
                "SUMMARY": "vide",
                "LOCATION": "vide",
                "DESCRIPTION": "vide"
            }

        # Lorsque nous rencontrons END:VEVENT, cela signifie la fin d'un événement
        elif line.startswith("END:VEVENT"):
            # Format pseudo-csv
            event_str = f"{event_data['UID']};{event_data['DTSTART']};{event_data['DTEND']};{event_data['SUMMARY']};{event_data['LOCATION']};{event_data['DESCRIPTION']}"
            events.append(event_str)

        # Recherche des propriétés spécifiques d'un événement (DTSTART, SUMMARY, etc.)
        else:
            match = re.match(r"^(UID|DTSTART|DTEND|SUMMARY|LOCATION|DESCRIPTION):(.*)$", line)
            if match:
                key, value = match.groups()
                # Nettoyer les espaces et remplacer par "vide" si la valeur est vide
                event_data[key] = value.strip() if value.strip() else "vide"

    return events

def main():
    ics_file = "Test.ics"  # Remplacez par le nom de votre fichier ICS
    try:
        events = parse_ics(ics_file)
        if events:
            print("Événements extraits :")
            for event in events:
                print(event)
        else:
            print("Aucun événement trouvé.")
    except FileNotFoundError:
        print(f"Erreur : le fichier {ics_file} est introuvable.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    main()
