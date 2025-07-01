# Step 1: Usa un'immagine Python ufficiale e leggera come base
FROM python:3.11-slim

# Step 2: Imposta una directory di lavoro all'interno del container
WORKDIR /app

# Step 3: Copia solo il file delle dipendenze.
# Questo sfrutta la cache di Docker: se requirements.txt non cambia,
# Docker non rieseguirà l'installazione, rendendo le build successive più veloci.
COPY requirements.txt .

# Step 4: Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copia tutto il resto del progetto nel container
COPY . .

# Step 6: Comando di default (può essere sovrascritto da docker-compose)
# Questo è utile per il debug, per entrare nel container e lanciare i comandi a mano.
CMD ["pytest"]