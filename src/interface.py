import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import threading
import sys
import os

# Add the parent directory to the path so we can import draft
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.draft import run_document_agent, process_user_input

class DrafterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drafter - AI Writing Assistant")
        self.root.geometry("800x600")
        self.root.config(bg="#f5f5f5")
        
        # Main frame
        self.main_frame = tk.Frame(root, bg="#f5f5f5")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat display
        self.chat_frame = tk.Frame(self.main_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, 
                                                    bg="#ffffff", fg="#333333",
                                                    font=("Arial", 10))
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        # Input area
        self.input_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        self.input_frame.pack(fill=tk.X, expand=False)
        
        self.input_box = scrolledtext.ScrolledText(self.input_frame, wrap=tk.WORD, 
                                                height=4, bg="#ffffff", fg="#333333",
                                                font=("Arial", 10))
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_box.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, 
                                    bg="#4caf50", fg="white", font=("Arial", 10, "bold"),
                                    relief=tk.FLAT, padx=15)
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize Drafter
        self.app, self.state = run_document_agent()
        
        # Welcome message
        self.display_message("🤖 DRAFTER: I'm ready to help you update a document. What would you like to create?", "bot")
        
        # Processing flag
        self.processing = False

    def display_message(self, message, sender):
        """Display a message in the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add appropriate icon based on sender
        if sender == "user":
            self.chat_display.insert(tk.END, "\n👤 YOU: ", "user_tag")
        elif sender == "bot":
            self.chat_display.insert(tk.END, "\n", "bot_tag")
        elif sender == "tool":
            self.chat_display.insert(tk.END, "\n", "tool_tag")
        
        # Insert the actual message
        self.chat_display.insert(tk.END, f"{message}\n")
        
        # Auto-scroll to the end
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        """Send user message to Drafter"""
        if self.processing:
            return "break"
            
        # Get user input
        user_input = self.input_box.get("1.0", tk.END).strip()
        if not user_input:
            return "break"  # Don't process empty messages
            
        # Clear input box
        self.input_box.delete("1.0", tk.END)
        
        # Display user message
        self.display_message(user_input, "user")
        
        # Flag that we're processing
        self.processing = True
        self.status_var.set("Processing...")
        self.send_button.config(state=tk.DISABLED)
        
        # Process in a separate thread to keep GUI responsive
        threading.Thread(target=self.process_input, args=(user_input,), daemon=True).start()
        
        # Prevent default behavior if called from an event
        return "break"
    
    def process_input(self, user_input):
        """Process the user input in a separate thread"""
        try:
            # Process the user input
            new_state, should_end = process_user_input(
                user_input, 
                self.state, 
                lambda msg: self.root.after(0, lambda: self.display_message(msg, "bot"))
            )
            
            # Update the state
            self.state = new_state
            
            # If we should end, enable "New Session" button
            if should_end:
                self.root.after(0, self.end_session)
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            # Reset processing flag
            self.processing = False
            self.root.after(0, lambda: self.status_var.set("Ready"))
            self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))
    
    def end_session(self):
        """End the current session and ask if user wants to start a new one"""
        response = messagebox.askyesno("Session Ended", 
                                     "The document has been saved. Would you like to start a new session?")
        if response:
            # Reset the state and start a new session
            self.app, self.state = run_document_agent()
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.display_message("🤖 DRAFTER: I'm ready to help you update a document. What would you like to create?", "bot")
        else:
            self.root.quit()

def main():
    root = tk.Tk()
    app = DrafterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
