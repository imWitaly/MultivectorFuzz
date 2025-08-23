# MultivectorFuzz

**MultivectorFuzz v1.0** is a semi-automatic multi-vector fuzzing utility for penetration testing.

## Features

- Raw HTTP request injection
- Payloads substitution in multiple FUZZ points
- Support for custom payloads via file or inline
- Response time, status code, and content length analysis
- Ideal request comparison baseline

## Usage

1. Edit `raw_request` variable in `fuzzme.py`.
2. Add your payloads either in the `payloads` variable or in a file named `payloads.txt`.
   - If the inline variable is set, it takes priority.
3. Run the script:

```bash
python3 fuzzme.py
```

## Encoding Modes

Supports:
- `url` (percent-encoding)
- `url+` (space as `+`)
- `urlen` (form encoding)
- `none` (raw)

## License

MIT License
