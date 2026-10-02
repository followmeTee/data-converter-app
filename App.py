import streamlit as st
import pandas as pd
import io

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="Data Converter Web App",
    page_icon="🔄",
    layout="wide"
)

# หัวข้อแอปพลิเคชัน
st.title("🔄 Data File Converter Web App")
st.write("แอปพลิเคชันแปลงไฟล์ข้อมูลอัตโนมัติ (รองรับ CSV, Excel, JSON และ Parquet)")

# 1. ส่วนอัปโหลดไฟล์
uploaded_file = st.file_uploader(
    "อัปโหลดไฟล์ข้อมูลของคุณที่นี่", 
    type=["csv", "xlsx", "xls", "json", "parquet"]
)

if uploaded_file is not None:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    
    try:
        # อ่านไฟล์ข้อมูลเข้า Pandas DataFrame
        if file_ext == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_ext in ["xlsx", "xls"]:
            df = pd.read_excel(uploaded_file)
        elif file_ext == "json":
            df = pd.read_json(uploaded_file)
        elif file_ext == "parquet":
            df = pd.read_parquet(uploaded_file)
        
        st.success(f"อัปโหลดไฟล์สำเร็จ: **{uploaded_file.name}** (จำนวน {len(df):,} แถว, {len(df.columns)} คอลัมน์)")
        
        # แสดงตัวอย่างข้อมูล (Data Preview)
        with st.expander("👀 ดูตัวอย่างข้อมูล (Data Preview)", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)
            
        st.divider()
        
        # 2. ตั้งค่าการแปลงไฟล์
        col1, col2 = st.columns([2, 1])
        
        with col1:
            target_format = st.selectbox(
                "เลือกรูปแบบไฟล์ปลายทางที่ต้องการ (Target Format)",
                ["CSV (.csv)", "Excel (.xlsx)", "JSON (.json)", "Parquet (.parquet)"]
            )
        
        # เตรียมระบบ แปลงข้อมูลในหน่วยความจำ (In-Memory Buffer)
        buffer = io.BytesIO()
        file_stem = uploaded_file.name.rsplit(".", 1)[0]
        
        if target_format == "CSV (.csv)":
            output_filename = f"{file_stem}_converted.csv"
            mime_type = "text/csv"
            # ใช้ utf-8-sig รองรับภาษาไทยใน Excel
            data_bytes = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            
        elif target_format == "Excel (.xlsx)":
            output_filename = f"{file_stem}_converted.xlsx"
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            data_bytes = buffer.getvalue()
            
        elif target_format == "JSON (.json)":
            output_filename = f"{file_stem}_converted.json"
            mime_type = "application/json"
            data_bytes = df.to_json(orient="records", indent=4, force_ascii=False).encode('utf-8')
            
        elif target_format == "Parquet (.parquet)":
            output_filename = f"{file_stem}_converted.parquet"
            mime_type = "application/octet-stream"
            df.to_parquet(buffer, index=False)
            data_bytes = buffer.getvalue()

        # 3. ปุ่มดาวน์โหลดไฟล์
        with col2:
            st.write(" ") # จัดระยะตำแหน่งปุ่ม
            st.write(" ")
            st.download_button(
                label=f"⬇️ ดาวน์โหลด {output_filename}",
                data=data_bytes,
                file_name=output_filename,
                mime=mime_type,
                type="primary",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")