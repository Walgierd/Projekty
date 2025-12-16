using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging; // Do zapisu
using System.Windows.Forms;

namespace PhotoPix
{
    public partial class Form1 : Form
    {
        // === ZMIENNE ===
        private Bitmap originalImage = null;
        private Bitmap resultImage = null;
        private ImageProcessor processor = new ImageProcessor();

        // === KONTROLKI ===
        private GroupBox grpOptions;
        private Button btnLoad, btnProcess, btnSave;
        private RadioButton rbCpp, rbAsm;
        private NumericUpDown numThreads, numPixelSize;
        private Label lblStatus;

        // Kontrolki układu (TableLayoutPanel gwarantuje równość)
        private TableLayoutPanel mainLayout;
        private PictureBox picOriginal;
        private PictureBox picResult;

        public Form1()
        {
            InitializeCustomGUI();
        }

        private void InitializeCustomGUI()
        {
            // Ustawienia głównego okna
            this.Text = "PhotoPix - Porównanie";
            this.Size = new Size(1200, 800);
            this.MinimumSize = new Size(900, 600);
            this.BackColor = Color.WhiteSmoke;

            // 1. PANEL GÓRNY (OPCJE)
            grpOptions = new GroupBox();
            grpOptions.Text = "Panel Sterowania";
            grpOptions.Dock = DockStyle.Top;
            grpOptions.Height = 110; // Troszkę wyższy dla wygody
            this.Controls.Add(grpOptions);

            // Przyciski
            btnLoad = CreateButton("1. Wczytaj", 20, 30, btnLoad_Click);
            btnProcess = CreateButton("2. Przetwarzaj", 130, 30, btnProcess_Click);
            btnProcess.Font = new Font(this.Font, FontStyle.Bold); // Wyróżnienie
            btnSave = CreateButton("3. Zapisz", 240, 30, btnSave_Click);
            btnSave.Enabled = false;

            grpOptions.Controls.Add(btnLoad);
            grpOptions.Controls.Add(btnProcess);
            grpOptions.Controls.Add(btnSave);

            // Wybór Biblioteki
            rbCpp = new RadioButton() { Text = "C++ DLL", Location = new Point(360, 30), Checked = true, AutoSize = true };
            rbAsm = new RadioButton() { Text = "ASM x64", Location = new Point(360, 55), AutoSize = true };
            grpOptions.Controls.Add(rbCpp);
            grpOptions.Controls.Add(rbAsm);

            // Parametry
            CreateParamControl("Wątki:", 450, 30, out numThreads, 1, 64, Environment.ProcessorCount);
            CreateParamControl("Piksel:", 450, 60, out numPixelSize, 2, 200, 16);

            // Status
            lblStatus = new Label() { Text = "Gotowy.", Location = new Point(580, 45), AutoSize = true, Font = new Font("Segoe UI", 10, FontStyle.Bold), ForeColor = Color.DarkBlue };
            grpOptions.Controls.Add(lblStatus);


            // 2. GŁÓWNY UKŁAD (TABLE LAYOUT) - To gwarantuje równe połówki!
            mainLayout = new TableLayoutPanel();
            mainLayout.Dock = DockStyle.Fill;
            mainLayout.ColumnCount = 2;
            mainLayout.RowCount = 1;
            // Ustawiamy obie kolumny na dokładnie 50%
            mainLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            mainLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            this.Controls.Add(mainLayout);

            // Upewniamy się, że panel opcji jest na samej górze
            this.Controls.SetChildIndex(grpOptions, 0);

            // --- LEWA STRONA (Oryginał) ---
            Panel leftPanel = new Panel() { Dock = DockStyle.Fill, Padding = new Padding(10) };
            Label lblOrig = new Label() { Text = "ORYGINAŁ", Dock = DockStyle.Top, TextAlign = ContentAlignment.MiddleCenter, Font = new Font(this.Font, FontStyle.Bold), Height = 30 };
            picOriginal = new PictureBox() { Dock = DockStyle.Fill, SizeMode = PictureBoxSizeMode.Zoom, BackColor = Color.Black, BorderStyle = BorderStyle.Fixed3D };

            leftPanel.Controls.Add(picOriginal);
            leftPanel.Controls.Add(lblOrig);
            mainLayout.Controls.Add(leftPanel, 0, 0); // Kolumna 0

            // --- PRAWA STRONA (Wynik) ---
            Panel rightPanel = new Panel() { Dock = DockStyle.Fill, Padding = new Padding(10) };
            Label lblRes = new Label() { Text = "WYNIK (PO)", Dock = DockStyle.Top, TextAlign = ContentAlignment.MiddleCenter, Font = new Font(this.Font, FontStyle.Bold), Height = 30 };
            picResult = new PictureBox() { Dock = DockStyle.Fill, SizeMode = PictureBoxSizeMode.Zoom, BackColor = Color.Black, BorderStyle = BorderStyle.Fixed3D };

            rightPanel.Controls.Add(picResult);
            rightPanel.Controls.Add(lblRes);
            mainLayout.Controls.Add(rightPanel, 1, 0); // Kolumna 1
        }

        // === METODY POMOCNICZE UI (Dla czytelności) ===
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

        private void CreateParamControl(string labelText, int x, int y, out NumericUpDown nud, int min, int max, int val)
        {
            Label lbl = new Label() { Text = labelText, Location = new Point(x, y + 3), AutoSize = true };
            grpOptions.Controls.Add(lbl);
            nud = new NumericUpDown() { Location = new Point(x + 50, y), Minimum = min, Maximum = max, Value = val, Width = 60 };
            grpOptions.Controls.Add(nud);
        }

        // === LOGIKA APLIKACJI ===

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

                    // Reset wyniku
                    if (picResult.Image != null) picResult.Image = null;
                    if (resultImage != null) { resultImage.Dispose(); resultImage = null; }

                    btnSave.Enabled = false;
                    lblStatus.Text = "Obraz wczytany.";
                }
            }
        }

        private void btnProcess_Click(object sender, EventArgs e)
        {
            if (originalImage == null) { MessageBox.Show("Wczytaj obraz!"); return; }

            int threads = (int)numThreads.Value;
            int pixelSize = (int)numPixelSize.Value;
            bool useAsm = rbAsm.Checked;

            // Kopia dla wyniku
            if (resultImage != null) resultImage.Dispose();
            resultImage = new Bitmap(originalImage);

            Stopwatch sw = new Stopwatch();
            try
            {
                this.Cursor = Cursors.WaitCursor;
                sw.Start();

                processor.ProcessImage(resultImage, threads, pixelSize, useAsm);

                sw.Stop();

                picResult.Image = resultImage;
                btnSave.Enabled = true;

                string lib = useAsm ? "ASM x64" : "C++";
                lblStatus.Text = $"Czas: {sw.ElapsedMilliseconds} ms | {lib} | Wątki: {threads}";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Błąd: {ex.Message}");
            }
            finally
            {
                this.Cursor = Cursors.Default;
            }
        }

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