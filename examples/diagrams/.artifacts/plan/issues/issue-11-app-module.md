# issue-11-app-module: Implement application orchestration layer

## Description
Create the high-level orchestration layer that coordinates the full pipeline from file I/O through parsing, validation, layout, and rendering. The App struct provides three public methods (compile, preview, validate) that CLI commands will invoke, handling all error propagation and file operations.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-diagrams/.artifacts/plan/architecture.md` Section "Component 9: Application Layer" for:
- App struct with compile(), preview(), validate() method signatures
- Internal parse_source() helper for lexer + parser coordination
- File I/O helper patterns (read_file, write_file)
- Error conversion from std::io::Error to DiagramError::Io

## Interface Contracts

```rust
pub struct App;
impl App {
    pub fn compile<P: AsRef<Path>>(input_path: P, output_path: P) -> Result<()>;
    pub fn preview<P: AsRef<Path>>(input_path: P) -> Result<String>;
    pub fn validate<P: AsRef<Path>>(input_path: P) -> Result<()>;
}
```

- **Implements**: Complete pipeline orchestration (read → lex → parse → validate → layout → render → write)
- **Exports**: App struct with three public methods for CLI consumption
- **Consumes**: Lexer, Parser, Validator, LayoutEngine, SvgRenderer, AsciiRenderer, DiagramError types
- **Consumed by**: cli-module (main.rs dispatches to App methods)

## Isolation Context
- **Available**: All prior-level modules (lexer, parser, validator, layout, svg-renderer, ascii-renderer, error, types)
- **NOT available**: cli-module (same level, built in parallel)
- **Source of truth**: Architecture document Section "Component 9: Application Layer"

## Files
- **Create**: `src/app.rs`
- **Modify**: `src/main.rs` (add `mod app;` declaration only)

## Dependencies
- issue-03-error-module (provides: DiagramError, Result<T> type alias)
- issue-04-lexer-module (provides: Lexer::new(), tokenize())
- issue-05-parser-module (provides: Parser::new(), parse())
- issue-06-validator-module (provides: Validator::validate())
- issue-07-layout-module (provides: LayoutEngine::layout())
- issue-09-svg-renderer (provides: SvgRenderer::render())
- issue-10-ascii-renderer (provides: AsciiRenderer::render())

## Provides
- App::compile() for DSL → SVG file generation
- App::preview() for DSL → ASCII string preview
- App::validate() for syntax/semantic checking
- Complete error handling with descriptive messages for file operations

## Acceptance Criteria
- [ ] src/app.rs exists and compiles without warnings
- [ ] compile() reads DSL file, generates SVG, writes output file successfully
- [ ] preview() reads DSL file, returns ASCII string
- [ ] validate() reads DSL file, validates, returns Ok(()) or error
- [ ] All methods return Result<_, DiagramError> for error propagation
- [ ] File read errors convert to DiagramError::Io with descriptive messages
- [ ] File write errors convert to DiagramError::Io with descriptive messages
- [ ] Pipeline chains correctly: read → lex → parse → validate → layout → render → write
- [ ] Internal parse_source() helper combines Lexer and Parser steps

## Testing Strategy

### Test Files
- `src/app.rs` with `#[cfg(test)] mod tests { ... }`

### Test Categories
- **Unit tests**: parse_source() helper, read_file() error handling, write_file() error handling
- **Functional tests**: compile() end-to-end (valid DSL → SVG file exists), preview() end-to-end (valid DSL → ASCII output), validate() returns Ok for valid input, validate() returns Err for invalid input
- **Edge cases**: Nonexistent input file produces DiagramError::Io, unwritable output path produces DiagramError::Io, empty DSL file handling

### Run Command
`cargo test --lib app`

## Verification Commands
- Build: `cargo build`
- Test: `cargo test --lib app`
- Check: `cargo clippy -- -D warnings && cargo fmt -- --check`
