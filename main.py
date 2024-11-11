from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
import pandas as pd
import os


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        btn_load_file = Button(text="Загрузить файл", on_press=self.load_file, font_size=32)
        btn_manual_input = Button(text="Ручной ввод", on_press=self.manual_input, font_size=32)

        layout.add_widget(btn_load_file)
        layout.add_widget(btn_manual_input)
        self.add_widget(layout)

    def load_file(self, instance):
        self.manager.current = 'filechooser'

    def manual_input(self, instance):
        self.manager.current = 'manualinput'


class FileChooserScreen(Screen):
    def __init__(self, **kwargs):
        super(FileChooserScreen, self).__init__(**kwargs)

        # Основной вертикальный layout
        layout = BoxLayout(orientation='vertical', padding=40, spacing=100)

        # Заголовок
        title = Label(text="Выберите файл для загрузки (xlsx):", font_size=22, size_hint_y=None, height=50)
        layout.add_widget(title)

        # Виджет выбора файла с установкой начального пути
        self.filechooser = FileChooserIconView(path=os.getcwd(), size_hint_y=None, height=400)
        layout.add_widget(self.filechooser)

        # Горизонтальный layout для кнопок "Назад" и "Открыть"
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=20)

        btn_back = Button(text="Назад", size_hint=(None, None), size=(120, 50), font_size=22)
        btn_back.bind(on_press=self.go_back)
        button_layout.add_widget(btn_back)

        btn_open = Button(text="Открыть", size_hint=(None, None), size=(160, 50), font_size=22)
        btn_open.bind(on_press=self.open_file)
        button_layout.add_widget(btn_open)

        layout.add_widget(button_layout)

        self.add_widget(layout)

    def go_back(self, instance):
        # Переход на главный экран
        self.manager.current = 'main'

    def open_file(self, instance):
        selected = self.filechooser.selection
        if selected:
            file_path = selected[0]
            if file_path.endswith('.xlsx'):
                # Загрузка данных из файла и переход к экрану просмотра
                self.manager.get_screen('dataview').display_data(file_path)
                self.manager.current = 'dataview'


