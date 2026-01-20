/*
Imię Nazwisko: Olivier Trela
Data:           20.01.2026
Temat:          Klasa przetwarzająca obraz.
Wersja:         2.0
Opis:           Zarządza logiką wielowątkową oraz wywołuje odpowiednie biblioteki DLL (C++ lub ASM).
*/

using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;

namespace PhotoPix
{
    public enum PixelationAlgorithm
    {
        Average,    // Średnia
        Median,     // Mediana
        Random      // Losowy
    }

    public class ImageProcessor
    {
        private const string CppDllPath = "C:\\Users\\trela\\Desktop\\Projekty\\Asembler\\PhotoPix\\PhotoPix\\PhotoPix\\x64\\Release\\PixCpp.dll";
        private const string AsmDllPath = "C:\\Users\\trela\\Desktop\\Projekty\\Asembler\\PhotoPix\\PhotoPix\\PhotoPix\\x64\\Release\\PixAsm.dll";

        [DllImport(CppDllPath, EntryPoint = "PixelateCpp_Average", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateCpp_Average(IntPtr data, int w, int h, int s, int p, int sr, int er);

        [DllImport(CppDllPath, EntryPoint = "PixelateCpp_Median", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateCpp_Median(IntPtr data, int w, int h, int s, int p, int sr, int er);

        [DllImport(CppDllPath, EntryPoint = "PixelateCpp_Random", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateCpp_Random(IntPtr data, int w, int h, int s, int p, int sr, int er);

        [DllImport(AsmDllPath, EntryPoint = "PixelateAsm_Average", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateAsm_Average(IntPtr data, int w, int h, int s, int p, int sr, int er);

        [DllImport(AsmDllPath, EntryPoint = "PixelateAsm_Median", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateAsm_Median(IntPtr data, int w, int h, int s, int p, int sr, int er);

        [DllImport(AsmDllPath, EntryPoint = "PixelateAsm_Random", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateAsm_Random(IntPtr data, int w, int h, int s, int p, int sr, int er);


        /*
        Nazwa: ProcessImage
        Opis:  Wykonuje przetwarzanie obrazu w zadanym zakresie wątków i przy użyciu wybranego algorytmu.
        Wejście: Bitmap, liczba wątków, rozmiar bloku, tryb (ASM/C++), algorytm
        Wyjście: Zmodyfikowana bitmapa (przez wskaźnik)
        */
        public void ProcessImage(Bitmap bmp, int threadCount, int pixelSize, bool useAsm, PixelationAlgorithm algorithm)
        {
            int minW, minIO;
            ThreadPool.GetMinThreads(out minW, out minIO);
            if (minW < threadCount)
            {
                ThreadPool.SetMinThreads(threadCount, minIO);
            }

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

                int totalBlocksY = (height + pixelSize - 1) / pixelSize;

                Parallel.For(0, threadCount, new ParallelOptions { MaxDegreeOfParallelism = threadCount }, i =>
                {
                    int startBlock = (int)((long)i * totalBlocksY / threadCount);
                    int endBlock = (int)((long)(i + 1) * totalBlocksY / threadCount);

                    int startRow = startBlock * pixelSize;
                    int endRow = endBlock * pixelSize;

                    if (endRow > height) endRow = height;
                    if (startRow >= endRow) return;

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