def afficher_fichier_ics(nom_fichier):
    """Lit et affiche le contenu d'un fichier .ics."""
    try:
        with open(nom_fichier, 'r') as fichier:
            contenu = fichier.read()
            print("Contenu du fichier .ics :")
            print(contenu)
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{nom_fichier}' est introuvable.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

# Nom du fichier à lire
nom_fichier = input("entrez le nom du fichier : ")

# Appel de la fonction
afficher_fichier_ics(nom_fichier)
