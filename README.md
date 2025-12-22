# Moje Projekty

Ten folder zawiera zbiór moich projektów programistycznych, pogrupowanych według języka i platformy.

## C# / .NET / C++ / Assembly

### PhotoPix Image Pixelator

PhotoPix to aplikacja desktopowa dla systemu Windows, przeznaczona do nakładania efektu pikselacji na obrazy. Jej głównym celem jest demonstracja i porównanie wydajności różnych bibliotek backendowych — jednej napisanej w C++ i drugiej w ręcznie zoptymalizowanym asemblerze x64 (MASM) — wywoływanych z frontendu napisanego w C# .NET.

**Funkcje:**
*   Ładowanie obrazów w popularnych formatach (JPG, PNG, BMP).
*   Nakładanie efektu pikselacji (mozaiki).
*   Regulowany rozmiar pikseli.

## C++

### Tetris

Prosta, konsolowa implementacja klasycznej gry Tetris napisana w języku C++. Projekt działa w konsoli systemu Windows i oferuje system punktacji, rosnący poziom trudności oraz podgląd następnego klocka.

## Python / Google Cloud

### AI Agent Blueprint

Szablon agenta AI dla Google Chat, zintegrowany z usługami Google, takimi jak Gemini, Dysk Google i Arkusze Google. Został zaprojektowany jako modułowa i rozszerzalna podstawa do budowy zaawansowanych chatbotów.

**Struktura i komponenty:**
*   **AIAgent_Blueprint.py:** Główny plik aplikacji z serwerem Flask, obsługujący zdarzenia z Google Chat.
*   **Handlers:** Moduły do obsługi czatu, poczty e-mail, poleceń slash (np. `/about`, `/research`) oraz złożonych formularzy interaktywnych.
*   **Konfiguracja:** Pliki do zarządzania kluczami API, modelami AI oraz danymi serwera SMTP.
*   **Integracje:** Przykłady interakcji z API Dysku, Arkuszy i Prezentacji Google w celu automatyzacji zadań, takich jak generowanie dokumentów i wysyłanie powiadomień.

Projekt wykorzystuje uwierzytelnianie Google Cloud Application Default Credentials (ADC) i jest gotowy do wdrożenia na platformach takich jak Cloud Run czy App Engine.
