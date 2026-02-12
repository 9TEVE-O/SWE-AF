# issue-07-svg-renderer: Implement SVG 1.1 renderer for diagram output

## Description
Create an SVG renderer that serializes LayoutDiagram to valid SVG 1.1 XML with type-specific node shapes, labeled connections with arrowheads, and proper XML escaping. This module transforms positioned layout data into production-quality scalable vector graphics.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-diagrams/.artifacts/plan/architecture.md` Section "Component 7: Renderer - SVG Module" for:
- SvgRenderer struct and render() method signature
- Node shape rendering functions (rectangles for services, cylinders for databases)
- Connection rendering with arrowhead markers
- SVG header structure with xmlns and viewBox
- XML escaping function
- Styling constants (SVG_FONT_SIZE, SVG_STROKE_WIDTH)

## Interface Contracts
```rust
pub struct SvgRenderer;
impl SvgRenderer {
    pub fn render(layout: &LayoutDiagram) -> String;
}
```

## Isolation Context
- Available: types module (LayoutDiagram, PositionedNode, PositionedConnection, NodeType, constants)
- Available: layout module (completed in previous level)
- NOT available: ascii module (sibling issue, parallel development)
- Source of truth: Architecture document Section 7

## Files
- **Create**: `src/svg.rs`
- **Modify**: `src/main.rs` (add `mod svg;`)

## Dependencies
- issue-01-types-module (provides: LayoutDiagram, NodeType, styling constants)
- issue-06-layout-module (provides: layout algorithm that produces LayoutDiagram)

## Provides
- SvgRenderer::render() that converts LayoutDiagram to SVG string
- Valid SVG 1.1 XML with xmlns declaration and viewBox
- Type-specific node rendering (rect for services, path for databases)
- Connection rendering with arrowhead markers and optional labels
- XML escaping for text content

## Acceptance Criteria
- [ ] `src/svg.rs` exists and compiles
- [ ] SvgRenderer::render() returns valid SVG starting with `<svg xmlns=...`
- [ ] SVG includes viewBox attribute calculated from layout width/height
- [ ] SVG defines arrowhead marker in `<defs>` section
- [ ] Service/External/Queue nodes rendered as `<rect>` with rounded corners
- [ ] Database nodes rendered as cylinder using `<path>` with bezier curves
- [ ] Connections rendered as `<line>` with `marker-end="url(#arrowhead)"`
- [ ] Connection labels rendered as `<text>` positioned at midpoint
- [ ] Node display names rendered as centered `<text>` elements
- [ ] XML special characters (`&`, `<`, `>`, `"`, `'`) properly escaped
- [ ] Generated SVG passes `xmllint --noout` validation
- [ ] At least 5 unit tests pass

## Testing Strategy

### Test Files
- `src/svg.rs` `#[cfg(test)]` module: unit tests for rendering functions

### Test Categories
- **Unit tests**: render_header(), render_defs(), render_node_shape(), render_cylinder(), escape_xml()
- **Functional tests**: Empty diagram produces valid SVG structure, service node contains `<rect>`, database node contains `<path>` for cylinder, connection produces `<line>` with marker, label text positioned at midpoint
- **Edge cases**: XML escaping with `&<>"'` characters, empty labels (None), zero-dimension layouts

### Run Command
`cargo test --lib svg`

## Verification Commands
- Build: `cargo build --release`
- Test: `cargo test --lib svg`
- Check: `echo 'node "API" as api' > /tmp/test.dsl && cargo run -- compile /tmp/test.dsl -o /tmp/test.svg && xmllint --noout /tmp/test.svg`
