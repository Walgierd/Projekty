/*
Imię Nazwisko: Olivier Trela
Data:           20.01.2026
Temat:          Graficzny Interfejs Użytkownika dla projektu PhotoPix.
Wersja:         2.0
Opis:           Główne okno aplikacji obsługujące interakcję z użytkownikiem,
                wybór parametrów przetwarzania oraz wyświetlanie wyników.
*/

using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace PhotoPix
{
    public partial class Form1 : Form
    {
        private Bitmap originalImage = null;
        private Bitmap resultImage = null;
        private ImageProcessor processor = new ImageProcessor();

        private GroupBox grpOptions;
        private Button btnLoad, btnProcess, btnSave, btnTest;
        private RadioButton rbCpp, rbAsm;
        private NumericUpDown numThreads;
        private TrackBar trkPixelSize;
        private Label lblPixelInfo;
        private ComboBox cmbAlgorithm;
        private Label lblStatus;

        private TableLayoutPanel mainLayout;
        private PictureBox picOriginal;
        private PictureBox picResult;

        /*
        Nazwa: Form1
        Opis:  Konstruktor głównego okna aplikacji. Inicjalizuje GUI.
        */
        public Form1()
        {
            InitializeCustomGUI();
        }

        /*
        Nazwa: InitializeCustomGUI
        Opis:  Tworzy i konfiguruje elementy interfejsu użytkownika (przyciski, panele, obrazki).
        */
        private void InitializeCustomGUI()
        {
            this.Text = "PhotoPix - Porownanie";
            this.Size = new Size(1250, 800);
            this.MinimumSize = new Size(950, 600);
            this.BackColor = Color.WhiteSmoke;

            grpOptions = new GroupBox();
            grpOptions.Text = "Panel Sterowania";
            grpOptions.Dock = DockStyle.Top;
            grpOptions.Height = 130; 
            this.Controls.Add(grpOptions);

            btnLoad = CreateButton("1. Wczytaj", 20, 30, btnLoad_Click);
            btnProcess = CreateButton("2. Przetwarzaj", 130, 30, btnProcess_Click);
            btnProcess.Font = new Font(this.Font, FontStyle.Bold); 
            btnSave = CreateButton("3. Zapisz", 240, 30, btnSave_Click);
            btnSave.Enabled = false;

            btnTest = CreateButton("TESTUJ", 240, 75, btnTest_Click);
            btnTest.Font = new Font(this.Font, FontStyle.Bold);
            btnTest.ForeColor = Color.DarkRed;

            grpOptions.Controls.Add(btnLoad);
            grpOptions.Controls.Add(btnProcess);
            grpOptions.Controls.Add(btnSave);
            grpOptions.Controls.Add(btnTest);

            rbCpp = new RadioButton() { Text = "C++ DLL", Location = new Point(360, 30), Checked = true, AutoSize = true };
            rbAsm = new RadioButton() { Text = "ASM x64", Location = new Point(360, 55), AutoSize = true };
            grpOptions.Controls.Add(rbCpp);
            grpOptions.Controls.Add(rbAsm);

            CreateParamControl("Watki:", 450, 30, out numThreads, 1, 64, Environment.ProcessorCount);
            
            Label lblP = new Label() { Text = "Rozdzieczosc:", Location = new Point(450, 63), AutoSize = true };
            grpOptions.Controls.Add(lblP);

            trkPixelSize = new TrackBar();
            trkPixelSize.Location = new Point(530, 60);
            trkPixelSize.Size = new Size(130, 45);
            trkPixelSize.Minimum = 5;
            trkPixelSize.Maximum = 200;
            trkPixelSize.Value = 100; 
            trkPixelSize.TickStyle = TickStyle.None;
            trkPixelSize.Scroll += (s, ev) => { lblPixelInfo.Text = $"{trkPixelSize.Value} blokow"; };
            grpOptions.Controls.Add(trkPixelSize);

            lblPixelInfo = new Label() { Text = $"{trkPixelSize.Value} blokow", Location = new Point(670, 63), AutoSize = true };
            grpOptions.Controls.Add(lblPixelInfo);

            Label lblAlgo = new Label() { Text = "Algorytm:", Location = new Point(530, 33), AutoSize = true };
            grpOptions.Controls.Add(lblAlgo);

            cmbAlgorithm = new ComboBox();
            cmbAlgorithm.Location = new Point(600, 30);
            cmbAlgorithm.Width = 100;
            cmbAlgorithm.DropDownStyle = ComboBoxStyle.DropDownList;
            cmbAlgorithm.Items.AddRange(new object[] { "Srednia", "Mediana", "Losowy" });
            cmbAlgorithm.SelectedIndex = 0;
            grpOptions.Controls.Add(cmbAlgorithm);

            lblStatus = new Label() { Text = "Gotowy.", Location = new Point(720, 35), AutoSize = true, Font = new Font("Segoe UI", 10, FontStyle.Bold), ForeColor = Color.DarkBlue };
            grpOptions.Controls.Add(lblStatus);

            mainLayout = new TableLayoutPanel();
            mainLayout.Dock = DockStyle.Fill;
            mainLayout.ColumnCount = 2;
            mainLayout.RowCount = 1;
            mainLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            mainLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            this.Controls.Add(mainLayout);

            this.Controls.SetChildIndex(grpOptions, 0);

            Panel leftPanel = new Panel() { Dock = DockStyle.Fill, Padding = new Padding(10) };
            Label lblOrig = new Label() { Text = "ORYGINAL", Dock = DockStyle.Top, TextAlign = ContentAlignment.MiddleCenter, Font = new Font(this.Font, FontStyle.Bold), Height = 30 };
            picOriginal = new PictureBox() { Dock = DockStyle.Fill, SizeMode = PictureBoxSizeMode.Zoom, BackColor = Color.Black, BorderStyle = BorderStyle.Fixed3D };

            leftPanel.Controls.Add(picOriginal);
            leftPanel.Controls.Add(lblOrig);
            mainLayout.Controls.Add(leftPanel, 0, 0);

            Panel rightPanel = new Panel() { Dock = DockStyle.Fill, Padding = new Padding(10) };
            Label lblRes = new Label() { Text = "WYNIK (PO)", Dock = DockStyle.Top, TextAlign = ContentAlignment.MiddleCenter, Font = new Font(this.Font, FontStyle.Bold), Height = 30 };
            picResult = new PictureBox() { Dock = DockStyle.Fill, SizeMode = PictureBoxSizeMode.Zoom, BackColor = Color.Black, BorderStyle = BorderStyle.Fixed3D };

            rightPanel.Controls.Add(picResult);
            rightPanel.Controls.Add(lblRes);
            mainLayout.Controls.Add(rightPanel, 1, 0); 
        }

        /*
        Nazwa: CreateButton
        Opis:  Pomocnicza metoda do tworzenia przycisków.
        Wejście: string text, int x, int y, EventHandler handler
        Wyjście: Obiekt Button
        */
        private Button CreateButton(string text, int x, int y, EventHandler handler)
        {
            Button btn = new Button();
            btn.Text = text;
            btn.Location = new Point(x, y);
            btn.Size = new Size(100, 40);
            btn.Click += handler;
            btn.UseVisualStyleBackColor = true;
            return btn;
        }

        /*
        Nazwa: CreateParamControl
        Opis:  Pomocnicza metoda do tworzenia kontrolek numerycznych z etykietami.
        Wejście/Wyjście: out NumericUpDown nud - utworzona kontrolka
        */
        private void CreateParamControl(string labelText, int x, int y, out NumericUpDown nud, int min, int max, int val)
        {
            Label lbl = new Label() { Text = labelText, Location = new Point(x, y + 3), AutoSize = true };
            grpOptions.Controls.Add(lbl);
            nud = new NumericUpDown() { Location = new Point(x + 50, y), Minimum = min, Maximum = max, Value = val, Width = 60 };
            grpOptions.Controls.Add(nud);
        }

        /*
        Nazwa: btnLoad_Click
        Opis:  Obsługa zdarzenia kliknięcia przycisku "Wczytaj". Otwiera okno dialogowe wyboru pliku.
        */
        private void btnLoad_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog ofd = new OpenFileDialog())
            {
                ofd.Filter = "Obrazy|*.jpg;*.jpeg;*.png;*.bmp";
                if (ofd.ShowDialog() == DialogResult.OK)
                {
                    if (originalImage != null) originalImage.Dispose();
                    using (var temp = new Bitmap(ofd.FileName))
                    {
                        originalImage = new Bitmap(temp);
                    }

                    picOriginal.Image = originalImage;

                    if (picResult.Image != null) picResult.Image = null;
                    if (resultImage != null) { resultImage.Dispose(); resultImage = null; }

                    btnSave.Enabled = false;
                    lblStatus.Text = "Obraz wczytany.";
                }
            }
        }

        /*
        Nazwa: btnProcess_Click
        Opis:  Obsługa zdarzenia kliknięcia przycisku "Przetwarzaj". Uruchamia przetwarzanie obrazu.
        */
        private void btnProcess_Click(object sender, EventArgs e)
        {
            if (originalImage == null) { MessageBox.Show("Wczytaj obraz!"); return; }

            int threads = (int)numThreads.Value;
            int blockCount = trkPixelSize.Value;
            int pixelSize = Math.Max(2, originalImage.Width / blockCount);
            bool useAsm = rbAsm.Checked;
            PixelationAlgorithm algo = (PixelationAlgorithm)cmbAlgorithm.SelectedIndex;

            RunProcessing(originalImage, threads, pixelSize, useAsm, algo);
        }

        /*
        Nazwa: RunProcessing
        Opis:  Metoda wykonująca właściwe przetwarzanie obrazu z pomiarem czasu.
        */
        private void RunProcessing(Bitmap src, int threads, int pixelSize, bool useAsm, PixelationAlgorithm algo)
        {
            if (resultImage != null) resultImage.Dispose();
            resultImage = new Bitmap(src);

            Stopwatch sw = new Stopwatch();
            try
            {
                this.Cursor = Cursors.WaitCursor;
                sw.Start();

                processor.ProcessImage(resultImage, threads, pixelSize, useAsm, algo);

                sw.Stop();

                picResult.Image = resultImage;
                btnSave.Enabled = true;

                string lib = useAsm ? "ASM x64" : "C++";
                string algoName = algo.ToString();
                lblStatus.Text = $"Czas: {sw.ElapsedMilliseconds} ms | {lib} | {algoName} | Watki: {threads}";
            }
            catch (AggregateException aggEx)
            {
                var realError = aggEx.InnerException;
                MessageBox.Show($"Błąd krytyczny (Aggregate): {realError.Message}\nTyp: {realError.GetType().Name}\n\n{realError.StackTrace}");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Błąd: {ex.Message}\nTyp: {ex.GetType().Name}\nStack: {ex.StackTrace}");
            }
            finally
            {
                this.Cursor = Cursors.Default;
            }
        }

        /*
        Nazwa: btnTest_Click
        Opis:  Obsługa przycisku "TESTUJ". Uruchamia automatyczną serię testów wydajnościowych.
        */
        private async void btnTest_Click(object sender, EventArgs e)
        {
            if (originalImage == null)
            {
                MessageBox.Show("Najpierw wczytaj obraz do testów!", "Błąd", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            grpOptions.Enabled = false;
            
            int[] threadCounts = { 1, 2, 4, 8, 12, 16, 32, 64 };
            PixelationAlgorithm[] algorithms = { 
                PixelationAlgorithm.Average, 
                PixelationAlgorithm.Median, 
                PixelationAlgorithm.Random 
            };
            
            int blockCount = trkPixelSize.Value;
            int pixelSize = Math.Max(2, originalImage.Width / blockCount);
            string resolutionStr = $"{originalImage.Width}x{originalImage.Height}";

            string outputFile = "test.txt";

            try
            {
                await Task.Run(() =>
                {
                    bool fileExists = File.Exists(outputFile);

                    using (StreamWriter sw = new StreamWriter(outputFile, true))
                    {
                        if (!fileExists)
                        {
                            sw.WriteLine("Watki;Biblioteka;Algorytm;Rozdzielczosc;CzasSredni_ms");
                        }

                        foreach (int threads in threadCounts)
                        {
                            for (int lib = 0; lib < 2; lib++)
                            {
                                bool useAsm = (lib == 1);

                                foreach (var algo in algorithms)
                                {
                                    double totalTime = 0;
                                    int iterations = 5;

                                    for (int i = 0; i < iterations; i++)
                                    {
                                        using (Bitmap testBmp = new Bitmap(originalImage))
                                        {
                                            string libNameStatus = useAsm ? "ASM" : "CPP";
                                            Invoke(new Action(() => {
                                                lblStatus.Text = $"TEST: T={threads} {libNameStatus} {algo} Iter={i+1}/{iterations}";
                                            }));

                                            System.GC.Collect();
                                            System.GC.WaitForPendingFinalizers();

                                            Stopwatch watch = Stopwatch.StartNew();
                                            processor.ProcessImage(testBmp, threads, pixelSize, useAsm, algo);
                                            watch.Stop();

                                            totalTime += watch.Elapsed.TotalMilliseconds;
                                        }
                                    }
                                    
                                    double avgTime = totalTime / iterations;
                                    string libName = useAsm ? "ASM" : "CPP";
                                    
                                    string logLine = $"{threads};{libName};{algo};{resolutionStr};{avgTime:F4}";
                                    sw.WriteLine(logLine);
                                    sw.Flush();
                                }
                            }
                        }
                    }
                });

                MessageBox.Show($"Testy zakończone!\nWyniki dopisano do: {Path.GetFullPath(outputFile)}", "Sukces");
                lblStatus.Text = "Testy zakonczone pomyślnie.";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Błąd podczas testowania: {ex.Message}", "Błąd");
            }
            finally
            {
                grpOptions.Enabled = true;
            }
        }

        /*
        Nazwa: btnSave_Click
        Opis:  Obsługa przycisku "Zapisz". Pozwala zapisać przetworzony obraz na dysku.
        */
        private void btnSave_Click(object sender, EventArgs e)
        {
            if (resultImage == null) return;

            using (SaveFileDialog sfd = new SaveFileDialog())
            {
                sfd.Filter = "PNG|*.png|JPEG|*.jpg|Bitmap|*.bmp";
                sfd.FileName = "pixel_art.png";
                if (sfd.ShowDialog() == DialogResult.OK)
                {
                    ImageFormat fmt = ImageFormat.Png;
                    if (sfd.FileName.EndsWith(".jpg")) fmt = ImageFormat.Jpeg;
                    else if (sfd.FileName.EndsWith(".bmp")) fmt = ImageFormat.Bmp;

                    resultImage.Save(sfd.FileName, fmt);
                    MessageBox.Show("Zapisano!");
                }
            }
        }
    }
}