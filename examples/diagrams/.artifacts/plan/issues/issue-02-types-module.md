# issue-02-types-module: Implement core type definitions for AST and layout structures

## Description
Define all foundational types in `src/types.rs` that serve as the single source of truth for the entire codebase. These types represent the Abstract Syntax Tree (AST), layout coordinates, and rendering constants. Every other module depends on these types.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-diagrams/.artifacts/plan/architecture.md` Section "Component 1: Foundation - Types Module" (lines 82-186) for:
- Complete type definitions with derive traits
- All struct fields and enum variants
- Constant values for layout and rendering

## Interface Contracts
Implements core types used throughout the codebase:
```rust
pub struct SourcePosition { pub line: usize, pub column: usize }
pub enum NodeType { Service, Database, External, Queue }
pub struct Node { pub identifier: String, pub display_name: String, pub node_type: NodeType, pub position: SourcePosition }
pub struct Connection { pub from: String, pub to: String, pub label: Option<String>, pub position: SourcePosition }
pub struct Diagram { pub nodes: Vec<Node>, pub connections: Vec<Connection> }
pub struct Point { pub x: f64, pub y: f64 }
pub struct PositionedNode { pub node: Node, pub position: Point, pub width: f64, pub height: f64 }
pub struct PositionedConnection { pub connection: Connection, pub start: Point, pub end: Point }
pub struct LayoutDiagram { pub nodes: Vec<PositionedNode>, pub connections: Vec<PositionedConnection>, pub width: f64, pub height: f64 }
pub const DEFAULT_NODE_WIDTH: f64 = 120.0; // plus 7 more constants
```

## Isolation Context
- Available: Cargo.toml and project structure from issue-01 (project-scaffold)
- NOT available: Code from sibling issues (error, lexer, parser, etc.)
- Source of truth: Architecture document lines 82-186

## Files
- **Create**: `src/types.rs`
- **Modify**: `src/main.rs` (add `mod types;`)

## Dependencies
- issue-01-project-scaffold (provides: Cargo.toml, src/ directory)

## Provides
- Complete AST type definitions (SourcePosition, NodeType, Node, Connection, Diagram)
- Layout type definitions (Point, PositionedNode, PositionedConnection, LayoutDiagram)
- Shared constants (DEFAULT_NODE_WIDTH, DEFAULT_NODE_HEIGHT, NODE_HORIZONTAL_SPACING, NODE_VERTICAL_SPACING, SVG_FONT_SIZE, SVG_STROKE_WIDTH, ASCII_NODE_PADDING, ASCII_MIN_NODE_WIDTH)

## Acceptance Criteria
- [ ] `src/types.rs` exists and compiles without warnings
- [ ] All 9 types defined: SourcePosition, NodeType, Node, Connection, Diagram, Point, PositionedNode, PositionedConnection, LayoutDiagram
- [ ] All 8 constants defined with correct values from architecture document
- [ ] All types derive Debug, Clone, and PartialEq/Eq where specified in architecture
- [ ] `cargo build` succeeds
- [ ] `cargo doc --no-deps` builds documentation for all public types

## Testing Strategy

### Test Files
- `tests/test_types.rs`: Unit tests for type instantiation and trait implementations

### Test Categories
- **Unit tests**: Verify each type can be instantiated with expected field values
- **Trait tests**: Verify Debug, Clone, PartialEq traits work correctly for all types
- **Constant tests**: Verify all constants have correct values as per architecture
- **Documentation tests**: Verify cargo doc builds without warnings

### Run Command
```bash
cargo test --test test_types && cargo doc --no-deps
```

## Verification Commands
- Build: `cargo build`
- Test: `cargo test --test test_types`
- Check: `cargo doc --no-deps 2>&1 | grep -v warning`
