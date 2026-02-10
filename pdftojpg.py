import streamlit as st
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import io
import zipfile
import os
import tempfile
import time
from datetime import datetime

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================
st.set_page_config(
    page_title="PDF to JPG Converter",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk UI yang lebih menarik
st.markdown("""
<style>
    /* Main container */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .info-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        color: black;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .success-card {
        background: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        color: black;
        margin: 1rem 0;
    }
    
    /* Stats box */
    .stats-box {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        color: black;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: bold;
        color: black;
    }
    
    .stats-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.5rem;
    }
    
    /* Upload area enhancement */
    .uploadedFile {
        border-left: 3px solid #667eea !important;
    }
    
    /* Preview grid */
    .preview-container {
        margin-top: 2rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🖼️ PDF to JPG Converter</h1>
    <p>Convert semua PDF Anda menjadi gambar JPG berkualitas tinggi</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - SETTINGS
# ============================================================================
with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    dpi = st.select_slider(
        "Kualitas Gambar (DPI)",
        options=[72, 96, 150, 200, 300, 400],
        value=200,
        help="• 150 DPI: Cepat, ukuran kecil\n• 200 DPI: ⭐ Rekomendasi (balance)\n• 300 DPI: Kualitas cetak\n• 400 DPI: Maksimal"
    )
    
    jpg_quality = st.slider(
        "Kualitas JPEG",
        min_value=60,
        max_value=100,
        value=92,
        step=5,
        help="85-92 = balance bagus, 95-100 = file lebih besar"
    )
    
    st.markdown("---")
    
    # DPI explanation
    dpi_info = {
        72: "⚡ Cepat - Web preview",
        96: "⚡ Cepat - Screen view",
        150: "📱 Standar - Social media",
        200: "⭐ Optimal - General use",
        300: "🖨️ Cetak - Print quality",
        400: "💎 Maksimal - Professional"
    }
    
    st.info(f"**{dpi_info.get(dpi, 'Custom')}**")
    
    st.markdown("---")
    st.markdown("""
    ### 📋 Tips:
    - Upload maksimal ~50-100 MB per file
    - Semakin tinggi DPI, semakin lama proses
    - File besar = butuh waktu lebih lama
    """)

# ============================================================================
# MAIN AREA - FILE UPLOAD
# ============================================================================

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📤 Upload File PDF")
    uploaded_files = st.file_uploader(
        "Drag & drop atau klik untuk memilih file",
        type=["pdf"],
        accept_multiple_files=True,
        help="Anda bisa upload beberapa file PDF sekaligus",
        label_visibility="collapsed"
    )

with col2:
    if uploaded_files:
        st.markdown("### 📊 Statistik")
        total_size = sum([f.size for f in uploaded_files]) / (1024 * 1024)  # MB
        
        st.markdown(f"""
        <div class="stats-box">
            <div class="stats-number">{len(uploaded_files)}</div>
            <div class="stats-label">File PDF</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stats-box" style="margin-top: 1rem;">
            <div class="stats-number">{total_size:.1f} MB</div>
            <div class="stats-label">Total Ukuran</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# UPLOADED FILES INFO
# ============================================================================
if uploaded_files:
    st.markdown("---")
    st.markdown("### 📁 File yang akan dikonversi:")
    
    # Show file list in expandable section
    with st.expander(f"Lihat {len(uploaded_files)} file", expanded=len(uploaded_files) <= 5):
        for idx, f in enumerate(uploaded_files, 1):
            size_mb = f.size / (1024 * 1024)
            st.markdown(f"`{idx}.` **{f.name}** — {size_mb:.2f} MB")
else:
    st.markdown("""
    <div class="info-card">
        <h4>👋 Cara Penggunaan:</h4>
        <ol>
            <li>Upload satu atau beberapa file PDF sekaligus</li>
            <li>Atur kualitas gambar di sidebar (opsional)</li>
            <li>Klik tombol <strong>"Convert Sekarang"</strong></li>
            <li>Download hasil dalam format ZIP</li>
        </ol>
        <p><strong>📌 Catatan:</strong> Semua proses dilakukan di browser Anda, file tetap aman!</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("---")

# ============================================================================
# CONVERT BUTTON & PROCESSING
# ============================================================================
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    convert_button = st.button(
        "🚀 Convert Sekarang",
        type="primary",
        use_container_width=True,
        help="Mulai proses konversi semua file PDF"
    )

if convert_button:
    # Progress tracking
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0, text="Memulai proses...")
        status_text = st.empty()
        
        # Metrics
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        metric_files = metrics_col1.empty()
        metric_pages = metrics_col2.empty()
        metric_time = metrics_col3.empty()
    
    total_files = len(uploaded_files)
    all_images_bytes = {}
    total_pages = 0
    
    start_time = time.time()
    
    # Process each PDF
    for idx, pdf_file in enumerate(uploaded_files, 1):
        file_name = pdf_file.name
        base_name = os.path.splitext(file_name)[0]
        
        # Update status
        progress_pct = (idx - 1) / total_files
        progress_bar.progress(
            progress_pct,
            text=f"Memproses {idx}/{total_files}: {file_name}"
        )
        status_text.info(f"📄 Converting **{file_name}**...")
        
        # Update metrics
        metric_files.metric("File Selesai", f"{idx-1}/{total_files}")
        metric_pages.metric("Total Halaman", total_pages)
        metric_time.metric("Waktu", f"{time.time() - start_time:.1f}s")
        
        try:
            # Read PDF bytes
            pdf_bytes = pdf_file.read()
            
            # Convert to images
            images = convert_from_bytes(
                pdf_bytes,
                dpi=dpi,
                fmt="jpg",
                thread_count=2,
                strict=False
            )
            
            # Convert to JPG bytes
            jpg_bytes_list = []
            num_pages = len(images)
            
            for i, img in enumerate(images, 1):
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=jpg_quality, optimize=True)
                
                # Smart naming: single page vs multiple pages
                if num_pages == 1:
                    jpg_name = f"{base_name}.jpg"
                else:
                    jpg_name = f"{base_name}_page{i:03d}.jpg"
                
                jpg_bytes_list.append((jpg_name, img_byte_arr.getvalue()))
            
            all_images_bytes[file_name] = jpg_bytes_list
            total_pages += num_pages
            
        except Exception as e:
            status_text.error(f"❌ Error pada {file_name}: {str(e)}")
            st.warning(f"File **{file_name}** gagal dikonversi dan akan dilewati.")
            time.sleep(1)
            continue
    
    # Final progress
    progress_bar.progress(1.0, text="✅ Konversi selesai!")
    elapsed_time = time.time() - start_time
    
    # Final metrics
    metric_files.metric("File Selesai", f"{len(all_images_bytes)}/{total_files}")
    metric_pages.metric("Total Halaman", total_pages)
    metric_time.metric("Waktu", f"{elapsed_time:.1f}s")
    
    status_text.empty()
    
    # ========================================================================
    # SUCCESS & DOWNLOAD
    # ========================================================================
    if all_images_bytes:
        st.markdown(f"""
        <div class="success-card">
            <h3>🎉 Konversi Berhasil!</h3>
            <p>✅ <strong>{len(all_images_bytes)}</strong> file PDF berhasil dikonversi menjadi <strong>{total_pages}</strong> gambar JPG</p>
            <p>⏱️ Waktu proses: <strong>{elapsed_time:.1f} detik</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
            for pdf_name, jpg_list in all_images_bytes.items():
                for jpg_name, jpg_bytes in jpg_list:
                    zip_file.writestr(jpg_name, jpg_bytes)
        
        zip_buffer.seek(0)
        
        # Download button
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"pdf_to_jpg_{timestamp}.zip"
        
        col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
        with col_dl2:
            st.download_button(
                label=f"⬇️ Download {total_pages} Gambar JPG (ZIP)",
                data=zip_buffer,
                file_name=zip_filename,
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
        
        # ====================================================================
        # PREVIEW
        # ====================================================================
        st.markdown("---")
        st.markdown("### 🖼️ Preview Hasil")
        
        preview_limit = st.slider(
            "Jumlah gambar preview",
            min_value=4,
            max_value=20,
            value=20,
            step=4,
            help="Pilih berapa gambar yang ingin ditampilkan"
        )
        
        st.markdown('<div class="preview-container">', unsafe_allow_html=True)
        
        # Create grid
        cols = st.columns(4)
        count = 0
        
        for pdf_name, jpgs in all_images_bytes.items():
            for jpg_name, jpg_bytes in jpgs:
                if count >= preview_limit:
                    break
                    
                with cols[count % 4]:
                    st.image(jpg_bytes, caption=jpg_name, use_container_width=True)
                    
                count += 1
            
            if count >= preview_limit:
                break
        
        if total_pages > preview_limit:
            st.caption(f"Menampilkan {preview_limit} dari {total_pages} gambar. Download ZIP untuk melihat semua.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.error("❌ Tidak ada file yang berhasil dikonversi. Silakan coba lagi.")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 1rem;">
    <p><strong>💡 Powered by pdf2image | Revaldy Hazza Daniswara </strong></p>
    <p style="font-size: 0.9rem;">
        Semua proses dilakukan secara lokal. File Anda tidak disimpan di server. <br>
    </p>
</div>
""", unsafe_allow_html=True)
