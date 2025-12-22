# PhotoPix Image Pixelator

PhotoPix is a Windows desktop application designed to apply a pixelation effect to images. Its primary purpose is to demonstrate and compare the performance of different backend libraries—one written in C++ and another in hand-optimized x64 Assembly (MASM)—called from a C# .NET frontend.

## Features

-   **Load Images**: Supports common image formats like JPG, PNG, and BMP.
-   **Pixelation Effect**: Applies a "pixelate" or "mosaic" filter to the loaded image.
-   **Backend Selection**: Allows users to switch between a C++ and an x64 Assembly implementation for the image processing algorithm.
-   **Performance Measurement**: Measures and displays the execution time in milliseconds for each processing operation, allowing for direct performance comparison.
-   **Multithreading Control**: Users can specify the number of threads to be used for processing, with the default set to the number of logical processor cores.
-   **Adjustable Pixel Size**: The size of the pixelation blocks can be adjusted through the UI.

## Technologies Used

-   **Frontend**: C# (.NET Framework 4.7.2), Windows Forms
-   **Backend Libraries**:
    -   C++ (compiled as a native DLL)
    -   x64 Assembly (MASM, compiled as a native DLL)
-   **IDE / Build**: Visual Studio

## Project Structure

The solution is composed of three main projects:

-   `PhotoPix`: The main C# Windows Forms project. It contains the user interface (`Form1.cs`) and the C# logic that manages the image data and calls the native libraries (`ImageProcessor.cs`).
-   `PixCpp`: A C++ project that compiles into `PixCpp.dll`. It contains the C++ implementation of the pixelation algorithm.
-   `PixAsm`: An x64 Assembly project that compiles into `PixAsm.dll` using MASM. It contains the assembly language version of the algorithm, optimized for performance.

## How It Works

1.  **Image Loading**: The C# application loads an image into a `Bitmap` object.
2.  **Memory Locking**: To allow direct memory access for the native code, the application locks the bitmap's data in memory using `LockBits`. This provides a raw pointer to the pixel data (in 32-bit BGRA format).
3.  **Work Division**: The image is horizontally divided into sections, and the processing for each section is assigned to a separate thread using `Parallel.For` to leverage multi-core processors.
4.  **Native Call**: Each thread calls the selected native function (`PixelateCpp` or `PixelateAsm`) via P/Invoke, passing the pointer to the image data, image dimensions, and the specific rows it is responsible for processing.
5.  **Pixelation Algorithm**:
    -   The native function iterates over its assigned portion of the image in blocks defined by `pixelSize`.
    -   For each block, it calculates the average color (Red, Green, and Blue channels).
    -   It then fills the entire block with that average color.
6.  **Memory Unlocking**: Once all threads have completed, the C# application unlocks the bitmap data, and the processed image is displayed in the UI.

## Build and Setup

1.  **Open the Solution**: Open the `.sln` file in Visual Studio.
2.  **Set Build Configuration**: Change the build configuration to **Release** and the platform to **x64**. This is crucial because the native libraries are built for this target.
3.  **Build the Solution**: Build the entire solution (`Build > Build Solution` or `Ctrl+Shift+B`). This will compile the `PixCpp` and `PixAsm` projects first, generating the required `.dll` files.
4.  **Run the Application**: Set the `PhotoPix` project as the startup project and run it.

> **Note on DLLs:** The C# project is configured to find the DLLs in the `x64/Release` output directory relative to the solution folder. If you encounter a `DllNotFoundException`, ensure that the build configuration is correct and that the `PixCpp.dll` and `PixAsm.dll` files are present in the expected location (`PhotoPix/bin/x64/Release/`).

