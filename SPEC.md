# Agent Workflow Builder - Visual DAG Construction for Multi-Agent Pipelines

## Project Overview

**Project Name:** Agent Workflow Builder
**Type:** Web Application (Single Page)
**Core Functionality:** A visual directed acyclic graph (DAG) editor that enables users to construct multi-agent pipelines through an intuitive drag-and-drop interface, with bidirectional code generation/translation.
**Target Users:** Business analysts, domain experts (declarative mode), software engineers, ML specialists (programmatic mode)

---

## UI/UX Specification

### Layout Structure

**Main Container:** Full viewport height, split layout

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: Logo + Mode Toggle + Actions (Export/Import/Generate) │
├────────────────┬────────────────────────────────────────────────┤
│                │                                                │
│   NODE         │           CANVAS AREA                          │
│   PALETTE      │        (DAG Editor Grid)                       │
│                │                                                │
│   - AgentNode  │    [Nodes are placed and connected here]       │
│   - GroupChat  │                                                │
│   - Sequential │                                                │
│   - Parallel   │                                                │
│                │                                                │
├────────────────┴────────────────────────────────────────────────┤
│  PROPERTIES PANEL: Selected node configuration                  │
└─────────────────────────────────────────────────────────────────┘
```

**Sections:**
- **Header (60px):** Logo, mode toggle (Visual/Code), action buttons
- **Left Sidebar - Node Palette (240px):** Draggable node types
- **Main Canvas (flex-grow):** SVG-based DAG editor with grid
- **Bottom Panel - Properties (280px, collapsible):** Node configuration form

### Responsive Breakpoints
- Desktop: Full layout as described (≥1200px)
- Tablet: Collapsed sidebar, floating palette (768px-1199px)
- Mobile: Stacked layout with tab navigation (< 768px)

### Visual Design

**Color Palette:**
- Background Primary: `#0D0D12` (deep space black)
- Background Secondary: `#16161D` (card surfaces)
- Background Tertiary: `#1E1E28` (elevated elements)
- Accent Primary: `#00D4AA` (teal cyan - agent nodes)
- Accent Secondary: `#7B61FF` (purple - group chat)
- Accent Tertiary: `#FF6B4A` (coral - sequential)
- Accent Quaternary: `#FFD93D` (gold - parallel)
- Text Primary: `#F4F4F6`
- Text Secondary: `#8B8B9A`
- Text Muted: `#5C5C6D`
- Border: `#2A2A36`
- Success: `#00D4AA`
- Warning: `#FFD93D`
- Error: `#FF4757`
- Grid Lines: `#1E1E28`

**Typography:**
- Font Family: `'JetBrains Mono', 'Fira Code', monospace` for code/technical
- Font Family: `'Outfit', sans-serif` for UI headings
- Font Family: `'IBM Plex Sans', sans-serif` for body text
- Heading 1: 28px, weight 700
- Heading 2: 20px, weight 600
- Heading 3: 16px, weight 600
- Body: 14px, weight 400
- Small/Label: 12px, weight 500
- Code: 13px, monospace

**Spacing System:**
- Base unit: 4px
- xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px, xxl: 48px

**Visual Effects:**
- Node shadows: `0 4px 24px rgba(0, 0, 0, 0.4)`
- Hover glow: `0 0 20px {node-color}40`
- Connection lines: Animated dashed stroke, 2px width
- Grid: Dotted pattern, 20px spacing
- Glass morphism on panels: `backdrop-filter: blur(12px)`

### Components

**1. Node Palette Item**
- Icon + Label layout
- Drag handle indicator
- Hover: Scale 1.02, border highlight
- States: default, hover, dragging

**2. Canvas Node (4 types)**
- Header: Type icon + name + expand/collapse
- Body: Input/Output ports (circles on edges)
- Footer: Quick actions (edit, delete, duplicate)
- States: default, selected, executing, error, disabled

**3. Connection Edge**
- SVG bezier curve
- Arrow marker at target
- Animated flow direction
- Hover: Highlight, show delete handle
- States: default, selected, animated

**4. Properties Panel**
- Collapsible sections
- Form fields: text, select, textarea, array
- Real-time validation
- Save/Cancel buttons

