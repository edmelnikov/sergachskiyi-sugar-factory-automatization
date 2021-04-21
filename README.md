# sergachskiyi-sugar-factory-automatization
## Проект "Автоматизированная система планирования раздачи топлива для рабочей техники"

Инструкция для корректного отображения техники на карте:
* cd <какой-то путь>\sergachskiyi-sugar-factory-automatization
* python -m http.server
* в браузере открыть http://localhost:8000/Map.html

Проблемы:
* В Хроме карта не реагирует на изменение kml файла, однако Microsoft Edge работает нормально (судя по логам сервера, гугл не шлет запрос GET /vehicles_and_polygons.kml HTTP/1.1, а Microsoft Edge шлет)
* Чтобы увидеть обновленную карту, нужно вручную обновлять страницу (Microsoft Edge) 
