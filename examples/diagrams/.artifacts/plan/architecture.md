# Architecture Document: Diagrams-as-Code CLI Tool

## Executive Summary

This architecture defines a clean, three-layer Rust CLI application that transforms a custom DSL into SVG diagrams with ASCII preview capability. The design emphasizes separation of concerns, testability, and parallel development. Core principle: **data flows unidirectionally from DSL text → AST → Layout → Output Format**.

The architecture decomposes into 8 independent modules with explicit interfaces. Agents can work in parallel on parsing, layout, SVG rendering, ASCII rendering, and CLI layers once the foundational types module is complete.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│  (main.rs, cli.rs)                                          │
│  - Argument parsing (clap)                                   │
│  - Subcommand dispatch                                       │
│  - Error formatting and exit codes                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (app.rs)                                                   │
│  - Orchestrates pipeline: parse → validate → layout → render│
│  - File I/O coordination                                     │
└────────┬───────────────────────────┬─────────────────────────┘
         │                           │
         v                           v
┌─────────────────┐         ┌──────────────────┐
│  Parser Layer   │         │  Renderer Layer   │
│  (lexer, parser,│         │  (svg, ascii)     │
│   validator)    │         │                   │
└────────┬────────┘         └─────────┬─────────┘
         │                            │
         v                            v
┌─────────────────────────────────────────────────────────────┐
│                     Foundation Layer                         │
│  (types.rs, error.rs)                                       │
│  - AST types (Node, Connection, Diagram)                    │
│  - Error types (all error variants)                         │
│  - Shared constants and utilities                           │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow**:
1. CLI reads file → bytes
2. Lexer tokenizes bytes → Token stream
3. Parser builds Token stream → AST (Diagram)
4. Validator checks AST → Result<(), SemanticError>
5. Layout algorithm positions AST nodes → LayoutDiagram
6. Renderer (SVG or ASCII) serializes LayoutDiagram → String
7. CLI writes String to output

---

## Module Dependency Graph

```
types ─┐
       ├─→ error ─┐
       │          ├─→ lexer ─→ parser ─→ validator ─┐
       │          │                                  ├─→ layout ─┬─→ svg ─┐
       │          │                                  │           ├─→ ascii ┤
       │          └──────────────────────────────────┘           │         ├─→ app ─→ cli ─→ main
                                                                  │         │
                                                                  └─────────┘
```

**Execution Order for Parallel Development**:
1. **Phase 0** (foundational): `types`, `error` (built first, no dependencies)
2. **Phase 1** (parsing stream): `lexer`, `parser`, `validator` (parallel after Phase 0)
3. **Phase 2** (layout): `layout` (depends on Phase 1)
4. **Phase 3** (rendering streams): `svg`, `ascii` (parallel after Phase 2)
5. **Phase 4** (orchestration): `app`, `cli`, `main` (depends on all previous)

---

## Component Definitions

### Component 1: Foundation - Types Module

**File**: `src/types.rs`

**Responsibility**: Define all AST types, shared data structures, and constants used across the entire application. This is the single source of truth for type definitions.

**Public Types**:

```rust
/// Position in source text (for error reporting)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct SourcePosition {
    pub line: usize,
    pub column: usize,
}

/// Node type determines visual rendering style
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NodeType {
    Service,
    Database,
    External,
    Queue,
}

/// A node in the architecture diagram
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Node {
    pub identifier: String,        // e.g., "api"
    pub display_name: String,      // e.g., "API Gateway"
    pub node_type: NodeType,
    pub position: SourcePosition,  // where defined in source
}

/// A directed connection between two nodes
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Connection {
    pub from: String,              // source node identifier
    pub to: String,                // target node identifier
    pub label: Option<String>,     // optional edge label
    pub position: SourcePosition,  // where defined in source
}

/// Complete diagram AST
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Diagram {
    pub nodes: Vec<Node>,
    pub connections: Vec<Connection>,
}

/// 2D coordinate for layout
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Point {
    pub x: f64,
    pub y: f64,
}

/// Positioned node after layout algorithm runs
#[derive(Debug, Clone, PartialEq)]
pub struct PositionedNode {
    pub node: Node,
    pub position: Point,
    pub width: f64,
    pub height: f64,
}

/// Positioned connection after layout algorithm runs
#[derive(Debug, Clone, PartialEq)]
pub struct PositionedConnection {
    pub connection: Connection,
    pub start: Point,
    pub end: Point,
}

/// Diagram with computed layout
#[derive(Debug, Clone, PartialEq)]
pub struct LayoutDiagram {
    pub nodes: Vec<PositionedNode>,
    pub connections: Vec<PositionedConnection>,
    pub width: f64,
    pub height: f64,
}
```

**Constants**:

```rust
// Node dimensions for layout calculations
pub const DEFAULT_NODE_WIDTH: f64 = 120.0;
pub const DEFAULT_NODE_HEIGHT: f64 = 60.0;
pub const NODE_HORIZONTAL_SPACING: f64 = 80.0;
pub const NODE_VERTICAL_SPACING: f64 = 100.0;

// SVG styling constants
pub const SVG_FONT_SIZE: f64 = 14.0;
pub const SVG_STROKE_WIDTH: f64 = 2.0;

// ASCII rendering constants
pub const ASCII_NODE_PADDING: usize = 2;
pub const ASCII_MIN_NODE_WIDTH: usize = 10;
```

**Dependencies**: None (foundation layer)

---

### Component 2: Foundation - Error Module

**File**: `src/error.rs`

**Responsibility**: Define all error types, implement Display and Error traits, provide exit code mapping.

**Public Types**:

```rust
use crate::types::SourcePosition;
use std::fmt;
use std::io;

/// Top-level error type for the entire application
#[derive(Debug)]
pub enum DiagramError {
    Syntax(SyntaxError),
    Semantic(SemanticError),
    Io(IoError),
}

/// Syntax error during lexing or parsing
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SyntaxError {
    pub message: String,
    pub position: SourcePosition,
}

/// Semantic error during validation
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SemanticError {
    UndefinedNode {
        identifier: String,
        position: SourcePosition,
    },
    DuplicateNode {
        identifier: String,
        first_position: SourcePosition,
        second_position: SourcePosition,
    },
    SelfConnection {
        identifier: String,
        position: SourcePosition,
    },
}

/// I/O error during file operations
#[derive(Debug)]
pub struct IoError {
    pub message: String,
    pub source: Option<io::Error>,
}

impl DiagramError {
    /// Map error to exit code as specified in PRD
    pub fn exit_code(&self) -> i32 {
        match self {
            DiagramError::Syntax(_) => 1,
            DiagramError::Semantic(_) => 2,
            DiagramError::Io(_) => 3,
        }
    }

    /// Format error for human-readable output
    pub fn format_detailed(&self) -> String {
        match self {
            DiagramError::Syntax(e) => format!(
                "Syntax error at line {}, column {}: {}",
                e.position.line, e.position.column, e.message
            ),
            DiagramError::Semantic(e) => match e {
                SemanticError::UndefinedNode { identifier, position } => format!(
                    "Semantic error at line {}, column {}: undefined node '{}'",
                    position.line, position.column, identifier
                ),
                SemanticError::DuplicateNode { identifier, first_position, second_position } => format!(
                    "Semantic error: node '{}' defined multiple times (first at line {}, duplicate at line {})",
                    identifier, first_position.line, second_position.line
                ),
                SemanticError::SelfConnection { identifier, position } => format!(
                    "Semantic error at line {}, column {}: node '{}' cannot connect to itself",
                    position.line, position.column, identifier
                ),
            },
            DiagramError::Io(e) => format!("I/O error: {}", e.message),
        }
    }
}

impl fmt::Display for DiagramError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.format_detailed())
    }
}

impl std::error::Error for DiagramError {}

impl From<io::Error> for DiagramError {
    fn from(err: io::Error) -> Self {
        DiagramError::Io(IoError {
            message: err.to_string(),
            source: Some(err),
        })
    }
}

pub type Result<T> = std::result::Result<T, DiagramError>;
```

