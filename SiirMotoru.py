# Author   : MUSTAFA ERGÜL

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import time
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pickle
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import webbrowser

# Türkçe karakter ve emoji desteği için font yükleme
pdfmetrics.registerFont(TTFont("CustomFont", "DejaVuSans.ttf"))

# Model ve Tokenizer'ı yükleme
model = load_model("SairAi.h5")
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)
input_length = model.input_shape[1]
max_seq_len = input_length + 1
def generate_poem(prompt_words, num_lines=4):
    poem = []
    for word in prompt_words:
        input_text = word
        for _ in range(num_lines):
            token_list = tokenizer.texts_to_sequences([input_text])[0]
            token_list = pad_sequences([token_list], maxlen=max_seq_len-1, padding='pre')
            predicted = np.argmax(model.predict(token_list, verbose=0), axis=-1)

            output_word = ''
            for w, index in tokenizer.word_index.items():
                if index == predicted:
                    output_word = w
                    break
            input_text += ' ' + output_word
        poem.append(input_text)
    return "\n".join(poem)
class PoemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yapay Zeka Şiir Makinesi 🎉")
        self.fullscreen = True
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#fff0f5")
        self.root.bind("<Escape>", self.exit_fullscreen)

        self.fullscreen_button = tk.Button(self.root, text="🔳 Tam Ekran", command=self.enter_fullscreen,
                                           font=("Comic Sans MS", 14), bg="#ffe4e1", fg="black")

        self.build_main_screen()
    def build_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.title = tk.Label(self.root, text="🌈 Yapay Zeka Şiir Makinesi 🌈", font=("Comic Sans MS", 30, "bold"), bg="#fff0f5")
        self.title.pack(pady=20)

        self.name_label = tk.Label(self.root, text="Öğrenci Adı:", font=("Comic Sans MS", 20), bg="#fff0f5")
        self.name_label.pack()
        self.name_entry = tk.Entry(self.root, font=("Comic Sans MS", 20), width=30)
        self.name_entry.pack(pady=5)

        self.word_entries = []
        for i in range(4):
            label = tk.Label(self.root, text=f"{i+1}. Kelime:", font=("Comic Sans MS", 20), bg="#fff0f5")
            label.pack()
            entry = tk.Entry(self.root, font=("Comic Sans MS", 20), width=30)
            entry.pack(pady=5)
            self.word_entries.append(entry)

        self.generate_button = tk.Button(self.root, text="🎨 Şiir Oluştur 🎨", font=("Comic Sans MS", 20, "bold"), bg="#ff69b4", fg="white", command=self.start_poem_thread)
        self.generate_button.pack(pady=40)

        self.footer = tk.Label(self.root, text="Bu yapay zeka şiir motoru Öğretmen Ayşe Dora için eğitilmiştir.",
                               font=("Comic Sans MS", 14, "italic"), bg="#fff0f5", fg="gray")
        self.footer.place(relx=0.5, rely=0.93, anchor="center")

    def start_poem_thread(self):
        thread = threading.Thread(target=self.generate_poem_ui)
        thread.start()

    def generate_poem_ui(self):
        name = self.name_entry.get().strip()
        words = [e.get().strip() for e in self.word_entries]

        if not name or any(not w for w in words):
            messagebox.showwarning("Eksik Bilgi", "Lütfen öğrenci adını ve dört kelimeyi giriniz.")
            return

        self.student_name = name
        for widget in self.root.winfo_children():
            widget.destroy()

        status_label = tk.Label(self.root, text="Şiiri heyecanla yazıyorum... Sende benim kadar heyecanlı mısın? 😍",
                                font=("Comic Sans MS", 24, "italic"), bg="#fff0f5", fg="purple")
        status_label.pack(pady=200)

        animation_label = tk.Label(self.root, text="", font=("Comic Sans MS", 50), bg="#fff0f5")
        animation_label.pack()

        for i in range(20):
            animation_label.config(text="🎵" * (i % 5 + 1))
            time.sleep(0.5)
            self.root.update()

        poem_text = generate_poem(words)
        self.last_poem = poem_text

        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="🎉 Şiir Hazır! 🎉", font=("Comic Sans MS", 30, "bold"), bg="#fff0f5", fg="green").pack(pady=20)
        tk.Label(self.root, text=f"{name} için oluşturduğum şiir:", font=("Comic Sans MS", 24), bg="#fff0f5").pack(pady=10)

        tk.Label(self.root, text="🌸🌟", font=("Comic Sans MS", 24), bg="#fff0f5").pack()

        output_label = tk.Label(self.root, text=poem_text, font=("Comic Sans MS", 20), bg="#fff0f5", justify="center", wraplength=1000)
        output_label.pack(pady=10)

        tk.Label(self.root, text="🌟🌸", font=("Comic Sans MS", 24), bg="#fff0f5").pack()

        btn_frame = tk.Frame(self.root, bg="#fff0f5")
        btn_frame.pack(pady=30)

        try:
            printer_img = Image.open("printer.png").resize((50, 50))
            self.printer_icon = ImageTk.PhotoImage(printer_img)
            print_button = tk.Button(btn_frame, image=self.printer_icon, command=self.print_pdf, bg="#fff0f5", border=0)
        except:
            print_button = tk.Button(btn_frame, text="🖨️ Yazdır", font=("Comic Sans MS", 18), command=self.print_pdf, bg="#87ceeb")

        print_button.grid(row=0, column=0, padx=20)

        new_poem_button = tk.Button(btn_frame, text="🔁 Yeni Şiir Oluştur", font=("Comic Sans MS", 18), bg="#ffb6c1", command=self.build_main_screen)
        new_poem_button.grid(row=0, column=1, padx=20)

    def print_pdf(self):
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        filename = f"{self.student_name}_Siiri.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Türkçe karakter ve stil desteği için yazı tipini yükle
        pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
        c.setFont("DejaVu", 20)

        # Üst süsleme
        c.drawCentredString(width / 2, height - 70, "❀ ✿ ❀  Şiir Zamanı  ❀ ✿ ❀")

        # Başlık
        c.setFont("DejaVu", 16)
        c.drawCentredString(width / 2, height - 110, f"{self.student_name} için Yapay Zeka Şiiri")

        # Şiir içeriği
        c.setFont("DejaVu", 14)
        y = height - 160
        for line in self.last_poem.split("\n"):
            c.drawCentredString(width / 2, y, line)
            y -= 25

        # Alt süsleme
        c.setFont("DejaVu", 20)
        c.drawCentredString(width / 2, y - 10, "♥ ~ ♥ ~ ♥")

        c.save()
        webbrowser.open_new(filename)
        messagebox.showinfo("Yazdır", f"PDF başarıyla oluşturuldu ve açıldı: {filename}")

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)
        self.root.after(100, self.show_fullscreen_button)
    def show_fullscreen_button(self):
        self.fullscreen_button.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-20)

    def enter_fullscreen(self):
        self.fullscreen = True
        self.root.attributes("-fullscreen", True)
        self.fullscreen_button.place_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = PoemApp(root)
    root.mainloop()