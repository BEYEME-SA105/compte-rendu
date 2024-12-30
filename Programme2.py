import matplotlib.pyplot as plt
from datetime import datetime

# Exemple d'événements au format (date, type, groupe)
evenements = [
    ['10-09-2023', 'TP', 'A1'],
    ['12-09-2023', 'TP', 'A1'],
    ['05-10-2023', 'TP', 'A1'],
    ['19-11-2023', 'CM', 'A1'],
    ['25-12-2023', 'TP', 'A1']
]

# Initialisation d'un dictionnaire pour compter les TP par mois (clé: mois, valeur: compteur)
tp_par_mois = {'09': 0, '10': 0, '11': 0, '12': 0}

# Parcourir les événements et compter les TP pour le groupe A1
for date_str, evenement_type, groupe in evenements:
    if evenement_type == 'TP' and groupe == 'A1':
        mois = datetime.strptime(date_str, '%d-%m-%Y').strftime('%m')
        if mois in tp_par_mois:
            tp_par_mois[mois] += 1

# Préparer les données pour le graphique
mois = ['Septembre', 'Octobre', 'Novembre', 'Décembre']
nombre_tp = [tp_par_mois[mois_num] for mois_num in ['09', '10', '11', '12']]

# Créer le graphique en bâtons
plt.bar(mois, nombre_tp, color='blue')

# Ajouter des titres et des étiquettes
plt.title('Nombre de séances TP pour le groupe A1')
plt.xlabel('Mois')
plt.ylabel('Nombre de séances TP')

# Afficher le graphique
plt.show()

# Sauvegarder le graphique en PNG
plt.savefig('nombre_seances_tp.png')
