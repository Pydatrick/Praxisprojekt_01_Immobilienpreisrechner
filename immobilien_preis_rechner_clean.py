#######################
# .exe erstellen:
# 1. pyinstaller installieren: 
# pip istall pyinstaller
# 2. pyinstaller laufen lassen um eine .spec Datei zu erstellen
# oder eine vorhandene editieren:
# pyinstaller --onefile --noconsole --icon=icon.ico immobilien_preis_rechner_clean.py
#  -> es wird vermutlich beim ersten mal nicht klappen, sprich die Dateien wurden nicht mit in die exe-Datei gepackt
# 3. immobilien_preis_rechner_clean.SPEC öffnen und bearbeiten. Unter Data müsssne die Pfade der Dateien eingeflegt werden:
#     datas=[('Logo.png', '.'),
#           ('icon.ico', '.')  
#           ],
#######################

#######################
# Import
#######################

from reportlab.pdfgen import canvas                # Erstellt und bearbeitet PDFs
from reportlab.lib.pagesizes import A4             # A4 Format
import pandas as pd                                # Daten in Form von DataFrames zu laden und zu bearbeiten. hier Excel 
import tkinter as tk                               # Standard-Modul für die Erstellung von grafischen Benutzeroberflächen (GUIs) in Python. 
                                                   # Erstellt Fenster, Buttons, Textfelder und andere GUI-Elemente erstellen
from tkinter import  ttk                           # bietet erweiterte GUI-Komponenten : ttk.Button, ttk.Entry und ttk.Combobox
from tkinter import messagebox                     # Erstellt einfache Pop-up-Nachrichten in der GUI wie Fehlermeldungen oder Warnungen
from tkinter.filedialog import askopenfile         # Datei-Dialog, mit dem der Benutzer eine Datei auswählen kann. Das Modul ermöglicht es, eine Datei zu laden z.B. eine Excel-Datei
from tkinter import Toplevel                       # Erstellt neue Fenster (sogenannte "Top-Level"-Fenster). Unabhängige Fenster. Wird für das Impressum verwendet
import datetime as dt                              # Bibliothek zur Arbeit mit Datum und Uhrzeit. Wird für das akutelle Jahr verwendet
from PIL import Image, ImageTk                     # (Python Imaging Library) ist eine Bibliothek zur Bildverarbeitung. 
                                                   # Image wird verwendet, um Bilder zu öffnen, zu bearbeiten und zu speichern, während ImageTk hilft, Bilder in Tkinter-GUIs anzuzeigen
import os                                          # Modul, das eine Schnittstelle zu Betriebssystemfunktionen bereitstellt. 
                                                   # Es hilft, mit Dateien und Verzeichnissen zu arbeiten, Pfade zu erstellen oder zu analysieren und Umgebungsvariablen zu verwenden.
import sys                                         # Ermöglicht den Zugriff auf bestimmte Systemfunktionen und -parameter. Hier im Speziellen: Pfade und Verzeichnisstruktur

#######################
# Standardwerte (aus der Excel Datei) und Variablen initiieren
#######################

bundeslaender_standard_dict =  {"Baden-Württemberg": 1.5,
                                "Bayern": 1.7,
                                "Berlin": 2.1,
                                "Brandenburg": 1.1,
                                "Bremen": 1.2,
                                "Hamburg": 2.5,
                                "Hessen": 1.3,
                                "Mecklenburg-Vorpommern": 0.9,
                                "Niedersachsen": 1.0,
                                "Nordrhein-Westfalen": 1.1,
                                "Rheinland-Pfalz": 1.0,
                                "Saarland": 0.7,
                                "Sachsen": 0.7,
                                "Sachsen-Anhalt": 0.6,
                                "Schleswig-Holstein": 1.4,
                                "Thüringen": 0.6
                               }

region_standard_dict =         {"Land": 1,
                                "Stadt": 2
                               }

ausstattung_standard_dict =    {"Rohbau": 0.5,
                                "Sanierungsbedarf": 0.8,
                                "Renovierungsbedarf": 0.9,
                                "Einfach": 1.0,
                                "Gehoben": 2.0
                               }

hausart_standard_dict =        {"Einfamilienhaus": 1,
                                "Doppelhaushälfte": 0.8,
                                "Mehrfamilienhaus": 0.7
                               }

grundstueck_standard_preis  = 160
wohnflaeche_standard_preis  = 2500
architekt_standard_rate     = 0.2
makler_standard_rate        = 0.2
denkmalschutz_standard_rate = 0.2
baujahr_standard_rate       = 0.001

