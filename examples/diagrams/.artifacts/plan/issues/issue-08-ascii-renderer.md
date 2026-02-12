# issue-08-ascii-renderer: Implement ASCII art renderer with Unicode box-drawing characters

## Description
Create src/ascii.rs module that serializes LayoutDiagram to terminal-friendly ASCII art using Unicode box-drawing characters (U+2500-U+257F). Scale layout coordinates to fit ~80 character terminal width, render nodes as boxes with centered/truncated text, and connections as lines with directional indicators.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-diagrams/.artifacts/plan/architecture.md` Section 8 (Component 8: Renderer - ASCII Module) for:
- AsciiRenderer struct with render() method signature
- Grid dimension computation and scaling algorithm
- ScaledNode and ScaledConnection internal types
- Box-drawing character mappings (┌─┐│└┘)
- Text truncation with ellipsis (…) logic
- Connection drawing algorithm (L-shape with corners)

## Interface Contracts
```rust
pub struct AsciiRenderer;
impl AsciiRenderer {
    pub fn render(layout: &LayoutDiagram) -> String
}
```
- Exports: AsciiRenderer::render() returning String
- Consumes: LayoutDiagram from layout module (PositionedNode, PositionedConnection)
- Consumed by: app module's preview() method

## Isolation Context
- Available: types module (LayoutDiagram, Point, ASCII_MIN_NODE_WIDTH, ASCII_NODE_PADDING constants), layout module (completed in phase 2)
- NOT available: svg module (sibling issue, parallel stream)
- Source of truth: architecture document section 8 for rendering logic

## Files
- **Create**: `src/ascii.rs`
- **Modify**: `src/main.rs` (add `mod ascii;`)

## Dependencies
- issue-02-types-module (provides: LayoutDiagram, Point, ASCII constants)
- issue-07-layout-module (provides: LayoutEngine producing LayoutDiagram)

## Provides
- AsciiRenderer struct with render() method
- Character grid scaling algorithm (layout coordinates → character positions)
- Unicode box-drawing for nodes: ┌─┐│└┘
- Text centering and truncation with ellipsis (…)
- Connection rendering with ─│└ characters and arrow indicators (>, v)

## Acceptance Criteria
- [ ] src/ascii.rs exists and compiles without warnings
- [ ] AsciiRenderer::render(layout: &LayoutDiagram) returns String
- [ ] Renderer scales layout to fit ~80 character terminal width
- [ ] Nodes rendered as boxes using Unicode: ┌─┐│└┘
- [ ] Node display names centered within boxes
- [ ] Long node names truncated with ellipsis (…) when box too small
- [ ] Connections rendered as lines using ─ and │ characters
- [ ] Connections use └ corner character when changing direction
- [ ] Arrow indicators (>, v) shown at connection endpoints
- [ ] Output contains Unicode box-drawing characters (U+2500-U+257F range)
- [ ] At least 4 unit tests pass

## Testing Strategy

### Test Files
- `src/ascii.rs` with `#[cfg(test)] mod tests`: unit tests for rendering logic

### Test Categories
- **Unit tests**:
  - `test_render_single_node`: single node produces box with ┌┐└┘─│
  - `test_render_connection`: two connected nodes produce line with arrow (>, v)
  - `test_scaling`: float coordinates correctly convert to character grid positions
  - `test_text_truncation`: long node name truncated with … ellipsis
- **Functional tests**:
  - Render complete LayoutDiagram and verify output string contains box characters
  - Verify grid dimensions match computed scaling (width ≈ 80 chars)
- **Edge cases**:
  - Empty layout (no nodes)
  - Single node (no connections)
  - Very long node name (>30 chars)

### Run Command
`cargo test --lib ascii`

## Verification Commands
- Build: `cargo build --lib`
- Test: `cargo test --lib ascii`
- Check: `echo 'node "API" as api' | cargo run -- preview /dev/stdin | grep -qE '[\u2500-\u257F]'`
