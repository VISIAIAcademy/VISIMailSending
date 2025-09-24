import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from string import Template
from io import StringIO

st.title("📧 Gửi Email Cá Nhân Hóa bằng Python")

# --- Nhập thông tin tài khoản Gmail ---
st.subheader("Thông tin Gmail")
sender_email = st.text_input("Email Gmail của bạn", "")
app_password = st.text_input("App Password (không phải mật khẩu Gmail thường)", "", type="password")

# --- Upload template ---
st.subheader("Tải file template (.txt)")
template_file = st.file_uploader("Chọn file template", type=['txt'])
template_text = ""
if template_file is not None:
    template_text = template_file.read().decode('utf-8')
    st.text_area("Nội dung template", template_text, height=150)

# --- Upload CSV ---
st.subheader("Tải file CSV dữ liệu")
csv_file = st.file_uploader("Chọn file CSV", type=['csv'])
data = None
if csv_file is not None:
    data = pd.read_csv(csv_file)
    st.dataframe(data)

st.info("File CSV cần có cột email (người nhận) + các cột placeholder khác.")

# --- Subject ---
subject = st.text_input("Tiêu đề email", "Thông báo kết quả")

# --- Nút gửi ---
if st.button("Gửi email"):
    if not sender_email or not app_password:
        st.error("Cần nhập email và app password.")
    elif not template_text:
        st.error("Chưa upload template.")
    elif data is None:
        st.error("Chưa upload CSV.")
    else:
        st.write("Bắt đầu gửi...")
        smtp_server = "smtp.gmail.com"
        port = 587
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            server.login(sender_email, app_password)
            template = Template(template_text)

            success, fail = 0, 0
            log = []

            for idx, row in data.iterrows():
                try:
                    # Tạo nội dung cá nhân hoá
                    message_body = template.safe_substitute(row.to_dict())
                    msg = MIMEText(message_body, 'plain', 'utf-8')
                    msg['From'] = sender_email
                    msg['To'] = row['email']
                    msg['Subject'] = subject

                    server.send_message(msg)
                    success += 1
                    log.append(f"✅ Gửi tới {row['email']} thành công")
                except Exception as e:
                    fail += 1
                    log.append(f"❌ Lỗi với {row['email']}: {e}")

            server.quit()

            st.success(f"Gửi xong: {success} thành công, {fail} lỗi.")
            st.text("\n".join(log))

        except Exception as e:
            st.error(f"Lỗi khi kết nối SMTP: {e}")
