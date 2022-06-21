# Лабораторный стенд "Изучение свойств терморегуляторов "ТРМ"

Последняя версия исходного кода находится [здесь](https://github.com/Marik28/dissertation)

## Установка и запуск

Версия python >= 3.7

Необходимые параметры конфигурации хранятся в .env (подробнее об используемых
параметрах можно узнать в `src/dissertation_gui/settings.py`):

`$ cp .env.example .env`

Установка всех необходимых зависимостей

`$ make install`

Создать БД:

`$ make fill-database`

Сгенерировать таблицы с характеристиками датчиков (будут храниться
в `data/dataframes`):

`$ make generate-dfs`

Запуск десктопного приложения:

`$ make run-gui`

## Полезная информация

Запуск скриптов для создания БД, генерации таблиц с кодами и тестирования
можно просмотреть в `Makefile`

В директории `data` хранятся различные таблицы с характеристиками и диаграммы

В директории `src/notebooks` находятся блокноты jupyter notebook c различными
расчетами

## Переключения реле для симуляции типов датчиков:

### Термометры сопротивления

- K1 -
- K2 -
- K3 on
- K4 off

### Термопары

- K1 on
- K2
    - on для отрицательного
    - off для положительного
- K3 off
- K4 on

### Датчики с УВС

- K1 off
- K2
    - on для отрицательного
    - off для положительного
- K3 off
- K4 on
