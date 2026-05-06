# edl-parse

A lightweight parser and converter for EDL (Edit Decision List) files to JSON for pipeline integration.

---

## Installation

```bash
pip install edl-parse
```

---

## Usage

```python
from edl_parse import EDLParser

parser = EDLParser()
result = parser.parse("my_edit.edl")

# Convert to JSON
import json
print(json.dumps(result.to_dict(), indent=2))
```

You can also use the CLI:

```bash
edl-parse input.edl --output output.json
```

**Example output:**

```json
{
  "title": "MY_EDIT",
  "events": [
    {
      "event": "001",
      "reel": "AX",
      "track": "V",
      "transition": "C",
      "source_in": "01:00:00:00",
      "source_out": "01:00:05:12",
      "record_in": "00:00:00:00",
      "record_out": "00:00:05:12"
    }
  ]
}
```

---

## Supported Formats

- CMX 3600 EDL
- Final Cut Pro XML export
- Avid Log Exchange (ALE)

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the [MIT License](LICENSE).