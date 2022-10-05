# crontab_updater

Редактор crontab

Этот скрипт позволяет редактировать и делать бэкапы кронтабов, запускающих скрипты на Питоне при помощи класса CrontabUpdater и аргументов командной строки.
Названия бэкапов имеют вид à la crontabs/crontab20221005135833518552, где: 
- crontabs - название директории, которое задается именованным аргументом класса CrontabUpdater 'dirname';
- crontab - префикс названия файла, который задается аргументом класса CrontabUpdater 'prefix';
- цифры после префикса - преобразованные дата и время создания бэкапа.

Сохраняются не более filelim (именованный аргумент класса CrontabUpdater, 10 по умолчанию) бэкапов. Бэкап происходит после всех операций.

В файле vars.py хранится переменная вида 
"{timelet} /path_to_my_virtual_environment/bin/python path/{proj}/{script}.py > path/{proj}/{script}.log 2> path/{proj}/{script}.err\n",
при форматировании которой получается кронтаб.


Примеры использования опций:
- 'python crontab_updater.py' печатает инструкцию;
- 'python crontab_updater.py restore' восстанавливает crontabs из последнего бэкапа;
- 'python crontab_updater.py add "0 9 * * *" my_dir upd_launch' добавляет новый кронтаб: скрипт my_dir/upd_launch.py будет запускаться еждневно в 9 утра;
- 'python crontab_updater.py del my_dir upd_launch' или 'python crontab_updater.py del "0 9 * * *" my_dir upd_launch' удаляет кронтаб с идентификатором по директории, названию скрипта либо времени запуска, директории и названию скрипта;
- 'python crontab_updater.py dump' бэкапит текущие кронтабы;
- 'python crontab_updater.py sort' сортирует кронтабы.
