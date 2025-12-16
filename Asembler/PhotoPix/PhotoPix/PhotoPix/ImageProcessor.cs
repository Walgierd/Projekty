using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Threading.Tasks;

namespace PhotoPix
{
    public class ImageProcessor
    {

        [DllImport(@"..\..\..\x64\Debug\PixCpp.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateCpp(IntPtr data, int width, int height, int stride, int pixelSize, int startRow, int endRow);

        [DllImport(@"..\..\..\x64\Debug\PixAsm.dll", CallingConvention = CallingConvention.Cdecl)]
        private static extern void PixelateAsm(IntPtr data, int width, int height, int stride, int pixelSize, int startRow, int endRow);


        public void ProcessImage(Bitmap bmp, int threadCount, int pixelSize, bool useAsm)
        {

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


                Parallel.For(0, threadCount, new ParallelOptions { MaxDegreeOfParallelism = threadCount }, i =>
                {

                    int startRow = i * height / threadCount;
                    int endRow = (i + 1) * height / threadCount;


                    startRow = (startRow / pixelSize) * pixelSize;
                    endRow = (endRow / pixelSize) * pixelSize;


                    if (i == threadCount - 1)
                    {
                        endRow = height;
                    }


                    if (startRow >= endRow) return;


                    if (useAsm)
                    {
                        PixelateAsm(scan0, width, height, stride, pixelSize, startRow, endRow);
                    }
                    else
                    {
                        PixelateCpp(scan0, width, height, stride, pixelSize, startRow, endRow);
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