# issue-12-cli-module: Implement CLI interface with clap argument parsing

## Description
Create the CLI layer with clap-based argument parsing and main entry point. This module defines the command-line interface structure, dispatches to App methods, and handles error formatting and exit codes.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-diagrams/.artifacts/plan/architecture.md` Section "Component 10: CLI Layer" for:
- Cli struct with Parser derive from clap
- Commands enum with three subcommand variants
- main.rs orchestration pattern
- Error formatting and exit code mapping

## Interface Contracts
- Implements:
```rust
pub struct Cli { pub command: Commands }
pub enum Commands { Compile { input: PathBuf, output: PathBuf }, Preview { input: PathBuf }, Validate { input: PathBuf } }
impl Cli { pub fn parse_args() -> Self }
fn main() // entry point with error handling
```
- Exports: CLI interface, argument parsing, main entry point
- Consumes: app::App::{compile, preview, validate}, error::DiagramError
- Consumed by: End users via command line

## Isolation Context
- Available: app module, error module (from completed prior-level issues)
- NOT available: None (final integration phase)
- Source of truth: architecture document at `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-diagrams/.artifacts/plan/architecture.md`

## Files
- **Create**: `src/cli.rs`
- **Modify**: `src/main.rs` (add module declarations and main implementation)

## Dependencies
- issue-11-app-module (provides: App::{compile, preview, validate})
- issue-03-error-module (provides: DiagramError, exit_code mapping)

## Provides
- Complete CLI interface with clap derive macros
- Subcommand routing (compile, preview, validate)
- Error formatting to stderr with eprintln!
- Exit code handling (0=success, 1=syntax, 2=semantic, 3=I/O)
- Main entry point that orchestrates full pipeline

## Acceptance Criteria
- [ ] src/cli.rs defines Cli struct with #[derive(Parser)] from clap
- [ ] Commands enum defines Compile, Preview, Validate variants
- [ ] Compile command accepts input: PathBuf and --output/-o: PathBuf
- [ ] Preview and Validate commands accept input: PathBuf
- [ ] src/main.rs calls Cli::parse_args() and dispatches to App methods
- [ ] Errors printed to stderr using eprintln!
- [ ] Exit codes: 0=success, 1=syntax, 2=semantic, 3=I/O
- [ ] Preview prints ASCII output to stdout
- [ ] ./target/release/diagrams --help displays all subcommands
- [ ] Each subcommand --help shows correct arguments

## Testing Strategy

### Test Files
- `src/cli.rs` #[cfg(test)] module: verify clap structure compiles
- `tests/integration.rs`: end-to-end CLI workflow tests

### Test Categories
- **Unit tests**: Verify Cli and Commands types compile with clap derives
- **Integration tests**: Test --help output, subcommand execution, error handling
- **Manual verification**: Run `cargo build --release && ./target/release/diagrams --help`

### Run Command
```bash
cargo test --lib cli
cargo test --test integration
cargo build --release && ./target/release/diagrams --help
```

## Verification Commands
- Build: `cargo build --release`
- Test: `cargo test --lib cli && cargo test --test integration`
- Check: `./target/release/diagrams --help | grep -q 'compile' && ./target/release/diagrams compile --help | grep -q 'output'`
