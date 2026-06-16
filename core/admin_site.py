from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    """Кастомная админка с группировкой моделей по 8 блокам."""
    site_header = 'Люберецкий техникум — Администрирование'
    site_title = 'Портал техникума'
    index_title = 'Панель управления'

    def get_app_list(self, request, app_label=None):
        """Переопределяем стандартный метод для группировки моделей."""
        if app_label:
            return super().get_app_list(request, app_label)

        app_list = super().get_app_list(request)

        # Находим приложение 'core' и остальные
        core_app = None
        other_apps = []
        for app in app_list:
            if app['app_label'] == 'core':
                core_app = app
            else:
                other_apps.append(app)

        if not core_app:
            return app_list

        # Определяем 8 групп и модели в каждой
        groups = {
            '📚 ГРУППА 1: СПРАВОЧНИКИ': [
                'Role', 'Campus', 'Specialty', 'DocumentType', 'Country',
                'Region', 'CityDistrict', 'Industry', 'EmploymentType',
                'FinancialAidGround', 'Setting', 'DocumentGenerationType',
                'DisciplineReference',
            ],
            '👥 ГРУППА 2: ПОЛЬЗОВАТЕЛИ И БАЗОВЫЕ СУЩНОСТИ': [
                'User', 'UserRole', 'Qualification', 'Order', 'MCK',
            ],
            '🎓 ГРУППА 3: ГРУППЫ И ДИСЦИПЛИНЫ': [
                'Group', 'DisciplineInGroup', 'AssessmentSchedule',
            ],
            '👨 ГРУППА 4: СТУДЕНТЫ И ИХ ДАННЫЕ': [
                'Passport', 'Health', 'Military', 'Family', 'FamilyMember',
                'Profile', 'EducationInstitution', 'Student',
            ],
            '💼 ГРУППА 5: ТРУДОУСТРОЙСТВО И ОРГАНИЗАЦИИ': [
                'Organization', 'Employment', 'TargetContract',
            ],
            '🏢 ГРУППА 6: ПРАКТИКА': [
                'PracticeOrder', 'Module', 'PracticeOrderModule',
                'StudentPracticePlace', 'PracticeTask', 'PracticeDiary',
                'PracticeControlPoint', 'PracticeAttestation',
            ],
            '📊 ГРУППА 7: ОЦЕНКИ И АТТЕСТАЦИЯ': [
                'Statement', 'StatementGrade', 'GEKProtocol', 'GEKMember',
                'GIAResult', 'GIADefenseQuestion',
            ],
            '📅 ГРУППА 8: ПОСЕЩАЕМОСТЬ': [
                'AttendanceTable', 'AttendanceTableRow',
            ],
        }

        # Создаём словарь моделей по имени класса
        models_by_name = {m['object_name']: m for m in core_app['models']}

        # Формируем новые группы
        new_apps = []
        for group_name, model_names in groups.items():
            group_models = []
            for model_name in model_names:
                if model_name in models_by_name:
                    group_models.append(models_by_name[model_name])

            if group_models:
                new_apps.append({
                    'name': group_name,
                    'app_label': core_app['app_label'],
                    'app_url': core_app['app_url'],
                    'has_module_perms': core_app['has_module_perms'],
                    'models': group_models,
                })

        # Добавляем остальные приложения (auth, sessions и т.д.)
        new_apps.extend(other_apps)

        return new_apps
