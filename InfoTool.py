# Tkinter gebruiken we om de GUI te maken
import tkinter as GUI
# Psutil gebruiken we om informatie van de computer op te vragen
# Bijvoorbeeld CPU-gebruik, RAM-gebruik en opslagruimte
import psutil
# Subprocess gebruiken we om een ander programma te openen (in dit geval een emulator))
import subprocess


# Deze functie haalt informatie van de computer op (alle info is van https://psutil.readthedocs.io/stable/ af te lezen)
def update_info():

    # Het huidige CPU gebruik als percentage ophalen
    cpu_gebruik = psutil.cpu_percent()

    # Het huidige RAM-gebruik als percentage ophalen
    ram_gebruik = psutil.virtual_memory().percent

    # Het opslaggebruik van de C-schijf als percentage ophalen
    # De dubbele \\ is nodig omdat het een Windows-pad is
    opslag_gebruik = psutil.disk_usage("C:\\").percent

    # De tekst van het CPU-label veranderen
    CpuLabel.config(text=f"CPU-gebruik: {cpu_gebruik}%")

    # De tekst van het RAM-label veranderen
    RamLabel.config(text=f"RAM-gebruik: {ram_gebruik}%")

    # De tekst van het opslaglabel veranderen
    OpslagLabel.config(text=f"Opslaggebruik: {opslag_gebruik}%")

    # Na 500 milliseconden deze functie opnieuw uitvoeren
    # 1000 milliseconden is 1 seconde
    Scherm.after(500, update_info)

    
# Deze functie opent een programma naar keuze (bijvoorbeeld een emulator)
def open_programma():

    # Vul hier het pad naar jouw programma of emulator in
    programma_pad = r"C:\Users\ReMarkt\Downloads\desmume-0.9.13-win64\DeSmuME_0.9.13_x64.exe"

    # Probeer het programma te openen
    try:

        # Het programma openen
        subprocess.Popen([programma_pad])

        # Een groene melding laten zien als het gelukt is
        StatusLabel.config(
            text="Het programma is geopend!",
            fg="green"
        )

    # Als het programma niet geopend kan worden
    except Exception:

        # Een rode foutmelding laten zien
        # Hierdoor crasht het programma niet
        StatusLabel.config(
            text="Het programma kon niet worden geopend.",
            fg="red"
        )

# Een nieuw Tkinter-venster maken
Scherm = GUI.Tk()

# De titel van het venster instellen
Scherm.title("Dylans PC Info Tool")

# De grootte van het venster instellen
# 400 is de breedte en 350 is de hoogte
Scherm.geometry("400x350")

# Voorkomen dat de gebruiker het venster groter of kleiner maakt
Scherm.resizable(True, True)

# Een persoonlijke achtergrondkleur instellen
Scherm.configure(bg="lightblue")

# Een titel bovenaan het venster maken
TitelLabel = GUI.Label(
    Scherm,
    text="Welkom bij Dylans PC Info Tool!",
    font=("Arial", 16, "bold"),
    bg="lightblue",
    fg="darkblue"
)

# De titel in het venster plaatsen
# pady voegt ruimte boven en onder het label toe
TitelLabel.pack(pady=20)

# Een label maken waarin het CPU-gebruik komt te staan
CpuLabel = GUI.Label(
    Scherm,
    text="CPU-gebruik: laden...",
    font=("Arial", 12),
    bg="lightblue"
)

# Het CPU-label in het venster plaatsen
CpuLabel.pack(pady=5)


# Een label maken waarin het RAM-gebruik komt te staan
RamLabel = GUI.Label(
    Scherm,
    text="RAM-gebruik: laden...",
    font=("Arial", 12),
    bg="lightblue"
)

# Het RAM-label in het venster plaatsen
RamLabel.pack(pady=5)

# Een label maken waarin het opslaggebruik komt te staan
OpslagLabel = GUI.Label(
    Scherm,
    text="Opslaggebruik: laden...",
    font=("Arial", 12),
    bg="lightblue"
)

# Het opslaglabel in het venster plaatsen
OpslagLabel.pack(pady=5)

# Een knop maken waarmee je jouw programma kunt openen
ProgrammaKnop = GUI.Button(
    Scherm,
    text="Open mij de emulator",

    # Bij een klik wordt de functie open_programma uitgevoerd
    # Hier mogen geen haakjes achter open_programma staan i found out the hard way xD
    command=open_programma,

    # Opmaak van de knop
    font=("Arial", 11, "bold"),
    bg="darkblue",
    fg="white"
)

# De knop in het venster plaatsen
ProgrammaKnop.pack(pady=20)

# Dit label laat zien of het openen gelukt is
StatusLabel = GUI.Label(
    Scherm,
    text="",
    font=("Arial", 10),
    bg="lightblue"
)

# Het statuslabel in het venster plaatsen
StatusLabel.pack(pady=5)

# De systeeminformatie voor het eerst ophalen
update_info()

# Het venster openhouden en reageren op knoppen
Scherm.mainloop()