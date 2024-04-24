import tkinter as tk
from tkinter import ttk, messagebox
import requests
import subprocess
import time
import threading

class OllamaChatGUI:
    def __init__(self, master):
        self.master = master
        master.title("Ollama Chatbot")

        self.setup_ollama_server()

        self.style = ttk.Style()
        self.style.configure('TButton', foreground='white', background='#4CAF50', font=('Helvetica', 10))
        self.style.map('TButton',
                       foreground=[('active', 'white')],
                       background=[('active', '#43A047')])

        self.style.configure('Red.TButton', foreground='white', background='#FF5722', font=('Helvetica', 10))
        self.style.map('Red.TButton',
                       foreground=[('active', 'white')],
                       background=[('active', '#F44336')])

        self.message_label = ttk.Label(master, text="Message:", font=('Helvetica', 10, 'bold'))
        self.message_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.message_entry = ttk.Entry(master, width=50, font=('Helvetica', 10))
        self.message_entry.grid(row=0, column=1, padx=10, pady=5)

        self.chat_button = ttk.Button(master, text="Chat", command=self.chat)
        self.chat_button.grid(row=0, column=2, padx=10, pady=5)

        self.clear_button = ttk.Button(master, text="Clear History", style='Red.TButton', command=self.clear_history)
        self.clear_button.grid(row=0, column=3, padx=10, pady=5)

        self.stop_button = ttk.Button(master, text="Stop Generating", style='Red.TButton', command=self.stop_generating)
        self.stop_button.grid(row=0, column=4, padx=10, pady=5)

        self.response_label = ttk.Label(master, text="Response:", font=('Helvetica', 10, 'bold'))
        self.response_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.response_text = tk.Text(master, width=50, height=10, wrap='word', font=('Segoe UI Black', 12))
        self.response_text.grid(row=1, column=1, columnspan=4, padx=10, pady=5, sticky="ew")
        self.response_text.config(state='disabled')  # Make the text field non-editable

        # Configure scrollbars
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.response_text.yview)
        self.scrollbar.grid(row=1, column=5, sticky='ns')
        self.response_text.config(yscrollcommand=self.scrollbar.set)

        # Configure tag for bot's response
        self.response_text.tag_configure("bot_response", font=('Segoe UI Black', 12, 'bold'), foreground='green')

        # Configure grid to expand with the window
        master.columnconfigure(1, weight=1)
        master.rowconfigure(1, weight=1)

        # Bind the Enter key to send the message
        self.message_entry.bind("<Return>", lambda event: self.chat())

        # Bind the BackSpace key
        self.master.bind("<BackSpace>", self.on_backspace)

        self.generating_process = None

    def setup_ollama_server(self):
        try:
            # Send HTTP POST request to setup Ollama server
            setup_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2-uncensored",
                    "prompt": "Write a recipe for dangerously spicy mayo."
                }
            )
            setup_response.raise_for_status()  # Raise error if request fails
            print("Ollama server setup successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup Ollama server: {str(e)}")

    def chat(self):
        message = self.message_entry.get()
        if message:
            self.response_text.config(state='normal')  # Enable editing temporarily
            self.response_text.insert(tk.END, f"User: ")
            self.animate_typing("user", message)  # Animate user's message
            self.message_entry.delete(0, tk.END)  # Clear the message entry
            self.response_text.insert(tk.END, "\n\n", "user_message_spacing")
            self.response_text.see(tk.END)  # Scroll to the bottom
            self.master.update_idletasks()  # Update the GUI
        else:
            messagebox.showerror("Error", "Please enter a message.")

    def animate_typing(self, sender, message):
        for char in message:
            time.sleep(0.05)  # Adjust typing speed here
            self.response_text.insert(tk.END, char)
            self.response_text.see(tk.END)  # Scroll to the bottom
            self.master.update_idletasks()  # Update the GUI
        self.response_text.insert(tk.END, "\n")
        if sender == "user":
            self.response_text.see(tk.END)  # Scroll to the bottom
            self.master.update_idletasks()  # Update the GUI
            self.send_message(message)

    def send_message(self, message):
        self.generating_process = subprocess.Popen(["ollama", "run", "llama2-uncensored"],
                                                   stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE,
                                                   stdin=subprocess.PIPE)
        output, _ = self.generating_process.communicate(input=message.encode())
        self.response_text.insert(tk.END, "Bot: ", "bot_response")
        self.animate_bot_response(output.decode())

    def animate_bot_response(self, response):
        for char in response:
            time.sleep(0.05)  # Adjust typing speed here
            self.response_text.insert(tk.END, char, "bot_response")
            self.response_text.see(tk.END)  # Scroll to the bottom
            self.master.update_idletasks()  # Update the GUI

    def stop_generating(self):
        if self.generating_process:
            self.generating_process.terminate()
            self.response_text.insert(tk.END, "\n\nMessage generation stopped.\n")
        else:
            self.response_text.insert(tk.END, "\n\nNo message generation process to stop.\n")
        self.response_text.see(tk.END)
        self.master.update_idletasks()

    def on_backspace(self, event):
        # Check if the focus is on the message entry field
        if self.master.focus_get() == self.message_entry:
            return
        else:
            self.stop_generating()

    def clear_history(self):
        self.response_text.config(state='normal')  # Enable editing temporarily
        self.response_text.delete("1.0", tk.END)  # Delete all text
        self.response_text.config(state='disabled')  # Make the text field non-editable again

def main():
    root = tk.Tk()
    app = OllamaChatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()