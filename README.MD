# Игрушка-залипалка.

`pythonru_com_shmup.py` - леталка, списанная отсюда: 
[pythonru.com](https://pythonru.com/tag/pishem-igru-na-pygame)
`stupid_plane.py` - моя версия. Поддерживает мышь.

---

### Settings

`pythonru_com_shmup.py` не требует изменения настроек.

`stupid_plane.py` available settings:
```python
# НЕ ТРОГАТЬ! Это определение размера монитора
monitor_width, monitor_height = pyautogui.size()
# Размер окна программы, можно менять
SIZE = WIDTH, HEIGHT = 800, 1000
# Центр окна
CENTER = CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
# Изначальная скорость игры
FPS = 60
# Если True: играет омерзительная музыка.
MUSIC = True
# Если True: звучат пиу-пиу и взрывы
SOUND = True
# Изначальное количество жизней
LIVES = 3
# Время работы супер-пушки
EXTRA_GUN_TIME = 5000
# Размер текста. High-score, жизни и прочее.
TEXT_SIZE = HEIGHT // 20
```