from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


# ==============================================================================
# МЕНЕДЖЕР ПОЛЬЗОВАТЕЛЕЙ
# ==============================================================================

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email обязателен'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# ==============================================================================
# БЛОК 1: ЯДРО СИСТЕМЫ
# ==============================================================================

class Role(models.Model):
    id_role = models.CharField(_('ID роли'), max_length=50, primary_key=True, help_text="Только латиница и _")
    name = models.CharField(_('Название'), max_length=100)

    class Meta:
        verbose_name = _('Роль')
        verbose_name_plural = _('Роли')
        app_label = 'core'

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    id_user = models.AutoField(_('ID пользователя'), primary_key=True)
    last_name = models.CharField(_('Фамилия'), max_length=100, blank=True, null=True)
    first_name = models.CharField(_('Имя'), max_length=100, blank=True, null=True)
    middle_name = models.CharField(_('Отчество'), max_length=100, blank=True, null=True)
    email = models.EmailField(_('Электронная почта'), unique=True)
    email_confirmed = models.BooleanField(_('Email подтвержден'), default=False)
    requires_password_change = models.BooleanField(_('Требует смены пароля'), default=True)
    esia_id = models.CharField(_('ESIA ID (Госуслуги)'), max_length=100, blank=True, null=True, unique=True)
    
    is_staff = models.BooleanField(_('Статус персонала'), default=False)
    is_active = models.BooleanField(_('Активен'), default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        app_label = 'core'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.email})"
    
    def get_full_name(self):
        """Возвращает ФИО пользователя."""
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(filter(None, parts)).strip()
    
    def get_short_name(self):
        """Возвращает Фамилия И.О."""
        parts = [self.last_name]
        if self.first_name:
            parts.append(f"{self.first_name[0]}.")
        if self.middle_name:
            parts.append(f"{self.middle_name[0]}.")
        return ' '.join(parts)


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name=_('Роль'))

    class Meta:
        verbose_name = _('Роль пользователя')
        verbose_name_plural = _('Роли пользователей')
        unique_together = ('user', 'role')
        app_label = 'core'

    def __str__(self):
        return f"{self.user} - {self.role}"