selected_bundesland  = None                             # Setze alle Auswahlen in der Combobox auf None                                                     
selected_region      = None
selected_ausstattung = None
selected_hausart     = None

config_status = False                                   # Überprüfen, ob eine Konfigurationsdatei geladen wurde   

#######################
# Klasse Immobilie mit Methoden zur Berechnung des Schätzwertes
#######################

class Immobilie:
   """  """
   
   def __init__(self,
                bundeslaender_dict:dict  = bundeslaender_standard_dict,       # Standardwerte von oben, falls nichts angegeben wird
                region_dict:dict         = region_standard_dict,
                ausstattung_dict:dict    = ausstattung_standard_dict,
                hausart_dict:dict        = hausart_standard_dict,
                grundstueck_preis:int    = grundstueck_standard_preis,
                wohnflaeche_preis:int    = wohnflaeche_standard_preis,
                architekt_rate:float     = architekt_standard_rate,
                makler_rate:float        = makler_standard_rate,
                denkmalschutz_rate:float = denkmalschutz_standard_rate,
                baujahr_rate:float       = baujahr_standard_rate,
                grundstuecksflaeche:int  = 0,                                 # Nutzereingabe
                wohnflaeche:int          = 0,                                 # Nutzereingabe
                baujahr:int              = 1900                               # Nutzereingabe
               ) -> None:
      
      self.bundeslaender_dict  = bundeslaender_dict
      self.region_dict         = region_dict
      self.ausstattung_dict    = ausstattung_dict
      self.hausart_dict        = hausart_dict
      self.grundstueck_preis   = grundstueck_preis
      self.wohnflaeche_preis   = wohnflaeche_preis
      self.architekt_rate      = architekt_rate
      self.makler_rate         = makler_rate
      self.denkmalschutz_rate  = denkmalschutz_rate
      self.baujahr_rate        = baujahr_rate
      self.grundstuecksflaeche = grundstuecksflaeche
      self.wohnflaeche         = wohnflaeche
      self.baujahr             = baujahr


   def grundpreis(self) -> int:                                                                    # Berechnet den Grundpreis
      """  """
      result_grundstueck = (self.grundstuecksflaeche - self.wohnflaeche) * self.grundstueck_preis  # Grunpreis Grundstück
      result_wohnflaeche = self.wohnflaeche * self.wohnflaeche_preis                               # Grundpreis Wohnfläche
      result = result_grundstueck + result_wohnflaeche                                             # Gesamtgrundpreis
      return result


   def baujahr_faktor(self) -> float:
      """  """
      result = 1 - (dt.date.today().year - self.baujahr) * self.baujahr_rate                       # Berechne Baujahrfaktor
      return result


   def berechnung(self, 
                  selected_bundesland:str,
                  selected_region:str, 
                  selected_ausstattung:str, 
                  selected_hausart:str, 
                  architekt_status:int,                                                            # Status ist int, 0 oder 1
                  makler_status:int, 
                  denkmalschutz_status:int
                 ) -> float:
      """  """
      
      result = round(self.bundeslaender_dict[selected_bundesland] *                                # Bundeslandfaktor
                     self.region_dict[selected_region] *                                           # Regionfaktor
                     self.ausstattung_dict[selected_ausstattung] *                                 # Ausstattungsfaktor
                     self.hausart_dict[selected_hausart] *                                         # Hausartfaktor
                     self.baujahr_faktor() *                                                       # Berechne Baujahrfaktor
                     (1 + int(architekt_status) * self.architekt_rate) *                           # Architektfaktor
                     (1 + int(makler_status) * self.makler_rate) *                                 # Maklerfaktor
                     (1 - int(denkmalschutz_status) * self.denkmalschutz_rate)*                    # Denkmalschutzfaktor
                     self.grundpreis(),                                                            # Berechne Grundpreis
                     2)                                                                            # Rundungsstellen
      return result
   
#######################
# TKinter Fenster mit Menu erstellen
#######################

