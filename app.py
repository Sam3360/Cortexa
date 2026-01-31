import customtkinter as ctk
import ollama
import threading
import time

MODEL = "llama3"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CortexaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cortexa 🧠")
        self.geometry("900x600")

        self.chat_history = []

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.chat_frame = ctk.CTkScrollableFrame(self)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_box = ctk.CTkEntry(
            self.input_frame, placeholder_text="Ask Cortexa..."
        )
        self.input_box.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_box.bind("<Return>", lambda e: self.send_message())

        ctk.CTkButton(
            self.input_frame, text="Send", command=self.send_message
        ).grid(row=0, column=1)

    # ---------------- BUBBLES ----------------
    def add_message(self, text, sender):
        if sender == "user":
            bg = "#1f6aa5"
            border = "#154a75"
            anchor = "e"
        else:
            bg = "#2a2a2a"
            border = "#1c1c1c"
            anchor = "w"

        outer = ctk.CTkFrame(
            self.chat_frame,
            fg_color=border,
            corner_radius=18,
        )

        inner = ctk.CTkFrame(
            outer,
            fg_color=bg,
            corner_radius=16,
        )

        label = ctk.CTkLabel(
            inner,
            text=text,
            wraplength=520,
            justify="left",
        )

        label.pack(padx=12, pady=8)
        inner.pack(padx=2, pady=2)
        outer.pack(anchor=anchor, padx=10, pady=5)

        self.chat_frame.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1)

    # ---------------- SEND ----------------
    def send_message(self):
        text = self.input_box.get().strip()
        if not text:
            return

        self.input_box.delete(0, "end")
        self.add_message(text, "user")
        self.chat_history.append({"role": "user", "content": text})

        thinking_label = self.start_thinking_animation()

        threading.Thread(
            target=self.run_ai,
            args=(thinking_label,),
            daemon=True,
        ).start()

    # ---------------- THINKING DOTS ----------------
    def start_thinking_animation(self):
        label = ctk.CTkLabel(self.chat_frame, text="Cortexa is thinking")
        label.pack(anchor="w", padx=10, pady=5)

        def animate():
            dots = ""
            while getattr(label, "alive", True):
                dots = "." * ((len(dots) % 3) + 1)
                label.configure(text=f"Cortexa is thinking{dots}")
                time.sleep(0.5)

        label.alive = True
        threading.Thread(target=animate, daemon=True).start()
        return label

    # ---------------- AI ----------------
    def run_ai(self, thinking_label):
        try:
            response = ollama.chat(
                model=MODEL,
                messages=self.chat_history,
                options={
                    "temperature": 0.4,
                    "num_predict": 180,
                },
            )
            text = response["message"]["content"]
        except Exception as e:
            text = f"⚠️ {e}"

        self.after(0, lambda: self.finish_response(thinking_label, text))

    def finish_response(self, thinking_label, text):
        thinking_label.alive = False
        thinking_label.destroy()

        self.fake_typing(text)
        self.chat_history.append({"role": "assistant", "content": text})

    # ---------------- FAKE TYPING ----------------
    def fake_typing(self, text):
        bg = "#2a2a2a"
        border = "#1c1c1c"

        outer = ctk.CTkFrame(
            self.chat_frame,
            fg_color=border,
            corner_radius=18,
        )
        inner = ctk.CTkFrame(
            outer,
            fg_color=bg,
            corner_radius=16,
        )

        label = ctk.CTkLabel(
            inner, text="", wraplength=520, justify="left"
        )

        label.pack(padx=12, pady=8)
        inner.pack(padx=2, pady=2)
        outer.pack(anchor="w", padx=10, pady=5)

        current = ""
        for char in text:
            current += char
            label.configure(text=current)
            self.chat_frame.update_idletasks()
            time.sleep(0.008)


if __name__ == "__main__":
    CortexaApp().mainloop()