**Dependencies**: `types` (for SourcePosition)

---

### Component 3: Parser - Lexer Module

**File**: `src/lexer.rs`

**Responsibility**: Tokenize input text into a stream of tokens. Handle comments, whitespace, and track source positions.

**Public Interface**:

```rust
use crate::error::{DiagramError, SyntaxError};
use crate::types::SourcePosition;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Token {
    // Keywords
    Node,
    As,
    Type,

    // Literals
    Identifier(String),
    String(String),

    // Operators
    Arrow,          // ->
    Colon,          // :
    LeftBracket,    // [
    RightBracket,   // ]

    // Special
    Newline,
    Eof,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PositionedToken {
    pub token: Token,
    pub position: SourcePosition,
}

pub struct Lexer {
    input: Vec<char>,
    position: usize,
    line: usize,
    column: usize,
}

impl Lexer {
    /// Create a new lexer from input string
    pub fn new(input: &str) -> Self {
        Self {
            input: input.chars().collect(),
            position: 0,
            line: 1,
            column: 1,
        }
    }

    /// Tokenize entire input into vector of positioned tokens
    pub fn tokenize(&mut self) -> Result<Vec<PositionedToken>, DiagramError> {
        // Returns all tokens including Eof at the end
        // Skips comments (lines starting with #)
        // Tracks line/column positions for error reporting
        unimplemented!("Implementation by lexer agent")
    }

    fn current_position(&self) -> SourcePosition {
        SourcePosition {
            line: self.line,
            column: self.column,
        }
    }

    fn peek(&self) -> Option<char> {
        self.input.get(self.position).copied()
    }

    fn advance(&mut self) -> Option<char> {
        // Advances position, updates line/column tracking
        unimplemented!()
    }

    fn skip_whitespace(&mut self) {
        // Skips spaces and tabs (but not newlines)
        unimplemented!()
    }

    fn skip_comment(&mut self) {
        // Skips from # to end of line
        unimplemented!()
    }

    fn read_string(&mut self) -> Result<String, DiagramError> {
        // Reads quoted string, handles escape sequences
        unimplemented!()
    }

    fn read_identifier(&mut self) -> String {
        // Reads alphanumeric + underscore sequence
        unimplemented!()
    }

    fn match_keyword(&self, s: &str) -> Token {
        // Maps identifier strings to keyword tokens or Identifier(_)
        match s {
            "node" => Token::Node,
            "as" => Token::As,
            "type" => Token::Type,
            _ => Token::Identifier(s.to_string()),
        }
    }
}
```

**Error Cases**:
- Unterminated string literal → SyntaxError
- Invalid character in identifier → SyntaxError

**Testing Requirements**:
- Test empty input → [Eof]
- Test comment-only input → [Eof]
- Test node declaration tokenization
- Test connection with arrow and colon
- Test string with escape sequences
- Test error on unterminated string

**Dependencies**: `types`, `error`

---

### Component 4: Parser - Parser Module

**File**: `src/parser.rs`

**Responsibility**: Build AST (Diagram) from token stream using recursive descent parsing.

**Public Interface**:

```rust
use crate::error::{DiagramError, SyntaxError};
use crate::lexer::{PositionedToken, Token};
use crate::types::{Connection, Diagram, Node, NodeType, SourcePosition};

pub struct Parser {
    tokens: Vec<PositionedToken>,
    position: usize,
}

impl Parser {
    /// Create parser from token stream
    pub fn new(tokens: Vec<PositionedToken>) -> Self {
        Self {
            tokens,
            position: 0,
        }
    }

    /// Parse tokens into Diagram AST
    /// Grammar:
    /// diagram := statement*
    /// statement := node_decl | connection_decl
    /// node_decl := "node" STRING "as" IDENTIFIER type_annotation? NEWLINE
    /// type_annotation := "[" "type" ":" IDENTIFIER "]"
    /// connection_decl := IDENTIFIER "->" IDENTIFIER (":" STRING)? NEWLINE
    pub fn parse(&mut self) -> Result<Diagram, DiagramError> {
        let mut nodes = Vec::new();
        let mut connections = Vec::new();

        while !self.is_at_end() {
            self.skip_newlines();
            if self.is_at_end() {
                break;
            }

            match self.peek_token() {
                Token::Node => nodes.push(self.parse_node_decl()?),
                Token::Identifier(_) => connections.push(self.parse_connection_decl()?),
                Token::Eof => break,
                _ => return Err(self.syntax_error("expected 'node' or connection")),
            }
        }

        Ok(Diagram { nodes, connections })
    }

    fn parse_node_decl(&mut self) -> Result<Node, DiagramError> {
        // node "Display Name" as identifier [type: database]
        unimplemented!()
    }

    fn parse_connection_decl(&mut self) -> Result<Connection, DiagramError> {
        // source_id -> target_id : "label"
        unimplemented!()
    }

    fn parse_node_type(&mut self) -> Result<NodeType, DiagramError> {
        // Parses type annotation or returns default (Service)
        unimplemented!()
    }

    fn peek_token(&self) -> &Token {
        &self.tokens[self.position].token
    }

    fn current_position(&self) -> SourcePosition {
        self.tokens[self.position].position
    }

    fn advance(&mut self) -> &PositionedToken {
        let tok = &self.tokens[self.position];
        self.position += 1;
        tok
    }

    fn expect(&mut self, expected: Token) -> Result<(), DiagramError> {
        if self.peek_token() == &expected {
            self.advance();
            Ok(())
        } else {
            Err(self.syntax_error(&format!("expected {:?}", expected)))
        }
    }

    fn skip_newlines(&mut self) {
        while self.peek_token() == &Token::Newline {
            self.advance();
        }
    }

    fn is_at_end(&self) -> bool {
        matches!(self.peek_token(), Token::Eof)
    }

    fn syntax_error(&self, message: &str) -> DiagramError {
        DiagramError::Syntax(SyntaxError {
            message: message.to_string(),
            position: self.current_position(),
        })
    }
}
```

**Error Cases**:
- Missing "as" keyword → SyntaxError
- Missing identifier after "as" → SyntaxError
- Invalid node type (not service/database/external/queue) → SyntaxError
- Missing arrow in connection → SyntaxError