def resource_path(relative_path):                           # Pfade und Verzeichnisstruktur bestimmen. Die Exe von Pyinstaller --onefile konnte die Bilder nicht finden.
    """ """
    try:                                                    # Zunächst wird versucht, den sys._MEIPASS zu verwenden.
         base_path = sys._MEIPASS                           # Dieser Wert wird von PyInstaller gesetzt, wenn eine Python-Anwendung als ausführbare Datei gepackt wurde.
                                                            # sys._MEIPASS gibt den temporären Ordner an, in dem PyInstaller die Ressourcen der Anwendung ablegt.

    except Exception:                                       # Falls sys._MEIPASS nicht gesetzt ist (also, wenn der Code nicht als ausführbare Datei läuft, 
         base_path = os.path.abspath(".")                   # sondern direkt als Skript), wird der base_path auf das aktuelle Arbeitsverzeichnis gesetzt (os.path.abspath(".")).

    return os.path.join(base_path, relative_path)           # Am Ende wird der vollständige Pfad zur Ressource durch die Funktion os.path.join(base_path, relative_path) gebildet,
                                                            # der den Basis-Pfad (entweder sys._MEIPASS oder das aktuelle Verzeichnis) mit dem relativ angegebenen Pfad der Ressource kombiniert.

# Real Estate Price Calculator REPC
window = tk.Tk()                                                                                     # Erstellt ein GUI Fenstser

window.geometry("700x370")                                                                           # Legt die Größe des Fensters fest
window.resizable(False, False)                                                                       # Fenstergröße kann nicht verändert werden
window.title("Real Estate Price Calculator")                                                         # Gibt dem Fenster einen Titel
icon_path = resource_path('icon.ico')                                                                # Path für Icons in der EXE
window.wm_iconbitmap(icon_path)                                                                      # Setzt das Icon

# Menubar erstellen
menubar = tk.Menu(window)                                                                            # Erstellt eine Menubar für das Fenster window
                                                                                                      
# Menubar Funktionen
def donothing():                                                                                     # Placeholder
   pass

def change_language() -> None:                                                                        # Noch nicht fertig
   pass

def config_load() -> None:                                                                            # Läd eine Konfig-Excel Datei
   """  """

   file = askopenfile(mode ='r', filetypes =[('Excel', '*.xlsx')])                                    # Zeigt nur .xlsx Dateien an

   if file is not None:
      file_path = file.name

   config_df = pd.read_excel(file_path, sheet_name="Preisinfo")                                       # Pandas liest Excel Datei in ein Dataframe ein

   bundeslaender_config_dict = dict(zip(list(config_df["Bundesland"].dropna()), 
                                        list(config_df["B-Kostenfaktor"].dropna())))                  # dropna ignoriert NaN Einträge
   region_config_dict        = dict(zip(list(config_df["Region"].dropna()), 
                                        list(config_df["R-Kostenfaktor"].dropna())))                  # Erstellung der Dictionaries
   ausstattung_config_dict   = dict(zip(list(config_df["Ausstattung"].dropna()), 
                                        list(config_df["A-Kostenfaktor"].dropna())))
   hausart_config_dict       = dict(zip(list(config_df["Hausart"].dropna()), 
                                        list(config_df["H-Kostenfaktor"].dropna())))


   grundstueck_config_preis  = list(config_df["Preis"])[0]
   wohnflaeche_config_preis  = list(config_df["Preis"])[1]
   architekt_config_rate     = list(config_df["Preis"])[2]
   makler_config_rate        = list(config_df["Preis"])[3]
   denkmalschutz_config_rate = list(config_df["Preis"])[4]
   baujahr_config_rate       = list(config_df["Preis"])[5]

   messagebox.showerror("Meldung","Konfiguration geladen!")
   global config_status, config_list                                          # globale Variablen
   config_status = True
   config_list =   [bundeslaender_config_dict,
                    region_config_dict,
                    ausstattung_config_dict,
                    hausart_config_dict,
                    grundstueck_config_preis,
                    wohnflaeche_config_preis,
                    architekt_config_rate,
                    makler_config_rate,
                    denkmalschutz_config_rate,
                    baujahr_config_rate
                   ]
   combobox_bundesland["values"]  = list(bundeslaender_config_dict.keys())      # Combobox-Werte ändern
   combobox_region["values"]      = list(region_config_dict.keys())
   combobox_ausstattung["values"] = list(ausstattung_config_dict.keys())
   combobox_hausart["values"]     = list(hausart_config_dict.keys())
   reset_all()                                                                  # Alle Werte zurücksetzen 


def config_delete() -> None:                                                    # Standardwerte wiederhergestellt
   """  """
   global config_status
   config_status = False

   combobox_bundesland["values"]  = list(bundeslaender_standard_dict.keys())    
   combobox_region["values"]      = list(region_standard_dict.keys())
   combobox_ausstattung["values"] = list(ausstattung_standard_dict.keys())
   combobox_hausart["values"]     = list(hausart_standard_dict.keys())
   messagebox.showerror("Meldung","Standardwerte wiederhergestellt")
   reset_all()

   # Impressum
