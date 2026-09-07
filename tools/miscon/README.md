# miscon-tools

Command-line tooling for Open Misconceptions. Python 3.10+,
`jsonschema` is the only dependency.

```sh
pip install -e tools/miscon
miscon validate records/          # schema + cross-record checks; non-zero exit on error
miscon index                      # regenerate records/INDEX.md
miscon export case|jsonl|csv|all  # write dist/
miscon build-site                 # write site/ (static HTML + JSON)
```

Run the tests from the repo root with `python -m unittest discover -s tools/tests`.
