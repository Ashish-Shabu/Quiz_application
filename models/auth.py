# models/auth.py
import os
import winsound
from tkinter import messagebox

class AuthManager:
    def __init__(self):
        pass
    
    def psdvalid(self, password):
        """Validate the admin password."""
        if len(password) < 6:
            return False
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(not c.isalnum() for c in password)
        return has_letter and has_digit and has_symbol

    def pcheck(self):
        """Retrieve the stored admin password and recovery key."""
        try:
            with open("assets/psd.bin", "rb") as f:
                data = list(f.read())
            if not data:
                return "", ""
            d = data[-1]  # length of digits for k
            g = data[-2]  # length of recovery key
            t = data[-(d+2):-2]  # digits of k
            k = 0
            for digit in t:
                k = k * 10 + digit
            n = (len(data) - (d+2)) // 2
            div_list = data[:n]
            rem_list = data[n:2*n]
            psd_chars = [chr(div_list[i] * k + rem_list[i]) for i in range(n)]
            psd_str = "".join(psd_chars)
            password = psd_str[:-g] if g > 0 else psd_str
            hint = psd_str[-g:] if g > 0 else ""
            return password, hint
        except Exception as e:
            messagebox.showerror("Error", f"Error reading password file: {str(e)}")
            return "", ""
    
    def save_password(self, password, hint, k=9):
        """Save the admin password"""
        try:
            with open("assets/psd.bin", "wb") as f:
                psd = password + hint
                a = [ord(i) for i in psd]
                t = [int(i) for i in str(k)]
                l2 = [len(t)]
                g = [len(hint)]
                qr = [i // k for i in a] + [i % k for i in a] + t + g + l2
                f.write(bytearray(qr))
            winsound.PlaySound("assets/03.wav", winsound.SND_FILENAME)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error saving password: {str(e)}")
            return False