def impressum() -> None:
   """  """
   impressum_window = tk.Toplevel(window)                                           # Erstellt neues Fenster über das Hauptfenster                                  
   impressum_window.title("Impressum")
   impressum_window.geometry("700x400")

   title = tk.Label(impressum_window, text="Impressum", font=("Arial", 16, "bold"))
   title.pack(pady=10)

   impressum_content = ("Firmenname: Hartstock, Krause & Schoer Real Estate AG\n"
                        "Adresse: Musterstraße 123, 12345 Musterstadt\n"
                        "Telefon: +49 123 456 789\n"
                        "E-Mail: kontakt@hks-realestate.de\n"
                        "Vertretungsberechtigter Geschäftsführer: Patrick Krause\n"
                        "Handelsregister: HRB 12345, Amtsgericht Musterstadt\n"
                        "USt-IdNr.: DE123456789"
                       )
   
   content_label = tk.Label(impressum_window, text=impressum_content, font=("Arial", 10), justify="left")
   content_label.pack(padx=20, pady=10)

   close_button = tk.Button(impressum_window, text="Schließen", command=impressum_window.destroy)
   close_button.pack(pady=10)
   
#######################
# Menubar
#######################

# Datei
filemenu = tk.Menu(menubar, tearoff=0)                                        # Tearoff 0 -> Fenster ist angeheftet    
filemenu.add_command(label="Kofiguration laden", command=config_load)         # command Funktion wird ausgeführt, wenn man den Button drückt
filemenu.add_command(label="Standardwerte laden", command=config_delete)      # Aufpassen: Button Funktionen mit () am Ende werden sofort ausgeführt bei Erstellung des Buttons
filemenu.add_separator()
filemenu.add_command(label="Beenden", command=window.destroy)
menubar.add_cascade(label="Datei", menu=filemenu)

# Sprache
languagemenu = tk.Menu(menubar, tearoff=0)
languagemenu.add_command(label="Deutsch", command=donothing)
languagemenu.add_command(label="English", command=donothing)
languagemenu.add_command(label="日本語", command=donothing)
menubar.add_cascade(label="Language", menu=languagemenu)

# Hilfe
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_separator()
helpmenu.add_command(label="Über", command=impressum)
menubar.add_cascade(label="Hilfe", menu=helpmenu)

# den Reiter Sprache durchwechseln lassen:
language_index = 0

def switch_language() -> None:
   """  """
   global language_index
   languages = ["Sprache", "Language", "言語"]
   menubar.entryconfig(2, label=languages[language_index])  # Ändert das Label von Menubar an der Stelle 2 -> label von languagemenu
   language_index = (language_index + 1) % len(languages)
   window.after(5000, switch_language)                      # Führt sich selbst nach 5000ms aus

window.after(5000, switch_language)                         # Führt nach 5000ms die Funktion switch_language aus

#######################
# Comboboxen, Checkbuttons, Entry-Widgets
#######################

# Comboboxen Auswahl Funktion
def select_combobox(event, combobox_name:str) -> None:
   """  """                                                                                             # Wenn eine Bundesland ausgewählt wird, wird es gespeichert
   global selected_bundesland, selected_region
   global selected_ausstattung, selected_hausart

   if combobox_name == "bundesland":
      selected_bundesland = event.widget.get()                                                          # Speichert den momentan ausgewählten Combobox Inhalt als globale variable
   elif combobox_name =="region":                                                                       # In event ist der Wert und welches Widget den Wert beinhaltet gespeichert
      selected_region = event.widget.get()                                                              # mit event.widget.get bekommt man den jeweiligen Wert der zugehörigen Combobox
   elif combobox_name == "ausstattung":
      selected_ausstattung = event.widget.get() 
   elif combobox_name == "hausart":
      selected_hausart = event.widget.get()

#######################
# Comboboxen
#######################
# Combobox Bundesländer                                                          
bundeslaender             = list(bundeslaender_standard_dict.keys())                                    # Liste der Bundesländer aus dem Dictionary bundeslaender_standard                  
label_combobox_bundesland = tk.Label(window, text="Bundesland auswählen:")                              # Label für Combobox  
combobox_bundesland       = ttk.Combobox(window, values=bundeslaender, state="readonly")                # "readonly" damit man nicht in die Box tippen kann
combobox_bundesland.set("Bundesland")                                                                   # Defaul Wert der Combobox
combobox_bundesland.bind("<<ComboboxSelected>>", lambda event: select_combobox(event, "bundesland"))    # Event Handle, wird etwas ausgewählt, wird select funktion ausgeführt

