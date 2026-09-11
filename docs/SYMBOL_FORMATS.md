# Symbol-file formats the bridge understands

## `splat`

```
FunctionName = 0x80072534; // type:func
some_data_thing = 0x80089f00; // type:data
```

One symbol per line, `NAME = 0xADDR;`, an optional `// type:...` comment.
Only lines with `type:func` are treated as function entries -- everything
else is parsed but ignored (kept for forward compatibility, e.g. a future
`type:data` pass for typed globals).

This is what `khasinski/parasite-eve-decomp` uses
(`configs/USA/sym.main.txt`, `configs/USA/overlays/sym.*.txt`), and it's the
same convention the wider splat/n64splat-family of decompilation tooling
produces, so it's a reasonable default to expect from other PS1 decomps too
-- check before assuming, though; verify the actual output of your game's
disassembly config.

## Adding another format

See **Adding a symbol format** in `ADDING_A_GAME.md`. The engine only needs
`(name, address, is_function)` tuples out of whatever format your decomp
uses -- the rest of the pipeline (filtering, overrides, output) doesn't
care how you got there.
