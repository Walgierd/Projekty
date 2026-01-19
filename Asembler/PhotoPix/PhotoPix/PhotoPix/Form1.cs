using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.Windows.Forms;

namespace PhotoPix
{
    public partial class Form1 : Form
    {
        private Bitmap originalImage = null;
        private Bitmap resultImage = null;
        private ImageProcessor processor = new ImageProcessor();

        private GroupBox grpOptions;
        private Button btnLoad, btnProcess, btnSave;
        private RadioButton rbCpp, rbAsm;
        private NumericUpDown numThreads;
        private TrackBar trkPixelSize;
        private Label lblPixelInfo;
        private ComboBox cmbAlgorithm;
        private Label lblStatus;

        private TableLayoutPanel mainLayout;
        private PictureBox picOriginal;
        private PictureBox picResult;

        public Form1()
        {
            InitializeCustomGUI();
        }

        private void InitializeCustomGUI()
        {
            this.Text = "PhotoPix - Porownanie";
            this.Size = new Size(1250, 800);
            this.MinimumSize = new Size(950, 600);
            this.BackColor = Color.WhiteSmoke;

            grpOptions = new GroupBox();
            grpOptions.Text = "Panel Sterowania";
            grpOptions.Dock = DockStyle.Top;
            grpOptions.Height = 110; 
            this.Controls.Add(grpOptions);

            btnLoad = CreateButton("1. Wczytaj", 20, 30, btnLoad_Click);
            btnProcess = CreateButton("2. Przetwarzaj", 130, 30, btnProcess_Click);
            btnProcess.Font = new Font(this.Font, FontStyle.Bold); 
            btnSave = CreateButton("3. Zapisz", 240, 30, btnSave_Click);
            btnSave.Enabled = false;

            grpOptions.Controls.Add(btnLoad);
            grpOptions.Controls.Add(btnProcess);
            grpOptions.Controls.Add(btnSave);

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

        private void btnProcess_Click(object sender, EventArgs e)
        {
            if (originalImage == null) { MessageBox.Show("Wczytaj obraz!"); return; }

            int threads = (int)numThreads.Value;
            int blockCount = trkPixelSize.Value;
            int pixelSize = Math.Max(2, originalImage.Width / blockCount); // Dynamic size based on width and desired resolution
            bool useAsm = rbAsm.Checked;
            
            PixelationAlgorithm algo = (PixelationAlgorithm)cmbAlgorithm.SelectedIndex;

            if (resultImage != null) resultImage.Dispose();
            resultImage = new Bitmap(originalImage);

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
                string algoName = cmbAlgorithm.SelectedItem.ToString();
                lblStatus.Text = $"Czas: {sw.ElapsedMilliseconds} ms | {lib} | {algoName} | Watki: {threads}";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Blad: {ex.Message}");
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