# Combobox Region
regionen              = list(region_standard_dict.keys())                                               # Liste der Regionen aus dem Dictionary region_standard                  
label_combobox_region = tk.Label(window, text="Region auswählen:")                                      # Label für Combobox
combobox_region       = ttk.Combobox(window, values=regionen, state="readonly")
combobox_region.set("Region")                                                                           # Defaul Wert der Combobox
combobox_region.bind("<<ComboboxSelected>>", lambda event: select_combobox(event, "region"))            # Event Handle: wird etwas ausgewählt, wird die jeweilige select funktion ausgeführt

# Combobox Ausstatttung
austattungen               = list(ausstattung_standard_dict.keys())                                     # Liste der Regionen aus dem Dictionary ausstattungen_standard              
label_combobox_ausstattung = tk.Label(window, text="Ausstattung auswählen:")                            # Label für Combobox
combobox_ausstattung       = ttk.Combobox(window, values=austattungen, state="readonly")
combobox_ausstattung.set("Ausstattung")                                                                 # Defaul Wert der Combobox
combobox_ausstattung.bind("<<ComboboxSelected>>", lambda event: select_combobox(event, "ausstattung"))  # Event Handle, wird etwas ausgewählt, wird select funktion ausgeführt

# Combobox Hausart
hausart                = list(hausart_standard_dict.keys())                                             # Liste der Regionen aus dem Dictionary hausart_standard                  
label_combobox_hausart = tk.Label(window, text="Hausart auswählen:")                                    # Label für Combobox
combobox_hausart       = ttk.Combobox(window, values=hausart, state="readonly")
combobox_hausart.set("Hausart")                                                                         # Defaul Wert der Combobox
combobox_hausart.bind("<<ComboboxSelected>>", lambda event: select_combobox(event, "hausart"))          # Event Handle, wird etwas ausgewählt, wird select funktion ausgeführt

#######################
# Checkbuttons
#######################
# Checkbuttons Architekt
label_checkbutton_architekt = tk.Label(window, text ="Architekt:")
checkbutton_architekt_var   = tk.IntVar()                                                               # Erstellt Variable. Kann mit .get() ausgelesen werden.                 
checkbutton_architekt       = tk.Checkbutton(window, variable=checkbutton_architekt_var)                # Erstellt Checkbuttons und verknüft mit Variablen

# Checkbuttons Makler
label_checkbutton_makler = tk.Label(window, text ="Makler:")                                              
checkbutton_makler_var   = tk.IntVar()                                                                    # 1 für ausgewählt, 0 für nicht ausgewählt
checkbutton_makler       = tk.Checkbutton(window, variable=checkbutton_makler_var)

# Checkbuttons Denkmalschutz
label_checkbutton_denkmalschutz = tk.Label(window, text ="Denkmalschutz:")
checkbutton_denkmalschutz_var   = tk.IntVar()
checkbutton_denkmalschutz       = tk.Checkbutton(window, variable=checkbutton_denkmalschutz_var)

#######################
# Entry-Widgets (Eingabefelder)
#######################

# Grundstückfläche
label_grundstuecksflaeche = tk.Label(window, text='Wie viel m² Grundstücksfläche?')                     # Erstellt Label für das Entry Grundstücksfläche
entry_grundstuecksflaeche = tk.Entry(window)                                                            # Erstellt Entry (Eingabefeld)

# Wohnfläche
label_wohnflaeche = tk.Label(window, text='Wie viel m² Wohnfläche?')                                    # Erstellt Label für das Entry Wohnfläche
entry_wohnflaeche = tk.Entry(window)                                                                    # Erstellt Entry (Eingabefeld)

# Baujahr   
label_baujahr = tk.Label(window, text='Welches Baujahr?')                                               # Erstellt Label
entry_baujahr = tk.Entry(window)                                                                        # Erstellt Entry (Eingabefeld)