class Campus(models.Model):
    id_campus = models.CharField(_('ID корпуса'), max_length=100, primary_key=True)
    address = models.CharField(_('Полный адрес'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Корпус')
        verbose_name_plural = _('Корпуса')
        app_label = 'core'

    def __str__(self):
        return self.id_campus


class Specialty(models.Model):
    id_specialty = models.CharField(_('Код ФГОС'), max_length=20, primary_key=True)
    name = models.CharField(_('Наименование'), max_length=255)
    level = models.CharField(_('Уровень'), max_length=50, choices=[
        ('специальность', 'Специальность'),
        ('профессия', 'Профессия')
    ], null=True, blank=True)

    class Meta:
        verbose_name = _('Специальность')
        verbose_name_plural = _('Специальности')
        app_label = 'core'

    def __str__(self):
        return f"{self.id_specialty} {self.name}"


class Qualification(models.Model):
    id_qualification = models.AutoField(_('ID квалификации'), primary_key=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, verbose_name=_('Специальность'))
    name = models.CharField(_('Квалификация'), max_length=255)
    professionalitet_role = models.CharField(_('Роль в профессионалитете'), max_length=50, choices=[
        ('ядро', 'Ядро'),
        ('сеть', 'Сеть'),
        ('нет', 'Нет'),
    ], null=True, blank=True)

    class Meta:
        verbose_name = _('Квалификация')
        verbose_name_plural = _('Квалификации')
        unique_together = ('specialty', 'name')
        app_label = 'core'

    def __str__(self):
        return self.name


class Setting(models.Model):
    id_setting = models.AutoField(_('ID настройки'), primary_key=True)
    field_name = models.CharField(_('Название поля'), max_length=100, unique=True)
    value = models.TextField(_('Значение'))
    description = models.TextField(_('Описание'), blank=True, null=True)

    class Meta:
        verbose_name = _('Настройка техникума')
        verbose_name_plural = _('Настройки техникума')
        app_label = 'core'

    def __str__(self):
        return self.field_name


class Order(models.Model):
    id_order = models.CharField(_('ID приказа (НОМЕР-ГОД)'), max_length=100, primary_key=True)
    number = models.CharField(_('Номер'), max_length=50)
    date = models.DateField(_('Дата'), help_text="Формат: ДД.ММ.ГГГГ")
    name = models.CharField(_('Название'), max_length=255)
    file_path = models.FileField(_('Файл приказа'), upload_to='orders/', blank=True, null=True)
    type = models.CharField(_('Тип'), max_length=50, choices=[
        ('зачисление', 'Зачисление'),
        ('отчисление', 'Отчисление'),
        ('перевод', 'Перевод'),
        ('иное', 'Иное')
    ])

    class Meta:
        verbose_name = _('Приказ')
        verbose_name_plural = _('Приказы')
        app_label = 'core'

    def __str__(self):
        return self.id_order


class Group(models.Model):
    id_group = models.CharField(_('ID группы'), max_length=50, primary_key=True)
    qualification = models.ForeignKey(Qualification, on_delete=models.PROTECT, verbose_name=_('Квалификация'))
    year_start = models.IntegerField(_('Год поступления'))
    year_end = models.IntegerField(_('Год окончания'))
    duration = models.CharField(_('Срок обучения'), max_length=50, choices=[
        ('1 год 10 месяцев', '1 год 10 месяцев'),
        ('2 года', '2 года'),
        ('2 года 6 месяцев', '2 года 6 месяцев'),
        ('2 года 10 месяцев', '2 года 10 месяцев'),
        ('3 года 10 месяцев', '3 года 10 месяцев'),
        ('4 года 10 месяцев', '4 года 10 месяцев'),
    ])
    form = models.CharField(_('Форма обучения'), max_length=50, choices=[
        ('очная', 'Очная'),
        ('очно-заочная', 'Очно-заочная'),
        ('заочная', 'Заочная'),
    ])
    financing = models.CharField(_('Финансирование'), max_length=50, choices=[
        ('бюджет', 'Бюджет'),
        ('внебюджет', 'Внебюджет'),
    ])
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, verbose_name=_('Корпус'))
    curator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Куратор'))

    class Meta:
        verbose_name = _('Группа')
        verbose_name_plural = _('Группы')
        app_label = 'core'

    def __str__(self):
        return self.id_group


# ==============================================================================
# БЛОК 2: ПЕРСОНАЛЬНЫЕ ДАННЫЕ
# ==============================================================================

class DocumentType(models.Model):
    code = models.CharField(_('Код'), max_length=50, primary_key=True)
    name = models.CharField(_('Название'), max_length=255)

    class Meta:
        verbose_name = _('Тип документа')
        verbose_name_plural = _('Типы документов')
        app_label = 'core'

    def __str__(self):
        return self.name


class FinancialAidGround(models.Model):
    id_ground = models.AutoField(_('ID основания'), primary_key=True)
    name = models.TextField(_('Название'))
    requires_mo = models.BooleanField(_('Требует проживания в МО'), default=False)
    required_docs = models.JSONField(_('Необходимые документы (коды)'), help_text="JSON-массив кодов из Типы_документов")

    class Meta:
        verbose_name = _('Основание мат. помощи')
        verbose_name_plural = _('Основания мат. помощи')
        app_label = 'core'

    def __str__(self):
        return self.name


class Passport(models.Model):
    id_passport = models.AutoField(_('ID паспорта'), primary_key=True)
    is_foreigner = models.BooleanField(_('Иностранный гражданин'), default=False)
    citizenship = models.CharField(_('Гражданство'), max_length=100, blank=True, null=True)
    series_number = models.CharField(_('Серия и номер'), max_length=20, blank=True, null=True)
    issue_date = models.DateField(_('Дата выдачи'), blank=True, null=True)
    issuer = models.CharField(_('Кем выдан'), max_length=255, blank=True, null=True)
    unit_code = models.CharField(_('Код подразделения'), max_length=10, blank=True, null=True)
    region_city = models.CharField(_('Регион и город'), max_length=255, blank=True, null=True)
    address_detail = models.CharField(_('Адрес детально'), max_length=255, blank=True, null=True)
    fact_region = models.CharField(_('Фактический регион'), max_length=255, blank=True, null=True)
    fact_detail = models.CharField(_('Фактический адрес детально'), max_length=255, blank=True, null=True)
    temp_reg = models.BooleanField(_('Временная прописка'), default=False)
    absence_reason = models.TextField(_('Причина отсутствия'), blank=True, null=True)
    file_path = models.FileField(_('Скан паспорта'), upload_to='docs/passports/', blank=True, null=True)

    class Meta:
        verbose_name = _('Паспорт')
        verbose_name_plural = _('Паспорта')
        app_label = 'core'

    def __str__(self):
        return self.series_number or f"Паспорт #{self.id_passport}"


class Health(models.Model):
    id_health = models.AutoField(_('ID здоровья'), primary_key=True)
    status = models.CharField(_('Состояние'), max_length=100, choices=[
        ('здоров', 'Здоров'),
        ('часто_болею', 'Часто болею'),
        ('хронические_заболевания', 'Хронические заболевания'),
        ('инвалидность', 'Инвалидность'),
    ])
    diagnosis = models.TextField(_('Диагноз (шифруется)'), blank=True, null=True)
    diagnosis_scan = models.FileField(_('Скан диагноза'), upload_to='docs/health/', blank=True, null=True)
    oms_number = models.CharField(_('Номер полиса ОМС'), max_length=20, blank=True, null=True)
    oms_date = models.DateField(_('Дата выдачи ОМС'), blank=True, null=True)
    oms_issuer = models.CharField(_('Кем выдан ОМС'), max_length=255, blank=True, null=True)
    oms_scan = models.FileField(_('Скан полиса'), upload_to='docs/health/', blank=True, null=True)
    oms_absence_reason = models.TextField(_('Причина отсутствия полиса'), blank=True, null=True)

    class Meta:
        verbose_name = _('Здоровье')
        verbose_name_plural = _('Здоровье')
        app_label = 'core'

    def __str__(self):
        return f"Мед. карта #{self.id_health}"


class Military(models.Model):
    id_military = models.AutoField(_('ID ВУ'), primary_key=True)
    registration_number = models.CharField(_('Номер приписного'), max_length=50, blank=True, null=True)
    commissariat = models.CharField(_('Военкомат'), max_length=255, blank=True, null=True)
    issue_date = models.DateField(_('Дата выдачи'), blank=True, null=True)
    fitness_category = models.CharField(_('Категория годности'), max_length=10, choices=[
        ('А', 'А'), ('Б', 'Б'), ('В', 'В'), ('Г', 'Г'), ('Д', 'Д')
    ], blank=True, null=True)
    absence_reason = models.TextField(_('Причина отсутствия'), blank=True, null=True)
    file_path = models.FileField(_('Скан ВУ'), upload_to='docs/military/', blank=True, null=True)

    class Meta:
        verbose_name = _('Воинский учет')
        verbose_name_plural = _('Воинский учет')
        app_label = 'core'

    def __str__(self):
        return self.registration_number or f"ВУ #{self.id_military}"


class Family(models.Model):
    id_family = models.AutoField(_('ID семьи'), primary_key=True)
    minors_count = models.IntegerField(_('Кол-во несовершеннолетних'), blank=True, null=True)
    adults_count = models.IntegerField(_('Кол-во совершеннолетних'), blank=True, null=True)
    status = models.CharField(_('Статус семьи'), max_length=100, choices=[
        ('полная', 'Полная'), ('родители_в_разводе', 'Родители в разводе'),
        ('малообеспеченная', 'Малообеспеченная'), ('многодетная', 'Многодетная'),
        ('потеря_кормильца', 'Потеря кормильца'), ('мать_одиночка', 'Мать-одиночка'),
        ('отец_одиночка', 'Отец-одиночка'), ('ребенок_инвалид', 'Ребенок-инвалид'),
        ('ребенок_сирота', 'Ребенок-сирота'), ('под_опекой', 'Под опекой'),
        ('приёмная_семья', 'Приёмная семья'), ('повторный_брак', 'Повторный брак'),
    ])
    housing_type = models.CharField(_('Тип жилья'), max_length=100, choices=[
        ('в_собственном_жилье_с_родителями', 'В собственном жилье с родителями'),
        ('в_съёмном_жилье_с_родителями', 'В съёмном жилье с родителями'),
        ('отдельно_от_родителей', 'Отдельно от родителей'),
        ('другое', 'Другое'),
    ])
    fin_aid_ground = models.ForeignKey(FinancialAidGround, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Основание мат. помощи'))

    class Meta:
        verbose_name = _('Семья')
        verbose_name_plural = _('Семьи')
        app_label = 'core'

    def __str__(self):
        return f"Семья #{self.id_family}"


class FamilyMember(models.Model):
    id_member = models.AutoField(_('ID члена семьи'), primary_key=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, verbose_name=_('Семья'))
    relation = models.CharField(_('Степень родства'), max_length=100, choices=[
        ('мать', 'Мать'), ('отец', 'Отец'), ('брат', 'Брат'), ('сестра', 'Сестра'),
        ('опекун', 'Опекун'), ('мачеха', 'Мачеха'), ('отчим', 'Отчим'),
        ('бабушка', 'Бабушка'), ('дедушка', 'Дедушка'), ('другое', 'Другое'),
    ])
    full_name = models.CharField(_('ФИО'), max_length=255)
    birth_date = models.DateField(_('Дата рождения'), blank=True, null=True)
    education = models.CharField(_('Образование'), max_length=255, blank=True, null=True)
    workplace = models.CharField(_('Место работы'), max_length=255, blank=True, null=True)
    phone = models.CharField(_('Телефон'), max_length=20, blank=True, null=True)
    is_pensioner = models.BooleanField(_('Пенсионер'), default=False)
    is_svo = models.BooleanField(_('На СВО'), default=False)
    is_priority_contact = models.BooleanField(_('Приоритетный контакт'), default=False)

    class Meta:
        verbose_name = _('Член семьи')
        verbose_name_plural = _('Члены семьи')
        app_label = 'core'

    def __str__(self):
        return f"{self.relation}: {self.full_name}"


class Profile(models.Model):
    id_profile = models.AutoField(_('ID профиля'), primary_key=True)
    it_skills = models.JSONField(_('IT-навыки'), blank=True, null=True)
    programming_langs = models.TextField(_('Языки программирования'), blank=True, null=True)
    creative_skills = models.JSONField(_('Творческие навыки'), blank=True, null=True)
    school_participation = models.JSONField(_('Участие в школе'), blank=True, null=True)
    college_participation = models.JSONField(_('Участие в техникуме'), blank=True, null=True)
    achievements = models.JSONField(_('Достижения'), blank=True, null=True)
    hobbies = models.TextField(_('Хобби'), blank=True, null=True)
    extra_edu = models.TextField(_('Дополнительное образование'), blank=True, null=True)
    social_networks = models.JSONField(_('Соцсети'), blank=True, null=True)
    motivation_college = models.JSONField(_('Мотивация техникум'), blank=True, null=True)
    motivation_specialty = models.JSONField(_('Мотивация специальность'), blank=True, null=True)
    desired_participation = models.JSONField(_('Желаемое участие'), blank=True, null=True)
    foreign_langs = models.JSONField(_('Иностранные языки'), blank=True, null=True)
    drivers_license = models.JSONField(_('Водительские права'), blank=True, null=True)
    sports_ranks = models.TextField(_('Спортивные разряды'), blank=True, null=True)
    character_behavior = models.TextField(_('Характер и поведение'), blank=True, null=True)

    class Meta:
        verbose_name = _('Профиль студента')
        verbose_name_plural = _('Профили студентов')
        app_label = 'core'

    def __str__(self):
        return f"Профиль #{self.id_profile}"


class EducationInstitution(models.Model):
    id_institution = models.AutoField(_('ID учреждения'), primary_key=True)
    name = models.CharField(_('Наименование'), max_length=255)
    type = models.CharField(_('Тип'), max_length=100, choices=[
        ('общеобразовательная_средняя', 'Общеобразовательная средняя'),
        ('лицей', 'Лицей'),
        ('гимназия', 'Гимназия'),
        ('техникум', 'Техникум'),
        ('колледж', 'Колледж'),
        ('ПТУ', 'ПТУ'),
        ('другое', 'Другое'),
    ])
    profile = models.CharField(_('Профиль класса'), max_length=100, blank=True, null=True)
    graduation_date = models.DateField(_('Дата окончания'), blank=True, null=True)

    class Meta:
        verbose_name = _('Учебное заведение')
        verbose_name_plural = _('Учебные заведения')
        app_label = 'core'

    def __str__(self):
        return self.name


class Student(models.Model):
    snils = models.CharField(_('СНИЛС'), max_length=20, primary_key=True, help_text="Формат: XXX-XXX-XXX XX")
    snils_file = models.FileField(_('Скан СНИЛС'), upload_to='docs/students/', blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Пользователь'))
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name=_('Группа'))
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name=_('Приказ о зачислении'))
    birth_date = models.DateField(_('Дата рождения'))
    gender = models.CharField(_('Пол'), max_length=10, choices=[('мужской', 'Мужской'), ('женский', 'Женский')])
    birth_place = models.CharField(_('Место рождения'), max_length=255)
    phone = models.CharField(_('Телефон'), max_length=20)
    inn = models.CharField(_('ИНН'), max_length=12, blank=True, null=True)
    inn_file = models.FileField(_('Скан ИНН'), upload_to='docs/students/', blank=True, null=True)
    pd_consent = models.BooleanField(_('Согласие на ПДн'), default=False)
    pd_consent_date = models.DateField(_('Дата согласия'), blank=True, null=True)
    status = models.CharField(_('Статус обучения'), max_length=100, choices=[
        ('обучается (студент)', 'Обучается (студент)'),
        ('не завершил обучение: академический отпуск', 'Академический отпуск'),
        ('не завершил обучение: отчислен по собственному желанию', 'Отчислен по собственному желанию'),
        ('не завершил обучение: отчислен в связи с неуспеваемостью', 'Отчислен в связи с неуспеваемостью'),
        ('завершил обучение (выпускник)', 'Завершил обучение (выпускник)'),
    ])
    last_change = models.DateTimeField(_('Дата последнего изменения'), auto_now=True)
    
    passport = models.OneToOneField(Passport, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Паспорт'))
    health = models.OneToOneField(Health, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Здоровье'))
    military = models.OneToOneField(Military, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Воинский учет'))
    family = models.OneToOneField(Family, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Семья'))
    education = models.OneToOneField(EducationInstitution, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Учебное заведение'))
    profile = models.OneToOneField(Profile, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Профиль'))
    
    photo_path = models.CharField(_('Путь к фото СКУД'), max_length=255, blank=True, null=True)
    study_plan = models.CharField(_('Учебный план'), max_length=50, choices=[('стандартный', 'Стандартный'), ('иуп', 'ИУП')], default='стандартный')
    dual_edu = models.BooleanField(_('Дуальное обучение'), default=False)
    target_contract = models.ForeignKey('TargetContract', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Целевой договор'), related_name='students')

    class Meta:
        verbose_name = _('Студент')
        verbose_name_plural = _('Студенты')
        app_label = 'core'

    def __str__(self):
        name = f"{self.user.last_name} {self.user.first_name}" if self.user else "Без ФИО"
        return f"{name} ({self.snils})"


# ==============================================================================
# БЛОК 3: ТРУДОУСТРОЙСТВО И ПРАКТИКА
# ==============================================================================

class Industry(models.Model):
    id_industry = models.AutoField(_('ID отрасли'), primary_key=True)
    name = models.CharField(_('Название'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Отрасль')
        verbose_name_plural = _('Отрасли')
        app_label = 'core'

    def __str__(self):
        return self.name


class Country(models.Model):
    id_country = models.CharField(_('Код страны'), max_length=10, primary_key=True)
    name = models.CharField(_('Название'), max_length=100, unique=True)

    class Meta:
        verbose_name = _('Страна')
        verbose_name_plural = _('Страны')
        app_label = 'core'

    def __str__(self):
        return self.name


class Region(models.Model):
    id_region = models.AutoField(_('ID области'), primary_key=True)
    name = models.CharField(_('Название'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Область')
        verbose_name_plural = _('Области')
        app_label = 'core'

    def __str__(self):
        return self.name


class CityDistrict(models.Model):
    id_district = models.AutoField(_('ID округа'), primary_key=True)
    name = models.CharField(_('Название'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Городской округ')
        verbose_name_plural = _('Городские округа')
        app_label = 'core'

    def __str__(self):
        return self.name


class EmploymentType(models.Model):
    id_type = models.AutoField(_('ID формы'), primary_key=True)
    name = models.CharField(_('Название'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Форма занятости')
        verbose_name_plural = _('Формы занятости')
        app_label = 'core'

    def __str__(self):
        return self.name


class TargetContract(models.Model):
    id_contract = models.CharField(_('ID договора'), max_length=100, primary_key=True, help_text="Формат: №НОМЕР от ДД.ММ.ГГГГ")
    student = models.OneToOneField(Student, on_delete=models.CASCADE, verbose_name=_('Студент'))
    has_contract = models.BooleanField(_('Наличие договора'), default=False)
    format = models.CharField(_('Формат'), max_length=50, choices=[
        ('оформлен_на_рвр', 'Оформлен на РвР'),
        ('в_бумажном_виде', 'В бумажном виде'),
    ], blank=True, null=True)
    number = models.CharField(_('Номер'), max_length=50, blank=True, null=True)
    date = models.DateField(_('Дата'), blank=True, null=True)
    company_name = models.CharField(_('Предприятие'), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _('Целевой договор')
        verbose_name_plural = _('Целевые договоры')
        app_label = 'core'

    def __str__(self):
        return self.id_contract


class Organization(models.Model):
    inn = models.CharField(_('ИНН'), max_length=12, primary_key=True)
    legal_name = models.CharField(_('Юридическое название'), max_length=255)
    short_name = models.CharField(_('Сокращенное название'), max_length=255, blank=True, null=True)
    kpp = models.CharField(_('КПП'), max_length=9, blank=True, null=True)
    ogrn = models.CharField(_('ОГРН'), max_length=15, blank=True, null=True)
    rusprofile_link = models.URLField(_('Ссылка Rusprofile'), blank=True, null=True)
    index = models.CharField(_('Индекс'), max_length=10, blank=True, null=True)
    region = models.CharField(_('Субъект РФ'), max_length=100, blank=True, null=True)
    city = models.CharField(_('Населенный пункт'), max_length=100, blank=True, null=True)
    street = models.CharField(_('Улица'), max_length=100, blank=True, null=True)
    building = models.CharField(_('Дом'), max_length=50, blank=True, null=True)
    extra_info = models.CharField(_('Доп. информация'), max_length=255, blank=True, null=True)
    fact_address = models.CharField(_('Фактический адрес'), max_length=255, blank=True, null=True)
    
    director_name = models.CharField(_('ФИО директора'), max_length=255, blank=True, null=True)
    director_position = models.CharField(_('Должность директора'), max_length=100, blank=True, null=True)
    director_phone = models.CharField(_('Телефон директора'), max_length=20, blank=True, null=True)
    email = models.EmailField(_('Email организации'), blank=True, null=True)
    
    responsible_name = models.CharField(_('ФИО ответственного'), max_length=255, blank=True, null=True)
    responsible_position = models.CharField(_('Должность ответственного'), max_length=100, blank=True, null=True)
    responsible_phone = models.CharField(_('Телефон ответственного'), max_length=20, blank=True, null=True)
    
    mentor_name = models.CharField(_('ФИО наставника ОО'), max_length=255, blank=True, null=True)
    mentor_position = models.CharField(_('Должность наставника ОО'), max_length=100, blank=True, null=True)
    mentor_phone = models.CharField(_('Телефон наставника ОО'), max_length=20, blank=True, null=True)
    
    bank_name = models.CharField(_('Название банка'), max_length=255, blank=True, null=True)
    account = models.CharField(_('Расчетный счет'), max_length=50, blank=True, null=True)
    corr_account = models.CharField(_('Корр. счет'), max_length=50, blank=True, null=True)
    bik = models.CharField(_('БИК'), max_length=20, blank=True, null=True)
    basis = models.CharField(_('Основание действий'), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _('Организация')
        verbose_name_plural = _('Организации')
        app_label = 'core'

    def __str__(self):
        return self.short_name or self.legal_name


class Employment(models.Model):
    id_employment = models.AutoField(_('ID трудоустройства'), primary_key=True)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, verbose_name=_('Студент'))
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Организация'))
    employment_type = models.ForeignKey(EmploymentType, on_delete=models.PROTECT, verbose_name=_('Форма занятости'))
    is_cluster_partner = models.BooleanField(_('Труд. у партнера кластера'), default=False)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Отрасль'))
    city_district = models.ForeignKey(CityDistrict, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Городской округ'))
    is_by_profession = models.BooleanField(_('Трудоустройство по профессии'), default=False)
    position = models.CharField(_('Должность'), max_length=255, blank=True, null=True)
    update_date = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    scan_szv_td = models.FileField(_('Скан СЗВ-ТД'), upload_to='docs/employment/', blank=True, null=True)
    scan_self_employed = models.FileField(_('Скан самозанятости'), upload_to='docs/employment/', blank=True, null=True)
    scan_ip = models.FileField(_('Скан ИП'), upload_to='docs/employment/', blank=True, null=True)
    scan_self_employed_tax = models.FileField(_('Скан налогов самозанятого'), upload_to='docs/employment/', blank=True, null=True)

    class Meta:
        verbose_name = _('Трудоустройство')
        verbose_name_plural = _('Трудоустройства')
        app_label = 'core'

    def __str__(self):
        return f"Трудоустройство: {self.student}"


class PracticeOrder(models.Model):
    id_order = models.CharField(_('ID приказа практики'), max_length=100, primary_key=True, help_text="Формат: №НОМЕР от ДД.ММ.ГГГГ")
    number = models.CharField(_('Номер'), max_length=50)
    date = models.DateField(_('Дата'))
    start_date = models.DateField(_('Дата начала'))
    end_date = models.DateField(_('Дата окончания'))
    report_date = models.DateField(_('Дата сдачи отчета'), blank=True, null=True)
    type = models.CharField(_('Вид практики'), max_length=50, choices=[
        ('учебная', 'Учебная'),
        ('производственная', 'Производственная'),
        ('преддипломная', 'Преддипломная'),
    ])
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name=_('Группа'))
    file_path = models.FileField(_('Файл приказа'), upload_to='docs/practice_orders/', blank=True, null=True)

    class Meta:
        verbose_name = _('Приказ о практике')
        verbose_name_plural = _('Приказы о практике')
        app_label = 'core'

    def __str__(self):
        return self.id_order


class Module(models.Model):
    id_module = models.CharField(_('ID модуля'), max_length=100, primary_key=True, help_text="Формат: КОД_МОДУЛЯ_ГРУППА")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_('Группа'))
    code = models.CharField(_('Код модуля'), max_length=50)
    name = models.TextField(_('Название модуля'))

    class Meta:
        verbose_name = _('Модуль')
        verbose_name_plural = _('Модули')
        app_label = 'core'

    def __str__(self):
        return f"{self.code} ({self.group})"


class PracticeOrderModule(models.Model):
    order = models.ForeignKey(PracticeOrder, on_delete=models.CASCADE, verbose_name=_('Приказ практики'))
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name=_('Модуль'))

    class Meta:
        verbose_name = _('Модуль в приказе')
        verbose_name_plural = _('Модули в приказах')
        unique_together = ('order', 'module')
        app_label = 'core'

    def __str__(self):
        return f"{self.order} - {self.module}"


class StudentPracticePlace(models.Model):
    id_place = models.AutoField(_('ID места практики'), primary_key=True)
    order = models.ForeignKey(PracticeOrder, on_delete=models.PROTECT, verbose_name=_('Приказ практики'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('Студент'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name=_('Организация'))
    position = models.CharField(_('Должность студента'), max_length=100, blank=True, null=True)
    status = models.CharField(_('Статус'), max_length=50, choices=[
        ('назначен', 'Назначен'),
        ('проходит', 'Проходит'),
        ('завершил', 'Завершил'),
        ('не_назначен', 'Не назначен'),
        ('отчислен', 'Отчислен'),
    ], default='назначен')
    teacher1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='practice_teacher1', verbose_name=_('Руководитель 1'))
    teacher2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='practice_teacher2', verbose_name=_('Руководитель 2'))

    class Meta:
        verbose_name = _('Место практики студента')
        verbose_name_plural = _('Места практик студентов')
        app_label = 'core'

    def __str__(self):
        return f"{self.student} - {self.organization}"


class DocumentGenerationType(models.Model):
    code = models.CharField(_('Код'), max_length=100, primary_key=True)
    name = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'))
    template_path = models.CharField(_('Путь к шаблон DOCX'), max_length=255)

    class Meta:
        verbose_name = _('Тип документа для генерации')
        verbose_name_plural = _('Типы документов для генерации')
        app_label = 'core'

    def __str__(self):
        return self.name


# ==============================================================================
# БЛОК 4: ОТЧЕТЫ ПО ПРАКТИКЕ
# ==============================================================================

class PracticeTask(models.Model):
    id_task = models.AutoField(_('ID задания'), primary_key=True)
    practice_place = models.ForeignKey(StudentPracticePlace, on_delete=models.CASCADE, verbose_name=_('Место практики'))
    topic_number = models.CharField(_('Номер темы'), max_length=50, blank=True, null=True)
    topic_name = models.TextField(_('Название темы'))
    work_types = models.TextField(_('Виды работ'))
    competencies = models.TextField(_('Формируемые компетенции'))
    hours = models.IntegerField(_('Количество часов'))

    class Meta:
        verbose_name = _('Задание практики')
        verbose_name_plural = _('Задания практики')
        app_label = 'core'

    def __str__(self):
        return f"Задание {self.topic_number}: {self.topic_name}"


class PracticeDiary(models.Model):
    id_entry = models.AutoField(_('ID записи'), primary_key=True)
    practice_place = models.ForeignKey(StudentPracticePlace, on_delete=models.CASCADE, verbose_name=_('Место практики'))
    date = models.DateField(_('Дата'))
    work_content = models.TextField(_('Содержание работы'))
    hours = models.IntegerField(_('Количество часов'))
    is_approved_by_org = models.BooleanField(_('Отметка руководителя орг.'), default=False)

    class Meta:
        verbose_name = _('Запись дневника практики')
        verbose_name_plural = _('Дневник практики')
        ordering = ['date']
        app_label = 'core'

    def __str__(self):
        return f"{self.date}: {self.work_content[:50]}..."


class PracticeControlPoint(models.Model):
    id_point = models.AutoField(_('ID точки'), primary_key=True)
    practice_place = models.ForeignKey(StudentPracticePlace, on_delete=models.CASCADE, verbose_name=_('Место практики'))
    control_date = models.DateField(_('Дата контроля'))
    work_done = models.TextField(_('Выполненная работа'))
    is_signed_by_org = models.BooleanField(_('Подпись руководителя орг.'), default=False)

    class Meta:
        verbose_name = _('Контрольная точка')
        verbose_name_plural = _('Контрольные точки')
        app_label = 'core'

    def __str__(self):
        return f"Контроль {self.control_date}"


class PracticeAttestation(models.Model):
    id_attestation = models.AutoField(_('ID аттестации'), primary_key=True)
    practice_place = models.OneToOneField(StudentPracticePlace, on_delete=models.CASCADE, verbose_name=_('Место практики'))
    competencies_eval = models.JSONField(_('Оценка компетенций'), blank=True, null=True)
    characteristic_text = models.TextField(_('Текст характеристики'), blank=True, null=True)
    recommended_grade = models.CharField(_('Рекомендуемая оценка'), max_length=50, choices=[
        ('отлично', 'Отлично'),
        ('хорошо', 'Хорошо'),
        ('удовлетворительно', 'Удовлетворительно'),
        ('неудовлетворительно', 'Неудовлетворительно'),
    ], blank=True, null=True)
    fill_date = models.DateField(_('Дата заполнения'))

    class Meta:
        verbose_name = _('Аттестация практики')
        verbose_name_plural = _('Аттестации практики')
        app_label = 'core'

    def __str__(self):
        return f"Аттестация: {self.practice_place.student}"


# ==============================================================================
# БЛОК 5: ОЦЕНКИ, ЗАЧЕТКА, ПРОТОКОЛЫ
# ==============================================================================

class MCK(models.Model):
    id_mck = models.AutoField(_('ID МЦК'), primary_key=True)
    name = models.CharField(_('Наименование'), max_length=255)
    short_name = models.CharField(_('Сокращенное наименование'), max_length=100, blank=True, null=True)
    chairman = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Председатель'))

    class Meta:
        verbose_name = _('Методическая цикловая комиссия')
        verbose_name_plural = _('Методические цикловые комиссии')
        app_label = 'core'

    def __str__(self):
        return self.short_name or self.name


class DisciplineReference(models.Model):
    code = models.CharField(_('Код дисциплины'), max_length=50, primary_key=True)
    name = models.TextField(_('Наименование'))
    type = models.CharField(_('Тип'), max_length=100, choices=[
        ('общеобразовательный', 'Общеобразовательный'),
        ('общепрофессиональный', 'Общепрофессиональный'),
        ('профессиональный_модуль', 'Профессиональный модуль'),
        ('мдк', 'МДК'),
        ('практика', 'Практика'),
        ('гиа', 'ГИА'),
    ])

    class Meta:
        verbose_name = _('Справочник дисциплин')
        verbose_name_plural = _('Справочник дисциплин')
        app_label = 'core'

    def __str__(self):
        return f"{self.code} {self.name}"


class DisciplineInGroup(models.Model):
    id_record = models.AutoField(_('ID записи'), primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_('Группа'))
    discipline_ref = models.ForeignKey(DisciplineReference, on_delete=models.PROTECT, verbose_name=_('Дисциплина'))
    semester = models.IntegerField(_('Семестр'))
    assessment_form = models.CharField(_('Форма аттестации'), max_length=50, choices=[
        ('экзамен', 'Экзамен'),
        ('дифференцированный_зачет', 'Дифференцированный зачет'),
        ('зачет', 'Зачет'),
        ('курсовая_работа', 'Курсовая работа'),
    ])
    hours = models.IntegerField(_('Объем часов'), blank=True, null=True)
    mck = models.ForeignKey(MCK, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('МЦК'))

    class Meta:
        verbose_name = _('Дисциплина в группе')
        verbose_name_plural = _('Дисциплины в группе')
        app_label = 'core'

    def __str__(self):
        return f"{self.discipline_ref.code} ({self.group})"


# ==============================================================================
# РАСПИСАНИЕ АТТЕСТАЦИИ (с поддержкой нескольких преподавателей через M2M)
# ==============================================================================

class AssessmentTeacher(models.Model):
    """
    Промежуточная модель для связи расписания аттестации с преподавателями.
    Реализует Many-to-Many через 'through' с указанием роли (основной/со-преподаватель).
    """
    
    ROLE_CHOICES = [
        ('primary', 'Основной преподаватель'),
        ('co', 'Со-преподаватель'),
    ]
    
    id_assessment_teacher = models.AutoField(
        primary_key=True,
        verbose_name='ID записи'
    )
    
    schedule = models.ForeignKey(
        'AssessmentSchedule',
        on_delete=models.CASCADE,
        related_name='assessment_teachers',
        verbose_name='Запись расписания'
    )
    
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assessment_teaching',
        verbose_name='Преподаватель'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='primary',
        verbose_name='Роль'
    )
    
    class Meta:
        verbose_name = 'Преподаватель в расписании'
        verbose_name_plural = 'Преподаватели в расписании'
        unique_together = ('schedule', 'teacher')
        ordering = ['-role', 'teacher__last_name']
    
    def __str__(self):
        role_label = self.get_role_display()
        return f"{self.teacher} ({role_label})"


class AssessmentSchedule(models.Model):
    """
    Расписание аттестации (зачёты и экзамены).
    
    Поддерживает нескольких преподавателей через M2M с промежуточной моделью AssessmentTeacher.
    Один преподаватель назначается основным (role='primary'), остальные — со-преподавателями (role='co').
    """
    
    id_schedule = models.AutoField(
        primary_key=True,
        verbose_name='ID расписания'
    )
    
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name='assessments',
        verbose_name='Группа'
    )
    
    discipline_in_group = models.ForeignKey(
        'DisciplineInGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assessments',
        verbose_name='Дисциплина в группе'
    )
    
    date = models.DateField(verbose_name='Дата проведения')
    time = models.TimeField(null=True, blank=True, verbose_name='Время начала')
    
    room = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Аудитория'
    )
    
    # Many-to-Many через промежуточную модель AssessmentTeacher
    teachers = models.ManyToManyField(
        User,
        through='AssessmentTeacher',
        related_name='assessment_schedules',
        verbose_name='Преподаватели',
        help_text='Основной преподаватель и со-преподаватели'
    )
    
    retake_date = models.DateField(null=True, blank=True, verbose_name='Дата пересдачи')
    retake_time = models.TimeField(null=True, blank=True, verbose_name='Время пересдачи')
    
    class Meta:
        verbose_name = 'Запись расписания аттестации'
        verbose_name_plural = 'Расписание аттестации'
        ordering = ['date', 'time', 'group']
    
    def __str__(self):
        primary = self.get_primary_teacher()
        teacher_name = primary.get_full_name() if primary else '—'
        discipline = self.discipline_in_group.discipline_ref.name if self.discipline_in_group else '—'
        return f"{self.group} | {discipline} | {self.date} | {teacher_name}"
    
    def get_primary_teacher(self):
        """Возвращает основного преподавателя или None."""
        try:
            at = self.assessment_teachers.select_related('teacher').get(role='primary')
            return at.teacher
        except AssessmentTeacher.DoesNotExist:
            return None
    
    def get_co_teachers(self):
        """Возвращает QuerySet со-преподавателей."""
        return User.objects.filter(
            assessment_teaching__schedule=self,
            assessment_teaching__role='co'
        )
    
    def get_all_teachers(self):
        """Возвращает QuerySet всех преподавателей (основной + со-преподаватели)."""
        return User.objects.filter(assessment_teaching__schedule=self)
    
    def set_primary_teacher(self, user):
        """Устанавливает основного преподавателя (удаляя предыдущего)."""
        self.assessment_teachers.filter(role='primary').delete()
        if user:
            AssessmentTeacher.objects.create(
                schedule=self,
                teacher=user,
                role='primary'
            )
    
    def add_co_teacher(self, user):
        """Добавляет со-преподавателя."""
        AssessmentTeacher.objects.get_or_create(
            schedule=self,
            teacher=user,
            defaults={'role': 'co'}
        )


class Statement(models.Model):
    id_statement = models.AutoField(_('ID ведомости'), primary_key=True)
    number = models.CharField(_('Номер ведомости'), max_length=50, unique=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name=_('Группа'))
    discipline_in_group = models.ForeignKey(DisciplineInGroup, on_delete=models.PROTECT, verbose_name=_('Дисциплина'))
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('Преподаватель'))
    issue_date = models.DateField(_('Дата выдачи'))
    return_date = models.DateField(_('Дата возврата'), blank=True, null=True)
    status = models.CharField(_('Статус'), max_length=50, choices=[
        ('в_работе', 'В работе'),
        ('закрыта', 'Закрыта'),
        ('сдана_в_архив', 'Сдана в архив'),
    ], default='в_работе')

    class Meta:
        verbose_name = _('Ведомость')
        verbose_name_plural = _('Ведомости')
        app_label = 'core'

    def __str__(self):
        return f"Ведомость {self.number}"


class StatementGrade(models.Model):
    id_grade = models.AutoField(_('ID оценки'), primary_key=True)
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE, verbose_name=_('Ведомость'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('Студент'))
    grade = models.CharField(_('Оценка'), max_length=50, choices=[
        ('5 (отлично)', '5 (отлично)'),
        ('4 (хорошо)', '4 (хорошо)'),
        ('3 (удовлетворительно)', '3 (удовлетворительно)'),
        ('2 (неудовлетворительно)', '2 (неудовлетворительно)'),
        ('н/а (не допущен)', 'н/а (не допущен)'),
        ('зачтено', 'Зачтено'),
        ('не_зачтено', 'Не зачтено'),
    ], blank=True, null=True)
    date = models.DateField(_('Дата сдачи'), blank=True, null=True)
    is_retake = models.BooleanField(_('Является пересдачей'), default=False)

    class Meta:
        verbose_name = _('Оценка в ведомости')
        verbose_name_plural = _('Оценки в ведомости')
        app_label = 'core'

    def __str__(self):
        return f"{self.student} - {self.grade}"


class GEKProtocol(models.Model):
    id_protocol = models.AutoField(_('ID протокола'), primary_key=True)
    number = models.CharField(_('Номер протокола'), max_length=50)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name=_('Группа'))
    date = models.DateField(_('Дата проведения'))
    gia_type = models.CharField(_('Тип ГИА'), max_length=50, choices=[
        ('только_дэ', 'Только ДЭ'),
        ('только_диплом', 'Только диплом'),
        ('дэ_и_диплом', 'ДЭ и диплом'),
    ])
    chairman = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('Председатель'))

    class Meta:
        verbose_name = _('Протокол ГЭК')
        verbose_name_plural = _('Протоколы ГЭК')
        app_label = 'core'

    def __str__(self):
        return f"Протокол {self.number} ({self.group})"


class GEKMember(models.Model):
    protocol = models.ForeignKey(GEKProtocol, on_delete=models.CASCADE, verbose_name=_('Протокол'))
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('Пользователь'))
    role = models.CharField(_('Роль в комиссии'), max_length=50, choices=[
        ('зам_председателя', 'Зам. председателя'),
        ('член_комиссии', 'Член комиссии'),
        ('секретарь', 'Секретарь'),
    ])

    class Meta:
        verbose_name = _('Член ГЭК')
        verbose_name_plural = _('Члены ГЭК')
        unique_together = ('protocol', 'user')
        app_label = 'core'

    def __str__(self):
        return f"{self.user} - {self.role}"


class GIAResult(models.Model):
    id_result = models.AutoField(_('ID результата'), primary_key=True)
    protocol = models.ForeignKey(GEKProtocol, on_delete=models.CASCADE, verbose_name=_('Протокол'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('Студент'))
    de_score = models.IntegerField(_('Балл ДЭ'), blank=True, null=True)
    de_grade = models.CharField(_('Оценка ДЭ'), max_length=50, choices=[
        ('отлично', 'Отлично'), ('хорошо', 'Хорошо'), ('удовл.', 'Удовлетворительно'), ('неуд.', 'Неудовлетворительно')
    ], blank=True, null=True)
    diploma_topic = models.TextField(_('Тема диплома'), blank=True, null=True)
    diploma_supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_diplomas', verbose_name=_('Руководитель диплома'))
    diploma_grade = models.CharField(_('Оценка диплома'), max_length=50, choices=[
        ('отлично', 'Отлично'), ('хорошо', 'Хорошо'), ('удовл.', 'Удовлетворительно'), ('неуд.', 'Неудовлетворительно')
    ], blank=True, null=True)
    final_gia_grade = models.CharField(_('Итоговая оценка ГИА'), max_length=50, choices=[
        ('отлично', 'Отлично'), ('хорошо', 'Хорошо'), ('удовл.', 'Удовлетворительно'), ('неуд.', 'Неудовлетворительно')
    ])

    class Meta:
        verbose_name = _('Результат ГИА')
        verbose_name_plural = _('Результаты ГИА')
        app_label = 'core'

    def __str__(self):
        return f"ГИА: {self.student} - {self.final_gia_grade}"


class GIADefenseQuestion(models.Model):
    id_question = models.AutoField(_('ID вопроса'), primary_key=True)
    gia_result = models.ForeignKey(GIAResult, on_delete=models.CASCADE, verbose_name=_('Результат ГИА'))
    question_number = models.IntegerField(_('Номер вопроса'))
    question_text = models.TextField(_('Текст вопроса'))
    expert = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('Эксперт'))
    student_answer = models.TextField(_('Ответ студента'), blank=True, null=True)

    class Meta:
        verbose_name = _('Вопрос на защите')
        verbose_name_plural = _('Вопросы на защите')
        app_label = 'core'

    def __str__(self):
        return f"Вопрос {self.question_number} для {self.gia_result.student}"


class AttendanceTable(models.Model):
    id_table = models.AutoField(_('ID табеля'), primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_('Группа'))
    month = models.IntegerField(_('Месяц'))
    year = models.IntegerField(_('Год'))
    curator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('Куратор'))

    class Meta:
        verbose_name = _('Табель посещаемости')
        verbose_name_plural = _('Табели посещаемости')
        unique_together = ('group', 'month', 'year')
        app_label = 'core'

    def __str__(self):
        return f"Табель: {self.group} ({self.month}/{self.year})"


class AttendanceTableRow(models.Model):
    id_row = models.AutoField(_('ID строки'), primary_key=True)
    table = models.ForeignKey(AttendanceTable, on_delete=models.CASCADE, verbose_name=_('Табель'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('Студент'))
    study_days = models.IntegerField(_('Учебные дни'), default=0)
    sick_leave = models.IntegerField(_('Больничный'), default=0)
    practice = models.IntegerField(_('Практика'), default=0)
    truancy = models.IntegerField(_('Прогулы'), default=0)

    class Meta:
        verbose_name = _('Строка табеля')
        verbose_name_plural = _('Строки табеля')
        app_label = 'core'

    def __str__(self):
        return f"{self.student} в табеле {self.table}"
