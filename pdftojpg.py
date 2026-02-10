# app.py
import streamlit as st
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import io
import zipfile
import os
import tempfile
import time

st.set_page_config(page_title="PDF to JPG Converter", layout="wide")

st.title("🖼️ Bulk PDF to JPG Converter")
st.markdown("Upload satu atau banyak file PDF, lalu convert sekaligus jadi JPG")

# -------------------------------
# Upload multiple files
# -------------------------------
uploaded_files = st.file_uploader(
    "Pilih file PDF (bisa banyak sekaligus)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Maksimal ukuran per file tergantung RAM yang tersedia (~50-150 MB biasanya aman)"
)

# Pilihan DPI (resolusi gambar)
dpi = st.slider("Resolusi (DPI)", min_value=100, max_value=400, value=200, step=50,
                help="200 = balance bagus ukuran vs kualitas, 300 = lebih tajam tapi file lebih besar")

if not uploaded_files:
    st.info("Silakan upload file PDF dulu...")
    st.stop()

# Tombol utama
if st.button("🔥 Convert Semua PDF ke JPG", type="primary", use_container_width=True):

    progress_bar = st.progress(0)
    status_text = st.empty()

    total_files = len(uploaded_files)
    all_images_bytes = {}  # simpan {nama_file.pdf : [bytes_jpg1, bytes_jpg2, ...]}

    start_time = time.time()

    # Buat folder sementara untuk poppler (jika di local)
    # Di Streamlit Cloud biasanya sudah include poppler via pdf2image

    for idx, pdf_file in enumerate(uploaded_files, 1):
        file_name = pdf_file.name
        status_text.text(f"Processing {idx}/{total_files} : {file_name}")

        try:
            # Baca bytes PDF
            pdf_bytes = pdf_file.read()

            # Convert ke list PIL Image
            images = convert_from_bytes(
                pdf_bytes,
                dpi=dpi,
                fmt="jpg",
                thread_count=2,  # percepat sedikit
                userpw=None,     # kalau ada password bisa ditambah
                strict=False
            )

            # Simpan sebagai bytes (supaya bisa langsung zip tanpa save ke disk)
            jpg_bytes_list = []
            for i, img in enumerate(images, 1):
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=92)
                jpg_bytes_list.append((f"{os.path.splitext(file_name)[0]}_page{i}.jpg", img_byte_arr.getvalue()))

            all_images_bytes[file_name] = jpg_bytes_list

        except Exception as e:
            st.error(f"Error saat proses {file_name} → {str(e)}")
            continue

        # Update progress
        progress_bar.progress(idx / total_files)

    progress_bar.progress(1.0)
    status_text.success(f"Selesai! Waktu proses: {time.time() - start_time:.1f} detik")

    # ---------------------------------------
    # Buat ZIP file
    # ---------------------------------------
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for pdf_name, jpg_list in all_images_bytes.items():
            for jpg_name, jpg_bytes in jpg_list:
                zip_file.writestr(jpg_name, jpg_bytes)

    zip_buffer.seek(0)

    # Tombol download
    st.download_button(
        label="⬇️ Download semua JPG (dalam 1 file .zip)",
        data=zip_buffer,
        file_name=f"converted_{len(all_images_bytes)}_pdfs.zip",
        mime="application/zip",
        use_container_width=True
    )

    # Preview beberapa gambar (opsional - biar kelihatan hasilnya)
    if all_images_bytes:
        st.markdown("### Preview beberapa hasil (sampel)")
        cols = st.columns(4)
        count = 0
        for jpgs in all_images_bytes.values():
            for _, jpg_bytes in jpgs[:8]:  # preview max 8 gambar
                cols[count % 4].image(jpg_bytes, use_column_width=True)
                count += 1
                if count >= 8:
                    break
            if count >= 8:
                break

st.markdown("---")
st.caption("Catatan: Aplikasi ini menggunakan pdf2image + poppler. Kalau deploy di Streamlit Cloud, pastikan sudah install dependencies dengan benar.")