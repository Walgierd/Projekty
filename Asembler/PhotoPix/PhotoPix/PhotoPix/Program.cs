/*
Imię Nazwisko: Olivier Trela
Data:           20.01.2026
Temat:          Punkt wejścia aplikacji.
Wersja:         2.0
Opis:           Klasa startowa konfigurująca środowisko i uruchamiająca główny formularz.
*/

using System;
using System.Threading;
using System.Windows.Forms;

namespace PhotoPix
{
    static class Program
    {
        /*
        Nazwa: Main
        Opis:  Główna metoda wejściowa aplikacji. Konfiguruje ThreadPool i Style.
        */
        [STAThread]
        static void Main()
        {
            int minWorker, minIOC;
            ThreadPool.GetMinThreads(out minWorker, out minIOC);
            if (minWorker < Environment.ProcessorCount)
            {
                ThreadPool.SetMinThreads(Environment.ProcessorCount, minIOC);
            }

            System.Windows.Forms.Application.EnableVisualStyles();
            System.Windows.Forms.Application.SetCompatibleTextRenderingDefault(false);
            System.Windows.Forms.Application.Run(new Form1());
        }
    }
}