# Legal Network Analytics
## Deskripsi
Legal Network Analytics adalah teknologi canggih yang mengaplikasikan AI dan teknologi graf untuk memetakan hubungan antar peraturan perundang-undangan. Proyek ini, yang merupakan inisiatif dari Biro Hukum Sekretariat Jenderal Kementerian Keuangan, berada di bawah naungan Pengembangan Teknologi Parser dan Sistem Temu Kembali pada Dokumen Peraturan Perundang-undangan. Tujuan utama dari Legal Network Analytics adalah untuk mendetailkan dan memvisualisasikan koneksi dan interaksi antar regulasi di Indonesia, sehingga mempermudah pemahaman terhadap kerangka hukum yang kompleks.

Dalam pengembangan ini, teknologi AI ChatGPT diterapkan untuk mengidentifikasi dan mengekstrak tema serta topik penting dari dokumen hukum. Sementara itu, Neo4j digunakan untuk membangun database graf yang efektif dalam memetakan hubungan inter-dokumentasi peraturan perundang-undangan. 

Setelah database graf terkonstruksi, proyek ini melangkah lebih jauh dengan mengembangkan sebuah halaman web interaktif. Halaman ini memungkinkan pengguna untuk melakukan pencarian peraturan perundang-undangan secara efisien, mengidentifikasi hubungan antar dokumen, mengeksplorasi topik-topik umum yang muncul, dan mengakses peraturan terkait dengan topik tertentu. Ini tidak hanya meningkatkan aksesibilitas dan pemahaman terhadap data perundang-undangan yang luas, tetapi juga mendukung proses pengambilan keputusan yang berbasis informasi dalam lingkup hukum dan kebijakan.

## Fitur Utama
- **Ekstraksi Topik dengan AI**: Memanfaatkan ChatGPT untuk mengidentifikasi dan mengekstrak tema dari dokumen hukum.
- **Database Graf dengan Neo4j**: Memetakan hubungan antara dokumen peraturan perundang-undangan secara efektif.
- **Halaman Web Interaktif**: Memberikan kemampuan pencarian dan eksplorasi terhadap peraturan serta hubungan antar dokumen.

## Teknologi
- **ChatGPT**: Untuk identifikasi dan ekstraksi topik.
- **Neo4j**: Database graf untuk menyimpan hubungan antar dokumen.

## Persyaratan
- **Python 3.12+**
- **Python libraries (install via `pip install -r requirements.txt`)**:
  - `openai`
  - `neo4j`
- **Node.js dependencies (install via `npm install`)**:
  - `express`
  - `neo4j-driver`
- **Neo4j Database**: Untuk menyimpan data hubungan antar peraturan perundang-undangan.
- **OpenSearch Database**: Untuk mengakses data hasil parser peraturan perundang-undangan dan menyimpan hasil ekstraksi topik.

## Penggunaan
1. **Atur variabel lingkungan**: Atur variabel lingkungan untuk OpenAI API Key, Neo4j Database, dan OpenSearch Database.
2. **Ekstraksi Topik dan Pembentukan graf**: Jalankan `python main.py` dengan argumen `--document_slug` yang merupakan id atau slug dari dokumen hukum yang ingin diekstraksi topiknya. Hasil ekstraksi akan disimpan di Neo4j.
3. **Halaman Web Interaktif**: Jalankan `node server.js` dan buka `localhost:3000` di browser untuk mengakses halaman web interaktif.