#######################
# Button Funktion: Berechnung
#######################
def button_berechnung_command() -> None:
   """  """
   try:
      # Benutzeingaben                                                                                                                                                                                   
      input_grundstuecksflaeche = entry_grundstuecksflaeche.get()                                     # .get() gibt den aktuellen Wert der Widget Variablen zurück    
      input_wohnflaeche         = entry_wohnflaeche.get()                                             # in diesem Fall die drei eingegebenen Integer
      input_baujahr             = entry_baujahr.get()
      architekt_status          = checkbutton_architekt_var.get()                                     # .get() gibt den aktuellen Wert der Widget Variablen zurück
      makler_status             = checkbutton_makler_var.get()                                        # in diesem Fall 0 oder 1, jenachdem ob ein Kästchen markiert wurde
      denkmalschutz_status      = checkbutton_denkmalschutz_var.get()

      fehlender_input = []
      
      # Überprüfung, ob Werte ausgewählt wurden
      if selected_bundesland is None:
         fehlender_input.append("Bundesland")
      if selected_region is None:
         fehlender_input.append("Region")
      if selected_ausstattung is None:
         fehlender_input.append("Ausstattung")
      if selected_hausart is None:
         fehlender_input.append("Hausart")
      if not input_grundstuecksflaeche: 
         fehlender_input.append("Grundstücksfläche")
      if not input_wohnflaeche: 
         fehlender_input.append("Wohnfläche")
      if not input_baujahr:  
         fehlender_input.append("Baujahr")
      
      # Liste mit fehlenden Werten erstellen und als Fehler ausgeben    
      if fehlender_input:
         fehlender_input_str = ", ".join(fehlender_input)
         messagebox.showerror("Fehlende oder ungültige Eingaben",
                             f"Bitte geben Sie ein(e) gültige(s) {fehlender_input_str} ein."
                             )
         return  
                
      falscher_input = []
      # Überprüfung ob falsche Werte eingetragen wurden, z.B. keine Zahlen  
      if not input_grundstuecksflaeche.isdigit():
            falscher_input.append("Grundstücksfläche")
      if not input_wohnflaeche.isdigit():
            falscher_input.append("Wohnfläche")
      if not input_baujahr.isdigit():
            falscher_input.append("Baujahr")

      # Liste mit falschen Werten erstellen und als Fehler ausgeben   
      if falscher_input:
            falscher_input_str = ", ".join(falscher_input)
            messagebox.showerror("Ungültige Eingabe", 
                                f"Bitte geben Sie ein(e) gültige(s) {falscher_input_str} ein."
                                )
            return
      
      # Überprüfung, ob das Baujahr in der Vergangenheit liegt
      current_year = dt.datetime.now().year
      if input_baujahr:
         baujahr = int(input_baujahr) 
      if baujahr > current_year:
         messagebox.showerror("Ungültiges Baujahr", "Das Baujahr kann nicht in der Zukunft liegen.")
         return
      
      # Konfiguation überprüfen
      global config_status
      global config_list
      
      if config_status == False:
         immobilie = Immobilie(grundstuecksflaeche = int(input_grundstuecksflaeche),             # Standardwerte nutzen, die in der Klasse vordefiniert sind
                               wohnflaeche         = int(input_wohnflaeche),
                               baujahr             = int(input_baujahr)
                              )
      else:
         immobilie = Immobilie(bundeslaender_dict  = config_list[0],                            # Werte aus der Konfigurationsliste benutzen   
                               region_dict         = config_list[1],
                               ausstattung_dict    = config_list[2],
                               hausart_dict        = config_list[3],
                               grundstueck_preis   = config_list[4],
                               wohnflaeche_preis   = config_list[5],
                               architekt_rate      = config_list[6],
                               makler_rate         = config_list[7],
                               denkmalschutz_rate  = config_list[8],
                               baujahr_rate        = config_list[9],
                               grundstuecksflaeche = int(input_grundstuecksflaeche),
                               wohnflaeche         = int(input_wohnflaeche),
                               baujahr             = int(input_baujahr)
                              )

      schaetzwert = immobilie.berechnung(selected_bundesland,                                # Berechnungs Methode aus der Klasse Immobilie
                                         selected_region,
                                         selected_ausstattung,
                                         selected_hausart,
                                         architekt_status,
                                         makler_status,
                                         denkmalschutz_status
                                        )
      label_output_text.config(text="Deine Immobilie hat den Schätzwert:")                   # Ausgabe des Ergebnisses
      label_output_result.config(text=f"{schaetzwert:,.2f}€")                                # Stringformat 2 Nachkommastellen

   except Exception as alle_fehler:                                                          # Sicherheitshalber, um unbekannte Fehler abzufangen
        messagebox.showerror("Fehler", f"Es ist ein Fehler aufgetreten: {str(alle_fehler)}")

