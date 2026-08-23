import datetime
import json
import os
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
  CONFIG_DIR = os.path.dirname(sys.executable)
else:
  BASE_DIR = r"F:\Files\Работа\Factory Motors\Генератор договоров"
  CONFIG_DIR = BASE_DIR

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
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

    self.default_output_dir = ctk.StringVar(value=load_default_dir())
    self.custom_output_dir = ctk.StringVar(value="")

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
        text="🌙 Сменить тему",
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
          text="Тёмная тема",
          fg_color="#e0e0e0",
          hover_color="#cccccc",
          text_color="#222222",
      )
    else:
      ctk.set_appearance_mode("Dark")
      self.theme_btn.configure(
          text="Светлая тема",
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

    # --- СЕКЦИЯ 6 ---
    f6 = self.create_card("6. Условия гарантии и установки")
    self.service_var = ctk.StringVar(value="our")

    ctk.CTkRadioButton(
        f6,
        text="Установка в нашем сервисе (Гарантия 6 месяцев или 30 000 км)",
        variable=self.service_var,
        value="our",
        border_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        fg_color=BRAND_YELLOW,
    ).pack(anchor="w", pady=3)
    ctk.CTkRadioButton(
        f6,
        text="Установка в стороннем сервисе (Гарантия 3 месяца или 20 000 км)",
        variable=self.service_var,
        value="other",
        border_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        fg_color=BRAND_YELLOW,
    ).pack(anchor="w", pady=3)

    # --- СЕКЦИЯ 7 ---
    f7 = self.create_card("7. Папка для сохранения документов")
    dir_row = ctk.CTkFrame(f7, fg_color="transparent")
    dir_row.pack(fill="x", pady=5)

    curr_default = self.default_output_dir.get()
    short_default = (
        curr_default if len(curr_default) < 50 else "..." + curr_default[-47:]
    )

    self.lbl_default_dir = ctk.CTkLabel(
        dir_row, text=f"По умолчанию: {short_default}"
    )
    self.lbl_default_dir.pack(side="left", padx=(0, 15))

    btn_set_default = ctk.CTkButton(
        dir_row,
        text="⚙️ Изменить папку",
        width=140,
        height=30,
        fg_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        text_color=TEXT_DARK,
        font=ctk.CTkFont(weight="bold"),
        command=self.change_default_directory,
    )
    btn_set_default.pack(side="left")

    # ЖЕЛТЫЕ КНОПКИ ДЕЙСТВИЙ ВНИЗУ
    btn_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
    btn_frame.pack(fill="x", padx=10, pady=20)
    btn_frame.grid_columnconfigure((0, 1), weight=1)

    save_btn = ctk.CTkButton(
        btn_frame,
        text="💾 Сохранить договор",
        height=45,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        text_color=TEXT_DARK,
        command=self.generate_doc,
    )
    save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))

    print_btn = ctk.CTkButton(
        btn_frame,
        text="🖨️ Сохранить и на печать",
        height=45,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=BRAND_YELLOW,
        hover_color=BRAND_YELLOW_HOVER,
        text_color=TEXT_DARK,
        command=self.print_doc,
    )
    print_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))

  def toggle_client_type(self):
    ctype = self.client_type_var.get()
    if ctype == "fiz":
      self.ur_frame.pack_forget()
      self.fiz_frame.pack(fill="x", expand=True)
    else:
      self.fiz_frame.pack_forget()
      self.ur_frame.pack(fill="x", expand=True)

  def change_default_directory(self):
    new_dir = filedialog.askdirectory(title="Выберите новую папку по умолчанию")
    if new_dir:
      self.default_output_dir.set(new_dir)
      save_default_dir(new_dir)
      short_path = new_dir if len(new_dir) < 50 else "..." + new_dir[-47:]
      self.lbl_default_dir.configure(text=f"По умолчанию: {short_path}")
      messagebox.showinfo(
          "Успех", f"Папка по умолчанию успешно изменена на:\n{new_dir}"
      )

  def validate_and_collect_data(self):
    ctype = self.client_type_var.get()
    price_val = self.e_price.get().strip()
    price_words = number_to_words_ru(price_val)
    raw_date = self.e_contract_date.get().strip()
    formatted_date = format_date_with_month_name(raw_date)

    if self.service_var.get() == "our":
      g_months, g_months_words, g_km, g_km_words, g_place = (
          "6",
          "шесть",
          "30 000",
          "тридцать тысяч",
          "в сертифицированном сервисе Продавца",
      )
    else:
      g_months, g_months_words, g_km, g_km_words, g_place = (
          "3",
          "три",
          "20 000",
          "двадцать тысяч",
          "в стороннем автосервисе",
      )

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
          "fio": self.e_fio.get().strip(),
          "passport_series": series,
          "passport_num": number,
          "passport_issued": self.e_passport_issued.get().strip(),
          "passport_code": self.e_passport_code.get().strip(),
          "inn": inn,
          "address": self.e_address.get().strip(),
      })
    else:
      data.update({
          "org_name": self.e_org_name.get().strip(),
          "director_fio": self.e_director.get().strip(),
          "rs": self.e_rs.get().strip(),
          "ks": self.e_ks.get().strip(),
          "bik": self.e_bik.get().strip(),
          "bank": self.e_bank.get().strip(),
          "inn": self.e_inn_ur.get().strip(),
          "kpp": self.e_kpp.get().strip(),
          "legal_address": self.e_legal_address.get().strip(),
          "phone": self.e_phone.get().strip(),
          "email": self.e_email.get().strip(),
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

      output_dir = self.default_output_dir.get()
      os.makedirs(output_dir, exist_ok=True)

      safe_num = data["contract_num"].replace("/", "_").replace("\\", "_")
      name_identifier = (
          data.get("org_name")
          if data["client_type"] == "ur"
          else data.get("fio")
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
              "Внимание", "Автопечать поддерживается только на Windows."
          )
      except Exception as e:
        messagebox.showerror(
            "Ошибка печати", f"Не удалось отправить на печать: {e}"
        )


if __name__ == "__main__":
  app = ModernContractApp()
  app.mainloop()