**Testing Requirements**:
- Test single node declaration
- Test node with type annotation
- Test connection with label
- Test connection without label
- Test multiple statements
- Test error on malformed node declaration
- Test error on invalid node type

**Dependencies**: `types`, `error`, `lexer`

---

### Component 5: Parser - Validator Module

**File**: `src/validator.rs`

**Responsibility**: Perform semantic validation on AST: ensure all connection endpoints reference defined nodes, no duplicate node IDs, no self-connections.

**Public Interface**:

```rust
use crate::error::{DiagramError, SemanticError};
use crate::types::Diagram;
use std::collections::{HashMap, HashSet};

pub struct Validator;

impl Validator {
    /// Validate diagram semantics
    /// Returns Ok(()) if valid, Err(SemanticError) otherwise
    pub fn validate(diagram: &Diagram) -> Result<(), DiagramError> {
        Self::check_duplicate_nodes(diagram)?;
        Self::check_undefined_connections(diagram)?;
        Self::check_self_connections(diagram)?;
        Ok(())
    }

    fn check_duplicate_nodes(diagram: &Diagram) -> Result<(), DiagramError> {
        let mut seen = HashMap::new();
        for node in &diagram.nodes {
            if let Some(first_pos) = seen.get(&node.identifier) {
                return Err(DiagramError::Semantic(SemanticError::DuplicateNode {
                    identifier: node.identifier.clone(),
                    first_position: *first_pos,
                    second_position: node.position,
                }));
            }
            seen.insert(node.identifier.clone(), node.position);
        }
        Ok(())
    }

    fn check_undefined_connections(diagram: &Diagram) -> Result<(), DiagramError> {
        let node_ids: HashSet<_> = diagram.nodes.iter().map(|n| &n.identifier).collect();

        for conn in &diagram.connections {
            if !node_ids.contains(&conn.from) {
                return Err(DiagramError::Semantic(SemanticError::UndefinedNode {
                    identifier: conn.from.clone(),
                    position: conn.position,
                }));
            }
            if !node_ids.contains(&conn.to) {
                return Err(DiagramError::Semantic(SemanticError::UndefinedNode {
                    identifier: conn.to.clone(),
                    position: conn.position,
                }));
            }
        }
        Ok(())
    }

    fn check_self_connections(diagram: &Diagram) -> Result<(), DiagramError> {
        for conn in &diagram.connections {
            if conn.from == conn.to {
                return Err(DiagramError::Semantic(SemanticError::SelfConnection {
                    identifier: conn.from.clone(),
                    position: conn.position,
                }));
            }
        }
        Ok(())
    }
}
```

**Testing Requirements**:
- Test valid diagram passes
- Test undefined source node error
- Test undefined target node error
- Test duplicate node ID error
- Test self-connection error

**Dependencies**: `types`, `error`

---

### Component 6: Layout Module

**File**: `src/layout.rs`

**Responsibility**: Compute 2D positions for nodes and connection paths. Implements simple left-to-right layered layout algorithm.

**Public Interface**:

```rust
use crate::types::{
    Diagram, LayoutDiagram, Point, PositionedConnection, PositionedNode,
    DEFAULT_NODE_HEIGHT, DEFAULT_NODE_WIDTH, NODE_HORIZONTAL_SPACING, NODE_VERTICAL_SPACING,
};
use std::collections::HashMap;

pub struct LayoutEngine;

impl LayoutEngine {
    /// Compute layout for diagram
    /// Algorithm: Simple left-to-right layout
    /// 1. Topological sort nodes by connection depth (BFS from sources)
    /// 2. Assign layers (x-coordinate groups)
    /// 3. Within each layer, distribute nodes vertically with even spacing
    /// 4. Compute connection paths as straight lines between node centers
    pub fn layout(diagram: &Diagram) -> LayoutDiagram {
        let layers = Self::assign_layers(diagram);
        let positioned_nodes = Self::position_nodes(&diagram.nodes, &layers);
        let node_positions = Self::build_position_map(&positioned_nodes);
        let positioned_connections = Self::position_connections(&diagram.connections, &node_positions);
        let (width, height) = Self::compute_bounds(&positioned_nodes);

        LayoutDiagram {
            nodes: positioned_nodes,
            connections: positioned_connections,
            width,
            height,
        }
    }

    fn assign_layers(diagram: &Diagram) -> HashMap<String, usize> {
        // BFS to assign layer index to each node
        // Nodes with no incoming edges → layer 0
        // Each successor → max(predecessors' layers) + 1
        unimplemented!()
    }

    fn position_nodes(
        nodes: &[crate::types::Node],
        layers: &HashMap<String, usize>,
    ) -> Vec<PositionedNode> {
        // Group nodes by layer, distribute vertically within layer
        // x = layer * (NODE_WIDTH + HORIZONTAL_SPACING)
        // y = index_in_layer * (NODE_HEIGHT + VERTICAL_SPACING)
        unimplemented!()
    }

    fn build_position_map(positioned_nodes: &[PositionedNode]) -> HashMap<String, Point> {
        // Map node ID → center point for connection routing
        positioned_nodes
            .iter()
            .map(|pn| {
                (
                    pn.node.identifier.clone(),
                    Point {
                        x: pn.position.x + pn.width / 2.0,
                        y: pn.position.y + pn.height / 2.0,
                    },
                )
            })
            .collect()
    }

    fn position_connections(
        connections: &[crate::types::Connection],
        node_positions: &HashMap<String, Point>,
    ) -> Vec<PositionedConnection> {
        connections
            .iter()
            .map(|conn| PositionedConnection {
                connection: conn.clone(),
                start: *node_positions.get(&conn.from).unwrap(),
                end: *node_positions.get(&conn.to).unwrap(),
            })
            .collect()
    }

    fn compute_bounds(positioned_nodes: &[PositionedNode]) -> (f64, f64) {
        let max_x = positioned_nodes
            .iter()
            .map(|pn| pn.position.x + pn.width)
            .fold(0.0, f64::max);
        let max_y = positioned_nodes
            .iter()
            .map(|pn| pn.position.y + pn.height)
            .fold(0.0, f64::max);
        (max_x, max_y)
    }
}
```

**Algorithm Details**:
- **Layer assignment**: Modified BFS that respects dependency ordering
- **Vertical distribution**: Centers nodes in each layer, evenly spaced
- **Connection routing**: Straight lines from source center to target center (no pathfinding needed for simple layout)

**Testing Requirements**:
- Test single node → layer 0, position (0, 0)
- Test linear chain → nodes in sequential layers
- Test branching → multiple nodes in same layer
- Test bounds calculation

**Dependencies**: `types`

---

### Component 7: Renderer - SVG Module

**File**: `src/svg.rs`

**Responsibility**: Serialize LayoutDiagram to valid SVG 1.1 XML. Render nodes with type-specific shapes (rectangles for services, cylinders for databases), arrows with labels.

**Public Interface**:

