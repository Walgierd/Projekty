/*
Imię Nazwisko: Olivier Trela
Data:           19.01.2025 
Wersja:         2.0
Opis:           Klasa zarządzająca przetwarzaniem obrazu i wywołująca odpowiednie
                funkcje z bibliotek DLL (C++ lub ASM) w zależności od wybranego algorytmu.
*/
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Threading.Tasks;

namespace PhotoPix
{
    // Enum określający dostępny algorytm pikselacji
    public enum PixelationAlgorithm
    {
        Average,    // Średnia
        Median,     // Mediana
        Random      // Losowy
    }

    public class ImageProcessor
    {
        // Ścieżki do bibliotek - wersja Release, x64
        private const string CppDllPath = "C:\\Users\\trela\\Desktop\\Projekty\\Asembler\\PhotoPix\\PhotoPix\\PhotoPix\\x64\\Debug\\PixCpp.dll";
        private const string AsmDllPath = "C:\\Users\\trela\\Desktop\\Projekty\\Asembler\\PhotoPix\\PhotoPix\\PhotoPix\\x64\\Debug\\PixAsm.dll";

        // --- IMPORTY FUNKCJI C++ ---
        [DllImport(CppDllPath, EntryPoint = "PixelateCpp_Average", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateCpp_Average(IntPtr data, int w, int h, int s, int p, int sr, int er);

        [DllImport(CppDllPath, EntryPoint = "PixelateCpp_Median", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateCpp_Median(IntPtr data, int w, int h, int s, int p, int sr, int er);

        [DllImport(CppDllPath, EntryPoint = "PixelateCpp_Random", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateCpp_Random(IntPtr data, int w, int h, int s, int p, int sr, int er);

        // --- IMPORTY FUNKCJI ASM ---
        [DllImport(AsmDllPath, EntryPoint = "PixelateAsm_Average", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateAsm_Average(IntPtr data, int w, int h, int s, int p, int sr, int er);

        [DllImport(AsmDllPath, EntryPoint = "PixelateAsm_Median", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateAsm_Median(IntPtr data, int w, int h, int s, int p, int sr, int er);

        [DllImport(AsmDllPath, EntryPoint = "PixelateAsm_Random", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateAsm_Random(IntPtr data, int w, int h, int s, int p, int sr, int er);


        /*
        Nazwa: ProcessImage
        Opis:  Główna metoda przetwarzająca obraz wielowątkowo.
        */
        public void ProcessImage(Bitmap bmp, int threadCount, int pixelSize, bool useAsm, PixelationAlgorithm algorithm)
        {
            // Blokada pamięci bitmapy
            BitmapData bmpData = bmp.LockBits(
                new Rectangle(0, 0, bmp.Width, bmp.Height),
                ImageLockMode.ReadWrite,
                PixelFormat.Format32bppArgb
            );

            try
            {
                int width = bmp.Width;
                int height = bmp.Height;
                int stride = bmpData.Stride;
                IntPtr scan0 = bmpData.Scan0;

                // Obliczanie liczby bloków w pionie
                int totalBlocksY = (height + pixelSize - 1) / pixelSize;

                // Podział pracy na wątki (dzielimy bloki, nie piksele)
                Parallel.For(0, threadCount, new ParallelOptions { MaxDegreeOfParallelism = threadCount }, i =>
                {
                    // Obliczanie zakresu bloków dla wątku
                    int startBlock = i * totalBlocksY / threadCount;
                    int endBlock = (i + 1) * totalBlocksY / threadCount;

                    // Konwersja na współrzędne pikselowe
                    int startRow = startBlock * pixelSize;
                    int endRow = endBlock * pixelSize;

                    if (endRow > height) endRow = height;
                    if (startRow >= endRow) return;

                    // Wybór biblioteki i algorytmu
                    if (useAsm)
                    {
                        switch (algorithm)
                        {
                            case PixelationAlgorithm.Average:
                                PixelateAsm_Average(scan0, width, height, stride, pixelSize, startRow, endRow);
                                break;
                            case PixelationAlgorithm.Median:
                                PixelateAsm_Median(scan0, width, height, stride, pixelSize, startRow, endRow);
                                break;
                            case PixelationAlgorithm.Random:
                                PixelateAsm_Random(scan0, width, height, stride, pixelSize, startRow, endRow);
                                break;
                        }
                    }
                    else
                    {
                        switch (algorithm)
                        {
                            case PixelationAlgorithm.Average:
                                PixelateCpp_Average(scan0, width, height, stride, pixelSize, startRow, endRow);
                                break;
                            case PixelationAlgorithm.Median:
                                PixelateCpp_Median(scan0, width, height, stride, pixelSize, startRow, endRow);
                                break;
                            case PixelationAlgorithm.Random:
                                PixelateCpp_Random(scan0, width, height, stride, pixelSize, startRow, endRow);
                                break;
                        }
                    }
                });
            }
            finally
            {
                bmp.UnlockBits(bmpData);
            }
        }
    }
}