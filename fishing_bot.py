import cv2
import numpy as np
import pyautogui
import time
import keyboard
import tkinter as tk
from PIL import ImageTk, Image

# Flaga kontrolująca działanie funkcji fish()
running = False
e_pressed = False
fish_caught = False
prev_fish_pull_image = False
last_x = 0

def fish():
    global running
    global e_pressed
    global fish_caught
    global prev_fish_pull_image
    global last_x
    
    if running:
        print(e_pressed)  
        if not e_pressed:
            time.sleep(2)
            pyautogui.press('e')
            print("Zarzucono wędkę")
            e_pressed = True
      
        template_path = "assets/fladra.png"
        confidence = 0.8
        fladra_pos = pyautogui.locateOnScreen(template_path, confidence=0.6, region=(0, 0, 500, 1980))

        if fladra_pos:
            # Pobierz współrzędne znalezionego obrazu
            fladra_x, fladra_y, _, _ = fladra_pos
            # Określ obszar poszukiwań dla screenshotu na podstawie współrzędnych znalezionego obrazu
            search_area = (fladra_x - 50, fladra_y - 50, 100, 100)
            screenshot = pyautogui.screenshot(region=search_area)
        else:
            # Jeśli obraz nie został znaleziony, wykonaj zwykły screenshot ekranu
            screenshot = pyautogui.screenshot()
        template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
        template_h, template_w = template.shape[:2]
        przycisk = 's'
        screenshot = pyautogui.screenshot()
        screenshot_arr = np.array(screenshot)[:, :, ::-1]
        mask = np.ones_like(template[:, :, 0])
        res = cv2.matchTemplate(screenshot_arr, template[:, :, :3], cv2.TM_CCOEFF_NORMED, mask=mask)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
        if max_val > confidence:
            center_x, center_y = max_loc[0] + template_w // 2, max_loc[1] + template_h // 2

            direction = center_x - last_x
            pyautogui.moveTo(center_x, center_y)
            if direction < 0:
                if przycisk != 'd':
                    keyboard.release('a')
                    keyboard.press('d')
                przycisk = 'd'
            if direction > 0:
                if przycisk != 'a':
                    keyboard.release('d')
                    keyboard.press('a')
                przycisk = 'a'
            last_x = center_x
        else:
            keyboard.release('a')
            keyboard.release('d')

        fish_pull_image = pyautogui.locateCenterOnScreen('assets/fish_caught.png', confidence=0.6)  # LPM
        if fish_pull_image:
            print("Złapano rybę")
            pyautogui.mouseDown()
            prev_fish_pull_image = True

        if prev_fish_pull_image:
            if not fish_pull_image:
                pyautogui.mouseUp()
                prev_fish_pull_image = False
                e_pressed = False
                print("Ryba wyłowiona") 
                fish()  
        else:
            print("Jeszcze nie ma")  

        fish_broken = pyautogui.locateCenterOnScreen('assets/zerwana.png', confidence=0.6)
        if fish_broken:
            keyboard.release('a')
            keyboard.release('d')
            prev_fish_pull_image = False
            e_pressed = False     
            fish()

    # Cykliczne wywoływanie funkcji fish() co 100 ms
    if running:
        root.after(100, fish)

def start_fishing():
    disable_button(start_button)
    enable_button(pause_button)
    global running
    if not running:
        running = True
        fish()

def stop_fishing():
    disable_button(pause_button)
    enable_button(start_button)
    global running
    global e_pressed
    running = False
    print("Zatrzymano łowienie")
    keyboard.release('a')
    keyboard.release('d')
    e_pressed = False

def stop_program():
    disable_button(stop_button)
    global running
    running = False
    quit()
    
def disable_button(button):
    button.config(state=tk.DISABLED)

def enable_button(button):
    button.config(state=tk.NORMAL)
# Tworzenie okna
root = tk.Tk()
root.title("Bot na rybki")
root.geometry("600x350")

# Ładowanie obrazka
image_path = "assets/range.png"
image = Image.open(image_path)
image = image.resize((430, 250))  # Zmiana rozmiaru obrazka
image = ImageTk.PhotoImage(image)

# Ramka dla obrazka
image_frame = tk.Frame(root)
image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # Ustawienie ramki po prawej stronie

# Dodawanie obrazka do etykiety
label = tk.Label(image_frame, image=image)
label.pack(anchor="ne")  # Ustawienie etykiety wewnątrz ramki

# Dodawanie napisu pod obrazkiem
text_below_image = "Obszar na którym program widzi rybę."
text_below_image2 = "Może nie działać, gdy patrzysz na niebo."
text_below_image3 = "Hotkey łowienia: '='"
text_below_image4 = "Hotkey zatrzymania łowienia: '-'"
label_text = tk.Label(image_frame, text=text_below_image)
label_text2 = tk.Label(image_frame, text=text_below_image2)
label_text3 = tk.Label(image_frame, text=text_below_image3)
label_text4 = tk.Label(image_frame, text=text_below_image4)
label_text.pack()
label_text2.pack()
label_text3.pack()
label_text4.pack()

# Ramka dla przycisków
button_frame = tk.Frame(root)
button_frame.pack(padx = 10,pady=40,side=tk.LEFT, fill=tk.Y)  # Ustawienie ramki po lewej stronie
filler_label = tk.Label(button_frame, text="")
filler_label.pack(pady=200)
# Przycisk do rozpoczęcia łowienia
start_button = tk.Button(root, text="Rozpocznij łowienie", command=start_fishing)
start_button.pack(pady=10)

# Przycisk do zatrzymania łowienia
pause_button = tk.Button(root, text="Zatrzymaj łowienie", command=stop_fishing)
pause_button.pack(pady=10)

# Przycisk do zakończenia programu
stop_button = tk.Button(root, text="Zakończ program", command=stop_program)
stop_button.pack(pady=10)



#Hotkeys
keyboard.add_hotkey('=', start_fishing)
keyboard.add_hotkey('-', stop_fishing)

root.mainloop()