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
    page_title="Universal File Converter",
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
        color: black
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
    
    .preview-container {
        margin-top: 2rem;
        padding: 1.5rem;
        background: #f8f9fa;
        color: black;
        border-radius: 12px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONVERSION MODES CONFIG
# ============================================================================
CONVERSION_MODES = {
    "PDF to JPG": {
        "icon": "🖼️",
        "description": "Convert PDF ke gambar JPG/PNG berkualitas tinggi",
        "input_formats": ["pdf"],
        "output_formats": ["JPG", "PNG"]
    },
    "JPG to PDF": {
        "icon": "📄",
        "description": "Gabungkan beberapa gambar menjadi satu file PDF",
        "input_formats": ["jpg", "jpeg", "png", "webp"],
        "output_formats": ["PDF"]
    },
    "Image Convert": {
        "icon": "🎨",
        "description": "Convert antar format gambar (JPG, PNG, WebP, dll)",
        "input_formats": ["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
        "output_formats": ["JPG", "PNG", "WebP", "BMP"]
    },
    "Image Resize": {
        "icon": "📐",
        "description": "Resize gambar dengan berbagai opsi (%, pixel, aspect ratio)",
        "input_formats": ["jpg", "jpeg", "png", "webp", "bmp"],
        "output_formats": ["Same as input"]
    }
}

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1>🔄 Universal File Converter</h1>
    <p>Convert file Anda dengan mudah - PDF, Gambar, dan lainnya</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - MODE SELECTION
# ============================================================================
with st.sidebar:
    st.header("⚙️ Pilih Mode Konversi")
    
    mode = st.radio(
        "Mode:",
        list(CONVERSION_MODES.keys()),
        format_func=lambda x: f"{CONVERSION_MODES[x]['icon']} {x}",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown(f"### {CONVERSION_MODES[mode]['icon']} {mode}")
    st.caption(CONVERSION_MODES[mode]['description'])
    
    st.markdown("---")

# ============================================================================
# PDF to JPG MODE
# ============================================================================
if mode == "PDF to JPG":
    with st.sidebar:
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
            72: "⚡ Cepat - Web", 96: "⚡ Cepat - Screen", 
            150: "📱 Social media", 200: "⭐ Optimal",
            300: "🖨️ Print quality", 400: "💎 Professional"
        }
        st.info(f"**{dpi_info.get(dpi)}**")
    
    st.markdown("### 📤 Upload File PDF")
    uploaded_files = st.file_uploader(
        "Drag & drop atau klik untuk memilih",
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
            
            all_images = {}
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
                    
                    img_list = []
                    for i, img in enumerate(images, 1):
                        buf = io.BytesIO()
                        if output_format == "PNG":
                            img.save(buf, format='PNG', optimize=True)
                            ext = ".png"
                        else:
                            img.save(buf, format='JPEG', quality=jpg_quality, optimize=True)
                            ext = ".jpg"
                        
                        name = f"{base_name}_page{i:03d}{ext}" if len(images) > 1 else f"{base_name}{ext}"
                        img_list.append((name, buf.getvalue()))
                    
                    all_images[file_name] = img_list
                    total_pages += len(images)
                    
                except Exception as e:
                    st.error(f"❌ {file_name}: {str(e)}")
            
            progress_bar.progress(1.0)
            elapsed = time.time() - start
            
            m1.metric("Selesai", f"{len(all_images)}/{len(uploaded_files)}")
            m2.metric("Halaman", total_pages)
            m3.metric("Waktu", f"{elapsed:.1f}s")
            status.empty()
            
            if all_images:
                st.markdown(f'<div class="success-card"><h3>🎉 Berhasil!</h3><p>✅ {len(all_images)} PDF → {total_pages} {output_format}</p><p>⏱️ {elapsed:.1f} detik</p></div>', unsafe_allow_html=True)
                
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                    for _, imgs in all_images.items():
                        for name, data in imgs:
                            zf.writestr(name, data)
                zip_buf.seek(0)
                
                st.download_button(
                    f"⬇️ Download {total_pages} {output_format} (ZIP)",
                    zip_buf,
                    f"pdf_to_{output_format.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    "application/zip",
                    use_container_width=True,
                    type="primary"
                )
                
                st.markdown("### 🖼️ Preview")
                prev = st.slider("Jumlah", 4, 20, 8, 4, key="prev1")
                cols = st.columns(4)
                count = 0
                for imgs in all_images.values():
                    for name, data in imgs:
                        if count >= prev: break
                        cols[count % 4].image(data, caption=name, use_container_width=True)
                        count += 1
                    if count >= prev: break
    else:
        st.markdown('<div class="info-card"><h4>📖 Cara Pakai:</h4><ol><li>Upload file PDF</li><li>Atur DPI & format</li><li>Klik Convert</li><li>Download ZIP</li></ol></div>', unsafe_allow_html=True)

# ============================================================================
# JPG to PDF MODE
# ============================================================================
elif mode == "JPG to PDF":
    with st.sidebar:
        st.markdown("### 🎛️ Pengaturan")
        quality = st.slider("Kualitas Gambar", 60, 100, 85, 5)
        compress = st.checkbox("Compress PDF", True)
    
    st.markdown("### 📤 Upload Gambar")
    uploaded_files = st.file_uploader(
        "Upload gambar yang akan digabung",
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
        
        st.markdown("#### 📋 Urutan Halaman")
        for idx, f in enumerate(uploaded_files, 1):
            st.markdown(f"`{idx}.` **{f.name}**")
        
        st.markdown("---")
        
        if st.button("🚀 Buat PDF", type="primary", use_container_width=True):
            prog = st.progress(0)
            
            try:
                images = []
                for idx, f in enumerate(uploaded_files, 1):
                    prog.progress(idx/len(uploaded_files))
                    
                    img = Image.open(f)
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
                
                pdf_buf = io.BytesIO()
                if len(images) == 1:
                    images[0].save(pdf_buf, format='PDF', quality=quality)
                else:
                    images[0].save(pdf_buf, format='PDF', save_all=True, append_images=images[1:], quality=quality)
                pdf_buf.seek(0)
                
                prog.progress(1.0)
                st.success(f"🎉 PDF dibuat dari {len(images)} gambar!")
                
                st.download_button(
                    "⬇️ Download PDF",
                    pdf_buf,
                    f"images_to_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    "application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.markdown('<div class="info-card"><h4>📖 Cara Pakai:</h4><ol><li>Upload beberapa gambar</li><li>Urutan sesuai upload</li><li>Klik Buat PDF</li><li>Download file PDF</li></ol></div>', unsafe_allow_html=True)

# ============================================================================
# IMAGE CONVERT MODE
# ============================================================================
elif mode == "Image Convert":
    with st.sidebar:
        st.markdown("### 🎛️ Pengaturan")
        out_fmt = st.selectbox("Format Output", ["JPG", "PNG", "WebP", "BMP"])
        
        if out_fmt in ["JPG", "WebP"]:
            qual = st.slider("Kualitas", 60, 100, 90, 5)
        
        resize_opt = st.checkbox("Resize juga?")
        if resize_opt:
            resize_pct = st.slider("Ukuran (%)", 10, 200, 100, 10)
    
    st.markdown("### 📤 Upload Gambar")
    uploaded_files = st.file_uploader(
        "Upload gambar",
        type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="conv_upload"
    )
    
    if uploaded_files:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stats-box"><div class="stats-number">{len(uploaded_files)}</div><div class="stats-label">Gambar</div></div>', unsafe_allow_html=True)
        with col2:
            total = sum([f.size for f in uploaded_files]) / (1024 * 1024)
            st.markdown(f'<div class="stats-box"><div class="stats-number">{total:.1f} MB</div><div class="stats-label">Input</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stats-box"><div class="stats-number">{out_fmt}</div><div class="stats-label">Output</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button(f"🚀 Convert ke {out_fmt}", type="primary", use_container_width=True):
            prog = st.progress(0)
            converted = []
            
            for idx, f in enumerate(uploaded_files, 1):
                prog.progress(idx/len(uploaded_files))
                
                try:
                    img = Image.open(f)
                    base = os.path.splitext(f.name)[0]
                    
                    if resize_opt and resize_pct != 100:
                        new_size = tuple(int(d * resize_pct / 100) for d in img.size)
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    buf = io.BytesIO()
                    
                    if out_fmt == "JPG":
                        if img.mode in ('RGBA', 'LA', 'P'):
                            bg = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            if img.mode in ('RGBA', 'LA'):
                                bg.paste(img, mask=img.split()[-1])
                            else:
                                bg.paste(img)
                            img = bg
                        img.save(buf, format='JPEG', quality=qual, optimize=True)
                        ext = ".jpg"
                    elif out_fmt == "PNG":
                        img.save(buf, format='PNG', optimize=True)
                        ext = ".png"
                    elif out_fmt == "WebP":
                        img.save(buf, format='WebP', quality=qual)
                        ext = ".webp"
                    else:
                        img.save(buf, format='BMP')
                        ext = ".bmp"
                    
                    converted.append((f"{base}{ext}", buf.getvalue()))
                except Exception as e:
                    st.error(f"❌ {f.name}: {str(e)}")
            
            prog.progress(1.0)
            
            if converted:
                st.success(f"🎉 {len(converted)} gambar → {out_fmt}!")
                
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for name, data in converted:
                        zf.writestr(name, data)
                zip_buf.seek(0)
                
                st.download_button(
                    f"⬇️ Download {len(converted)} {out_fmt} (ZIP)",
                    zip_buf,
                    f"converted_{out_fmt.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    "application/zip",
                    use_container_width=True,
                    type="primary"
                )
                
                st.markdown("### 🖼️ Preview")
                cols = st.columns(4)
                for idx, (name, data) in enumerate(converted[:8]):
                    cols[idx % 4].image(data, caption=name, use_container_width=True)
    else:
        st.markdown('<div class="info-card"><h4>📖 Cara Pakai:</h4><ol><li>Upload gambar</li><li>Pilih format output</li><li>Opsional: resize</li><li>Download hasil</li></ol></div>', unsafe_allow_html=True)

# ============================================================================
# IMAGE RESIZE MODE
# ============================================================================
elif mode == "Image Resize":
    with st.sidebar:
        st.markdown("### 🎛️ Pengaturan")
        
        resize_mode = st.radio("Mode", ["Percentage (%)", "Fixed Width", "Fixed Height", "Custom Size"])
        
        if resize_mode == "Percentage (%)":
            pct = st.slider("Ukuran (%)", 10, 200, 100, 10)
        elif resize_mode == "Fixed Width":
            w = st.number_input("Lebar (px)", 10, 5000, 800)
            ratio = st.checkbox("Keep ratio", True)
        elif resize_mode == "Fixed Height":
            h = st.number_input("Tinggi (px)", 10, 5000, 600)
            ratio = st.checkbox("Keep ratio", True)
        else:
            c1, c2 = st.columns(2)
            w = c1.number_input("Lebar", 10, 5000, 800)
            h = c2.number_input("Tinggi", 10, 5000, 600)
            ratio = st.checkbox("Keep ratio", False)
        
        keep_fmt = st.checkbox("Format asli", True)
        if not keep_fmt:
            new_fmt = st.selectbox("Format", ["JPG", "PNG", "WebP"])
            if new_fmt in ["JPG", "WebP"]:
                qual = st.slider("Kualitas", 60, 100, 90, 5)
    
    st.markdown("### 📤 Upload Gambar")
    uploaded_files = st.file_uploader(
        "Upload gambar",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="resize_upload"
    )
    
    if uploaded_files:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="stats-box"><div class="stats-number">{len(uploaded_files)}</div><div class="stats-label">Gambar</div></div>', unsafe_allow_html=True)
        with col2:
            total = sum([f.size for f in uploaded_files]) / (1024 * 1024)
            st.markdown(f'<div class="stats-box"><div class="stats-number">{total:.1f} MB</div><div class="stats-label">Total</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🚀 Resize", type="primary", use_container_width=True):
            prog = st.progress(0)
            resized = []
            
            for idx, f in enumerate(uploaded_files, 1):
                prog.progress(idx/len(uploaded_files))
                
                try:
                    img = Image.open(f)
                    ow, oh = img.size
                    base = os.path.splitext(f.name)[0]
                    ext_orig = os.path.splitext(f.name)[1]
                    
                    if resize_mode == "Percentage (%)":
                        nw, nh = int(ow * pct / 100), int(oh * pct / 100)
                    elif resize_mode == "Fixed Width":
                        nw = w
                        nh = int(oh * w / ow) if ratio else oh
                    elif resize_mode == "Fixed Height":
                        nh = h
                        nw = int(ow * h / oh) if ratio else ow
                    else:
                        if ratio:
                            r = min(w / ow, h / oh)
                            nw, nh = int(ow * r), int(oh * r)
                        else:
                            nw, nh = w, h
                    
                    img_r = img.resize((nw, nh), Image.Resampling.LANCZOS)
                    buf = io.BytesIO()
                    
                    if keep_fmt:
                        fmt = img.format or 'PNG'
                        ext = ext_orig
                        if fmt == 'JPEG':
                            if img_r.mode in ('RGBA', 'LA', 'P'):
                                bg = Image.new('RGB', img_r.size, (255, 255, 255))
                                if img_r.mode == 'P':
                                    img_r = img_r.convert('RGBA')
                                if img_r.mode in ('RGBA', 'LA'):
                                    bg.paste(img_r, mask=img_r.split()[-1])
                                else:
                                    bg.paste(img_r)
                                img_r = bg
                            img_r.save(buf, format='JPEG', quality=90)
                        else:
                            img_r.save(buf, format=fmt)
                    else:
                        if new_fmt == "JPG":
                            if img_r.mode in ('RGBA', 'LA', 'P'):
                                bg = Image.new('RGB', img_r.size, (255, 255, 255))
                                if img_r.mode == 'P':
                                    img_r = img_r.convert('RGBA')
                                if img_r.mode in ('RGBA', 'LA'):
                                    bg.paste(img_r, mask=img_r.split()[-1])
                                else:
                                    bg.paste(img_r)
                                img_r = bg
                            img_r.save(buf, format='JPEG', quality=qual)
                            ext = ".jpg"
                        elif new_fmt == "PNG":
                            img_r.save(buf, format='PNG')
                            ext = ".png"
                        else:
                            img_r.save(buf, format='WebP', quality=qual)
                            ext = ".webp"
                    
                    resized.append((f"{base}_resized{ext}", buf.getvalue()))
                except Exception as e:
                    st.error(f"❌ {f.name}: {str(e)}")
            
            prog.progress(1.0)
            
            if resized:
                st.success(f"🎉 {len(resized)} gambar resized!")
                
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for name, data in resized:
                        zf.writestr(name, data)
                zip_buf.seek(0)
                
                st.download_button(
                    f"⬇️ Download {len(resized)} Resized (ZIP)",
                    zip_buf,
                    f"resized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    "application/zip",
                    use_container_width=True,
                    type="primary"
                )
                
                st.markdown("### 🖼️ Before → After")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Original**")
                    st.image(uploaded_files[0], use_container_width=True)
                    orig = Image.open(uploaded_files[0])
                    st.caption(f"{orig.size[0]} x {orig.size[1]} px")
                with c2:
                    st.markdown("**Resized**")
                    st.image(resized[0][1], use_container_width=True)
                    new = Image.open(io.BytesIO(resized[0][1]))
                    st.caption(f"{new.size[0]} x {new.size[1]} px")
    else:
        st.markdown('<div class="info-card"><h4>📖 Cara Pakai:</h4><ol><li>Upload gambar</li><li>Pilih mode resize</li><li>Atur ukuran</li><li>Download hasil</li></ol></div>', unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 2rem 0;">
    <p><strong>🔄 Universal File Converter</strong></p>
    <p style="font-size: 0.9rem;">
        Semua proses di browser. File tidak disimpan.<br>
        PDF ↔ JPG/PNG | Image Convert | Image Resize
    </p>
</div>
""", unsafe_allow_html=True)
