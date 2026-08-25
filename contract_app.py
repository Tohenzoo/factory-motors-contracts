import datetime
import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from docxtpl import DocxTemplate
from num2words import num2words
from PIL import Image

# Устанавливаем тему
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Фирменный желтый цвет Factory Motors и оттенки для наведения
BRAND_YELLOW = "#f1c40f"
BRAND_YELLOW_HOVER = "#d4ac0d"
TEXT_DARK = "#121212"

if getattr(sys, "frozen", False):
  BASE_DIR = sys._MEIPASS
else:
  BASE_DIR = r"F:\Files\Работа\Factory Motors\Генератор договоров"

IMAGES_DIR = os.path.join(BASE_DIR, "images")

# Конфиг сохраняется в системной папке профиля пользователя
CONFIG_DIR = os.path.join(
    os.getenv("APPDATA") or os.path.expanduser("~"), "FactoryMotorsContracts"
)
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Заполнитель для пустых полей, чтобы текст в договоре не слипался
BLANK_LINE = "____________________"


def load_default_dir():
  default_path = os.path.join(CONFIG_DIR, "generated_contracts")
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
      return BLANK_LINE
    amount = int(clean_str)
    words = num2words(amount, lang="ru")
    words = words.split(" целых")[0]
    return words.capitalize()
  except Exception:
    return BLANK_LINE


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
  return date_str if date_str else BLANK_LINE


class ModernContractApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("Factory Motors: Генератор Договоров")
    self.geometry("900x950")
    self.minsize(800, 700)

    try:
      self.iconbitmap(os.path.join(IMAGES_DIR, "logo.ico"))
    except Exception:
      pass

    self.current_output_dir = ctk.StringVar(value=load_default_dir())

    self.scroll_frame = ctk.CTkScrollableFrame(
        self, corner_radius=0, fg_color="transparent"
    )
    self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    self.create_header()
    self.create_form_sections()

  def create_header(self):
    header_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
    header_frame.pack(fill="x", padx=10, pady=(10, 20))

    logo_path = os.path.join(IMAGES_DIR, "logo_dark.png")
    if not os.path.exists(logo_path):
      logo_path = os.path.join(IMAGES_DIR, "logo.png")

    if os.path.exists(logo_path):
      try:
        pil_img = Image.open(logo_path)
        self.logo_img = ctk.CTkImage(
            light_image=pil_img, dark_image=pil_img, size=(70, 70)
        )
        logo_lbl = ctk.CTkLabel(header_frame, image=self.logo_img, text="")
        logo_lbl.pack(side="left", padx=(0, 15))
      except Exception:
        pass

    title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    title_frame.pack(side="left", fill="y", expand=True)

    lbl_brand = ctk.CTkLabel(
        title_frame,
        text="FACTORY MOTORS",
        font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        text_color=BRAND_YELLOW,
    )
    lbl_brand.pack(anchor="w")

    lbl_sub = ctk.CTkLabel(
        title_frame,
        text="Современная система формирования договоров",
        font=ctk.CTkFont(family="Segoe UI", size=12),
    )
    lbl_sub.pack(anchor="w", pady=(2, 0))

    self.theme_btn = ctk.CTkButton(
        header_frame,
        text="🌙 Светлая тема",
        width=140,
        height=32,
        font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        fg_color="#333333",
        hover_color="#444444",
        text_color="#ffffff",
        command=self.toggle_theme,
    )
    self.theme_btn.pack(side="right", anchor="ne")

  def toggle_theme(self):
    current = ctk.get_appearance_mode()
    if current == "Dark":
      ctk.set_appearance_mode("Light")
      self.theme_btn.configure(
          text="☀️ Темная тема",
          fg_color="#e0e0e0",
          hover_color="#cccccc",
          text_color="#222222",
      )
    else:
      ctk.set_appearance_mode("Dark")
      self.theme_btn.configure(
          text="🌙 Светлая тема",
          fg_color="#333333",
          hover_color="#444444",
          text_color="#ffffff",
      )

  def create_card(self, title_text):
    card = ctk.CTkFrame(self.scroll_frame, corner_radius=10, border_width=1)
    card.pack(fill="x", padx=10, pady=8)

    title_lbl = ctk.CTkLabel(
        card,
        text=title_text,
        font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
        text_color=BRAND_YELLOW,
    )
    title_lbl.pack(anchor="w", padx=15, pady=(12, 5))

    content_frame = ctk.CTkFrame(card, fg_color="transparent")
    content_frame.pack(fill="x", padx=15, pady=(0, 12))
    return content_frame

  def create_form_sections(self):
    # --- СЕКЦИЯ 1 ---
    f1 = self.create_card("1. Основные данные договора")
    f1.grid_columnconfigure((0, 1), weight=1)

    ctk.CTkLabel(f1, text="Номер договора:").grid(
        row=0, column=0, sticky="w", pady=2
    )
    self.e_contract_num = ctk.CTkEntry(
        f1, placeholder_text="Например: 1337", height=32, border_color=BRAND_YELLOW
    )
    self.e_contract_num.grid(
        row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 10)
    )

    ctk.CTkLabel(f1, text="Дата договора (ДД.ММ.ГГГГ):").grid(
        row=0, column=1, sticky="w", pady=2
    )
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    self.e_contract_date = ctk.CTkEntry(
        f1, height=32, border_color=BRAND_YELLOW
    )
    self.e_contract_date.insert(0, today_str)
    self.e_contract_date.grid(row=1, column=1, sticky="ew", pady=(0, 10))

    # --- СЕКЦИЯ 2 ---
    f2 = self.create_card("2. Тип покупателя")
    self.client_type_var = ctk.StringVar(value="fiz")

    type_frame = ctk.CTkFrame(f2, fg_color="transparent")
    type_frame.pack(fill="x", pady=5)

    r_fiz = ctk.CTkRadioButton(
        type_frame,
        text="Физическое лицо",
        variable=self.client_type_var,
        value="fiz",
        command=self.toggle_client_type,
        border_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        fg_color=BRAND_YELLOW,
    )
    r_fiz.pack(side="left", padx=(0, 30))

    r_ur = ctk.CTkRadioButton(
        type_frame,
        text="Юридическое лицо (ООО, АО)",
        variable=self.client_type_var,
        value="ur",
        command=self.toggle_client_type,
        border_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        fg_color=BRAND_YELLOW,
    )
    r_ur.pack(side="left")

    # --- СЕКЦИЯ 3 ---
    self.card_buyer = self.create_card("3. Данные покупателя")

    self.fiz_frame = ctk.CTkFrame(self.card_buyer, fg_color="transparent")
    self.fiz_frame.pack(fill="x", expand=True)

    def add_f_entry(parent, label, placeholder=""):
      ctk.CTkLabel(parent, text=label).pack(anchor="w", pady=(4, 2))
      ent = ctk.CTkEntry(
          parent,
          placeholder_text=placeholder,
          height=32,
          border_color=BRAND_YELLOW,
      )
      ent.pack(fill="x", pady=(0, 8))
      return ent

    self.e_fio = add_f_entry(
        self.fiz_frame, "Фамилия Имя Отчество:", "Иванов Иван Иванович"
    )

    row_p = ctk.CTkFrame(self.fiz_frame, fg_color="transparent")
    row_p.pack(fill="x", pady=(0, 8))
    row_p.grid_columnconfigure((0, 1, 2), weight=1)

    ctk.CTkLabel(row_p, text="Серия (4 цифр):").grid(row=0, column=0, sticky="w")
    self.e_passport_series = ctk.CTkEntry(
        row_p, height=32, border_color=BRAND_YELLOW
    )
    self.e_passport_series.grid(row=1, column=0, sticky="ew", padx=(0, 5))

    ctk.CTkLabel(row_p, text="Номер (6 цифр):").grid(row=0, column=1, sticky="w")
    self.e_passport_num = ctk.CTkEntry(
        row_p, height=32, border_color=BRAND_YELLOW
    )
    self.e_passport_num.grid(row=1, column=1, sticky="ew", padx=5)

    ctk.CTkLabel(row_p, text="ИНН (12 цифр):").grid(row=0, column=2, sticky="w")
    self.e_inn_fiz = ctk.CTkEntry(row_p, height=32, border_color=BRAND_YELLOW)
    self.e_inn_fiz.grid(row=1, column=2, sticky="ew", padx=(5, 0))

    self.e_passport_issued = add_f_entry(self.fiz_frame, "Кем выдан паспорт:")
    self.e_passport_code = add_f_entry(self.fiz_frame, "Код подразделения:")
    self.e_address = add_f_entry(self.fiz_frame, "Адрес прописки:")

    self.ur_frame = ctk.CTkFrame(self.card_buyer, fg_color="transparent")
    self.e_org_name = add_f_entry(
        self.ur_frame, "Название организации (ООО, АО и т.д.):", "ООО «Компания»"
    )
    self.e_director = add_f_entry(
        self.ur_frame, "Генеральный директор (ФИО полностью):"
    )

    row_b = ctk.CTkFrame(self.ur_frame, fg_color="transparent")
    row_b.pack(fill="x", pady=(0, 8))
    row_b.grid_columnconfigure((0, 1), weight=1)

    ctk.CTkLabel(row_b, text="Расчетный счет (р/с):").grid(
        row=0, column=0, sticky="w"
    )
    self.e_rs = ctk.CTkEntry(row_b, height=32, border_color=BRAND_YELLOW)
    self.e_rs.grid(row=1, column=0, sticky="ew", padx=(0, 5))

    ctk.CTkLabel(row_b, text="Корр. счет (к/с):").grid(
        row=0, column=1, sticky="w"
    )
    self.e_ks = ctk.CTkEntry(row_b, height=32, border_color=BRAND_YELLOW)
    self.e_ks.grid(row=1, column=1, sticky="ew", padx=(5, 0))

    row_b2 = ctk.CTkFrame(self.ur_frame, fg_color="transparent")
    row_b2.pack(fill="x", pady=(0, 8))
    row_b2.grid_columnconfigure((0, 1, 2), weight=1)

    ctk.CTkLabel(row_b2, text="БИК банка:").grid(row=0, column=0, sticky="w")
    self.e_bik = ctk.CTkEntry(row_b2, height=32, border_color=BRAND_YELLOW)
    self.e_bik.grid(row=1, column=0, sticky="ew", padx=(0, 5))

    ctk.CTkLabel(row_b2, text="ИНН организации:").grid(
        row=0, column=1, sticky="w"
    )
    self.e_inn_ur = ctk.CTkEntry(row_b2, height=32, border_color=BRAND_YELLOW)
    self.e_inn_ur.grid(row=1, column=1, sticky="ew", padx=5)

    ctk.CTkLabel(row_b2, text="КПП организации:").grid(
        row=0, column=2, sticky="w"
    )
    self.e_kpp = ctk.CTkEntry(row_b2, height=32, border_color=BRAND_YELLOW)
    self.e_kpp.grid(row=1, column=2, sticky="ew", padx=(5, 0))

    self.e_bank = add_f_entry(self.ur_frame, "Наименование банка:")
    self.e_legal_address = add_f_entry(self.ur_frame, "Юридический адрес:")

    row_c = ctk.CTkFrame(self.ur_frame, fg_color="transparent")
    row_c.pack(fill="x", pady=(0, 8))
    row_c.grid_columnconfigure((0, 1), weight=1)

    ctk.CTkLabel(row_c, text="Телефон:").grid(row=0, column=0, sticky="w")
    self.e_phone = ctk.CTkEntry(row_c, height=32, border_color=BRAND_YELLOW)
    self.e_phone.grid(row=1, column=0, sticky="ew", padx=(0, 5))

    ctk.CTkLabel(row_c, text="E-mail:").grid(row=0, column=1, sticky="w")
    self.e_email = ctk.CTkEntry(row_c, height=32, border_color=BRAND_YELLOW)
    self.e_email.grid(row=1, column=1, sticky="ew", padx=(5, 0))

    self.ur_frame.pack_forget()

    # --- СЕКЦИЯ 4 ---
    f4 = self.create_card("4. Двигатель и автомобиль")
    f4.grid_columnconfigure((0, 1), weight=1)

    ctk.CTkLabel(f4, text="Модель двигателя:").grid(row=0, column=0, sticky="w")
    self.e_engine_model = ctk.CTkEntry(
        f4, height=32, border_color=BRAND_YELLOW
    )
    self.e_engine_model.grid(
        row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 8)
    )

    ctk.CTkLabel(f4, text="Номер двигателя:").grid(row=0, column=1, sticky="w")
    self.e_engine_num = ctk.CTkEntry(f4, height=32, border_color=BRAND_YELLOW)
    self.e_engine_num.grid(row=1, column=1, sticky="ew", pady=(0, 8))

    ctk.CTkLabel(f4, text="Марка машины:").grid(row=2, column=0, sticky="w")
    self.e_car_brand = ctk.CTkEntry(f4, height=32, border_color=BRAND_YELLOW)
    self.e_car_brand.grid(
        row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 8)
    )

    ctk.CTkLabel(f4, text="Модель автомобиля:").grid(row=2, column=1, sticky="w")
    self.e_car_model = ctk.CTkEntry(f4, height=32, border_color=BRAND_YELLOW)
    self.e_car_model.grid(row=3, column=1, sticky="ew", pady=(0, 8))

    ctk.CTkLabel(f4, text="Госномер:").grid(row=4, column=0, sticky="w")
    self.e_car_gosnum = ctk.CTkEntry(f4, height=32, border_color=BRAND_YELLOW)
    self.e_car_gosnum.grid(row=5, column=0, sticky="ew", padx=(0, 10))

    # --- СЕКЦИЯ 5 ---
    f5 = self.create_card("5. Стоимость товара")
    ctk.CTkLabel(f5, text="Стоимость (цифрами, например 120000):").pack(
        anchor="w", pady=(0, 2)
    )
    self.e_price = ctk.CTkEntry(f5, height=32, border_color=BRAND_YELLOW)
    self.e_price.pack(fill="x", pady=(0, 5))

    # --- СЕКЦИЯ 6: Гарантия (3 месяца сверху, 6 месяцев снизу) ---
    f6 = self.create_card("6. Условия гарантии и установки")
    self.service_var = ctk.StringVar(value="other")

    ctk.CTkRadioButton(
        f6,
        text="Установка в стороннем сервисе (Гарантия 3 месяца или 20 000 км)",
        variable=self.service_var,
        value="other",
        border_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        fg_color=BRAND_YELLOW,
    ).pack(anchor="w", pady=4)

    ctk.CTkRadioButton(
        f6,
        text="Установка в нашем сервисе (Гарантия 6 месяцев или 30 000 км)",
        variable=self.service_var,
        value="our",
        border_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        fg_color=BRAND_YELLOW,
    ).pack(anchor="w", pady=4)

    # --- СЕКЦИЯ 7: Папка для сохранения документов ---
    f7 = self.create_card("7. Папка для сохранения документов")

    dir_row = ctk.CTkFrame(f7, fg_color="transparent")
    dir_row.pack(fill="x", pady=5)

    curr_path = self.current_output_dir.get()
    short_path = curr_path if len(curr_path) < 45 else "..." + curr_path[-42:]

    self.lbl_current_dir = ctk.CTkLabel(
        dir_row, text=f"Текущий путь: {short_path}", font=ctk.CTkFont(size=12)
    )
    self.lbl_current_dir.pack(side="left", padx=(0, 15))

    btn_choose_dir = ctk.CTkButton(
        dir_row,
        text="📁 Выбрать папку",
        width=150,
        height=32,
        fg_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        text_color=TEXT_DARK,
        font=ctk.CTkFont(weight="bold"),
        command=self.choose_directory,
    )
    btn_choose_dir.pack(side="left", padx=(0, 8))

    btn_set_default = ctk.CTkButton(
        dir_row,
        text="⚙️ Выбрать папку по умолчанию",
        width=210,
        height=32,
        fg_color="#333333",
        hover_color="#444444",
        text_color="#ffffff",
        command=self.set_as_default_directory,
    )
    btn_set_default.pack(side="left")

    # КНОПКИ ДЕЙСТВИЙ ВНИЗУ
    btn_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
    btn_frame.pack(fill="x", padx=10, pady=20)
    btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

    save_btn = ctk.CTkButton(
        btn_frame,
        text="💾 Сохранить договор",
        height=45,
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        text_color=TEXT_DARK,
        command=self.generate_doc,
    )
    save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

    print_btn = ctk.CTkButton(
        btn_frame,
        text="🖨️ Сохранить и на печать",
        height=45,
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        text_color=TEXT_DARK,
        command=self.print_doc,
    )
    print_btn.grid(row=0, column=1, sticky="ew", padx=6)

    reset_btn = ctk.CTkButton(
        btn_frame,
        text="🗑️ Стереть всё",
        height=45,
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color="#c0392b",
        hover_color="#962d22",
        text_color="#ffffff",
        command=self.reset_form,
    )
    reset_btn.grid(row=0, column=2, sticky="ew", padx=(6, 0))

  def toggle_client_type(self):
    ctype = self.client_type_var.get()
    if ctype == "fiz":
      self.ur_frame.pack_forget()
      self.fiz_frame.pack(fill="x", expand=True)
    else:
      self.fiz_frame.pack_forget()
      self.ur_frame.pack(fill="x", expand=True)

  def reset_form(self):
    all_entries = [
        self.e_contract_num,
        self.e_fio,
        self.e_passport_series,
        self.e_passport_num,
        self.e_inn_fiz,
        self.e_passport_issued,
        self.e_passport_code,
        self.e_address,
        self.e_org_name,
        self.e_director,
        self.e_rs,
        self.e_ks,
        self.e_bik,
        self.e_inn_ur,
        self.e_kpp,
        self.e_bank,
        self.e_legal_address,
        self.e_phone,
        self.e_email,
        self.e_engine_model,
        self.e_engine_num,
        self.e_car_brand,
        self.e_car_model,
        self.e_car_gosnum,
        self.e_price,
    ]

    for ent in all_entries:
      ent.delete(0, tk.END)

    self.e_contract_date.delete(0, tk.END)
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    self.e_contract_date.insert(0, today_str)

    self.client_type_var.set("fiz")
    self.toggle_client_type()

    self.service_var.set("other")

  def choose_directory(self):
    initial_dir = self.current_output_dir.get()
    if not os.path.exists(initial_dir):
      initial_dir = os.getenv("APPDATA") or os.path.expanduser("~")

    new_dir = filedialog.askdirectory(
        title="Выберите папку для сохранения договора", initialdir=initial_dir
    )
    if new_dir:
      self.current_output_dir.set(new_dir)
      short_path = new_dir if len(new_dir) < 45 else "..." + new_dir[-42:]
      self.lbl_current_dir.configure(text=f"Текущий путь: {short_path}")

  def set_as_default_directory(self):
    initial_dir = self.current_output_dir.get()
    if not os.path.exists(initial_dir):
      initial_dir = os.getenv("APPDATA") or os.path.expanduser("~")

    new_dir = filedialog.askdirectory(
        title="Выберите общую корневую папку по умолчанию",
        initialdir=initial_dir,
    )
    if new_dir:
      self.current_output_dir.set(new_dir)
      save_default_dir(new_dir)
      short_path = new_dir if len(new_dir) < 45 else "..." + new_dir[-42:]
      self.lbl_current_dir.configure(text=f"Текущий путь: {short_path}")
      messagebox.showinfo(
          "Успех", f"Корневая папка по умолчанию успешно сохранена:\n{new_dir}"
      )

  def get_field_val(self, entry_widget):
    val = entry_widget.get().strip()
    return val if val else BLANK_LINE

  def validate_and_collect_data(self):
    ctype = self.client_type_var.get()
    price_val = self.e_price.get().strip()
    price_words = (
        number_to_words_ru(price_val) if price_val else BLANK_LINE
    )
    raw_date = self.e_contract_date.get().strip()
    formatted_date = format_date_with_month_name(raw_date)

    # Правильное склонение месяцев в зависимости от выбранного срока
    if self.service_var.get() == "our":
      g_months, g_months_words, g_km, g_km_words, g_place = (
          "6 месяцев",
          "шесть месяцев",
          "30 000",
          "тридцать тысяч",
          "в сертифицированном сервисе Продавца",
      )
    else:
      g_months, g_months_words, g_km, g_km_words, g_place = (
          "3 месяца",
          "три месяца",
          "20 000",
          "двадцать тысяч",
          "в стороннем автосервисе",
      )

    contract_num_val = self.e_contract_num.get().strip()

    data = {
        "contract_num": (
            contract_num_val if contract_num_val else BLANK_LINE
        ),
        "contract_date": formatted_date,
        "engine_model": self.get_field_val(self.e_engine_model),
        "engine_num": self.get_field_val(self.e_engine_num),
        "car_brand": self.get_field_val(self.e_car_brand),
        "car_model": self.get_field_val(self.e_car_model),
        "car_gosnum": self.get_field_val(self.e_car_gosnum),
        "price": price_val if price_val else BLANK_LINE,
        "price_words": price_words,
        "warranty_months": g_months,
        "warranty_months_words": g_months_words,
        "warranty_km": g_km,
        "warranty_km_words": g_km_words,
        "warranty_place": g_place,
        "quantity": "1",
        "client_type": ctype,
    }

    if ctype == "fiz":
      series = self.e_passport_series.get().strip()
      number = self.e_passport_num.get().strip()
      inn = self.e_inn_fiz.get().strip()

      if series and (not series.isdigit() or len(series) != 4):
        messagebox.showerror(
            "Ошибка в паспорте", "Серия паспорта должна состоять из 4 цифр!"
        )
        return None
      if number and (not number.isdigit() or len(number) != 6):
        messagebox.showerror(
            "Ошибка в паспорте", "Номер паспорта должен состоять из 6 цифр!"
        )
        return None

      data.update({
          "fio": self.get_field_val(self.e_fio),
          "passport_series": series if series else BLANK_LINE,
          "passport_num": number if number else BLANK_LINE,
          "passport_issued": self.get_field_val(self.e_passport_issued),
          "passport_code": self.get_field_val(self.e_passport_code),
          "inn": inn if inn else BLANK_LINE,
          "address": self.get_field_val(self.e_address),
      })
    else:
      data.update({
          "org_name": self.get_field_val(self.e_org_name),
          "director_fio": self.get_field_val(self.e_director),
          "rs": self.get_field_val(self.e_rs),
          "ks": self.get_field_val(self.e_ks),
          "bik": self.get_field_val(self.e_bik),
          "bank": self.get_field_val(self.e_bank),
          "inn": self.get_field_val(self.e_inn_ur),
          "kpp": self.get_field_val(self.e_kpp),
          "legal_address": self.get_field_val(self.e_legal_address),
          "phone": self.get_field_val(self.e_phone),
          "email": self.get_field_val(self.e_email),
      })

    return data

  def build_document(self):
    data = self.validate_and_collect_data()
    if not data:
      return None

    template_filename = (
        "template_fiz.docx" if data["client_type"] == "fiz" else "template_ur.docx"
    )
    template_path = os.path.join(BASE_DIR, template_filename)

    if not os.path.exists(template_path):
      messagebox.showerror(
          "Ошибка",
          (
              f"Файл шаблона '{template_filename}' не найден по пути:\n"
              f"{template_path}"
          ),
      )
      return None

    try:
      doc = DocxTemplate(template_path)
      doc.render(data)

      output_dir = self.current_output_dir.get()
      os.makedirs(output_dir, exist_ok=True)

      raw_num = self.e_contract_num.get().strip()
      safe_num = (
          raw_num.replace("/", "_").replace("\\", "_")
          if raw_num
          else "БЕЗ_НОМЕРА"
      )
      name_identifier = (
          self.e_org_name.get().strip()
          if data["client_type"] == "ur"
          else self.e_fio.get().strip()
      )

      if name_identifier:
        safe_name = name_identifier.split()[0]
        filename = os.path.join(
            output_dir, f"Договор_{safe_num}_{safe_name}.docx"
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

  def open_target_folder(self, filename):
    try:
      if os.name == "nt":
        norm_path = os.path.normpath(filename)
        subprocess.Popen(f'explorer /select,"{norm_path}"')
      else:
        os.startfile(os.path.dirname(filename))
    except Exception:
      try:
        os.startfile(os.path.dirname(filename))
      except Exception:
        pass

  def generate_doc(self):
    filename = self.build_document()
    if filename:
      messagebox.showinfo("Успех", f"Договор успешно сохранен в файл:\n{filename}")
      self.open_target_folder(filename)

  def print_doc(self):
    filename = self.build_document()
    if filename:
      try:
        if os.name == "nt":
          os.startfile(filename, "print")
          messagebox.showinfo(
              "Печать", "Документ отправлен на принтер по умолчанию."
          )
          self.open_target_folder(filename)
        else:
          messagebox.showwarning(
              "Внимание", "Автопечать поддерживается только на Windows."
          )
      except Exception as e:
        messagebox.showerror(
            "Ошибка печати", f"Не удалось отправить на печать: {e}"
        )


if __name__ == "__main__":
  app = ModernContractApp()
  app.mainloop()