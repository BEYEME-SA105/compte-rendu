import re

def parse_ics(file_path):
    """
    Lit le fichier ICS et retourne une liste de chaînes de caractères représentant les événements.
    Chaque événement est une ligne du tableau sous la forme d'un texte séparé par des virgules.
    """
    events = []
    
    # Ouverture du fichier ICS
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    event_data = {"SUMMARY": "vide", "LOCATION": "vide", "DTSTART": "vide", "DTEND": "vide", "DESCRIPTION": "vide"}
    inside_event = False

    for line in lines:
        line = line.strip()

        # Début d'un événement
        if line == "BEGIN:VEVENT":
            inside_event = True
            # Réinitialisation des données de l'événement
            event_data = {"SUMMARY": "vide", "LOCATION": "vide", "DTSTART": "vide", "DTEND": "vide", "DESCRIPTION": "vide"}

        # Fin d'un événement
        elif line == "END:VEVENT" and inside_event:
            inside_event = False
            # Création de la chaîne de caractères pour cet événement et ajout à la liste
            event_str = f'{event_data["SUMMARY"]},{event_data["LOCATION"]},{event_data["DTSTART"]},{event_data["DTEND"]},{event_data["DESCRIPTION"]}'
            events.append(event_str)

        # Extraction des données à l'intérieur de l'événement
        elif inside_event:
            match = re.match(r"^(SUMMARY|LOCATION|DTSTART|DTEND|DESCRIPTION):(.*)$", line)
            if match:
                key, value = match.groups()
                event_data[key] = value.strip() if value.strip() else "vide"

    return events


# Programme principal
if __name__ == "__main__":
    ics_file = "Test.ics"  # Nom du fichier ICS
    try:
        events_table = parse_ics(ics_file)
        print("Tableau des événements :")
        for event in events_table:
            print(event)
    except FileNotFoundError:
        print(f"Erreur : le fichier {ics_file} est introuvable.")
