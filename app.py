from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import threading
import time
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        try:
            # Utilisation de on_bad_lines pour ignorer les lignes problématiques
            df = pd.read_csv(filepath, on_bad_lines='skip')
            # Lancer l'interface Tkinter pour l'analyse du fichier
            app.tcpdump_analyzer = TcpdumpAnalyzer(filepath)
            app.tcpdump_analyzer.mainloop()
            return 'File uploaded and analyzed successfully'
        except pd.errors.ParserError as e:
            return f"Error reading the file: {str(e)}"

@app.route('/send-message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    # Logique pour traiter le message (par exemple, l'enregistrer dans une base de données ou l'envoyer par email)
    return f"Merci {name}, votre message a été envoyé avec succès !"

class TcpdumpAnalyzer(tk.Tk):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.title("Analyseur de fichiers tcpdump")
        self.geometry("1200x800")
        self.configure(bg='#2b2b2b')

        # Style pour le thème sombre
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabelFrame', background='#2b2b2b', foreground='white')
        style.configure('TLabel', background='#2b2b2b', foreground='white')
        style.configure('TButton', background='#2b2b2b', foreground='white')

        # Variables
        self.data = []
        self.is_monitoring = False
        
        # Interface
        self.create_widgets()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        self.create_status_bar()

        # Analyse initiale du fichier
        self.analyze_file()

    def create_status_bar(self):
        """Crée une barre de statut en bas de la fenêtre."""
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_widgets(self):
        # Frame principale
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Section sélection fichier
        file_frame = ttk.LabelFrame(main_frame, text="Sélection du fichier")
        file_frame.pack(fill='x', pady=5)

        ttk.Entry(file_frame, textvariable=tk.StringVar(value=self.filename), width=70).pack(side='left', padx=5, pady=5)
        ttk.Button(file_frame, text="🔍 Analyser", command=self.analyze_file).pack(side='left', padx=5)
        self.monitor_button = ttk.Button(file_frame, text="▶️ Surveillance en direct", command=self.toggle_monitoring)
        self.monitor_button.pack(side='left', padx=5)
        ttk.Button(file_frame, text="💾 Exporter rapport", command=self.export_report).pack(side='left', padx=5)

        # Notebook pour les différents graphiques
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill='both', pady=5)

        # Onglets
        self.traffic_tab = ttk.Frame(self.notebook)
        self.protocol_tab = ttk.Frame(self.notebook)
        self.ip_tab = ttk.Frame(self.notebook)
        self.flags_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.traffic_tab, text="📊 Trafic")
        self.notebook.add(self.protocol_tab, text="🔄 Protocoles")
        self.notebook.add(self.ip_tab, text="🌐 Adresses IP")
        self.notebook.add(self.flags_tab, text="🚩 Flags TCP")

    def parse_tcpdump(self, filename):
        data = []
        with open(filename, 'r') as file:
            for line in file:
                if not line.startswith('\t'):  # Ignorer les lignes hexadécimales
                    # Parser les informations importantes
                    timestamp_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{6})', line)
                    ip_match = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                    protocol_match = re.search(r'> .*?\.(\w+):', line)
                    flags_match = re.search(r'Flags \[(.*?)\]', line)
                    length_match = re.search(r'length (\d+)', line)

                    if timestamp_match and ip_match:
                        entry = {
                            'timestamp': datetime.strptime(timestamp_match.group(1), '%H:%M:%S.%f'),
                            'source_ip': ip_match[0] if ip_match else None,
                            'dest_ip': ip_match[1] if len(ip_match) > 1 else None,
                            'protocol': protocol_match.group(1) if protocol_match else 'Unknown',
                            'flags': flags_match.group(1) if flags_match else None,
                            'length': int(length_match.group(1)) if length_match else 0
                        }
                        data.append(entry)
        return data

    def plot_traffic_over_time(self, data, frame):
        # Nettoyer le frame
        for widget in frame.winfo_children():
            widget.destroy()

        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        df['length'].resample('1S').sum().plot(ax=ax)
        ax.set_title('Trafic réseau au fil du temps')
        ax.set_xlabel('Temps')
        ax.set_ylabel('Taille des paquets (octets)')
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')

    def plot_protocol_distribution(self, data, frame):
        for widget in frame.winfo_children():
            widget.destroy()

        protocols = Counter(d['protocol'] for d in data)
        total_count = sum(protocols.values())
        
        sorted_protocols = dict(sorted(protocols.items(), key=lambda x: x[1], reverse=True))
        values = list(sorted_protocols.values())
        labels = list(sorted_protocols.keys())
        
        fig = plt.figure(figsize=(10, 6))
        gs = fig.add_gridspec(1, 2, width_ratios=[1.5, 1])
        ax_pie = fig.add_subplot(gs[0])
        
        # Utilisation d'une palette de couleurs distinctes
        colors = plt.get_cmap('tab20')(np.linspace(0, 1, len(protocols)))
        wedges, _ = ax_pie.pie(values, labels=None, colors=colors, startangle=90)
        
        legend_labels = [f"{protocol} - {count/total_count:.1%}" for protocol, count in sorted_protocols.items()]
        
        ax_legend = fig.add_subplot(gs[1])
        ax_legend.axis('off')
        ax_legend.legend(wedges, legend_labels, title="Protocoles", loc='center left', frameon=True, fancybox=True, shadow=True)
        ax_pie.set_title('Distribution des protocoles réseau')
        plt.tight_layout(pad=2.0)
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')

    def plot_ip_connections(self, data, frame):
        for widget in frame.winfo_children():
            widget.destroy()

        source_ips = Counter(d['source_ip'] for d in data)
        dest_ips = Counter(d['dest_ip'] for d in data)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        source_df = pd.DataFrame.from_dict(source_ips, orient='index').head()
        source_df.plot(kind='bar', ax=ax1, legend=False)
        ax1.set_title('Top 5 IPs sources')
        ax1.set_ylabel('Nombre de paquets')
        
        dest_df = pd.DataFrame.from_dict(dest_ips, orient='index').head()
        dest_df.plot(kind='bar', ax=ax2, legend=False)
        ax2.set_title('Top 5 IPs destinations')
        ax2.set_ylabel('Nombre de paquets')
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')

    def plot_tcp_flags(self, data, frame):
        for widget in frame.winfo_children():
            widget.destroy()

        flags = Counter()
        for d in data:
            if d['flags']:
                for flag in d['flags'].split(','):
                    flags[flag.strip()] += 1
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(flags.keys(), flags.values())
        ax.set_title('Distribution des flags TCP')
        ax.set_ylabel('Nombre d\'occurrences')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')

    def analyze_file(self):
        if not self.filename:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier")
            return

        try:
            self.data = self.parse_tcpdump(self.filename)
            
            self.plot_traffic_over_time(self.data, self.traffic_tab)
            self.plot_protocol_distribution(self.data, self.protocol_tab)
            self.plot_ip_connections(self.data, self.ip_tab)
            self.plot_tcp_flags(self.data, self.flags_tab)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse du fichier: {str(e)}")

    def toggle_monitoring(self):
        self.is_monitoring = not self.is_monitoring
        state = "actif" if self.is_monitoring else "désactivé"
        self.monitor_button.config(text="⏸️ Arrêter la surveillance" if self.is_monitoring else "▶️ Surveillance en direct")
        self.status_var.set(f"Surveillance {state}.")
        if self.is_monitoring:
            threading.Thread(target=self.monitor_traffic).start()

    def monitor_traffic(self):
        while self.is_monitoring:
            time.sleep(1)
            new_data = self.parse_line("Simulated Line")
            self.data.append(new_data)
            self.display_traffic_data()
            self.display_protocol_data()
            self.display_ip_data()
            self.display_flags_data()

    def export_report(self):
        if not self.data:
            messagebox.showerror("Erreur", "Aucune donnée à exporter")
            return
        report_filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if report_filename:
            df = pd.DataFrame(self.data)
            df.to_csv(report_filename, index=False)
            self.status_var.set(f"Rapport exporté : {report_filename}")

if __name__ == '__main__':
    app.run(debug=True)