```rust
use crate::types::{LayoutDiagram, NodeType, PositionedConnection, PositionedNode, SVG_FONT_SIZE, SVG_STROKE_WIDTH};

pub struct SvgRenderer;

impl SvgRenderer {
    /// Render layout to SVG string
    pub fn render(layout: &LayoutDiagram) -> String {
        let mut svg = String::new();

        // SVG header with viewBox
        svg.push_str(&Self::render_header(layout.width, layout.height));

        // Define arrow marker for connections
        svg.push_str(&Self::render_defs());

        // Render all connections (draw before nodes so arrows are behind)
        for conn in &layout.connections {
            svg.push_str(&Self::render_connection(conn));
        }

        // Render all nodes
        for node in &layout.nodes {
            svg.push_str(&Self::render_node(node));
        }

        svg.push_str("</svg>\n");
        svg
    }

    fn render_header(width: f64, height: f64) -> String {
        format!(
            r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {:.0} {:.0}" width="{:.0}" height="{:.0}">
"#,
            width + 20.0, height + 20.0, width + 20.0, height + 20.0
        )
    }

    fn render_defs() -> String {
        // Define arrowhead marker
        r#"  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#333" />
    </marker>
  </defs>
"#.to_string()
    }

    fn render_node(node: &PositionedNode) -> String {
        let shape = Self::render_node_shape(node);
        let text = Self::render_node_text(node);
        format!("  <g>\n{}{}</g>\n", shape, text)
    }

    fn render_node_shape(node: &PositionedNode) -> String {
        match node.node.node_type {
            NodeType::Service | NodeType::External | NodeType::Queue => {
                // Rectangle
                format!(
                    r#"    <rect x="{:.1}" y="{:.1}" width="{:.1}" height="{:.1}" fill="#E3F2FD" stroke="#1976D2" stroke-width="{:.1}" rx="5" />
"#,
                    node.position.x, node.position.y, node.width, node.height, SVG_STROKE_WIDTH
                )
            }
            NodeType::Database => {
                // Cylinder (approximated with path)
                Self::render_cylinder(node)
            }
        }
    }

    fn render_cylinder(node: &PositionedNode) -> String {
        // SVG path for cylinder shape
        let x = node.position.x;
        let y = node.position.y;
        let w = node.width;
        let h = node.height;
        let eh = h * 0.1; // ellipse height

        format!(
            r#"    <path d="M {:.1},{:.1} L {:.1},{:.1} Q {:.1},{:.1} {:.1},{:.1} Q {:.1},{:.1} {:.1},{:.1} L {:.1},{:.1} Q {:.1},{:.1} {:.1},{:.1} Q {:.1},{:.1} {:.1},{:.1} Z M {:.1},{:.1} Q {:.1},{:.1} {:.1},{:.1} Q {:.1},{:.1} {:.1},{:.1}" fill="#FFF3E0" stroke="#E65100" stroke-width="{:.1}" />
"#,
            x, y + eh,
            x, y + h - eh,
            x + w/2.0, y + h - eh + eh/2.0, x + w, y + h - eh,
            x + w - w/2.0, y + h - eh + eh/2.0, x + w, y + h - eh,
            x + w, y + eh,
            x + w - w/2.0, y + eh + eh/2.0, x + w, y + eh,
            x + w/2.0, y + eh - eh/2.0, x, y + eh,
            x, y + eh,
            x + w/2.0, y + eh + eh/2.0, x + w, y + eh,
            x + w - w/2.0, y + eh - eh/2.0, x + w, y + eh,
            SVG_STROKE_WIDTH
        )
    }

    fn render_node_text(node: &PositionedNode) -> String {
        let cx = node.position.x + node.width / 2.0;
        let cy = node.position.y + node.height / 2.0;
        format!(
            r#"    <text x="{:.1}" y="{:.1}" text-anchor="middle" dominant-baseline="middle" font-size="{:.0}" font-family="Arial, sans-serif">{}</text>
"#,
            cx, cy, SVG_FONT_SIZE, Self::escape_xml(&node.node.display_name)
        )
    }

    fn render_connection(conn: &PositionedConnection) -> String {
        let line = format!(
            r#"    <line x1="{:.1}" y1="{:.1}" x2="{:.1}" y2="{:.1}" stroke="#333" stroke-width="{:.1}" marker-end="url(#arrowhead)" />
"#,
            conn.start.x, conn.start.y, conn.end.x, conn.end.y, SVG_STROKE_WIDTH
        );

        let label = if let Some(ref text) = conn.connection.label {
            let mid_x = (conn.start.x + conn.end.x) / 2.0;
            let mid_y = (conn.start.y + conn.end.y) / 2.0 - 5.0; // Offset above line
            format!(
                r#"    <text x="{:.1}" y="{:.1}" text-anchor="middle" font-size="{:.0}" font-family="Arial, sans-serif" fill="#666">{}</text>
"#,
                mid_x, mid_y, SVG_FONT_SIZE - 2.0, Self::escape_xml(text)
            )
        } else {
            String::new()
        };

        format!("  <g>\n{}{}</g>\n", line, label)
    }

    fn escape_xml(s: &str) -> String {
        s.replace('&', "&amp;")
            .replace('<', "&lt;")
            .replace('>', "&gt;")
            .replace('"', "&quot;")
            .replace('\'', "&apos;")
    }
}
```

