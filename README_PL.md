# System Inteligentnego Asystenta Szachowego

Projekt realizuje system śledzenia partii szachów fizycznych w czasie rzeczywistym z wykorzystaniem algorytmów wizji komputerowej (Computer Vision) oraz sztucznej inteligencji.

## 🏗 Architektura Systemu

System opiera się na architekturze mikrousług konteneryzowanych za pomocą Dockera:

1.  **AI Vision Service (AVS)**: Przetwarzanie obrazu z wielu kamer, detekcja figur za pomocą YOLOv8, transformacja perspektywy i fuzja danych.
2.  **Game Logic & API Service (GLAS)**: Zarządzanie stanem gry (python-chess), silnik Stockfish, komunikacja przez WebSockets.
3.  **Frontend UI**: Panel sterowania i wizualizacja deski w czasie rzeczywistym (React).
4.  **Message Broker**: RabbitMQ służący do asynchronicznej komunikacji między usługami.

## ✅ Zrealizowane Funkcjonalności

### 1. Wizja Komputerowa (AVS)
*   **Obsługa wielu kamer**: Dynamiczne wsparcie dla konfiguracji z **1, 2 lub 4 kamerami** jednocześnie.
*   **Fuzja danych (Multi-Camera Fusion)**: Autorski algorytm łączący wyniki z wielu kamer w celu eliminacji martwych pól i przesłonięć (occlusions).
*   **Kalibracja Interaktywna**: Narzędzie `calibrate.py` pozwalające na mapowanie narożników fizycznej deski do idealnego kwadratu 2D.
*   **Integracja YOLO**: Moduł detekcji figur gotowy do współpracy z modelem YOLOv8.
*   **Tryb Symulacji (Mock Capture)**: Możliwość użycia statycznych obrazów lub zapętlonych filmów wideo zamiast realnych kamer (sterowane przez `USE_MOCK_DATA`).


### 2. Logika i API (GLAS)
*   **Komunikacja Real-Time**: Serwer WebSockets przesyłający stan szachownicy do frontendu natychmiast po wykryciu zmiany.
*   **Tryb Symulacji (Mock)**: Wbudowany pętla testowa generująca ruchy szachowe, co pozwala na testowanie systemu bez fizycznego sprzętu.
*   **CORS & Health Checks**: Pełna konfiguracja bezpieczeństwa i monitoringu usług.

### 3. Interfejs Użytkownika (Web UI)
*   **Dynamiczny Dashboard**: Nowoczesny interfejs zbudowany w React i TailwindCSS.
*   **Automatyczna Synchronizacja**: Wirtualna szachownica reaguje na sygnały z backendu bez konieczności odświeżania strony.
*   **Monitor Statusu**: Podgląd stanu połączenia z usługami w czasie rzeczywistym.

## 🚀 Jak uruchomić projekt

### Wymagania
*   Docker & Docker Compose
*   (Opcjonalnie) Kamery USB podłączone do systemu

### Kroki instalacji

1.  **Sklonuj repozytorium**:
    ```bash
    git clone https://github.com/Nikitaaaaa1/chess_assistant.git
    cd chess_assistant
    ```

2.  **Uruchomienie kontenerów**:
    Aby uruchomić wszystkie usługi (AVS, GLAS, UI, RabbitMQ):
    ```bash
    docker-compose up --build
    ```

3.  **Konfiguracja kamer (Opcjonalnie)**:
    Domyślnie system szuka dwóch kamer. Możesz to zmienić w pliku `docker-compose.yml` lub ustawiając zmienną środowiskową:
    ```bash
    # Przykład dla 1 kamery
    export CAMERA_SOURCES=0
    # Przykład dla 4 kamer
    export CAMERA_SOURCES=0,1,2,3
    ```

### Dostęp do usług
*   **Frontend UI**: [http://localhost:3000](http://localhost:3000)
*   **API (FastAPI)**: [http://localhost:8000](http://localhost:8000)
*   **Panel RabbitMQ**: [http://localhost:15672](http://localhost:15672) (użytkownik/hasło: guest/guest)

## 🛠 Narzędzia Diagnostyczne

Aby skalibrować kamery ręcznie:
1. Wejdź do katalogu `chess-vision-service`.
2. Uruchom skrypt: `python calibrate.py [index_kamery] [id_konfiguracji]`.
   Przykład: `python calibrate.py 0 0` (kalibracja pierwszej kamery).

---
*Projekt realizowany w ramach prac uniwersyteckich nad systemami AI.*