class ManualInputScreen(Screen):
    def __init__(self, **kwargs):
        super(ManualInputScreen, self).__init__(**kwargs)

        layout = GridLayout(cols=2, spacing=10, padding=40)

        # Поля для ввода данных с подсказками
        self.inputs = {}

        fields = [
            ("ID:", "Индивидуальный номер"),
            ("Кол-во метастазов:", "1 - солитарные, 2 - единичные, 3 - множественные"),
            ("ECOG:", "Значение от 0 до 3"),
            ("ПКР:", "Значение от 1 до 4"),
            ("Дифференциовка опухоли:", "Значение от 1 до 3"),
            ("Градация N:", "Значение от 0 до 2"),
            ("Синхронные и Метахронные метастазы:", "1 - синхронные, 2 - метахронные"),
            ("Локализация метастазов:", "1 - почка слева, 2 - почка справа, 3 - обе почки"),
            ("Наличие метастазэктомии:", "0 - нет, 1 - есть"),
            ("Число органов с метастазами:", "Значение от 0 до n"),
            ("Наличие нефрэктомии:", "0 - нет, 1 - есть"),
            ("Heng:", "1 - благоприятная, 2 - промежуточная, 3 - неблагоприятная")
        ]

        for label_text, hint_text in fields:
            # Метка для поля
            layout.add_widget(Label(text=label_text, font_size=22))

            # Поле ввода с подсказкой
            input_field = TextInput(
                hint_text=hint_text,
                hint_text_color=(0.5, 0.5, 0.5, 1),
                font_size=22,
                multiline=False
            )
            self.inputs[label_text] = input_field
            layout.add_widget(input_field)

        back_button = Button(text="Назад", size_hint=(None, None), size=(120, 50), font_size=22)
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        btn_save = Button(text="Сохранить", size_hint=(None, None), size=(160, 50), font_size=22)
        btn_save.bind(on_press=self.save_data)
        layout.add_widget(btn_save)

        self.add_widget(layout)

    def save_data(self, instance):
        # Сохранение данных из полей
        data = {field: self.inputs[field].text for field in self.inputs}
        df = pd.DataFrame([data])

        # Указание пути к файлу
        file_path = "Input.xlsx"

        # Заголовки для файла
        headers = [
            "ID", "Кол-во метастазов", "ECOG", "ПКР", "Дифференциовка опухоли",
            "Градация N", "Синхронные и Метахронные метастазы", "Локализация метастазов",
            "Наличие метастазэктомии", "Число органов с метастазами", "Наличие нефрэктомии", "Heng"
        ]

        # Проверка, существует ли файл
        if not os.path.exists(file_path):
            # Если файл не существует, создать его с заголовками
            df.to_excel(file_path, index=False, header=headers)
        else:
            # Если файл существует, добавить данные в конец
            with pd.ExcelWriter(file_path, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
                df.to_excel(writer, index=False, header=False, startrow=writer.sheets["Sheet1"].max_row)

        # Очистка всех полей ввода
        for input_field in self.inputs.values():
            input_field.text = ""

        # Переход к экрану просмотра
        self.manager.get_screen('dataview').display_data(file_path)
        self.manager.current = 'dataview'

    def go_back(self, instance):
        # Очистка всех полей ввода
        for input_field in self.inputs.values():
            input_field.text = ""

        # Возвращение на главный экран
        self.manager.current = 'main'


class DataViewScreen(Screen):
    def __init__(self, **kwargs):
        super(DataViewScreen, self).__init__(**kwargs)

        # Основной вертикальный layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Прокручиваемая область для таблицы данных (по горизонтали и вертикали)
        self.scroll_view = ScrollView(size_hint=(1, None), size=(800, 700), do_scroll_x=True, do_scroll_y=True)
        self.data_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, size_hint_x=None)
        self.scroll_view.add_widget(self.data_layout)

        # Кнопки "Получить результат" и "Отмены"
        buttons_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        btn_analyze = Button(text="Получить результат")
        buttons_layout.add_widget(btn_analyze)

        btn_cancel = Button(text="Отмена")
        btn_cancel.bind(on_press=self.go_back_to_main)
        buttons_layout.add_widget(btn_cancel)

        # Добавление виджетов на главный layout
        layout.add_widget(self.scroll_view)
        layout.add_widget(buttons_layout)
        self.add_widget(layout)

    def go_back_to_main(self, instance):
        # Очистка таблицы данных
        self.data_layout.clear_widgets()

        # Возвращение на главный экран
        self.manager.current = 'main'

    def display_data(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)

            # Установка количества столбцов и высоты
            self.data_layout.cols = len(df.columns)
            self.data_layout.height = 40 * (len(df) + 1)

            # Расчет ширины всего GridLayout для горизонтальной прокрутки
            column_widths = [max(len(str(column)), 10) * 10 for column in df.columns]
            self.data_layout.width = sum(column_widths) + 40

            # Добавление заголовков столбцов с шириной, рассчитанной по длине заголовка
            for i, column in enumerate(df.columns):
                label = Label(text=str(column), bold=True, size_hint_x=None, width=column_widths[i], height=40)
                self.data_layout.add_widget(label)

            # Добавление данных с выравниванием по рассчитанной ширине столбцов
            for _, row in df.iterrows():
                for i, cell in enumerate(row):
                    # Проверка, является ли значение числом
                    if isinstance(cell, float) and cell.is_integer():
                        cell = int(cell)  # Преобразование в целое число
                    label = Label(text=str(cell), size_hint_x=None, width=column_widths[i], height=40)
                    self.data_layout.add_widget(label)


class MyApp(App):
    def build(self):
        Window.size = (1400, 800)
        sm = ScreenManager()

        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(FileChooserScreen(name='filechooser'))
        sm.add_widget(ManualInputScreen(name='manualinput'))
        sm.add_widget(DataViewScreen(name='dataview'))

        return sm


if __name__ == '__main__':
    MyApp().run()
