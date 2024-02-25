import tkinter as tk
from configparser import ConfigParser
from tkinter import messagebox, filedialog

from auto_seedr import AutoSeedrClient, setup_config


class AutoSeedrGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoSeedr GUI")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Email:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.email_entry = tk.Entry(self.root)
        self.email_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Password:").grid(row=0, column=4, padx=10, pady=5, sticky="w")
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=0, column=5, padx=10, pady=5)

        tk.Label(self.root, text="Torrent Directory:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.torrent_directory_entry = tk.Entry(self.root)
        self.torrent_directory_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Download Directory:").grid(row=2, column=4, padx=10, pady=5, sticky="w")
        self.download_directory_entry = tk.Entry(self.root)
        self.download_directory_entry.grid(row=2, column=5, padx=10, pady=5)

        tk.Button(self.root, text="Directory Download", command=self.directory_download, width=20, height=1).grid(row=4, column=0,
                                                                                              columnspan=2, pady=10)
        tk.Button(self.root, text="Load from INI", command=self.load_from_ini).grid(row=4, column=1, columnspan=4,
                                                                                    pady=10)
        tk.Button(self.root, text="Create INI", command=self.create_ini, width=10, height=1).grid(row=5, column=1, columnspan=4, pady=10)
        tk.Button(self.root, text="Quit", command=self.root.quit).grid(row=5, column=0, columnspan=2)

    def directory_download(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        torrent_directory = self.torrent_directory_entry.get()
        download_directory = self.download_directory_entry.get()

        seedr_client = AutoSeedrClient(email=email, password=password, torrent_directory=torrent_directory,
                                       download_directory=download_directory)

        try:
            seedr_client.directory_download()
            messagebox.showinfo("Success", "Directory download completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def load_from_ini(self):
        ini_file = filedialog.askopenfilename(title="Select INI file", filetypes=[("INI files", "*.ini")])

        if ini_file:
            config = ConfigParser()
            config.read(ini_file)

            try:
                email = config.get('SEEDR', 'user')
                password = config.get('SEEDR', 'password')
                torrent_directory = config.get('APP', 'torrent_folder')
                download_directory = config.get('APP', 'download_folder')

                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, email)

                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, password)

                self.torrent_directory_entry.delete(0, tk.END)
                self.torrent_directory_entry.insert(0, torrent_directory)

                self.download_directory_entry.delete(0, tk.END)
                self.download_directory_entry.insert(0, download_directory)

                messagebox.showinfo("Success", f"Configuration loaded from {ini_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Error reading configuration from {ini_file}: {e}")

    def create_ini(self):
        ini_file = filedialog.asksaveasfilename(title="Save INI file", defaultextension=".ini",
                                                filetypes=[("INI files", "*.ini")])

        if ini_file:
            setup_config(
                email=self.email_entry.get(),
                password=self.password_entry.get(),
                config_file=ini_file,
                torrent_directory=self.torrent_directory_entry.get(),
                download_directory=self.download_directory_entry.get()
            )

            messagebox.showinfo("Success", f"INI file created successfully at {ini_file}")


def main():
    root = tk.Tk()
    root.geometry("600x200")
    root.iconphoto(False, tk.PhotoImage(file="images/icon.png"))
    AutoSeedrGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
