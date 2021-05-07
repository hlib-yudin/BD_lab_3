# BD_lab_3
# Веб-додаток "Replay Project" (музичний плеєр)
Комп'ютерний практикум з баз даних №3  
Виконав: Юдін Гліб, КМ-82  
Для тестування роботи додатка можна скористатись mp3-файлами з папки *test_music_files*.

-----------------------------------
# Цілі комп'ютерного практикуму та як вони виконані:
## 1. Навчитись використовувати ОРМ для роботи з даними
### 1.1. Організація CRUD-операцій:
* CREATE -- створення нового користувача, завантаження пісні (створення нової пісні, виконавця, альбому), створення плейлісту.
* READ -- прослуховування пісень (як завантажених самостійно, так і завантажених іншими користувачами), перегляд вмісту альбому/плейліста.
* UPDATE -- оновлення інформації про пісню, операції над плейлістом (наприклад, зробити його приватним).
* DELETE -- видалення пісні, якщо її завантажив поточний користувач (зокрема виконавця й альбому), плейліста.

### 1.2. Робота з сутностями, що містять вкладені колекції інших сутностей: 
* сутність "Користувач" містить сутність "Пісня".
* "Виконавець" містить "Пісні" та "Альбоми".
* "Альбом" містить "Пісні".
* "Плейліст" містить "Пісні", так само як і "Пісня" містить "Плейлісти", в які вона додана (зв'язок багато-до-багатьох).


## 2. Отримати навички роботи з веб-фреймворками
Організація бізнес-логіки на сервері -- файл app.py містить усю бізнес-логіку, що включає: 
* завантаження пісні на сервер
* пошук пісень, виконавців, альбомів, плейлістів за запитом
* редагування даних про пісню
* створення плейліста і додавання пісні до нього
* можливість зробити плейліст приватним чи публічним
* видалення пісні з плейліста, видалення самої пісні (якщо її завантажив поточний користувач) і самого плейліста (якщо його створив поточний користувач)
* реєстрація й авторизація користувачів
* автоматичне створення плейліста "Улюблене"

Побудова веб-інтерфейсу для відображення списків сутностей та CRUD-операцій -- користувач може переглянути список пісень, які він завантажив або які відповідають певному пошуковому запиту, вміст плейліста чи альбома. Веб-інтерфейс реалізовано за допомогою Flask.


## 3.Отримати навички розбиття системи на слої
Система складається з чотирьох слоїв:
* database layer -- БД Postresql.
* persistence layer -- файл persistence_layer.py, відповідає за безпосередній зв'язок з БД.
* business layer -- файл app.py, містить усю бізнес-логіку.
* presentation layer -- html-файли, які і складають користувацький інтерфейс.

## 4. Навчитись розгортати систему на хмарному хостингу
Систему розгорнуто на хмарному хостингу Heroku: https://replay-project.herokuapp.com.

## 5. Розвинути навички моделювання даних, створення ERD та проєктуванням БД
Усе це було виконано при проєктуванні, створенні та розгортанні веб-додатку.

--------------------------
# Інструкція з розгортання
1. У папці з проєктом ініціалізувати git-репозиторій
2. Увійти в Heroku-акаунт (через heroku login).
3. Додати зміни, закомітити та задеплоїти (git add .; git commit -am "some message"; git push heroku master)

-------------------------
ERD-діаграма міститься у файлі ERD.png.
