/*
Imię Nazwisko: [Twoje Imię]
Data: 2023/2024
Temat: Biblioteka C++ wykonująca efekt pixelowania (mozaiki).
Opis: Algorytm oblicza średnią koloru w blokach NxN i nadpisuje piksele.
*/

#include "pch.h"     
#include <cstdint>    
#include <algorithm>  

#define DLL_EXPORT extern "C" __declspec(dllexport)

/*
Parametry:
data      - Wskaźnik do pierwszego bajtu danych obrazu (format BGRA 32-bit)
width     - Szerokość obrazu w pikselach
height    - Wysokość obrazu w pikselach
stride    - Liczba bajtów na jeden wiersz obrazu (może zawierać padding!)
pixelSize - Rozmiar bloku (np. 16 dla kwadratu 16x16)
startRow  - Indeks wiersza, od którego ten wątek ma zacząć
endRow    - Indeks wiersza, na którym ten wątek ma skończyć
*/

DLL_EXPORT void PixelateCpp(uint8_t* data, int width, int height, int stride, int pixelSize, int startRow, int endRow)
{

    for (int y = startRow; y < endRow; y += pixelSize)
    {
        
        for (int x = 0; x < width; x += pixelSize)
        {
            // Zmienne na sumę kolorów w bloku
            long sumB = 0; // Blue
            long sumG = 0; // Green
            long sumR = 0; // Red
            int count = 0; // Liczba przetworzonych pikseli (ważne przy krawędziach)

            // Obliczamy granice aktualnego bloku (żeby nie wyjść poza obraz)
            int blockHeight = (pixelSize < height - y) ? pixelSize : (height - y);
            int blockWidth = (pixelSize < width - x) ? pixelSize : (width - x);

            // --- KROK 1: Sumowanie kolorów w bloku ---
            for (int by = 0; by < blockHeight; by++)
            {
                // Obliczamy wskaźnik na początek wiersza wewnątrz bloku
                // data + (numer wiersza * długość wiersza)
                uint8_t* rowPtr = data + (y + by) * stride;

                for (int bx = 0; bx < blockWidth; bx++)
                {
                    // Wskaźnik na konkretny piksel.
                    // (x + bx) * 4, bo każdy piksel ma 4 bajty (B, G, R, A)
                    int xOffset = (x + bx) * 4;

                    sumB += rowPtr[xOffset + 0];
                    sumG += rowPtr[xOffset + 1];
                    sumR += rowPtr[xOffset + 2];
                    // Alpha (offset + 3) pomijamy w obliczaniu średniej

                    count++;
                }
            }

            // Zabezpieczenie przed dzieleniem przez zero (teoretycznie niemożliwe, ale dobre dla stabilności)
            if (count == 0) continue;

            // Obliczamy średnie
            uint8_t avgB = (uint8_t)(sumB / count);
            uint8_t avgG = (uint8_t)(sumG / count);
            uint8_t avgR = (uint8_t)(sumR / count);

            // --- KROK 2: Zapisywanie średniego koloru do całego bloku ---
            for (int by = 0; by < blockHeight; by++)
            {
                uint8_t* rowPtr = data + (y + by) * stride;

                for (int bx = 0; bx < blockWidth; bx++)
                {
                    int xOffset = (x + bx) * 4;

                    rowPtr[xOffset + 0] = avgB;
                    rowPtr[xOffset + 1] = avgG;
                    rowPtr[xOffset + 2] = avgR;
                    // Alpha zostawiamy bez zmian lub ustawiamy na 255
                }
            }
        }
    }
}