#######################
# Button Funktion: PDF Erstellung, 
#######################
def pdf_create():
   """  """
   try:
      # Benutzeingaben  
      input_grundstuecksflaeche = entry_grundstuecksflaeche.get()                                     # .get() gibt den aktuellen Wert der Widget Variablen zurück    
      input_wohnflaeche         = entry_wohnflaeche.get()                                             # in diesem Fall die drei eingegebenen Integer
      input_baujahr             = entry_baujahr.get()
      architekt_status          = checkbutton_architekt_var.get()                                     # .get() gibt den aktuellen Wert der Widget Variablen zurück
      makler_status             = checkbutton_makler_var.get()                                        # in diesem Fall 0 oder 1, jenachdem ob ein Kästchen markiert wurde
      denkmalschutz_status      = checkbutton_denkmalschutz_var.get()


      # Schätzwert berechnen
      # Konfiguation überprüfen
      global config_status
      global config_list
      
      if config_status == False:
         immobilie = Immobilie(grundstuecksflaeche = int(input_grundstuecksflaeche),                  # Standardwerte nutzen, die in der Klasse vordefiniert sind
                               wohnflaeche         = int(input_wohnflaeche),
                               baujahr             = int(input_baujahr)
                              )
      else:
         immobilie = Immobilie(bundeslaender_dict = config_list[0],                                   # Werte aus der Konfigurationsliste benutzen    
                              region_dict         = config_list[1],
                              ausstattung_dict    = config_list[2],
                              hausart_dict        = config_list[3],
                              grundstueck_preis   = config_list[4],
                              wohnflaeche_preis   = config_list[5],
                              architekt_rate      = config_list[6],
                              makler_rate         = config_list[7],
                              denkmalschutz_rate  = config_list[8],
                              baujahr_rate        = config_list[9],
                              grundstuecksflaeche = int(input_grundstuecksflaeche),
                              wohnflaeche         = int(input_wohnflaeche),
                              baujahr             = int(input_baujahr)
                              )

      schaetzwert = immobilie.berechnung(selected_bundesland,
                                         selected_region,
                                         selected_ausstattung,
                                         selected_hausart,
                                         architekt_status,
                                         makler_status,
                                         denkmalschutz_status
                                        )
      # Übersetzte 1 und 0 in "Ja" und Nein für das PDF
      architekt_text     = "Ja" if architekt_status else "Nein"
      makler_text        = "Ja" if makler_status else "Nein"
      denkmalschutz_text = "Ja" if denkmalschutz_status else "Nein"

      # PDF erstellen
      filename = "Immobilien_Schaetzwert.pdf"
      c = canvas.Canvas(filename, pagesize = A4)                                    # Erstellt PDF
      c.setFont("Courier", 18)                                                      # Font und Schriftgröße
      c.drawString(100, 750, "Immobilien Schätzwert Berechnung")                    # Schreibt einen String in die PDF an den angegebenen Positionen

      # Ausgewählte Daten in das PDF schreiben
      c.setFont("Courier", 16)
      c.drawString(100, 720, f"Bundesland: {selected_bundesland}")
      c.drawString(100, 700, f"Region: {selected_region}")
      c.drawString(100, 680, f"Ausstattung: {selected_ausstattung}")
      c.drawString(100, 660, f"Hausart: {selected_hausart}")
      c.drawString(100, 640, f"Architekt: {architekt_text}")
      c.drawString(100, 620, f"Makler: {makler_text}")
      c.drawString(100, 600, f"Denkmalschutz: {denkmalschutz_text}")
      c.drawString(100, 580, f"Grundstücksfläche: {input_grundstuecksflaeche} m²")
      c.drawString(100, 560, f"Wohnfläche: {input_wohnflaeche} m²")
      c.drawString(100, 540, f"Baujahr: {input_baujahr}")
      c.drawString(100, 500, f"Schätzwert: {schaetzwert:,.2f}€")
      c.drawImage(bild_pfad, 450, 780, width=150, height=50, preserveAspectRatio=True, mask='auto')   # Logo in das PDF schreiben
      c.showPage()

      # PDF speichern
      c.save()

   # Fehlermeldung
   except Exception as pdf_fehler:
         messagebox.showerror("Fehler", f"Es gab einen Fehler beim Erstellen der PDF: {pdf_fehler}")

