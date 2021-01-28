# lkfm

Программа для управления аудиокнигами на картах памяти в формате LKF.

Для корректной работы требуется установка программы unrar или p7zip
    `apt install unrar`

При работе нужно сначала перейти в каталог примонтированной карты и зафиксировать целевой каталог командой 
    `lkfm set-work-dir`
либо указать целевой каталог аргументом командной строки
    `lkfm set-work-dir /media/sd-card/`

настройки сохраняются в /home/%user%/.local/share/lkfm.conf

```
lkfm [-h, --help] действие [файл, ...]

-h, --help - Вывести справку

действие - Доступны действия: list, add, delete, clear, work-dir, clear-config:
help, h            - Вывести справку;
list, l            - Вывести список книг на карте;
add, a             - Добавить книгу на карту;
delete, d          - Удалить книгу с карты;
pack, p            - Упаковать книгу с карты
clear, c           - Очистить карту от не до конца удалённых книг;
set-work-dir, sd   - Установить целевой каталог для записи книг;
unset-work-dir, ud - Очистить настройки;

файл - Файл книги

© ptah_alexs 2020. Автор программы, как всегда, не несет никакой ответственности ни за что.
```