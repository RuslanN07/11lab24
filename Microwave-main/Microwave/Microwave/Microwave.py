import tkinter as tk
from tkinter import messagebox
import winsound
from enum import Enum
from PIL import Image, ImageTk, ImageDraw
import os

class MicrowaveState(Enum):
    WAITING = "waiting"
    RUNNING = "running"
    FINISHED = "finished"
    PAUSED = "paused"

class Microwave:
    def __init__(self):
        self.state = MicrowaveState.WAITING
        self.time_left = 0
        self.is_door_open = False
        self.selected_food = None
        self.max_time = 60 * 60

    def set_time(self, seconds):
        if self.state == MicrowaveState.RUNNING:
            return False
        if not isinstance(seconds, int) or seconds < 0 or seconds > self.max_time:
            return False
        self.time_left = seconds
        return True

    def add_time(self, seconds):
        return self.set_time(self.time_left + seconds)

    def subtract_time(self, seconds):
        return self.set_time(self.time_left - seconds)

    def start(self):
        if self.is_door_open or self.time_left <= 0 or self.selected_food is None:
            return False
        if self.state in [MicrowaveState.WAITING, MicrowaveState.PAUSED]:
            self.state = MicrowaveState.RUNNING
            return True
        return False

    def stop(self):
        self.state = MicrowaveState.WAITING
        self.time_left = 0
        self.selected_food = None
        return True

    def open_door(self):
        self.is_door_open = True
        if self.state == MicrowaveState.RUNNING:
            self.state = MicrowaveState.PAUSED
        return True

    def close_door(self):
        self.is_door_open = False
        return True

    def tick(self):
        if self.state != MicrowaveState.RUNNING:
            return False
        if self.time_left > 0:
            self.time_left -= 1
            if self.time_left == 0:
                self.state = MicrowaveState.FINISHED
                return "finished"
            return "tick"
        return False

    def get_time_display(self):
        return f"{self.time_left // 60:02d}:{self.time_left % 60:02d}"

    def can_start(self):
        return not self.is_door_open and self.time_left > 0 and self.state in [MicrowaveState.WAITING, MicrowaveState.PAUSED]


class MicrowaveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Микроволновая печь")
        self.root.geometry("750x650")
        self.root.resizable(False, False)

        self.microwave = Microwave()
        self.timer_id = None
        self.rotation_angle = 0
        self.food_on_plate = None
        self.food_images = {}

        self.load_food_images()

        self.canvas = tk.Canvas(self.root, width=750, height=600, bg="#1E1E1E", highlightthickness=0)
        self.canvas.pack()

        self.display_text_id = None
        self.door_button = None

        self.draw_microwave()
        self.create_buttons()
        self.create_food_selection()
        self.update_display()

    def load_food_images(self):
        """Загружает изображения продуктов"""
        food_dir = "foods"
        for food_name in ["Курица", "Пицца", "Суп"]:
            file_name = food_name.lower() + ".png"
            path = os.path.join(food_dir, file_name)
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    self.food_images[food_name] = img
                except Exception as e:
                    print(f"Ошибка загрузки {file_name}: {e}")

    def create_food_selection(self):
        frame = tk.Frame(self.root, bg="#1E1E1E", height=50)
        frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        tk.Label(frame, text="Выберите продукт:", bg="#1E1E1E", fg="#E0E0E0", font=("Consolas", 10)).pack(side=tk.LEFT, padx=10)

        foods = ["Курица", "Пицца", "Суп"]
        for food in foods:
            btn = tk.Button(
                frame,
                text=food,
                width=8,
                font=("Consolas", 9),
                bg="#333333",
                fg="#E0E0E0",
                activebackground="#444444",
                activeforeground="#4CFF96",
                command=lambda f=food: self.select_food(f)
            )
            btn.pack(side=tk.LEFT, padx=5)

        self.food_label = tk.Label(frame, text="Не выбрано", bg="#1E1E1E", fg="#FF6B6B", font=("Consolas", 10))
        self.food_label.pack(side=tk.RIGHT, padx=20)

    def select_food(self, food_name):
        self.microwave.selected_food = food_name
        self.food_label.config(text=f"Выбрано: {food_name}", fg="#4CFF96")
        self.update_display()

    def draw_microwave(self):
        self.canvas.delete("microwave")

        self.canvas.create_rectangle(100, 50, 680, 310, fill="#d9d9d9", outline="#a0a0a0", width=3, tags="microwave")

        if not self.microwave.is_door_open:
            self.canvas.create_rectangle(120, 70, 440, 290, fill="#4a4a4a", outline="#2e2e2e", width=2, tags="microwave")
            self.canvas.create_rectangle(140, 90, 420, 270, fill="#3a3a3a", outline="#1e1e1e", width=2, tags="microwave")
            self.canvas.create_rectangle(430, 130, 440, 240, fill="#cfcfcf", outline="#888888", width=2, tags="microwave")
            self.canvas.create_oval(200, 220, 380, 270, fill="#f7f7f7", outline="#bfbfbf", tags="microwave")
        else:
            self.canvas.create_rectangle(140, 70, 440, 270, fill="#3a3a3a", outline="#1e1e1e", width=2, tags="microwave")
            self.canvas.create_oval(200, 205, 380, 260, fill="#f7f7f7", outline="#bfbfbf", tags="microwave")
            self.canvas.create_rectangle(140, 270, 440, 285, fill="#2b2b2b", outline="#2b2b2b", tags="microwave")
            self.canvas.create_polygon(140, 70, 50, 100, 50, 300, 140, 270,
                                      fill="#4a4a4a", outline="#2e2e2e", width=2, tags="microwave")
            self.canvas.create_polygon(130, 90, 65, 115, 65, 285, 130, 260,
                                      fill="#3a3a3a", outline="#1e1e1e", width=2, tags="microwave")
            self.canvas.create_polygon(50, 100, 65, 115, 65, 285, 50, 300,
                                      fill="#2a2a2a", outline="#1c1c1c", tags="microwave")
            self.canvas.create_polygon(50, 100, 140, 70, 130, 90, 65, 115,
                                      fill="#555555", outline="#333333", tags="microwave")
            self.canvas.create_rectangle(55, 160, 68, 240, fill="#d0d0d0", outline="#888888", width=2, tags="microwave")

        # display
        self.canvas.create_rectangle(480, 60, 655, 110, fill="#121212", outline="#2a2a2a", width=2, tags="microwave")
        self.update_display_text()
        self.draw_food_inside()

    def draw_food_inside(self):
        """Отображает ЕДИНОЕ изображение с тарелкой и едой, заполняющее ВЕСЬ внутренний прямоугольник"""
        if self.food_on_plate:
            self.canvas.delete(self.food_on_plate)
            self.food_on_plate = None

        if self.microwave.is_door_open or not self.microwave.selected_food:
            return

        cam_left, cam_top = 140, 90
        cam_right, cam_bottom = 420, 270
        cam_width = cam_right - cam_left
        cam_height = cam_bottom - cam_top
        center_x = cam_width // 2
        center_y = cam_height // 2

        cam_img = Image.new("RGBA", (cam_width, cam_height), (58, 58, 58, 255))

        max_diameter = int(0.8 * min(cam_width, cam_height))
        plate_diameter = max_diameter

        plate_img = Image.new("RGBA", (plate_diameter, plate_diameter), (0, 0, 0, 0))
        draw = ImageDraw.Draw(plate_img)
        draw.ellipse((0, 0, plate_diameter, plate_diameter), fill=(220, 220, 220), outline=(100, 100, 100), width=2)
        draw.ellipse((8, 8, plate_diameter - 8, plate_diameter - 8), fill=(200, 200, 200))

        rotated_plate = plate_img.rotate(self.rotation_angle, expand=False)
        plate_pos = (center_x - plate_diameter // 2, center_y - plate_diameter // 2)
        cam_img.paste(rotated_plate, plate_pos, rotated_plate)

        food_name = self.microwave.selected_food
        if food_name in self.food_images:
            food_img = self.food_images[food_name]
            food_size = int(plate_diameter * 0.75)
            food_img = food_img.resize((food_size, food_size), Image.LANCZOS)
            rotated_food = food_img.rotate(self.rotation_angle, expand=False)
            food_pos = (center_x - food_size // 2, center_y - food_size // 2)
            cam_img.paste(rotated_food, food_pos, rotated_food)

        cam_photo = ImageTk.PhotoImage(cam_img)
        self.food_on_plate = self.canvas.create_image(cam_left, cam_top, image=cam_photo, anchor="nw", tags="food")
        self.canvas.cam_cache = cam_photo

    def update_display_text(self):
        if self.display_text_id:
            self.canvas.delete(self.display_text_id)

        if self.microwave.is_door_open:
            text = "DOOR OPEN"
            color = "#FFD666"  
        else:
            time_str = self.microwave.get_time_display()
            if self.microwave.selected_food:
                text = f"{time_str}\n{self.microwave.selected_food}"
            else:
                text = f"{time_str}\n(Выберите продукт)"
            color = "#4CFF96" 

        self.display_text_id = self.canvas.create_text(
            568, 85, text=text, fill=color,
            font=("Consolas", 16, "bold"), justify="center", tags="microwave"
        )

    def create_buttons(self):
        btn_start = tk.Button(self.root, text="START", width=8, height=2, bg="white", font=("Arial", 9),
                              command=self.start)
        btn_stop = tk.Button(self.root, text="STOP\nCANCEL", width=8, height=2, bg="white", font=("Arial", 9),
                             command=self.stop)
        btn_minus10 = tk.Button(self.root, text="-10 sec", width=8, height=2, bg="white", font=("Arial", 9),
                                command=lambda: self.subtract_time(10))
        btn_30 = tk.Button(self.root, text="+30 sec", width=8, height=2, bg="white", font=("Arial", 9),
                           command=lambda: self.add_time(30))
        btn_60 = tk.Button(self.root, text="+60 sec", width=8, height=2, bg="white", font=("Arial", 9),
                           command=lambda: self.add_time(60))
        self.door_button = tk.Button(self.root, text="OPEN\nDOOR", width=8, height=2, bg="white", font=("Arial", 9),
                                     command=self.toggle_door)

        # Три ряда по две кнопки
        btn_start.place(x=480, y=120)
        btn_stop.place(x=570, y=120)

        btn_minus10.place(x=480, y=180)
        btn_30.place(x=570, y=180)

        btn_60.place(x=480, y=240)
        self.door_button.place(x=570, y=240)

    def update_display(self):
        self.update_display_text()
        self.door_button.config(text="CLOSE\nDOOR" if self.microwave.is_door_open else "OPEN\nDOOR")
        self.draw_microwave()

    def add_time(self, seconds):
        if not self.microwave.is_door_open and not self.microwave.state == MicrowaveState.RUNNING:
            self.microwave.add_time(seconds)
            self.update_display()

    def subtract_time(self, seconds):
        if not self.microwave.is_door_open and not self.microwave.state == MicrowaveState.RUNNING:
            self.microwave.subtract_time(seconds)
            self.update_display()

    def start(self):
        if self.microwave.start():
            self.update_display()
            self.start_rotation_animation()
            self.run_timer()

    def stop(self):
        self.microwave.stop()
        self.cancel_timer()
        self.rotation_angle = 0
        self.update_display()

    def toggle_door(self):
        was_open = self.microwave.is_door_open
        if was_open:
            self.microwave.close_door()
        else:
            self.microwave.open_door()
        self.draw_microwave()
        self.update_display()

    def start_rotation_animation(self):
        if self.microwave.state == MicrowaveState.RUNNING and not self.microwave.is_door_open:
            self.animate_rotation()

    def animate_rotation(self):
        if self.microwave.state != MicrowaveState.RUNNING or self.microwave.is_door_open:
            return
        self.rotation_angle = (self.rotation_angle + 5) % 360
        self.draw_food_inside()
        self.root.after(100, self.animate_rotation)

    def run_timer(self):
        self.cancel_timer()
        self._tick()

    def cancel_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def _tick(self):
        if self.microwave.state == MicrowaveState.RUNNING:
            result = self.microwave.tick()
            self.update_display()
            if result == "finished":
                self.on_finish()
            else:
                self.timer_id = self.root.after(1000, self._tick)

    def on_finish(self):
        try:
            winsound.Beep(1000, 1000)
        except:
            pass
        food = self.microwave.selected_food or "Еда"
        messagebox.showinfo("Готово!", f"{food} разогрета!")
        self.rotation_angle = 0
        self.update_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = MicrowaveApp(root)
    root.mainloop()