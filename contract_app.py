import datetime
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from docxtpl import DocxTemplate
from num2words import num2words
from PIL import Image, ImageTk

# Определяем правильный путь для автономного .exe (включая распаковку во временную папку)
if getattr(sys, "frozen", False):
  BASE_DIR = sys._MEIPASS
  CONFIG_DIR = os.path.dirname(sys.executable)
else:
  BASE_DIR = r"F:\Files\Работа\Factory Motors\Генератор договоров"
  CONFIG_DIR = BASE_DIR

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
# Путь к папке с графикой
IMAGES_DIR = os.path.join(BASE_DIR, "images")


def load_default_dir():
  default_path = os.path.join(BASE_DIR, "generated_contracts")
  if os.path.exists(CONFIG_FILE):
    try:
      with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        saved_dir = data.get("default_dir")
        if saved_dir and os.path.exists(saved_dir):
          return saved_dir
    except Exception:
      pass
  return default_path


def save_default_dir(path):
  try:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
      json.dump({"default_dir": path}, f, ensure_ascii=False, indent=4)
  except Exception:
    pass


def number_to_words_ru(amount_str):
  try:
    clean_str = (
        amount_str.replace(" ", "").replace(".", "").replace(",", "")
    )
    if not clean_str.isdigit():
      return amount_str
    amount = int(clean_str)
    words = num2words(amount, lang="ru")
    words = words.split(" целых")[0]
    return words.capitalize()
  except Exception:
    return str(amount_str)


def format_date_with_month_name(date_str):
  months = {
      "01": "января",
      "02": "февраля",
      "03": "марта",
      "04": "апреля",
      "05": "мая",
      "06": "июня",
      "07": "июля",
      "08": "августа",
      "09": "сентября",
      "10": "октября",
      "11": "ноября",
      "12": "декабря",
  }
  try:
    parts = date_str.strip().split(".")
    if len(parts) == 3:
      day, month, year = parts
      if month in months:
        return f"{int(day)} {months[month]} {year} г."
  except Exception:
    pass
  return date_str


class ModernContractApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Factory Motors: Contract Hub")
    self.root.geometry("850x1020")
    self.root.minsize(750, 700)

    # Установка иконки приложения и панели задач из папки images
    try:
      self.root.iconbitmap(os.path.join(IMAGES_DIR, "logo.ico"))
    except Exception:
      pass

    self.current_theme = "dark"
    self.default_output_dir = tk.StringVar(value=load_default_dir())
    self.custom_output_dir = tk.StringVar(value="")

    container = ttk.Frame(root)
    container.pack(fill="both", expand=True)

    self.canvas = tk.Canvas(container, highlightthickness=0)
    self.scrollbar = ttk.Scrollbar(
        container, orient="vertical", command=self.canvas.yview
    )
    self.scrollable_frame = ttk.Frame(self.canvas, padding=20)

    self.scrollable_frame.bind(
        "<Configure>",
        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
    )

    self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
    self.canvas.configure(yscrollcommand=self.scrollbar.set)

    self.canvas.pack(side="left", fill="both", expand=True)
    self.scrollbar.pack(side="right", fill="y")

    self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    self.entries = []
    self.labels = []
    self.headers = []
    self.dir_labels = []

    self.create_form_elements()
    self.apply_theme("dark")

  def _on_mousewheel(self, event):
    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

  def toggle_theme(self):
    if self.current_theme == "dark":
      self.apply_theme("light")
    else:
      self.apply_theme("dark")

  def update_logo(self, theme_name):
    if theme_name == "dark":
      logo_filename = "logo_dark.png"
    else:
      logo_filename = "logo_light.png"

    path = os.path.join(IMAGES_DIR, logo_filename)
    if not os.path.exists(path):
      path = os.path.join(IMAGES_DIR, "logo.png")

    if os.path.exists(path):
      try:
        img = Image.open(path)
        img = img.resize((110, 110), Image.Resampling.LANCZOS)
        self.logo_img = ImageTk.PhotoImage(img)
        self.logo_lbl.config(image=self.logo_img)
      except Exception:
        pass

  def apply_theme(self, theme_name):
    self.current_theme = theme_name

    if theme_name == "dark":
      bg_color = "#121212"
      fg_color = "#ffffff"
      entry_bg = "#252525"
      entry_fg = "#ffffff"
      header_color = "#f1c40f"
      dir_text_color = "#dddddd"
      btn_text = "☀️ Светлая тема"
    else:
      bg_color = "#f5f6fa"
      fg_color = "#2f3640"
      entry_bg = "#ffffff"
      entry_fg = "#2f3640"
      header_color = "#e74c3c"
      dir_text_color = "#555555"
      btn_text = "🌙 Темная тема"

    self.root.configure(bg=bg_color)
    self.canvas.configure(bg=bg_color)

    if hasattr(self, "theme_btn"):
      self.theme_btn.config(text=btn_text)

    self.update_logo(theme_name)

    for lbl in self.labels:
      lbl.config(background=bg_color, foreground=fg_color)

    for lbl in self.headers:
      lbl.config(background=bg_color, foreground=header_color)

    for ent in self.entries:
      ent.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)

    if hasattr(self, "lbl_brand"):
      self.lbl_brand.config(bg=bg_color, fg=header_color)
    if hasattr(self, "lbl_sub"):
      self.lbl_sub.config(
          bg=bg_color, fg="#888888" if theme_name == "dark" else "#555555"
      )

    for lbl in self.dir_labels:
      lbl.config(bg=bg_color, fg=dir_text_color)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background=bg_color)
    style.configure("TLabel", background=bg_color, foreground=fg_color)
    style.configure(
        "TRadiobutton",
        background=bg_color,
        foreground=fg_color,
        font=("Segoe UI", 10),
    )
    style.map(
        "TRadiobutton",
        background=[("active", bg_color)],
        foreground=[("active", header_color)],
    )

  def create_form_elements(self):
    form = self.scrollable_frame
    row = 0

    self.header_frame = ttk.Frame(form)
    self.header_frame.grid(
        row=row, column=0, columnspan=2, sticky="ew", pady=(0, 15)
    )
    row += 1

    self.logo_lbl = ttk.Label(self.header_frame)
    self.logo_lbl.pack(side="left", padx=(0, 15))

    self.title_frame = ttk.Frame(self.header_frame)
    self.title_frame.pack(side="left", fill="y", expand=True)

    self.lbl_brand = tk.Label(
        self.title_frame,
        text="FACTORY MOTORS",
        font=("Segoe UI", 18, "bold"),
    )
    self.lbl_brand.pack(anchor="w")

    self.lbl_sub = tk.Label(
        self.title_frame,
        text="Система автоматического формирования договоров",
        font=("Segoe UI", 10),
    )
    self.lbl_sub.pack(anchor="w", pady=(2, 0))

    self.theme_btn = tk.Button(
        self.header_frame,
        text="☀️ Светлая тема",
        font=("Segoe UI", 9, "bold"),
        command=self.toggle_theme,
        relief="flat",
        padx=10,
        pady=5,
        cursor="hand2",
        bg="#333333",
        fg="#ffffff",
    )
    self.theme_btn.pack(side="right", anchor="ne")

    sep_top = ttk.Separator(form, orient="horizontal")
    sep_top.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(5, 10))
    row += 1

    def add_section_header(title):
      nonlocal row
      lbl = tk.Label(
          form, text=title, font=("Segoe UI", 11, "bold"), anchor="w"
      )
      lbl.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(15, 5))
      self.headers.append(lbl)
      row += 1
      sep = ttk.Separator(form, orient="horizontal")
      sep.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 10))
      row += 1

    def add_field(label_text, default=""):
      nonlocal row
      lbl = ttk.Label(form, text=label_text)
      lbl.grid(row=row, column=0, sticky="w", padx=5, pady=4)
      self.labels.append(lbl)

      ent = tk.Entry(form, width=45, font=("Segoe UI", 10), relief="flat")
      ent.grid(row=row, column=1, sticky="w", padx=5, pady=4, ipady=4)
      if default:
        ent.insert(0, default)
      self.entries.append(ent)
      row += 1
      return ent

    add_section_header("1. Основные данные договора")
    self.e_contract_num = add_field("Номер договора:")
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    self.e_contract_date = add_field("Дата договора (ДД.ММ.ГГГГ):", today_str)

    add_section_header("2. Папка для сохранения документов")

    dir_default_frame = ttk.Frame(form)
    dir_default_frame.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=5, pady=2
    )
    row += 1

    curr_default = self.default_output_dir.get()
    short_default = (
        curr_default if len(curr_default) < 45 else "..." + curr_default[-42:]
    )
    self.lbl_default_dir = tk.Label(
        dir_default_frame,
        text=f"По умолчанию: {short_default}",
        font=("Segoe UI", 9),
    )
    self.lbl_default_dir.pack(side="left", padx=(0, 10))
    self.dir_labels.append(self.lbl_default_dir)

    btn_set_default = ttk.Button(
        dir_default_frame,
        text="⚙️ Изменить папку по умолчанию",
        command=self.change_default_directory,
    )
    btn_set_default.pack(side="left")

    dir_custom_frame = ttk.Frame(form)
    dir_custom_frame.grid(
        row=row, column=0, columnspan=2, sticky="w", padx=5, pady=4
    )
    row += 1

    self.lbl_custom_dir = tk.Label(
        dir_custom_frame,
        text="Папка для этого договора: (не выбрана, по умолчанию)",
        font=("Segoe UI", 9, "italic"),
    )
    self.lbl_custom_dir.pack(side="left", padx=(0, 10))
    self.dir_labels.append(self.lbl_custom_dir)

    btn_choose_dir = ttk.Button(
        dir_custom_frame,
        text="📁 Выбрать другую...",
        command=self.choose_custom_directory,
    )
    btn_choose_dir.pack(side="left")

    add_section_header("3. Двигатель и автомобиль")
    self.e_engine_model = add_field("Модель двигателя:")
    self.e_engine_num = add_field("Номер двигателя:")
    self.e_car_brand = add_field("Марка машины:")
    self.e_car_model = add_field("Модель автомобиля:")
    self.e_car_gosnum = add_field("Госномер:")

    add_section_header("4. Стоимость товара")
    self.e_price = add_field("Стоимость (цифрами, например 120000):")

    add_section_header("5. Условия гарантии и установки")
    self.service_var = tk.StringVar(value="our")

    r1 = ttk.Radiobutton(
        form,
        text="Установка в нашем сервисе (Гарантия 6 месяцев или 30 000 км)",
        variable=self.service_var,
        value="our",
    )
    r1.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=2)
    row += 1

    r2 = ttk.Radiobutton(
        form,
        text=(
            "Установка в стороннем сервисе (Гарантия 3 месяца или 20 000 км)"
        ),
        variable=self.service_var,
        value="other",
    )
    r2.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=2)
    row += 1

    add_section_header("6. Данные покупателя (Паспортные данные и адрес)")
    self.e_fio = add_field("Фамилия Имя Отчество:")
    self.e_passport_series = add_field("Серия паспорта (4 цифры):")
    self.e_passport_num = add_field("Номер паспорта (6 цифр):")
    self.e_passport_issued = add_field("Кем выдан:")
    self.e_passport_code = add_field("Код подразделения:")
    self.e_inn = add_field("ИНН клиента (12 цифр):")
    self.e_address = add_field("Адрес прописки:")

    btn_frame = ttk.Frame(form)
    btn_frame.grid(row=row, column=0, columnspan=2, pady=25)

    save_btn = ttk.Button(
        btn_frame, text="💾 Сохранить договор", command=self.generate_doc
    )
    save_btn.pack(side="left", padx=10)

    print_btn = ttk.Button(
        btn_frame, text="🖨️ Сохранить и на печать", command=self.print_doc
    )
    print_btn.pack(side="left", padx=10)

  def change_default_directory(self):
    new_dir = filedialog.askdirectory(title="Выберите новую папку по умолчанию")
    if new_dir:
      self.default_output_dir.set(new_dir)
      save_default_dir(new_dir)
      short_path = (
          new_dir if len(new_dir) < 45 else "..." + new_dir[-42:]
      )
      header_color = "#f1c40f" if self.current_theme == "dark" else "#e74c3c"
      self.lbl_default_dir.config(
          text=f"По умолчанию: {short_path}", fg=header_color
      )
      messagebox.showinfo(
          "Успех", f"Папка по умолчанию успешно изменена на:\n{new_dir}"
      )

  def choose_custom_directory(self):
    chosen_dir = filedialog.askdirectory(
        title="Выберите папку для этого договора"
    )
    if chosen_dir:
      self.custom_output_dir.set(chosen_dir)
      display_path = (
          chosen_dir if len(chosen_dir) < 40 else "..." + chosen_dir[-37:]
      )
      header_color = "#f1c40f" if self.current_theme == "dark" else "#e74c3c"
      self.lbl_custom_dir.config(text=f"Папка: {display_path}", fg=header_color)

  def validate_and_collect_data(self):
    series = self.e_passport_series.get().strip()
    number = self.e_passport_num.get().strip()
    inn = self.e_inn.get().strip()

    if series and (not series.isdigit() or len(series) != 4):
      messagebox.showerror(
          "Ошибка в паспорте",
          (
              "Если серия паспорта указана, она должна состоять ровно из 4"
              f" цифр!\nВы ввели: '{series}'"
          ),
      )
      return None

    if number and (not number.isdigit() or len(number) != 6):
      messagebox.showerror(
          "Ошибка в паспорте",
          (
              "Если номер паспорта указан, он должен состоять ровно из 6"
              f" цифр!\nВы ввели: '{number}'"
          ),
      )
      return None

    if inn and (not inn.isdigit() or len(inn) != 12):
      messagebox.showerror(
          "Ошибка в ИНН",
          (
              "Если ИНН указан, он должен состоять ровно из 12 цифр!\nВы ввели:"
              f" '{inn}'"
          ),
      )
      return None

    price_val = self.e_price.get().strip()
    price_words = number_to_words_ru(price_val)

    raw_date = self.e_contract_date.get().strip()
    formatted_date = format_date_with_month_name(raw_date)

    if self.service_var.get() == "our":
      g_months = "6"
      g_months_words = "шесть"
      g_km = "30 000"
      g_km_words = "тридцать тысяч"
      g_place = "в сертифицированном сервисе Продавца"
    else:
      g_months = "3"
      g_months_words = "три"
      g_km = "20 000"
      g_km_words = "двадцать тысяч"
      g_place = "в стороннем автосервисе"

    data = {
        "contract_num": self.e_contract_num.get().strip(),
        "contract_date": formatted_date,
        "engine_model": self.e_engine_model.get().strip(),
        "engine_num": self.e_engine_num.get().strip(),
        "car_brand": self.e_car_brand.get().strip(),
        "car_model": self.e_car_model.get().strip(),
        "car_gosnum": self.e_car_gosnum.get().strip(),
        "price": price_val,
        "price_words": price_words,
        "warranty_months": g_months,
        "warranty_months_words": g_months_words,
        "warranty_km": g_km,
        "warranty_km_words": g_km_words,
        "warranty_place": g_place,
        "fio": self.e_fio.get().strip(),
        "passport_series": series,
        "passport_num": number,
        "passport_issued": self.e_passport_issued.get().strip(),
        "passport_code": self.e_passport_code.get().strip(),
        "inn": inn,
        "address": self.e_address.get().strip(),
        "quantity": "1",
    }
    return data

  def build_document(self):
    template_path = os.path.join(BASE_DIR, "template.docx")
    if not os.path.exists(template_path):
      messagebox.showerror(
          "Ошибка",
          (
              "Файл шаблона 'template.docx' не найден по пути:\n"
              f"{template_path}\n\nПоложите шаблон в эту папку перед запуском."
          ),
      )
      return None

    data = self.validate_and_collect_data()
    if not data:
      return None

    try:
      doc = DocxTemplate(template_path)
      doc.render(data)

      user_custom_dir = self.custom_output_dir.get()
      if user_custom_dir:
        output_dir = user_custom_dir
      else:
        output_dir = self.default_output_dir.get()

      os.makedirs(output_dir, exist_ok=True)

      safe_num = data["contract_num"].replace("/", "_").replace("\\", "_")
      if data["fio"]:
        safe_fio = data["fio"].split()[0]
        filename = os.path.join(
            output_dir, f"Договор_{safe_num}_{safe_fio}.docx"
        )
      else:
        filename = os.path.join(output_dir, f"Договор_{safe_num}.docx")

      doc.save(filename)
      return filename
    except Exception as e:
      messagebox.showerror(
          "Ошибка генерации", f"Не удалось создать документ: {e}"
      )
      return None

  def generate_doc(self):
    filename = self.build_document()
    if filename:
      messagebox.showinfo("Успех", f"Договор успешно сохранен в файл:\n{filename}")

  def print_doc(self):
    filename = self.build_document()
    if filename:
      try:
        if os.name == "nt":
          os.startfile(filename, "print")
          messagebox.showinfo(
              "Печать", "Документ отправлен на принтер по умолчанию."
          )
        else:
          messagebox.showwarning(
              "Внимание",
              (
                  "Автопечать поддерживается только на Windows.\nФайл сохранен:"
                  f" {filename}"
              ),
          )
      except Exception as e:
        messagebox.showerror(
            "Ошибка печати",
            f"Не удалось отправить на печать автоматически: {e}",
        )


if __name__ == "__main__":
  root = tk.Tk()
  app = ModernContractApp(root)
  root.mainloop()