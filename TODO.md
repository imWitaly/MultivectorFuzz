# TODO — MultivectorFuzz

## Known bugs
- [ ] Payloads inside the `Cookie:` header do not work (cookies are excluded when building requests).
  - Fix planned for version v1.1

## Planned features
- [ ] Add command-line argument support (via argparse)
- [ ] Add encoding mode selection via flag
- [x] Auto-detection of multiple FUZZ points — already implemented
- [ ] Add support for WAF bypass techniques (encoding, obfuscation, etc.)

