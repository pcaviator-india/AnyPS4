import main_app
import tkinter as tk
root = tk.Tk()
app = main_app.App(root)
print('GUI instantiated successfully')
print('Notebook tabs:', app.notebook.index('end'))
for i in range(app.notebook.index('end')):
    tab_text = app.notebook.tab(i, 'text')
    print(f'  Tab {i}: {tab_text}')
root.destroy()