**5. Mode Toggle**
- Pill-style toggle
- Visual (left) / Code (right)
- Smooth slide animation

**6. Code Editor Panel**
- Syntax highlighted JSON
- Line numbers
- Error indicators
- Copy button

---

## Functionality Specification

### Core Features

**1. Node Palette & Drag-Drop**
- Four node types available:
  - `AgentNode` - Single agent with I/O transformation
  - `GroupChatNode` - Multi-agent conversation
  - `SequentialNode` - Ordered execution with chaining
  - `ParallelNode` - Concurrent execution with aggregation
- Drag from palette to canvas to create nodes
- Snap to grid on drop (20px grid)

**2. Canvas Interactions**
- Pan: Click and drag on empty space
- Zoom: Mouse wheel (50% - 200%)
- Select: Click node/edge
- Multi-select: Shift+click or drag selection box
- Delete: Backspace/Delete key or context menu
- Undo/Redo: Ctrl+Z / Ctrl+Shift+Z

**3. Node Connections**
- Click output port → drag to input port → release to connect
- Visual feedback during drag (temporary edge)
- Validate connection rules:
  - AgentNode: 1 input, 1 output
  - GroupChatNode: Multiple inputs, 1 output
  - SequentialNode: Multiple inputs, 1 output
  - ParallelNode: Multiple inputs, Multiple outputs

**4. Properties Configuration**
- Click node to select → Properties panel shows form
- AgentNode fields:
  - Name (required)
  - Class (dropdown: AssistantAgent, UserProxyAgent, etc.)
  - System Message (textarea)
  - LLM Config (model, temperature, max tokens)
  - Tools (multi-select array)
- GroupChatNode fields:
  - Name
  - Agents (reference array)
  - Manager selection_strategy
  - max_rounds
- SequentialNode/ParallelNode:
  - Name
  - Description

**5. Code Generation**
- "Generate Code" button creates JSON
- Schema version 2.0 format
- Includes: schema_version, workflow_id, agents[], orchestration{}
- Bidirectional: Paste JSON → visual updates

**6. Export/Import**
- Export: Download as .json file
- Import: Upload .json to load workflow
- Auto-save to localStorage

### User Interactions and Flows

**Flow 1: Create New Workflow**
1. User lands on empty canvas
2. Drags "AgentNode" from palette
3. Node appears at drop position
4. Click node to configure in Properties panel
5. Add more nodes, connect them
6. Click "Generate Code" to see JSON

**Flow 2: Edit Existing Workflow**
1. Import JSON or load from localStorage
2. Visual DAG renders automatically
3. Modify nodes/connections
4. Export or regenerate code

**Flow 3: Switch to Code Mode**
1. Toggle to "Code" mode
2. JSON displays in code editor
3. Edit JSON directly
4. Toggle back to "Visual" to see changes rendered

### Edge Cases
- Circular dependency prevention (DAG validation)
- Invalid JSON handling with error messages
- Empty canvas state with helpful prompt
- Maximum nodes limit (50 for performance)
- Connection validation with user feedback

---

## Acceptance Criteria

### Visual Checkpoints
- [ ] Dark theme with specified color palette applied
- [ ] Grid background visible on canvas
- [ ] All 4 node types render with correct icons and colors
- [ ] Node palette items are draggable
- [ ] Connections render as smooth bezier curves
- [ ] Selected nodes show highlight state
- [ ] Properties panel shows form when node selected
- [ ] Mode toggle switches between Visual and Code views

### Functional Checkpoints
- [ ] Drag node from palette creates new node on canvas
- [ ] Nodes can be selected and moved
- [ ] Connections can be created by dragging between ports
- [ ] Delete key removes selected nodes/edges
- [ ] Properties panel updates node data
- [ ] "Generate Code" produces valid JSON
- [ ] Code mode JSON edits reflect in visual mode
- [ ] Export downloads JSON file
- [ ] Import loads JSON and renders DAG

### Performance
- [ ] Smooth 60fps interactions
- [ ] No lag with 20+ nodes
- [ ] Responsive within 100ms to user input
