# MultivectorFuzz

**MultivectorFuzz v1.1** is a semi-automatic multi-vector fuzzing utility for penetration testing.

## Features

- Raw HTTP request injection
- Payloads substitution in multiple FUZZ points
- Support for custom payloads via file or inline
- Response time, status code, and content length analysis
- Ideal request comparison baseline
- Timeout detection and colored output for anomalies
- HTTP/2 support (auto-detected per request)

## Usage

1. Edit the `raw` variable in `fuzzme.py` (this is your raw HTTP request).
2. Add your payloads:
   - Inline: using the `payloads` variable in the script
   - Or via external file: `payloads.txt`
   - Inline payloads override the file if both are present.
3. Run the script:

```bash
python3 fuzzme.py
```

After execution:
- The baseline (ideal) request will be sent first.
- All fuzzed requests will be executed.
- Each result is printed with HTTP status, length, and response time.
- Time-based injection candidates and anomalies are color-highlighted.

## Encoding Modes

You can control payload encoding via this line in the script:

```python
payloads_codes = _payloads_codes(payloads_baypas, "none", debug=0)
```

Available modes:
- `"url"` – percent encoding (`%`)
- `"url+"` – plus for space (`+`)
- `"urlen"` – form encoding (as in POST forms)
- `"none"` – no encoding (raw)

## License

MIT License

---

## MultivectorFuzz (Русская версия)

_Двуязычная документация: EN / RU_

**MultivectorFuzz v1.1** — полуавтоматический мультивекторный FUZZ-сканер для задач пентестинга.

## Возможности

- Инъекция в «сырые» HTTP-запросы  
- Подстановка пейлоадов в несколько FUZZ-точек  
- Поддержка пользовательских пейлоадов (через файл или inline)  
- Анализ времени отклика, кода ответа и длины контента  
- Сравнение с эталонным запросом (baseline)  
- Обработка таймаутов и цветной вывод в терминал  
- Поддержка HTTP/2 (определяется автоматически)

## Использование

1. Отредактируйте переменную `raw` в `fuzzme.py` — это ваш исходный HTTP-запрос.  
2. Добавьте пейлоады:
   - Внутри скрипта (inline) — переменная `payloads`
   - Или через внешний файл `payloads.txt`
   - Inline имеет приоритет, если заданы оба варианта.
3. Запустите скрипт:

```bash
python3 fuzzme.py
```

После запуска:
- Сначала отправляется эталонный запрос (без FUZZ).
- Затем исполняются все сгенерированные fuzz-запросы.
- Вывод включает код ответа, длину и время.
- Потенциальные time-based уязвимости и аномалии подсвечиваются цветом.

## Режимы кодирования

Режим задаётся в строке:

```python
payloads_codes = _payloads_codes(payloads_baypas, "none", debug=0)
```

Поддерживаются:
- `"url"` — percent-кодирование (`%`)  
- `"url+"` — пробел как `+`  
- `"urlen"` — форма x-www-form-urlencoded  
- `"none"` — без кодирования

## Лицензия

MIT License
