import base64
import io
import os
import threading
from socket import socket, AF_INET, SOCK_STREAM

from customtkinter import *
from tkinter import filedialog
from PIL import Image

class RegisterWindow(CTk):
   def __init__(self):
       super().__init__()
       self.username = None
       self.title('Приєднатися до сервера')
       self.geometry('300x300')


       CTkLabel(self, text='Вхід в LogiTalk', font=('Arial', 20, 'bold')).pack(pady=40)
       self.name_entry = CTkEntry(self, placeholder_text='Введіть імʼя')
       self.name_entry.pack()


       self.host_entry = CTkEntry(self, placeholder_text='Введіть хост сервера localhost')
       self.host_entry.pack(pady=5)
       self.port_entry = CTkEntry(self, placeholder_text='Введіть порт сервера 12334 ')
       self.port_entry.pack()


       self.submit_button = CTkButton(self, text='Приєднатися', command=self.start_chat)
       self.submit_button.pack(pady=5)


   def start_chat(self):
       self.username = self.name_entry.get().strip()
       try:
           self.sock = socket(AF_INET, SOCK_STREAM)
           self.sock.connect((self.host_entry.get(), int(self.port_entry.get())))
           hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
           self.sock.send(hello.encode('utf-8'))


           self.destroy()


           win = MainWindow(self.sock, self.username)
           win.mainloop()


       except Exception as e:
           print(f"Не вдалося підключитися до сервера: {e}")

class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        self.geometry("600x400")
        self.title("LogiTalk")
        self.configure(fg_color="#2B2B2B")

        self.username = "Денис"
        self.avatar_image = None  # аватар користувача

        # === МЕНЮ ===
        self.menu_frame = CTkFrame(self, width=30, height=400, fg_color="indigo")
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.is_menu_shown = False
        self.menu_animate_speed = -20

        self.menu_btn = CTkButton(self, text="⚙", command=self.toggle_menu, width=30)
        self.menu_btn.place(x=0, y=0)

        # === ПОЛЕ ЧАТУ ===
        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)

        # === ПОЛЕ ВВЕДЕННЯ ===
        self.msg_entry = CTkEntry(self, placeholder_text="Введіть повідомлення 💬", height=40)
        self.msg_entry.place(x=0, y=0)

        self.send_button = CTkButton(self, text="➡", width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        self.open_img = CTkButton(self, text="📂", width=50, height=40, command=self.open_image)
        self.open_img.place(x=0, y=0)

        # === АДАПТИВНЕ РОЗТАШУВАННЯ ===
        self.adaptive_ui()

        # === ДЕМО ===
        self.add_msg(f"{self.username}: test")
        self.add_msg("Демонстрація відображення зображення:",
                     CTkImage(Image.open("bg2.jpg"), size=(300, 150)))

        # === З'ЄДНАННЯ З СЕРВЕРОМ ===
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode("utf-8"))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_msg(f"Не вдалося підключитися до сервера: {e}")

    # === МЕНЮ ===
    def toggle_menu(self):
        if self.is_menu_shown:
            self.is_menu_shown = False
            self.menu_animate_speed *= -1
            self.show_menu()
        else:
            self.is_menu_shown = True
            self.menu_animate_speed *= -1
            self.show_menu()

            # Вміст меню
            self.label = CTkLabel(self.menu_frame, text="Імʼя")
            self.label.pack(pady=10)

            self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...")
            self.entry.insert(0, self.username)
            self.entry.pack(pady=(0, 10))

            self.avatar_btn = CTkButton(self.menu_frame, text="Обрати аватарку", command=self.choose_avatar)
            self.avatar_btn.pack(pady=(5, 10))

            self.avatar_preview = CTkLabel(self.menu_frame, text="(немає)")
            self.avatar_preview.pack(pady=(0, 10))

            if self.avatar_image:
                self.avatar_preview.configure(image=self.avatar_image, text="")

            self.save_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name)
            self.save_button.pack()

            self.theme_option = CTkOptionMenu(self.menu_frame, values=["Темна", "Світла"], command=self.change_theme)
            self.theme_option.pack(side="bottom", pady=20)

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.menu_animate_speed)
        if not self.menu_frame.winfo_width() >= 200 and self.is_menu_shown:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 60 and not self.is_menu_shown:
            self.after(10, self.show_menu)
            for widget in self.menu_frame.winfo_children():
                widget.destroy()

    # === ІМ'Я ===
    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_msg(f"Ваш новий нік: {self.username}")

    # === АВАТАРКА ===
    def choose_avatar(self):
        file_path = filedialog.askopenfilename(
            title="Оберіть аватарку", filetypes=[("Images", "*.png;*.jpg;*.jpeg")]
        )
        if not file_path:
            return
        try:
            size = (40, 40)
            img = Image.open(file_path).resize(size)
            self.avatar_image = CTkImage(img, size=size)
            self.avatar_preview.configure(image=self.avatar_image, text="")
        except Exception as e:
            self.add_msg(f"Помилка вибору аватарки: {e}")

    # === АДАПТИВНИЙ ІНТЕРФЕЙС ===
    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
            height=self.winfo_height() - 50
        )

        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.msg_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.msg_entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 110)
        self.open_img.place(x=self.winfo_width() - 105, y=self.send_button.winfo_y())

        self.after(50, self.adaptive_ui)

    # === ДОДАВАННЯ ПОВІДОМЛЕНЬ ===
    def add_msg(self, message, img=None, avatar=None):
        msg_frame = CTkFrame(self.chat_field, fg_color="gray")
        msg_frame.pack(pady=5, anchor="w")

        wrap_size = max(300, self.chat_field.winfo_width() - 100)

        if avatar:
            CTkLabel(msg_frame, image=avatar, text="").pack(side="left", padx=(10, 5), pady=5)

        if not img:
            CTkLabel(msg_frame, text=message, wraplength=wrap_size,
                     text_color='white', justify='left').pack(padx=10, pady=5)
        else:
            CTkLabel(msg_frame, text=message, wraplength=wrap_size,
                     text_color='white', image=img, compound='top',
                     justify='left').pack(padx=10, pady=5)

    # === ВІДПРАВКА ПОВІДОМЛЕНЬ ===
    def send_message(self):
        message = self.msg_entry.get()
        if message:
            self.add_msg(f"{self.username}: {message}", avatar=self.avatar_image)
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.msg_entry.delete(0, END)

    # === ОТРИМАННЯ ПОВІДОМЛЕНЬ ===
    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8", errors="ignore")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_msg(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img, size=(300, 300))
                    self.add_msg(f"{author} надіслав(ла) зображення: {filename}", img=ctk_img)
                except Exception as e:
                    self.add_msg(f"Помилка відображення зображення: {e}")
        else:
            self.add_msg(line)

    # === ВІДПРАВКА ЗОБРАЖЕНЬ ===
    def open_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)
            data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
            self.sock.sendall(data.encode())
            self.add_msg("", CTkImage(light_image=Image.open(file_name), size=(300, 300)),
                         avatar=self.avatar_image)
        except Exception as e:
            self.add_msg(f"Не вдалося надіслати зображення: {e}")

    # === ЗМІНА ТЕМИ ===
    def change_theme(self, value):
        if value == "Темна":
            set_appearance_mode("dark")
            self.configure(fg_color="indigo")
            self.menu_frame.configure(fg_color="indigo")
        else:
            set_appearance_mode("light")
            self.configure(fg_color="violet")
            self.menu_frame.configure(fg_color="violet")

if __name__ == "__main__":
    RegisterWindow().mainloop()