**Styling Decisions**:
- **Service nodes**: Blue (#E3F2FD fill, #1976D2 stroke), rounded rectangles
- **Database nodes**: Orange (#FFF3E0 fill, #E65100 stroke), cylinder shape
- **External/Queue nodes**: Same as service (differentiation can be added later)
- **Connections**: Dark gray (#333), 2px stroke, arrowhead marker
- **Labels**: Medium gray (#666), slightly smaller font

**Testing Requirements**:
- Test render single node → valid SVG with <rect> or <path>
- Test render connection → valid SVG with <line> and marker
- Test XML escaping in labels
- Test viewBox calculation

**Dependencies**: `types`

---

### Component 8: Renderer - ASCII Module

**File**: `src/ascii.rs`

**Responsibility**: Serialize LayoutDiagram to ASCII art using Unicode box-drawing characters. Scale layout to fit typical terminal dimensions.

**Public Interface**:

```rust
use crate::types::{LayoutDiagram, Point, PositionedNode, ASCII_MIN_NODE_WIDTH, ASCII_NODE_PADDING};

pub struct AsciiRenderer;

impl AsciiRenderer {
    /// Render layout to ASCII art string
    /// Uses Unicode box-drawing characters (U+2500-U+257F)
    /// Scales coordinates to character grid
    pub fn render(layout: &LayoutDiagram) -> String {
        // 1. Scale layout to character grid
        let (grid_width, grid_height, scale) = Self::compute_grid_dimensions(layout);
        let scaled_nodes = Self::scale_nodes(&layout.nodes, scale);
        let scaled_connections = Self::scale_connections(&layout.connections, scale);

        // 2. Initialize character grid
        let mut grid = vec![vec![' '; grid_width]; grid_height];

        // 3. Draw connections first (so they go under nodes)
        for conn in scaled_connections {
            Self::draw_connection(&mut grid, &conn);
        }

        // 4. Draw nodes on top
        for node in scaled_nodes {
            Self::draw_node(&mut grid, &node);
        }

        // 5. Convert grid to string
        Self::grid_to_string(&grid)
    }

    fn compute_grid_dimensions(layout: &LayoutDiagram) -> (usize, usize, f64) {
        // Target 80 columns wide
        const TARGET_WIDTH: usize = 80;
        let scale = TARGET_WIDTH as f64 / layout.width.max(1.0);
        let grid_width = (layout.width * scale).ceil() as usize;
        let grid_height = (layout.height * scale).ceil() as usize;
        (grid_width, grid_height, scale)
    }

    fn scale_nodes(nodes: &[PositionedNode], scale: f64) -> Vec<ScaledNode> {
        nodes
            .iter()
            .map(|n| ScaledNode {
                display_name: n.node.display_name.clone(),
                x: (n.position.x * scale) as usize,
                y: (n.position.y * scale) as usize,
                width: ((n.width * scale) as usize).max(ASCII_MIN_NODE_WIDTH),
                height: ((n.height * scale) as usize).max(3),
            })
            .collect()
    }

    fn scale_connections(
        connections: &[crate::types::PositionedConnection],
        scale: f64,
    ) -> Vec<ScaledConnection> {
        connections
            .iter()
            .map(|c| ScaledConnection {
                start_x: (c.start.x * scale) as usize,
                start_y: (c.start.y * scale) as usize,
                end_x: (c.end.x * scale) as usize,
                end_y: (c.end.y * scale) as usize,
                label: c.connection.label.clone(),
            })
            .collect()
    }

    fn draw_node(grid: &mut Vec<Vec<char>>, node: &ScaledNode) {
        // Draw box with corners and edges
        // ┌─────────┐
        // │  Name   │
        // └─────────┘
        let x = node.x;
        let y = node.y;
        let w = node.width;
        let h = node.height;

        // Top edge
        grid[y][x] = '┌';
        for i in 1..w - 1 {
            grid[y][x + i] = '─';
        }
        grid[y][x + w - 1] = '┐';

        // Middle rows
        for j in 1..h - 1 {
            grid[y + j][x] = '│';
            grid[y + j][x + w - 1] = '│';
        }

        // Bottom edge
        grid[y + h - 1][x] = '└';
        for i in 1..w - 1 {
            grid[y + h - 1][x + i] = '─';
        }
        grid[y + h - 1][x + w - 1] = '┘';

        // Center text
        let text = Self::truncate_text(&node.display_name, w - 2 * ASCII_NODE_PADDING);
        let text_x = x + (w - text.len()) / 2;
        let text_y = y + h / 2;
        for (i, ch) in text.chars().enumerate() {
            if text_x + i < grid[0].len() {
                grid[text_y][text_x + i] = ch;
            }
        }
    }

    fn draw_connection(grid: &mut Vec<Vec<char>>, conn: &ScaledConnection) {
        // Draw line from start to end
        // Simple algorithm: horizontal then vertical (L-shape)
        let x1 = conn.start_x;
        let y1 = conn.start_y;
        let x2 = conn.end_x;
        let y2 = conn.end_y;

        // Horizontal segment
        let (h_start, h_end) = if x1 < x2 { (x1, x2) } else { (x2, x1) };
        for x in h_start..=h_end {
            if grid[y1][x] == ' ' {
                grid[y1][x] = '─';
            }
        }

        // Vertical segment
        let (v_start, v_end) = if y1 < y2 { (y1, y2) } else { (y2, y1) };
        for y in v_start..=v_end {
            if grid[y][x2] == ' ' {
                grid[y][x2] = '│';
            }
        }

        // Corner
        if x1 != x2 && y1 != y2 {
            grid[y1][x2] = '└';
        }

        // Arrowhead at end
        if y2 > 0 && grid[y2 - 1][x2] == '│' {
            grid[y2][x2] = 'v';
        } else if x2 > 0 && grid[y2][x2 - 1] == '─' {
            grid[y2][x2] = '>';
        }
    }

    fn truncate_text(text: &str, max_len: usize) -> String {
        if text.len() <= max_len {
            text.to_string()
        } else {
            format!("{}…", &text[..max_len - 1])
        }
    }

    fn grid_to_string(grid: &[Vec<char>]) -> String {
        grid.iter()
            .map(|row| row.iter().collect::<String>())
            .collect::<Vec<_>>()
            .join("\n")
    }
}

// Internal types for scaled layout
struct ScaledNode {
    display_name: String,
    x: usize,
    y: usize,
    width: usize,
    height: usize,
}

struct ScaledConnection {
    start_x: usize,
    start_y: usize,
    end_x: usize,
    end_y: usize,
    label: Option<String>,
}
```

**Box-Drawing Characters Used**:
- `┌` `┐` `└` `┘` - corners (U+250C, U+2510, U+2514, U+2518)
- `─` - horizontal line (U+2500)
- `│` - vertical line (U+2502)
- `>` `v` - arrowheads (ASCII fallback)

**Testing Requirements**:
- Test render single node → box with text
- Test render two connected nodes → boxes with line and arrow
- Test scaling to terminal width
- Test text truncation for long node names

**Dependencies**: `types`

---

### Component 9: Application Layer

**File**: `src/app.rs`

**Responsibility**: Orchestrate the full pipeline: file I/O, parsing, validation, layout, rendering. Provide high-level functions for CLI commands.

**Public Interface**:

```rust
use crate::error::{DiagramError, IoError, Result};
use crate::lexer::Lexer;
use crate::parser::Parser;
use crate::validator::Validator;
use crate::layout::LayoutEngine;
use crate::svg::SvgRenderer;
use crate::ascii::AsciiRenderer;
use std::fs;
use std::path::Path;

pub struct App;

impl App {
    /// Compile DSL file to SVG
    pub fn compile<P: AsRef<Path>>(input_path: P, output_path: P) -> Result<()> {
        // 1. Read input file
        let source = Self::read_file(&input_path)?;

        // 2. Parse to AST
        let diagram = Self::parse_source(&source)?;

        // 3. Validate semantics
        Validator::validate(&diagram)?;

        // 4. Compute layout
        let layout = LayoutEngine::layout(&diagram);

        // 5. Render to SVG
        let svg = SvgRenderer::render(&layout);

        // 6. Write output file
        Self::write_file(&output_path, &svg)?;

        Ok(())
    }

    /// Preview DSL file as ASCII art
    pub fn preview<P: AsRef<Path>>(input_path: P) -> Result<String> {
        // 1. Read input file
        let source = Self::read_file(&input_path)?;

        // 2. Parse to AST
        let diagram = Self::parse_source(&source)?;

        // 3. Validate semantics
        Validator::validate(&diagram)?;

        // 4. Compute layout
        let layout = LayoutEngine::layout(&diagram);

        // 5. Render to ASCII
        let ascii = AsciiRenderer::render(&layout);

        Ok(ascii)
    }

    /// Validate DSL file without generating output
    pub fn validate<P: AsRef<Path>>(input_path: P) -> Result<()> {
        // 1. Read input file
        let source = Self::read_file(&input_path)?;

        // 2. Parse to AST
        let diagram = Self::parse_source(&source)?;

        // 3. Validate semantics
        Validator::validate(&diagram)?;

        Ok(())
    }

    fn read_file<P: AsRef<Path>>(path: P) -> Result<String> {
        fs::read_to_string(&path).map_err(|e| {
            DiagramError::Io(IoError {
                message: format!("Failed to read file '{}': {}", path.as_ref().display(), e),
                source: Some(e),
            })
        })
    }

    fn write_file<P: AsRef<Path>>(path: P, content: &str) -> Result<()> {
        fs::write(&path, content).map_err(|e| {
            DiagramError::Io(IoError {
                message: format!("Failed to write file '{}': {}", path.as_ref().display(), e),
                source: Some(e),
            })
        })
    }

    fn parse_source(source: &str) -> Result<crate::types::Diagram> {
        let mut lexer = Lexer::new(source);
        let tokens = lexer.tokenize()?;
        let mut parser = Parser::new(tokens);
        parser.parse()
    }
}
```

**Testing Requirements**:
- Integration test: compile valid DSL → SVG file exists and is valid
- Integration test: preview valid DSL → ASCII output contains box characters
- Integration test: validate invalid DSL → returns semantic error
- Integration test: read nonexistent file → returns IoError

**Dependencies**: All modules (lexer, parser, validator, layout, svg, ascii, error, types)

---

### Component 10: CLI Layer

**File**: `src/cli.rs`

**Responsibility**: Define CLI structure using clap, parse arguments, dispatch to App functions, format errors, set exit codes.

**Public Interface**:

```rust
use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "diagrams")]
#[command(about = "A CLI tool for generating architecture diagrams from DSL", long_about = None)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Compile DSL to SVG diagram
    Compile {
        /// Input DSL file path
        input: PathBuf,

        /// Output SVG file path
        #[arg(short, long)]
        output: PathBuf,
    },

    /// Preview DSL as ASCII art in terminal
    Preview {
        /// Input DSL file path
        input: PathBuf,
    },

    /// Validate DSL syntax and semantics
    Validate {
        /// Input DSL file path
        input: PathBuf,
    },
}

impl Cli {
    pub fn parse_args() -> Self {
        <Self as Parser>::parse()
    }
}
```

**File**: `src/main.rs`

**Responsibility**: Entry point, execute CLI commands, handle errors and exit codes.

```rust
mod types;
mod error;
mod lexer;
mod parser;
mod validator;
mod layout;
mod svg;
mod ascii;
mod app;
mod cli;

use cli::{Cli, Commands};
use error::DiagramError;
use std::process;

fn main() {
    let cli = Cli::parse_args();

    let result = match cli.command {
        Commands::Compile { input, output } => {
            app::App::compile(input, output)
        }
        Commands::Preview { input } => {
            match app::App::preview(input) {
                Ok(ascii) => {
                    println!("{}", ascii);
                    Ok(())
                }
                Err(e) => Err(e),
            }
        }
        Commands::Validate { input } => {
            app::App::validate(input)
        }
    };

    if let Err(e) = result {
        eprintln!("{}", e);
        process::exit(e.exit_code());
    }
}
```

**Testing Requirements**:
- Test --help output contains subcommands
- Test compile subcommand help contains --output
- Test invalid subcommand → clap error

**Dependencies**: `app`, `error`, `cli` (clap)

---

## External Dependencies

**Cargo.toml**:

```toml
[package]
name = "diagrams"
version = "0.1.0"
edition = "2021"
rust-version = "1.70"

[dependencies]
clap = { version = "4.4", features = ["derive"] }

[dev-dependencies]
# For snapshot testing
insta = "1.34"
# For integration tests
tempfile = "3.8"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true
```

**Dependency Rationale**:
- **clap 4.4**: Industry-standard CLI parsing, derive macros for minimal boilerplate
- **insta 1.34** (dev): Snapshot testing for SVG output validation
- **tempfile 3.8** (dev): Safe temporary file creation for integration tests

**Binary Size Optimization**:
- `lto = true`: Link-time optimization reduces dead code
- `codegen-units = 1`: Maximizes optimization opportunities
- `strip = true`: Removes debug symbols
- Target: <10MB (AC8)

---

## Data Flow Examples

### Example 1: Compile Command

**Input DSL**:
```
node "API" as api
node "DB" as db
api -> db : "SQL"
```

**Flow**:
1. CLI: Read file → `"node \"API\" as api\nnode \"DB\" as db\napi -> db : \"SQL\"\n"`
2. Lexer: Tokenize → `[Node, String("API"), As, Identifier("api"), Newline, ...]`
3. Parser: Parse → `Diagram { nodes: [Node { identifier: "api", display_name: "API", ... }], connections: [...] }`
4. Validator: Check → `Ok(())`
5. Layout: Position → `LayoutDiagram { nodes: [PositionedNode { position: Point { x: 0.0, y: 0.0 }, ... }], ... }`
6. SVG Renderer: Serialize → `"<svg ...><rect .../><text>API</text>..."`
7. CLI: Write file → SVG saved to disk

### Example 2: Syntax Error

**Input DSL**:
```
node "API" as
```

**Flow**:
1. CLI: Read file → `"node \"API\" as\n"`
2. Lexer: Tokenize → `[Node, String("API"), As, Newline, Eof]`
3. Parser: Parse → Expects `Identifier` after `As`, finds `Newline`
4. Parser: Return `Err(SyntaxError { message: "expected identifier", position: SourcePosition { line: 1, column: 15 } })`
5. CLI: Print error → `"Syntax error at line 1, column 15: expected identifier"`
6. CLI: Exit code 1

### Example 3: Semantic Error

**Input DSL**:
```
node "API" as api
api -> db : "SQL"
```

**Flow**:
1-3. Lexer and Parser succeed
4. Validator: Check connections → `db` not in node set
5. Validator: Return `Err(SemanticError::UndefinedNode { identifier: "db", position: ... })`
6. CLI: Print error → `"Semantic error at line 2, column 8: undefined node 'db'"`
7. CLI: Exit code 2

---

## Testing Strategy

### Unit Tests (per module)

**lexer.rs**:
- `test_tokenize_empty` → empty input produces [Eof]
- `test_tokenize_node_decl` → node declaration produces correct tokens
- `test_tokenize_connection` → arrow and colon tokenized correctly
- `test_tokenize_string_escape` → escaped quotes handled
- `test_tokenize_comment` → comments skipped
- `test_error_unterminated_string` → SyntaxError returned

**parser.rs**:
- `test_parse_single_node` → AST has one node
- `test_parse_node_with_type` → NodeType correctly parsed
- `test_parse_connection` → Connection in AST
- `test_error_missing_as` → SyntaxError on malformed node
- `test_error_invalid_node_type` → SyntaxError on unknown type

**validator.rs**:
- `test_validate_success` → valid diagram passes
- `test_error_undefined_node` → SemanticError::UndefinedNode
- `test_error_duplicate_node` → SemanticError::DuplicateNode
- `test_error_self_connection` → SemanticError::SelfConnection

**layout.rs**:
- `test_layout_single_node` → positioned at (0, 0)
- `test_layout_linear_chain` → nodes in sequential layers
- `test_layout_bounds` → width and height computed correctly

**svg.rs**:
- `test_render_empty_diagram` → valid SVG with header and footer
- `test_render_node_service` → contains <rect>
- `test_render_node_database` → contains <path> (cylinder)
- `test_render_connection` → contains <line> with marker
- `test_xml_escaping` → special characters escaped

**ascii.rs**:
- `test_render_single_node` → box with corners
- `test_render_connection` → line with arrow
- `test_scaling` → coordinates scaled to grid
- `test_text_truncation` → long names truncated

### Integration Tests

**File**: `tests/integration.rs`

```rust
use std::process::Command;
use tempfile::TempDir;
use std::fs;

#[test]
fn test_compile_valid_dsl() {
    let tmp = TempDir::new().unwrap();
    let input = tmp.path().join("input.dsl");
    let output = tmp.path().join("output.svg");

    fs::write(&input, r#"
node "API" as api
node "DB" as db
api -> db : "SQL"
"#).unwrap();

    let status = Command::new("cargo")
        .args(&["run", "--release", "--", "compile", input.to_str().unwrap(), "-o", output.to_str().unwrap()])
        .status()
        .unwrap();

    assert!(status.success());
    assert!(output.exists());

    let svg = fs::read_to_string(output).unwrap();
    assert!(svg.starts_with("<svg"));
    assert!(svg.contains("API"));
    assert!(svg.contains("DB"));
    assert!(svg.contains("SQL"));
}

#[test]
fn test_preview_renders_ascii() {
    let tmp = TempDir::new().unwrap();
    let input = tmp.path().join("input.dsl");

    fs::write(&input, r#"
node "API" as api
node "DB" as db
api -> db
"#).unwrap();

    let output = Command::new("cargo")
        .args(&["run", "--release", "--", "preview", input.to_str().unwrap()])
        .output()
        .unwrap();

    assert!(output.status.success());
    let ascii = String::from_utf8(output.stdout).unwrap();
    assert!(ascii.contains('┌') || ascii.contains('─') || ascii.contains('│'));
}

#[test]
fn test_validate_syntax_error() {
    let tmp = TempDir::new().unwrap();
    let input = tmp.path().join("input.dsl");

    fs::write(&input, "invalid syntax").unwrap();

    let output = Command::new("cargo")
        .args(&["run", "--release", "--", "validate", input.to_str().unwrap()])
        .output()
        .unwrap();

    assert!(!output.status.success());
    assert_eq!(output.status.code().unwrap(), 1);
    let stderr = String::from_utf8(output.stderr).unwrap();
    assert!(stderr.to_lowercase().contains("syntax error"));
}

#[test]
fn test_validate_semantic_error() {
    let tmp = TempDir::new().unwrap();
    let input = tmp.path().join("input.dsl");

    fs::write(&input, r#"
node "API" as api
api -> undefined_node
"#).unwrap();

    let output = Command::new("cargo")
        .args(&["run", "--release", "--", "validate", input.to_str().unwrap()])
        .output()
        .unwrap();

    assert!(!output.status.success());
    assert_eq!(output.status.code().unwrap(), 2);
    let stderr = String::from_utf8(output.stderr).unwrap();
    assert!(stderr.to_lowercase().contains("undefined node"));
}
```

### Snapshot Tests

**File**: `tests/snapshots.rs`

```rust
use insta::assert_snapshot;
use diagrams::{App, LayoutEngine, SvgRenderer};
use std::fs;

#[test]
fn test_svg_snapshot_simple() {
    let source = r#"
node "API Gateway" as api [type: service]
node "PostgreSQL" as db [type: database]
api -> db : "SQL queries"
"#;

    let diagram = /* parse source */;
    let layout = LayoutEngine::layout(&diagram);
    let svg = SvgRenderer::render(&layout);

    assert_snapshot!(svg);
}
```

---

## Architecture Decisions

### Decision 1: Single-Pass Lexer with Lookahead

**Chosen**: Lexer produces full token vector in one pass, parser consumes with arbitrary lookahead.

**Rejected**: Streaming lexer/parser with iterator pattern.

**Rationale**:
- DSL files are small (<10MB per PRD assumptions), full token vector fits in memory
- Simplifies parser implementation (no need for complex iterator state)
- Enables better error messages (parser can look ahead/behind for context)
- Performance cost is negligible: lexing 10MB text is <10ms

**Consequences**: Memory usage is O(n) in input size, acceptable given constraints.

---

### Decision 2: Separate Layout Pass Before Rendering

**Chosen**: Layout algorithm produces `LayoutDiagram` with absolute positions, renderers consume this.

**Rejected**: Renderers compute layout themselves, or embed layout logic in AST.

**Rationale**:
- **Separation of concerns**: Layout is independent of output format (SVG vs ASCII use same algorithm)
- **Testability**: Can test layout algorithm without involving rendering
- **Parallel development**: Layout and renderer modules can be built independently
- **Future extensibility**: Different layout algorithms (force-directed, hierarchical) can be swapped without touching renderers

**Consequences**: Additional data structure (`LayoutDiagram`), but gains in modularity outweigh cost.

---

### Decision 3: Simple Left-to-Right Layered Layout

**Chosen**: BFS-based layer assignment, even vertical spacing within layers.

**Rejected**: Force-directed layout, hierarchical Sugiyama layout, manual positioning DSL.

**Rationale**:
- **Simplicity**: Implements in <100 lines, no external graph layout library needed
- **Performance**: O(V + E) complexity meets <1s requirement for 100 nodes
- **Predictability**: Users can understand layout logic (source nodes left, targets right)
- **Sufficient for MVP**: PRD acceptance criteria don't require optimal layouts, just "no overlaps"

**Consequences**: Complex graphs may have suboptimal spacing. Document limitation, add better layouts as Phase 2 nice-to-have.

---

### Decision 4: SVG 1.1 (Not 2.0) for Maximum Compatibility

**Chosen**: Use SVG 1.1 spec features only.

**Rejected**: SVG 2.0 features like `<marker>` enhancements, `<text>` auto-sizing.

**Rationale**:
- **Browser support**: SVG 1.1 universally supported (IE11+, all modern browsers)
- **Documentation tools**: GitHub Markdown, Confluence, etc. render SVG 1.1 reliably
- **No feature loss**: 1.1 sufficient for rectangles, cylinders, arrows, text

**Consequences**: Slightly more verbose SVG code (e.g., manual arrowhead marker definition), but gains in compatibility.

---

### Decision 5: Unicode Box-Drawing for ASCII Preview

**Chosen**: Use Unicode U+2500-U+257F characters (─, │, ┌, etc.).

**Rejected**: Pure ASCII (-, |, +) or Braille characters for higher resolution.

**Rationale**:
- **Visual quality**: Box-drawing looks clean in modern terminals
- **PRD requirement**: AC4 explicitly tests for U+2500-U+257F range
- **UTF-8 ubiquity**: 99% of developer terminals in 2024 support UTF-8

**Consequences**: May render incorrectly on misconfigured terminals. Mitigation: detect locale, print warning if not UTF-8.

---

### Decision 6: No External Parser Generator (e.g., nom, pest)

**Chosen**: Hand-written recursive descent parser.

**Rejected**: Using `nom`, `pest`, or `lalrpop` parser generator libraries.

**Rationale**:
- **Binary size**: AC8 requires <10MB binary; parser generators add 1-3MB dependencies
- **Simplicity**: DSL grammar is simple (3 statement types), hand-written parser is <200 lines
- **Error messages**: Full control over error formatting and recovery
- **Learning curve**: Agents can implement recursive descent without learning library-specific DSL

**Consequences**: More code than using library, but total control and minimal dependencies.

---

### Decision 7: Clap for CLI (Not structopt or manual parsing)

**Chosen**: Use `clap` v4 with derive macros.

**Rejected**: `structopt` (merged into clap), manual `std::env::args()` parsing.

**Rationale**:
- **Industry standard**: Clap is de facto Rust CLI parsing library
- **Derive ergonomics**: Minimal boilerplate, types map directly to CLI structure
- **Help generation**: Auto-generated --help messages pass AC2 requirements
- **Binary size**: Clap v4 is ~200KB (acceptable for 10MB budget)

**Consequences**: Dependency on clap, but benefits justify cost.

---

### Decision 8: Exit Codes Match PRD Specification Exactly

**Chosen**: 0=success, 1=syntax error, 2=semantic error, 3=I/O error.

**Rejected**: Generic 0=success, 1=any error.

**Rationale**:
- **PRD requirement**: Error handling section explicitly defines exit code mapping
- **Scriptability**: Shell scripts can distinguish error types (e.g., retry on I/O error, fail on syntax error)
- **POSIX compatibility**: Exit codes 1-3 are valid, no conflicts with shell reserved codes (126, 127, 128+)

**Consequences**: None, this is a strict requirement.

---

## File Structure

```
diagrams/
├── Cargo.toml
├── Cargo.lock
├── src/
│   ├── main.rs          # Entry point, error handling
│   ├── cli.rs           # Clap CLI definitions
│   ├── app.rs           # High-level orchestration
│   ├── types.rs         # AST and data structure definitions
│   ├── error.rs         # Error types and formatting
│   ├── lexer.rs         # Tokenization
│   ├── parser.rs        # AST construction
│   ├── validator.rs     # Semantic validation
│   ├── layout.rs        # Graph layout algorithm
│   ├── svg.rs           # SVG rendering
│   └── ascii.rs         # ASCII rendering
├── tests/
│   ├── integration.rs   # End-to-end CLI tests
│   ├── snapshots.rs     # SVG snapshot tests
│   └── fixtures/        # Example DSL files
│       ├── simple.dsl
│       ├── three_tier.dsl
│       └── invalid_syntax.dsl
└── README.md            # Usage documentation
```

---

## Performance Budget Breakdown

**Target**: <1s compilation for 100-node diagram (AC7)

| Phase            | Budget  | Rationale                                      |
|------------------|---------|------------------------------------------------|
| File I/O         | ~5ms    | 100KB file read, SSD                          |
| Lexing           | ~10ms   | Single pass, no backtracking                  |
| Parsing          | ~15ms   | Recursive descent, linear in tokens           |
| Validation       | ~5ms    | HashMap lookups, O(V + E)                     |
| Layout           | ~50ms   | BFS + positioning, O(V + E)                   |
| SVG Rendering    | ~100ms  | String building, no complex geometry          |
| File Write       | ~10ms   | ~500KB SVG output                             |
| **Total**        | ~195ms  | **Margin: 805ms for optimization if needed**  |

**Fallback optimizations if budget exceeded**:
1. Use `BufWriter` for SVG output (reduces write time 50%)
2. Pre-allocate token/node vectors (reduces allocations)
3. Use `SmallVec` for connections (most nodes have <3 edges)

---

## Extension Points (Future Work)

These are NOT implemented in MVP but architecture supports clean addition:

1. **Custom node shapes**: Add `NodeShape` enum to types, extend SVG renderer with new shape functions
2. **Color customization**: Add `color: Option<String>` to Node type, extend DSL parser for color syntax
3. **Multi-file includes**: Add `Import` statement to AST, parser resolves includes before validation
4. **PNG export**: Add `png.rs` module using `resvg` crate, render SVG to raster (requires external dependency)
5. **Better layout algorithms**: Replace `LayoutEngine::assign_layers` with force-directed or Sugiyama algorithm (no interface changes)

---

## Implementation Checklist

### Phase 0: Foundation (Build First)
- [ ] Create Cargo project: `cargo new diagrams --bin`
- [ ] Define `src/types.rs` with all AST types (copy signatures from this document verbatim)
- [ ] Define `src/error.rs` with error types and Display impls
- [ ] Verify: `cargo build` succeeds

### Phase 1: Parsing Stream (Parallel After Phase 0)
- [ ] Implement `src/lexer.rs` with unit tests
- [ ] Implement `src/parser.rs` with unit tests
- [ ] Implement `src/validator.rs` with unit tests
- [ ] Verify: `cargo test --lib lexer parser validator` passes

### Phase 2: Layout (After Phase 1)
- [ ] Implement `src/layout.rs` with unit tests
- [ ] Verify: `cargo test --lib layout` passes

### Phase 3: Rendering Streams (Parallel After Phase 2)
- [ ] Implement `src/svg.rs` with unit tests
- [ ] Implement `src/ascii.rs` with unit tests
- [ ] Verify: `cargo test --lib svg ascii` passes

### Phase 4: Orchestration (After Phase 3)
- [ ] Implement `src/app.rs` with integration tests
- [ ] Implement `src/cli.rs` with clap definitions
- [ ] Implement `src/main.rs` entry point
- [ ] Verify: `cargo build --release` succeeds

### Phase 5: End-to-End Testing
- [ ] Create `tests/integration.rs` (copy tests from this document)
- [ ] Create `tests/fixtures/` with example DSL files
- [ ] Verify: All 12 acceptance criteria pass (AC1-AC12)

---

## Summary

This architecture defines a clean, layered Rust CLI tool with explicit module boundaries and data flow. Core principles:

1. **Foundation-first**: Types and errors defined before anything else
2. **Unidirectional data flow**: DSL → Tokens → AST → Layout → Output
3. **Separation of concerns**: Each module has single responsibility, clear interface
4. **Parallel development**: Lexer, parser, validator can be built concurrently; SVG and ASCII renderers are independent
5. **No unsafe code**: Pure safe Rust (enforced by AC11)
6. **Minimal dependencies**: Only clap for CLI, insta/tempfile for tests

Every type signature, function signature, and error variant in this document is **canonical** — they should be copied verbatim into implementation code. Any deviation requires architecture update.

Two engineers implementing independently from this document should produce code that integrates on first attempt.
