import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000/api'
import warnings
warnings.filterwarnings('ignore')

def print_step(msg):
    print(f"\n{'='*50}\n[STEP] {msg}\n{'='*50}")

def signup_and_login(email, password, name):
    res_reg = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "full_name": name})
    print(f"Register: {res_reg.status_code} - {res_reg.text}")
    time.sleep(1)
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if res.status_code == 200:
        return res.json().get('access_token') or res.json().get('token')
    else:
        print(f"Login failed: {res.status_code} - {res.text}")
        
    if "mock_otp" in res_reg.json():
        otp = res_reg.json()["mock_otp"]
        res_ver = requests.post(f"{BASE_URL}/auth/verify-otp", json={"email": email, "otp": otp})
        if res_ver.status_code == 200:
            return res_ver.json().get("access_token")
        else:
            print(f"OTP verify failed: {res_ver.status_code} - {res_ver.text}")
    return None

def main():
    print_step("1. Starting acceptance tests")
    
    unique_id = int(time.time())
    token1 = signup_and_login(f"user{unique_id}@example.com", "Password123!", "User One")
    if not token1:
        print("Failed to login User 1")
        return
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    print_step("3. Upload Valid CSV Statement")
    with open('data/prototype/financial_events.csv', 'rb') as f:
        # Just send a small chunk to not overwhelm
        csv_data = f.read(2000)
    res_csv = requests.post(f"{BASE_URL}/statements/upload", headers=headers1, files={"file": ("test.csv", csv_data, "text/csv")})
    print(f"CSV Upload Response: {res_csv.status_code}")
    print(res_csv.json())

    print_step("4. Upload Sample PDF")
    pdf_path = "/Users/geetish/Desktop/FIN4YOU_Integrated/synthetic_statement.pdf"
    try:
        with open(pdf_path, 'rb') as f:
            res_pdf = requests.post(f"{BASE_URL}/statements/upload", headers=headers1, files={"file": ("sample.pdf", f, "application/pdf")})
        print(f"PDF Upload Response: {res_pdf.status_code}")
        print(res_pdf.json())
    except Exception as e:
        print(f"Could not open PDF: {e}")

    print_step("6. Verify Categorization")
    res_tx = requests.get(f"{BASE_URL}/users/transactions", headers=headers1)
    if res_tx.status_code == 200:
        txs = res_tx.json()
        print(f"Found {len(txs)} transactions.")
        if txs:
            print(f"Sample Tx: {txs[0]}")
    else:
        print("Failed to fetch transactions.")

    print_step("7. Verify Dashboard Totals")
    res_summary = requests.get(f"{BASE_URL}/users/state", headers=headers1)
    print(f"Summary Response: {res_summary.status_code}")
    if res_summary.status_code == 200:
        print(res_summary.json())

    print_step("8. Test Forecasts")
    res_fc = requests.get(f"{BASE_URL}/users/prediction", headers=headers1)
    print(f"Forecast Response: {res_fc.status_code}")

    print_step("9 & 10. Ask Copilot")
    res_cp1 = requests.post(f"{BASE_URL}/copilot/query", headers=headers1, json={"message": "Hello, who are you?"})
    print(f"Copilot Normal: {res_cp1.status_code} - {res_cp1.json() if res_cp1.status_code==200 else res_cp1.text}")
    
    res_cp2 = requests.post(f"{BASE_URL}/copilot/query", headers=headers1, json={"message": "What is my total spending this month?"})
    print(f"Copilot Financial: {res_cp2.status_code} - {res_cp2.json() if res_cp2.status_code==200 else res_cp2.text}")

    print_step("12. Test Invalid Files")
    res_inv = requests.post(f"{BASE_URL}/statements/upload", headers=headers1, files={"file": ("test.txt", b"invalid", "text/plain")})
    print(f"Invalid File Response: {res_inv.status_code} - {res_inv.text}")

    print_step("13. Check Isolation")
    token2 = signup_and_login(f"user2_{unique_id}@example.com", "Password123!", "User Two")
    headers2 = {"Authorization": f"Bearer {token2}"}
    res_tx2 = requests.get(f"{BASE_URL}/users/transactions", headers=headers2)
    txs2 = res_tx2.json() if res_tx2.status_code == 200 else []
    print(f"User 2 found {len(txs2)} transactions. (Should be 0 if isolation works).")

if __name__ == "__main__":
    main()
