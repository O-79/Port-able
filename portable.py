import psutil
import socket
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

class PortViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Active Ports Viewer")
        self.root.geometry("1000x600")

        self.search_var = tb.StringVar()
        self.refresh_interval = 5000  # ms

        self.current_theme = "darkly"

        # === Search bar ===
        frm = tb.Frame(root)
        frm.pack(fill=X, padx=10, pady=5)

        tb.Label(frm, text="Filter:").pack(side=LEFT)
        tb.Entry(frm, textvariable=self.search_var).pack(side=LEFT, fill=X, expand=True, padx=5)
        tb.Button(frm, text="Refresh Now", command=self.refresh_connections).pack(side=LEFT, padx=5)
        tb.Button(frm, text="Toggle Theme", command=self.toggle_theme).pack(side=LEFT, padx=5)

        # === Table ===
        self.table = tb.Treeview(root, bootstyle="dark", columns=("Proto", "Local", "Remote", "Status", "PID", "Process Name"), show='headings')
        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, stretch=True)
        self.table.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # === Buttons ===
        btn_frm = tb.Frame(root)
        btn_frm.pack(fill=X, padx=10, pady=5)

        tb.Button(btn_frm, text="Kill Selected", bootstyle="danger", command=self.kill_selected).pack(side=LEFT)

        self.refresh_connections()
        self.auto_refresh()

    def toggle_theme(self):
        if self.current_theme == "darkly":
            self.root.style.theme_use("flatly")  # Light theme
            self.current_theme = "flatly"
        else:
            self.root.style.theme_use("darkly")  # Dark theme
            self.current_theme = "darkly"

    def get_connections(self):
        conns = psutil.net_connections(kind='inet')
        rows = []
        for c in conns:
            pid = c.pid or ''
            try:
                pname = psutil.Process(c.pid).name() if c.pid else ''
            except Exception:
                pname = ''
            laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else ''
            raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else ''
            proto = 'TCP' if c.type == socket.SOCK_STREAM else 'UDP'
            rows.append((proto, laddr, raddr, c.status, str(pid), pname))
        return rows

    def refresh_connections(self):
        search = self.search_var.get().lower()
        rows = self.get_connections()

        self.table.delete(*self.table.get_children())

        for row in rows:
            if search:
                if any(search in str(cell).lower() for cell in row):
                    self.table.insert('', 'end', values=row)
            else:
                self.table.insert('', 'end', values=row)

    def auto_refresh(self):
        self.refresh_connections()
        self.root.after(self.refresh_interval, self.auto_refresh)

    def kill_selected(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("No selection", "Please select a row.")
            return
        pid = self.table.item(selected[0])['values'][4]
        pname = self.table.item(selected[0])['values'][5]
        confirm = messagebox.askyesno("Confirm Terminate", f"Terminate process {pid} ({pname})?")
        if confirm:
            try:
                p = psutil.Process(int(pid))
                p.terminate()
                messagebox.showinfo("Success", f"Terminated process {pid} ({pname})")
                self.refresh_connections()
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = tb.Window(themename="darkly")
    PortViewerApp(app)
    app.mainloop()
