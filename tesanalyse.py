import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from collections import Counter
import base64
from PIL import Image, ImageTk
import io
import threading
import time

class TcpdumpAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Network Traffic Analyzer Pro")
        self.geometry("1200x800")
        
        # Ajouter une icône (un exemple d'icône en base64)
        self.icon = """
        iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA
        7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGiSURBVFiF7ZY9
        SwNBEIYfRRELQVErwUpiBBsbjYKVjYVgYeGvsLCxFBTBwkbBwlZBEM0PWFiIhYVgYWFhYWFhYZFCFBQR
        FEXx42kxe2STu01yd5tA8IGD29md2Xdudm8XKikl0wDLQAyI5hitwDqwCbRbOS4BvcBn4KFSIh+xGQP6
        gKbIoy0GgAVg0rdFgd4yxL3RBwznIj8DjoEXwAAawE5A4eqY+Z6AHWA4l/wzMKrJPALnwHgZBLQMAhfA
        m3dWw/PuX2gDvZrME7DkJT0DrlwKCPE5L/mQ99vVxXQmVyKVgO99kxMR/36qgt9U0VclARu2ZmQS8L1v
        ciLifwcsAjXbIiKXQMheTLUK+NxnHonx95N34LeQ5CESxr/RJOA4YfwbXRFwnjD+jVEFvKWMf2NUAY0p
        498YVcBYyvg3RhWwmjL+jVEFbKSMf2OqKiRqtAFHwBewB9QXElDPcR24BZLA0R/Et4Ft4BYYsW3GzcAk
        cAB8AIlf4i+BQ2AKaHAh4IunwDGQyBA/AU6BTteJdYwC88ARMOc6WSX/K98sUS04RxuYywAAAABJRU5E
        rkJggg==
        """
        icon_data = base64.b64decode(self.icon)
        icon_image = Image.open(io.BytesIO(icon_data))
        photo = ImageTk.PhotoImage(icon_image)
        self.iconphoto(True, photo)

        # Thème sombre
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure(bg='#2b2b2b')
        
        # Variables
        self.filename = tk.StringVar()
        self.data = []
        self.is_monitoring = False
        
        # Interface
        self.create_widgets()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        self.create_status_bar()

    def create_status_bar(self):
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_widgets(self):
        # Frame principale avec style sombre
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Section sélection fichier avec style amélioré
        file_frame = ttk.LabelFrame(main_frame, text="Configuration")
        file_frame.pack(fill='x', pady=5)

        # Entrée fichier avec style
        entry_frame = ttk.Frame(file_frame)
        entry_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Entry(entry_frame, textvariable=self.filename, width=70).pack(side='left', padx=5)
        ttk.Button(entry_frame, text="📂 Parcourir", command=self.browse_file).pack(side='left', padx=5)
        
        # Boutons d'action
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="🔍 Analyser", command=self.analyze_file).pack(side='left', padx=5)
        self.monitor_button = ttk.Button(button_frame, text="▶️ Surveillance en direct", command=self.toggle_monitoring)
        self.monitor_button.pack(side='left', padx=5)
        ttk.Button(button_frame, text="💾 Exporter rapport", command=self.export_report).pack(side='left', padx=5)

        # Notebook pour les graphiques
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill='both', pady=5)

        # Onglets avec icônes
        self.traffic_tab = ttk.Frame(self.notebook)
        self.protocol_tab = ttk.Frame(self.notebook)
        self.ip_tab = ttk.Frame(self.notebook)
        self.flags_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.traffic_tab, text="📊 Trafic")
        self.notebook.add(self.protocol_tab, text="🔄 Protocoles")
        self.notebook.add(self.ip_tab, text="🌐 Adresses IP")
        self.notebook.add(self.flags_tab, text="🚩 Flags TCP")

    def toggle_monitoring(self):
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.monitor_button.configure(text="⏹️ Arrêter surveillance")
            self.status_var.set("Surveillance en cours...")
            threading.Thread(target=self.live_monitoring, daemon=True).start()
        else:
            self.monitor_button.configure(text="▶️ Surveillance en direct")
            self.status_var.set("Surveillance arrêtée")

    def live_monitoring(self):
        while self.is_monitoring:
            if self.filename.get():
                self.analyze_file(silent=True)
                self.status_var.set(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
            time.sleep(5)  # Actualisation toutes les 5 secondes

    def export_report(self):
        if not self.data:
            messagebox.showwarning("Attention", "Aucune donnée à exporter. Veuillez d'abord analyser un fichier.")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
            )
            if filename:
                self.generate_html_report(filename)
                messagebox.showinfo("Succès", "Rapport exporté avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exportation : {str(e)}")

    def generate_html_report(self, filename):
        # Création d'un rapport HTML basique
        html_content = f"""
        <html>
            <head>
                <title>Rapport d'analyse réseau - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    .section {{ margin: 20px 0; padding: 10px; border: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <h1>Rapport d'analyse réseau</h1>
                <div class="section">
                    <h2>Résumé</h2>
                    <p>Nombre total de paquets: {len(self.data)}</p>
                    <p>Période d'analyse: {min(d['timestamp'] for d in self.data)} à {max(d['timestamp'] for d in self.data)}</p>
                </div>
            </body>
        </html>
        """
        with open(filename, 'w') as f:
            f.write(html_content)

    def analyze_file(self, silent=False):
        if not self.filename.get():
            if not silent:
                messagebox.showerror("Erreur", "Veuillez sélectionner un fichier")
            return

        try:
            new_data = self.parse_tcpdump(self.filename.get())
            if not new_data:
                if not silent:
                    messagebox.showinfo("Aucun résultat", "Aucune donnée à analyser dans le fichier sélectionné.")
                return

            self.data = new_data
            self.plot_traffic_over_time(self.data, self.traffic_tab)
            self.plot_protocol_distribution(self.data, self.protocol_tab)
            self.plot_ip_connections(self.data, self.ip_tab)
            self.plot_tcp_flags(self.data, self.flags_tab)

        except Exception as e:
            if not silent:
                messagebox.showerror("Erreur", f"Erreur lors de l'analyse du fichier : {str(e)}")

    # [Garder les autres méthodes existantes comme parse_tcpdump, plot_traffic_over_time, etc.]

if __name__ == "__main__":
    app = TcpdumpAnalyzer()
    app.mainloop()