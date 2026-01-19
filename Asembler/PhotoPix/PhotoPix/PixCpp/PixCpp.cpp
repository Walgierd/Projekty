/*
Imię Nazwisko: Olivier Trela
Data:           19.01.2026
Temat:          Biblioteka C++ wykonująca efekt pixelowania (mozaiki).
Wersja:         2.0
Opis:           Algorytmy: Średnia (Average), Mediana (Median), Losowy (Random).
*/

#include "pch.h"
#include <cstdint>
#include <vector>
#include <algorithm>
#include <random>

#define DLL_EXPORT extern "C" __declspec(dllexport)

// --- Struktury i funkcje pomocnicze ---

struct PixelColor {
    uint8_t b, g, r;
};

// Sortowanie po luminancji dla mediany
bool comparePixels(const PixelColor& a, const PixelColor& b) {
    return (0.299 * a.r + 0.587 * a.g + 0.114 * a.b) < (0.299 * b.r + 0.587 * b.g + 0.114 * b.b);
}

// --- Implementacje ---

/*
Nazwa: PixelateCpp_Average
Opis:  Oblicza średnią arytmetyczną kolorów w bloku.
*/
DLL_EXPORT void PixelateCpp_Average(uint8_t* data, int width, int height, int stride, int pixelSize, int startRow, int endRow)
{
    for (int y = startRow; y < endRow; y += pixelSize) {
        for (int x = 0; x < width; x += pixelSize) {
            long sumB = 0, sumG = 0, sumR = 0;
            int count = 0;
            int blockH = (std::min)(pixelSize, height - y);
            int blockW = (std::min)(pixelSize, width - x);

            for (int by = 0; by < blockH; by++) {
                uint8_t* row = data + (y + by) * stride;
                for (int bx = 0; bx < blockW; bx++) {
                    int offset = (x + bx) * 4;
                    sumB += row[offset + 0];
                    sumG += row[offset + 1];
                    sumR += row[offset + 2];
                    count++;
                }
            }

            if (count == 0) continue;
            uint8_t avgB = (uint8_t)(sumB / count);
            uint8_t avgG = (uint8_t)(sumG / count);
            uint8_t avgR = (uint8_t)(sumR / count);

            for (int by = 0; by < blockH; by++) {
                uint8_t* row = data + (y + by) * stride;
                for (int bx = 0; bx < blockW; bx++) {
                    int offset = (x + bx) * 4;
                    row[offset + 0] = avgB;
                    row[offset + 1] = avgG;
                    row[offset + 2] = avgR;
                }
            }
        }
    }
}

/*
Nazwa: PixelateCpp_Median
Opis:  Wybiera kolor będący medianą (środkową wartością) w bloku.
*/
DLL_EXPORT void PixelateCpp_Median(uint8_t* data, int width, int height, int stride, int pixelSize, int startRow, int endRow)
{
    std::vector<PixelColor> blockPixels;
    // Rezerwacja pamięci dla wydajności (max rozmiar bloku)
    blockPixels.reserve(pixelSize * pixelSize);

    for (int y = startRow; y < endRow; y += pixelSize) {
        for (int x = 0; x < width; x += pixelSize) {
            blockPixels.clear();
            int blockH = (std::min)(pixelSize, height - y);
            int blockW = (std::min)(pixelSize, width - x);

            for (int by = 0; by < blockH; by++) {
                uint8_t* row = data + (y + by) * stride;
                for (int bx = 0; bx < blockW; bx++) {
                    int offset = (x + bx) * 4;
                    blockPixels.push_back({ row[offset + 0], row[offset + 1], row[offset + 2] });
                }
            }

            if (blockPixels.empty()) continue;
            
            size_t medianIndex = blockPixels.size() / 2;
            std::nth_element(blockPixels.begin(), blockPixels.begin() + medianIndex, blockPixels.end(), comparePixels);
            PixelColor medianColor = blockPixels[medianIndex];

            for (int by = 0; by < blockH; by++) {
                uint8_t* row = data + (y + by) * stride;
                for (int bx = 0; bx < blockW; bx++) {
                    int offset = (x + bx) * 4;
                    row[offset + 0] = medianColor.b;
                    row[offset + 1] = medianColor.g;
                    row[offset + 2] = medianColor.r;
                }
            }
        }
    }
}

/*
Nazwa: PixelateCpp_Random
Opis:  Wybiera losowy piksel z danego bloku i wypełnia nim cały blok.
*/
DLL_EXPORT void PixelateCpp_Random(uint8_t* data, int width, int height, int stride, int pixelSize, int startRow, int endRow)
{
    // Inicjalizacja generatora losowego (raz na wywołanie wątku)
    std::mt19937 rng(std::random_device{}());

    for (int y = startRow; y < endRow; y += pixelSize) {
        for (int x = 0; x < width; x += pixelSize) {
            int blockH = (std::min)(pixelSize, height - y);
            int blockW = (std::min)(pixelSize, width - x);

            if (blockW <= 0 || blockH <= 0) continue;

            std::uniform_int_distribution<int> randX(0, blockW - 1);
            std::uniform_int_distribution<int> randY(0, blockH - 1);
            int chosenX = randX(rng);
            int chosenY = randY(rng);

            // Pobranie koloru wylosowanego piksela
            uint8_t* row = data + (y + chosenY) * stride;
            int offset = (x + chosenX) * 4;
            PixelColor randomColor = { row[offset + 0], row[offset + 1], row[offset + 2] };

            // Zapisanie koloru do całego bloku
            for (int by = 0; by < blockH; by++) {
                uint8_t* writeRow = data + (y + by) * stride;
                for (int bx = 0; bx < blockW; bx++) {
                    int writeOffset = (x + bx) * 4;
                    writeRow[writeOffset + 0] = randomColor.b;
                    writeRow[writeOffset + 1] = randomColor.g;
                    writeRow[writeOffset + 2] = randomColor.r;
                }
            }
        }
    }
}