#######################
# Button Funktion: Reset
#######################
def reset_all() -> None:
   """  """
   # Comboboxen Anzeige
   combobox_bundesland.set("Bundesland")  
   combobox_region.set("Region")          
   combobox_ausstattung.set("Ausstattung") 
   combobox_hausart.set("Hausart")

   # Comboboxwerte
   global selected_bundesland, selected_region
   global selected_ausstattung, selected_hausart
   selected_bundesland  = None                                                               # Werte auf None um später zu prüfen, ob etwas ausgewählt wurde.
   selected_region      = None
   selected_ausstattung = None
   selected_hausart     = None       

   # Checkbuttons
   checkbutton_architekt_var.set(0)       
   checkbutton_makler_var.set(0)         
   checkbutton_denkmalschutz_var.set(0)   

   # Entry 
   entry_grundstuecksflaeche.delete(0, tk.END)                                               # tk.END: Der Index für das Ende des Texts im Widget.
   entry_wohnflaeche.delete(0, tk.END)          
   entry_baujahr.delete(0, tk.END)              

   # Label
   label_output_text.config(text="")
   label_output_result.config(text="")

#######################
# Fenster Design
#######################

label_welcome = tk.Label(window, text='Willkommen!')    # Erstellt ein Label im Fenster "window"

bild_pfad = resource_path('Logo.png')                   # Bildpfad setzen mit Hilfe der resource_path Funktion
image = Image.open(bild_pfad)                           # Bild laden
image = image.resize((340, 200))                        # Bildgröße auf 340x200 Pixel ändern
photo = ImageTk.PhotoImage(image)

label = tk.Label(window, image=photo)                   # Label mit Bild erstellen
label.image = photo                                     # WICHTIG: Referenz speichern, sonst wird das Bild gelöscht
                                              
# Button Berechnung
button_berechnung = tk.Button(window, text="Berechne", width=14,command=button_berechnung_command)  # Erstellt Button mit der berechnungs Funktion
# Button Reset
button_reset = tk.Button(window, text="Reset", width=14, command=reset_all)                         # Erstellt Button mit der reset Funktion
# Button PDF
button_pdf = tk.Button(window, text='PDF erstellen', width=14, command=pdf_create)                  # Erstellt Button mit der pdf Funktion

# Label Ausgabe
label_output_text = tk.Label(window, text="")
label_output_result = tk.Label(window, text="") 

#######################
# Layout Manager
#######################
# Label
label_welcome.grid(row=0, column=0, columnspan=2, sticky=tk.N)                                      # .grid(): row und column geben die Positionen an
label_combobox_bundesland.grid(row=1, column=0, sticky=tk.W)                                        # rowspan oder columnspan über wieviele Zeilen und Spalten ein Widget gehen soll
label_combobox_region.grid(row=2,  column=0, sticky=tk.W)                                           # sticky gibt die Ausrichtung an
label_combobox_ausstattung.grid(row=3,  column=0, sticky=tk.W)
label_combobox_hausart.grid(row=4, column=0, sticky=tk.W)
label_checkbutton_architekt.grid(row=5, column=0, sticky=tk.W)
label_checkbutton_makler.grid(row=6, column=0, sticky=tk.W) 
label_checkbutton_denkmalschutz.grid(row=7, column=0, sticky=tk.W)
label_grundstuecksflaeche.grid(row=8, column=0, sticky=tk.W) 
label_wohnflaeche.grid(row=9, column=0, sticky=tk.W)
label_baujahr.grid(row=10, column=0, sticky=tk.W)
label_output_text.grid(row=12, columnspan=2) 
label_output_result.grid(row=13, columnspan=2)  

# Widgets
combobox_bundesland.grid(row=1, column=1, sticky=tk.W)
combobox_region.grid(row=2, column=1, sticky=tk.W)
combobox_ausstattung.grid(row=3, column=1,  sticky=tk.W)
combobox_hausart.grid(row=4, column=1, sticky=tk.W)
checkbutton_architekt.grid(row=5, column=1, sticky=tk.W)
checkbutton_makler.grid(row=6, column=1, sticky=tk.W)
checkbutton_denkmalschutz.grid(row=7, column=1, sticky=tk.W)
entry_grundstuecksflaeche.grid(row=8, column=1,sticky=tk.W)
entry_wohnflaeche.grid(row=9, column=1, sticky=tk.W)
entry_baujahr.grid(row=10, column=1, sticky=tk.W)

# Buttons
button_berechnung.grid(row=10, column=3, columnspan=2, padx=(10,0),sticky=tk.W)
button_reset.grid(row=10, column=4, columnspan=2, padx=(10,10))
button_pdf.grid(row=10,column=5, columnspan=2,padx=(0,10),sticky=tk.E)        # padx Einrücken links, rechts Pixel

# Bild
label.grid(row=0, column=4, columnspan=2, rowspan=10, padx=10, pady=(20,5))   # Bild über Spalten 4 und 5 erstrecken, pady Einrücken oben , unten Pixel

# Starten des GUI
window.config(menu=menubar)
window.mainloop()            