import json
import tkinter as tk
from threading import Thread
from datetime import datetime
from nova_space_armada import config
from nova_space_armada.utilities import rabbitmq


class TkinterWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root_log = tk.Text(self.root, font=('Helvetica', 10))
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

    def logger(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        # Setting the geometry of window
        width, height = 650, 100
        position_x = self.screen_w - (self.screen_h * 1.4)
        position_y = self.screen_h - (self.screen_h * 0.132)
        self.root.geometry('%dx%d+%d+%d' % (width, height, position_x, position_y))

        # Create a Label
        self.root_log = tk.Text(self.root, font=('Helvetica', 10), bg='black', fg='orange', highlightthickness=0, borderwidth=0)
        self.root_log.tag_configure("last_insert")
        self.root_log.pack(fill=tk.BOTH)

        # Make the window jump above all
        self.root.attributes('-topmost', True)

        # window opacity level
        self.root.attributes('-alpha', 0.9)

        app_cmd_listener = Thread(target=self.rabbit_listener, daemon=True)
        app_cmd_listener.start()

        self.root.mainloop()

    def rabbit_listener(self):
        rabbitmq.host(config.rabbit_q, self.log)

    def log(self, h=None, method=None, properties=None, body=None):

        commands = json.loads(body.decode())
        print(commands)

        for command in commands:
            inplace = command.get('inplace', False)
            text = command.get('text', 'no text provided')
            if text == 'clean log':
                self.root_log.delete(1.0, tk.END)
                break

            text_with_ts = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: " + text
            if inplace is True:
                self.root_log.configure(state="normal")
                last_insert = self.root_log.tag_ranges("last_insert")
                if last_insert:
                    self.root_log.delete(last_insert[0], last_insert[1])
                    self.root_log.configure(state="normal")
                    self.root_log.tag_remove("last_insert", "1.0", "end")
                    self.root_log.insert("end", text_with_ts, "last_insert")
                    self.root_log.configure(state="disabled")
                else:
                    self.root_log.insert("end", text_with_ts, "last_insert")
            else:
                self.root_log.configure(state="normal")
                last_insert = self.root_log.tag_ranges("last_insert")
                if last_insert:
                    text_with_ts = "\n" + text_with_ts
                    self.root_log.tag_remove("last_insert", "1.0", "end")
                self.root_log.insert('end', text_with_ts + '\n')
            self.root_log.see('end')


if __name__ == '__main__':
    gui = TkinterWindow()
    gui.logger()