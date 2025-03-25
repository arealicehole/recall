from src.gui.app import TranscriberApp
import customtkinter as ctk

def main():
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    # Create and run the application
    app = TranscriberApp()
    app.mainloop()

if __name__ == "__main__":
    main() 