import streamlit as st
import requests
import datetime

BACKEND_URL = "http://backend:8000"

st.title("Company AI Chatbot Demos 🚀")

# === CHAT SECTION ===
st.subheader("Chat with Acme Corp Assistant")

company = st.selectbox("Pick a mock company:", ["Acme Corp (HR & Policies)"])

company_id = company.split()[0].lower()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything about the company..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"question": prompt, "company_id": company_id}
                )
                resp.raise_for_status()
                answer = resp.json()["answer"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Oops: {e}")

# === DOCUMENT UPLOAD SECTION ===
st.subheader("Upload Company Documents (PDF only)")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    company_id_upload = st.selectbox("Company for this document:", ["acme"], key="upload_company")
    if st.button("Upload Document"):
        with st.spinner("Uploading and indexing..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                resp = requests.post(
                    f"{BACKEND_URL}/upload?company_id={company_id_upload}",
                    files=files
                )
                resp.raise_for_status()
                result = resp.json()
                st.success(result["status"])
            except Exception as e:
                st.error(f"Upload failed: {e}")

# === INTERVIEW BOOKING SECTION ===
st.subheader("Book an Interview with Acme Corp")

with st.form("interview_form"):
    name = st.text_input("Your Full Name", placeholder="John Doe")
    email = st.text_input("Your Email", placeholder="john@example.com")
    phone = st.text_input("Phone Number (optional)")
    position = st.selectbox("Position You're Interested In", [
        "R&D Engineer (Explosives Division)",
        "Marketing - Anvil Product Specialist",
        "HR Manager",
        "Other"
    ])
    preferred_date = st.date_input("Preferred Interview Date", min_value=datetime.date.today())
    preferred_time = st.time_input("Preferred Time", value=datetime.time(10, 0))

    submit = st.form_submit_button("Book Interview")

if submit:
    if not name or not email:
        st.error("Name and email are required!")
    else:
        with st.spinner("Booking your interview..."):
            try:
                payload = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "position": position,
                    "date": str(preferred_date),
                    "time": str(preferred_time),
                    "company_id": company_id
                }
                resp = requests.post(f"{BACKEND_URL}/book-interview", json=payload)
                resp.raise_for_status()
                result = resp.json()
                st.success(result.get("message", "Interview booked! Check your email for confirmation."))
            except Exception as e:
                st.error(f"Booking failed: {e}")