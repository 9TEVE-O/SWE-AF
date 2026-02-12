# issue-04-layout-module: Implement graph layout algorithm for node positioning

## Description
Create `src/layout.rs` with `LayoutEngine` that computes 2D positions for nodes and connection paths. Implements simple left-to-right layered layout using BFS-based layer assignment to transform validated AST into positioned output ready for rendering.

## Architecture Reference
Read `architecture.md` Section 6 (Layout Module) for:
- BFS layer assignment algorithm
- Vertical distribution within layers
- Connection routing as straight lines between node centers
- Bounding box computation

## Interface Contracts
```rust
impl LayoutEngine {
    pub fn layout(diagram: &Diagram) -> LayoutDiagram;
}
```
- **Implements**: `LayoutEngine::layout()` method
- **Exports**: `LayoutEngine` struct and layout computation
- **Consumes**: `Diagram` from `types.rs`, layout constants from `types.rs`
- **Consumed by**: `svg-renderer` (issue-08), `ascii-renderer` (issue-09), `app-module` (issue-10)

## Isolation Context
- **Available**: Core types from `types-module` (Diagram, LayoutDiagram, Point, PositionedNode, PositionedConnection, constants)
- **NOT available**: Parser, validator, renderer code (sibling/later issues)
- **Source of truth**: `architecture.md` Section 6 for algorithm details

## Files
- **Create**: `src/layout.rs`
- **Modify**: `src/main.rs` (add `pub mod layout;`)

## Dependencies
- issue-02 (types-module): provides Diagram, LayoutDiagram, Point, PositionedNode, PositionedConnection, DEFAULT_NODE_WIDTH, DEFAULT_NODE_HEIGHT, NODE_HORIZONTAL_SPACING, NODE_VERTICAL_SPACING

## Provides
- `LayoutEngine` struct with `layout()` method
- BFS-based layer assignment (nodes with no incoming edges → layer 0)
- Node positioning with configurable spacing from constants
- Connection path computation between node centers
- Bounding box calculation for diagram dimensions

## Acceptance Criteria
- [ ] `src/layout.rs` exists and compiles
- [ ] `LayoutEngine::layout(diagram: &Diagram)` returns `LayoutDiagram`
- [ ] Layer assignment uses BFS (nodes with no incoming connections in layer 0)
- [ ] Nodes in same layer distributed with `NODE_VERTICAL_SPACING` between them
- [ ] Node x-coordinate = layer × (NODE_WIDTH + NODE_HORIZONTAL_SPACING)
- [ ] Connection start/end points computed from node center positions
- [ ] `LayoutDiagram` width and height include all positioned nodes
- [ ] Single node positioned at (0, 0) with default dimensions
- [ ] Linear chain produces sequential layers (0, 1, 2...)
- [ ] Branching topology produces multiple nodes per layer
- [ ] At least 4 unit tests pass

## Testing Strategy

### Test Files
- `src/layout.rs` `#[cfg(test)]` module: unit tests for layout algorithm

### Test Categories
- **Unit tests**: `test_layout_single_node`, `test_layout_linear_chain`, `test_layout_branching`, `test_layout_bounds`
- **Functional tests**: Layer assignment correctness, position calculation accuracy, connection routing
- **Edge cases**: Empty diagram (0 nodes), single node, disconnected components, cyclic graphs

### Run Command
`cargo test --lib layout`

## Verification Commands
- Build: `cargo build`
- Test: `cargo test --lib layout`
- Check: `cargo test --lib layout -- --nocapture | grep "test result: ok"`
