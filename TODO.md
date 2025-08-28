# TODO — MultivectorFuzz
*(English version below, Russian version after)*

## Implemented features
- [x] Raw HTTP request parsing (method, URL, headers, cookies, body, HTTP version)
- [x] Multi-point FUZZ marker detection and template generation
- [x] Payload injection into all FUZZ points
- [x] Request preparation into structured objects (HTTPRequest class)
- [x] Sending requests with full control (headers, cookies, data, http/2 support)
- [x] Baseline request execution ("ideal request")
- [x] Measurement of response time, length, and status code
- [x] Timeout handling (configurable, default 10s)
- [x] Highlighting anomalies (status/length/time differences) in terminal with colors
- [x] Time-based SQLi detection (flag when response time ≈ baseline_time)
- [x] Unified output format in terminal

## Known bugs
- [x] Payloads inside the `Cookie:` header do not work (cookies are excluded when building requests).
  - Fix planned for version v1.1

## Planned features
- [ ] Add command-line argument support (via argparse)
- [ ] Add encoding mode selection via flag
- [ ] Add support for WAF bypass techniques (encoding, obfuscation, etc.)
- [ ] Add CSV/JSON export of results for later analysis
- [ ] Add parallel execution for faster fuzzing
- [ ] Add customizable baseline detection (dynamic learning instead of static 5s)


---

## Реализованные функции
- [x] Парсинг raw HTTP-запроса (метод, URL, заголовки, куки, тело, версия HTTP)
- [x] Авто-определение нескольких FUZZ-точек и генерация шаблонов
- [x] Подстановка пейлоадов во все FUZZ-точки
- [x] Подготовка запросов в структурированные объекты (класс HTTPRequest)
- [x] Отправка запросов с полной поддержкой (заголовки, куки, тело, http/2)
- [x] Эталонный запрос (ideal request)
- [x] Замер времени ответа, длины и кода
- [x] Обработка таймаута (по умолчанию 10 сек)
- [x] Подсветка аномалий (код/длина/время) в терминале цветами
- [x] Определение time-based SQLi (флаг при совпадении времени с baseline_time)
- [x] Единый формат вывода в терминале

## Известные ошибки
- [x] Пейлоады внутри заголовка `Cookie:` не работают (куки исключаются при построении запросов).
  - Исправление запланировано в версии v1.1

## Запланированные функции
- [ ] Добавить поддержку аргументов командной строки (через argparse)
- [ ] Добавить выбор режима кодирования через флаг
- [ ] Добавить поддержку техник обхода WAF (кодирование, обфускация и т.д.)
- [ ] Добавить экспорт результатов в CSV/JSON для последующего анализа
- [ ] Добавить параллельное выполнение для ускорения фаза
- [ ] Добавить динамическое определение baseline (а не фиксированные 5 секунд)

