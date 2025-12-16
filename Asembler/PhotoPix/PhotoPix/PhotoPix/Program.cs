using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace PhotoPix
{
    class Program
    {
        
        [DllImport(@"C:\Users\trela\Desktop\Projekty\Asembler\PhotoPix\PhotoPix\x64\Debug\PixAsm.dll")]
        static extern long MyProc1(long a, long b);

        static void Main(string[] args)
        {
            long x = 5, y = 3;
            long retVal = MyProc1(x, y); 

            Console.Write("Moja pierwsza wartość obliczona w asm to: ");
            Console.WriteLine(retVal);
            Console.ReadLine();
        }
    }
}
