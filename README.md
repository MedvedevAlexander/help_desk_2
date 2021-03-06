# help_desk_2

Исправленная версия проекта help_desk.

Было принято решение переписать проект **help_desk**, т.к. первоначально в нем была заложена неправильная архитектура:
* Чрезмереное дробление близких функционально участков кода на несколько, что в итоге привело к нарушению принципа DRY
* Нецелесообразность разнесения функций, имеющих общее предназначение, в разные приложения. Как итог сложности в понимании кода, нелогичность некоторых решений.
* Использование негибкие поля моделей из-за чего данные модели было неудобно повторно использовать.
* Отказ от использования библиотеки service_objects.services, т.к. ее использование приводило к появлению дополнительных SQL запросов, что негативно сказывалось на производительности БД

###Что было изменено при переносе изменении первой версии приложения:
* Изменены классы `CheckTicketViewPermissions`, `CheckFileDownloadPermissions` из модуля `main/services.py`.
* Изменения модели `File`:
    * Удалены поля `comment`, `ticket`
    * Заменены поля  `comment`, `ticket` на `content_type`, `object_id`, `content_object` для создания полиморфных связей с другими моделями.
    * Изменен метод `def get_file_path` с учетом применения полиморфных связей.
* Оптимизация работы с БД благодаря применению в запросах методов `select_related` и `prefetch_related`.
* Объединение функционала всех приложений (`accounts`, `tickets`, `help_desk`) в одно `main`.
* Изменение маршрутизации `urls.py`
* Мелкие изменения в шаблонах
* Устранение ошибок в работе пагинатора на главной странице
* Удаление путей из `check_file_permissions` в модуле `views.py`, использование вместо них переменных среды окружения.
* Добавлено описание принципа работы самописной системы разграничения доступа к файлам, тикетам в корень проекта в файл `docs.md`.
* Добавлено описание порядка разворачивания проекта с нуля `REAME.MD`.
* Изменены пути по умолчанию для сохранения файлов, загруженных пользователем. Теперь файлы хранятся в корне проекта в директории `/data`
* Добавлен файл `requirement.txt` для быстрой установки всех зависимостей.
* Множество других мелких изменений.

Для запуска проекта требуется:
1. Скопировать репозиторий с проектом
2. Установить в проект все зависимости из файла requirements.txt
`pip install -r requirements.txt`
3. Разместить в пакете конфигурации, рядом с файлом `settings.py` файл с переменными среды окружения `.env`. Пример файла с переменными среды окружения имеется в корне проекта.
4. Сконфигурировать nginx для работы django-sendfile2, для отдачи статического контента. Пример конфигурации в корне GIT проекта, в файле nginx.conf:
4.1. Создать директиву для загрузки главной страницы.
4.2. Создать директиву для загрузки статических файлов.
   
4.3. Создать директиву для хранения файлов, загруженных пользователями, работы приложения `django-sendfile2`.
5. Через интерфейс администратора добавить следующие записи в БД:
- Категории заявок (разделы заявок по теме)
- Желаемые статусы заявок (Открыта, в работе и т.д.)
- Приоритеты заявок (Высокий, средний, низкий)
- Пользователей - администраторов разделов. Возможно добавлении учетных записей обычных пользователей (предусмотрена страница регистрации пользователя).
6. Для пользователей - администраторов разделов через административный интерфейс требуется назначить права доступа к разделам, находящимся в зоне их ответственности.
Права доступа назначаются путем помещения пользователя в группу с codename = <имя раздела>_admins. Группы пользователей создаются автоматически при создании категории.
   
7. Осуществить копирование статических файлов из директорий приложений в директорию, обслуживаемую nginx, выполнив команду:
```shell
python manage.py collectstatic
```


Текст ниже не актуален. Еще раз проверить и удалить


Какие записи в таблицах БД требуется создать для успешной работы приложения:
1. django.contrib.auth.models.User
2. TicketPriority
3. TicketCategory
4. TicketStatus
5. Права доступа:
Подумать на добавлением сигнала, который бы после создания новой категории, создавал соответствующие группы 
   пользователей и права доступа.
5.1. Создать нужные права доступа (content_type используем для модели Ticket):
    1) codename = 'full_access'
    2) codename = 'can_view_название_категории', например can_view_ca
    
5.2. Создать нужные группы пользователей:
    1) name = 'root_users'
    2) name = 'название_категории_admins', например ca_admins
5.3. Добавить пользователей в указанные группы в соответствии с их правами

