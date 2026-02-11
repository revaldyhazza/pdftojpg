import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
import io
import zipfile
import os
from datetime import datetime
import time

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================
st.set_page_config(
    page_title="PDF & Image Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    .info-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        color: black;
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
    
    .stats-box {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: black;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stats-number {
        font-size: 2.2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stats-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.5rem;
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
    <h1>🔄 PDF & Image Converter</h1>
    <p>Convert (.pdf) ke (.jpg) dan sebaliknya</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - MODE SELECTION
# ============================================================================
with st.sidebar:
    st.header("⚙️ Pilih Mode Konversi")
    
    mode = st.radio(
        "Mode:",
        ["PDF to JPG", "JPG to PDF"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")

# ============================================================================
# PDF to JPG MODE
# ============================================================================
if mode == "PDF to JPG":
    with st.sidebar:
        st.markdown("### 🖼️ PDF to JPG")
        st.caption("Convert PDF ke gambar JPG/PNG berkualitas tinggi")
        
        st.markdown("---")
        st.markdown("### 🎛️ Pengaturan")
        
        output_format = st.selectbox(
            "Format Output",
            ["JPG", "PNG"],
            help="JPG = ukuran lebih kecil, PNG = kualitas lossless"
        )
        
        dpi = st.select_slider(
            "Kualitas (DPI)",
            options=[72, 96, 150, 200, 300, 400],
            value=200
        )
        
        if output_format == "JPG":
            jpg_quality = st.slider("JPEG Quality", 60, 100, 92, 5)
        
        dpi_info = {
            72: "⚡ Cepat - Web", 
            96: "⚡ Cepat - Screen", 
            150: "📱 Social media", 
            200: "⭐ Optimal",
            300: "🖨️ Print quality", 
            400: "💎 Professional"
        }
        st.info(f"**{dpi_info.get(dpi)}**")
    
    st.markdown("### 📤 Upload File PDF")
    uploaded_files = st.file_uploader(
        "Drag & drop atau klik untuk memilih file PDF",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="pdf_upload"
    )
    
    if uploaded_files:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stats-box"><div class="stats-number">{len(uploaded_files)}</div><div class="stats-label">File PDF</div></div>', unsafe_allow_html=True)
        with col2:
            total_size = sum([f.size for f in uploaded_files]) / (1024 * 1024)
            st.markdown(f'<div class="stats-box"><div class="stats-number">{total_size:.1f} MB</div><div class="stats-label">Total Size</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stats-box"><div class="stats-number">{output_format}</div><div class="stats-label">Output</div></div>', unsafe_allow_html=True)
        
        with st.expander(f"📁 Lihat {len(uploaded_files)} file", expanded=len(uploaded_files) <= 5):
            for idx, f in enumerate(uploaded_files, 1):
                st.markdown(f"`{idx}.` **{f.name}** — {f.size / (1024*1024):.2f} MB")
        
        st.markdown("---")
        
        if st.button("🚀 Convert ke " + output_format, type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status = st.empty()
            
            col1, col2, col3 = st.columns(3)
            m1, m2, m3 = col1.empty(), col2.empty(), col3.empty()
            
            all_images = []
            total_pages = 0
            start = time.time()
            
            for idx, pdf_file in enumerate(uploaded_files, 1):
                file_name = pdf_file.name
                base_name = os.path.splitext(file_name)[0]
                
                progress_bar.progress((idx-1)/len(uploaded_files))
                status.info(f"📄 Converting {idx}/{len(uploaded_files)}: **{file_name}**")
                
                m1.metric("Selesai", f"{idx-1}/{len(uploaded_files)}")
                m2.metric("Halaman", total_pages)
                m3.metric("Waktu", f"{time.time()-start:.1f}s")
                
                try:
                    pdf_bytes = pdf_file.read()
                    images = convert_from_bytes(pdf_bytes, dpi=dpi, thread_count=2)
                    
                    for i, img in enumerate(images, 1):
                        buf = io.BytesIO()
                        if output_format == "PNG":
                            img.save(buf, format='PNG', optimize=True)
                            ext = ".png"
                        else:
                            img.save(buf, format='JPEG', quality=jpg_quality, optimize=True)
                            ext = ".jpg"
                        
                        # Nama file sesuai original PDF
                        if len(images) > 1:
                            name = f"{base_name}_page{i:03d}{ext}"
                        else:
                            name = f"{base_name}{ext}"
                        
                        all_images.append((name, buf.getvalue()))
                    
                    total_pages += len(images)
                    
                except Exception as e:
                    st.error(f"❌ {file_name}: {str(e)}")
            
            progress_bar.progress(1.0)
            elapsed = time.time() - start
            
            m1.metric("Selesai", f"{len(uploaded_files)}/{len(uploaded_files)}")
            m2.metric("Halaman", total_pages)
            m3.metric("Waktu", f"{elapsed:.1f}s")
            status.empty()
            
            if all_images:
                st.markdown(f'<div class="success-card"><h3>🎉 Berhasil!</h3><p>✅ {len(uploaded_files)} PDF → {total_pages} {output_format}</p><p>⏱️ {elapsed:.1f} detik</p></div>', unsafe_allow_html=True)
                
                # Download single file atau ZIP
                if len(all_images) == 1:
                    # Single file - download langsung
                    st.download_button(
                        f"⬇️ Download {all_images[0][0]}",
                        all_images[0][1],
                        all_images[0][0],
                        f"image/{output_format.lower()}",
                        use_container_width=True,
                        type="primary"
                    )
                else:
                    # Multiple files - download as ZIP
                    zip_buf = io.BytesIO()
                    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                        for name, data in all_images:
                            zf.writestr(name, data)
                    zip_buf.seek(0)
                    
                    st.download_button(
                        f"⬇️ Download {total_pages} {output_format} (ZIP)",
                        zip_buf,
                        f"converted_images.zip",
                        "application/zip",
                        use_container_width=True,
                        type="primary"
                    )
                
                # Preview
                st.markdown("### 🖼️ Preview")
                prev = st.slider("Tentukan Jumlah Preview", 4, 50, 20, 4, key="prev1")
                cols = st.columns(4)
                for idx, (name, data) in enumerate(all_images[:prev]):
                    cols[idx % 4].image(data, caption=name, use_container_width=True)
    else:
        st.markdown('<div class="info-card"><h4>📖 Cara Pakai:</h4><ol><li>Upload satu atau beberapa file PDF</li><li>Atur DPI & format output</li><li>Klik tombol Convert</li><li>Download file hasil (ZIP jika lebih dari 1 file)</li></ol></div>', unsafe_allow_html=True)

# ============================================================================
# JPG to PDF MODE
# ============================================================================
elif mode == "JPG to PDF":
    with st.sidebar:
        st.markdown("### 📄 JPG to PDF")
        st.caption("Gabungkan beberapa gambar menjadi satu file PDF")
        
        st.markdown("---")
        st.markdown("### 🎛️ Pengaturan")
        
        quality = st.slider("Kualitas Gambar", 60, 100, 85, 5)
        
        pdf_name = st.text_input(
            "Nama file PDF (opsional)", 
            placeholder="Kosongkan untuk nama otomatis",
            help="Jika kosong, akan menggunakan nama file pertama"
        )
    
    st.markdown("### 📤 Upload Gambar")
    uploaded_files = st.file_uploader(
        "Upload satu atau beberapa gambar yang akan digabung",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="img_upload"
    )
    
    if uploaded_files:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="stats-box"><div class="stats-number">{len(uploaded_files)}</div><div class="stats-label">Gambar</div></div>', unsafe_allow_html=True)
        with col2:
            total = sum([f.size for f in uploaded_files]) / (1024 * 1024)
            st.markdown(f'<div class="stats-box"><div class="stats-number">{total:.1f} MB</div><div class="stats-label">Total Size</div></div>', unsafe_allow_html=True)
        
        st.markdown("#### 📋 Urutan Halaman PDF")
        st.caption("Gambar akan disusun sesuai urutan upload")
        for idx, f in enumerate(uploaded_files, 1):
            st.markdown(f"`{idx}.` **{f.name}**")
        
        st.markdown("---")
        
        if st.button("🚀 Buat PDF", type="primary", use_container_width=True):
            prog = st.progress(0)
            status = st.empty()
            
            try:
                images = []
                for idx, f in enumerate(uploaded_files, 1):
                    prog.progress(idx/len(uploaded_files))
                    status.info(f"📷 Memproses gambar {idx}/{len(uploaded_files)}: **{f.name}**")
                    
                    img = Image.open(f)
                    
                    # Convert to RGB jika perlu
                    if img.mode in ('RGBA', 'LA', 'P'):
                        bg = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        if img.mode in ('RGBA', 'LA'):
                            bg.paste(img, mask=img.split()[-1])
                        else:
                            bg.paste(img)
                        img = bg
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    images.append(img)
                
                # Buat PDF
                status.info("📄 Membuat file PDF...")
                pdf_buf = io.BytesIO()
                
                if len(images) == 1:
                    images[0].save(pdf_buf, format='PDF', quality=quality)
                else:
                    images[0].save(
                        pdf_buf, 
                        format='PDF', 
                        save_all=True, 
                        append_images=images[1:], 
                        quality=quality
                    )
                
                pdf_buf.seek(0)
                prog.progress(1.0)
                status.empty()
                
                st.success(f"🎉 PDF berhasil dibuat dari {len(images)} gambar!")
                
                # Tentukan nama file PDF
                if pdf_name.strip():
                    # Gunakan nama yang diinput user
                    final_name = pdf_name.strip()
                    if not final_name.endswith('.pdf'):
                        final_name += '.pdf'
                else:
                    # Gunakan nama file pertama
                    base_name = os.path.splitext(uploaded_files[0].name)[0]
                    final_name = f"{base_name}.pdf"
                
                st.download_button(
                    f"⬇️ Download {final_name}",
                    pdf_buf,
                    final_name,
                    "application/pdf",
                    use_container_width=True,
                    type="primary"
                )
                
                # Info PDF
                pdf_size = len(pdf_buf.getvalue()) / (1024 * 1024)
                st.info(f"📊 File PDF: **{final_name}** — {pdf_size:.2f} MB — {len(images)} halaman")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.markdown('<div class="info-card"><h4>📖 Cara Pakai:</h4><ol><li>Upload satu atau beberapa gambar</li><li>Gambar akan disusun sesuai urutan upload</li><li>Atur kualitas PDF</li><li>Opsional: tentukan nama file PDF</li><li>Klik Buat PDF dan download</li></ol></div>', unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 2rem 0;">
    <p><strong>🔄 PDF & Image Converter</strong></p>
    <p style="font-size: 0.9rem;">
        Semua proses di browser. File tidak disimpan di server.<br>
        PDF → JPG/PNG | JPG/PNG → PDF
    </p>
</div>
""", unsafe_allow_html=True)
