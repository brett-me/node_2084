# NODE 2084  
*A minimal psychological systems game built in Pygame*

---

# 1. Core Concept

**Node 2084** is a short-form psychological prototype set one hundred years after the ideological climate of *Nineteen Eighty-Four*.

In **2084**, control is no longer social.

It is **perceptual**.

Human cognition has been reduced to a constrained simulation environment — a low-bandwidth phosphor grid inspired by the IBM 5151 monochrome monitor.

This is not retro nostalgia.

It is the totality of the player’s sensory experience.

The player does not look at a monitor.

**The monitor is their world.**

This is not a story about escape.

It is about **realisation**.

Not heroic rebellion.

But complicity.

---

# 2. Scope & Constraints (4-Day Prototype)

This project is intentionally contained.

### Scope

- One full-screen map
- 2–3 infrared sensors
- 3 rotating tasks
- 3 structured discoveries
- 1 ending sequence
- Recursive continuation (no restart)

### Explicit Non-Goals

- No branching narrative
- No death state
- No restart mechanic
- No large world
- No scrolling map
- No procedural generation
- No advanced AI
- No dynamic lighting or shaders

### Implementation Constraints

- All collision via `pygame.Rect`
- Single main loop
- Minimal architecture layers
- Manual timers
- Deterministic cycle progression

This is achievable in four focused days.

---

# 3. World Model

## 3.1 The Player

- Represented as a glowing square
- Top-down view
- Arrow/WASD movement
- Layered draw calls for faux glow (no shaders)

The player is not a person.

They are a **Node**.

---

## 3.2 The Map

The entire screen **is the map**.

- No camera movement
- No scrolling
- No off-screen zones
- Player never leaves the screen

The map is:

- Static in bounds
- Mutable in configuration per cycle
- Built entirely from rectangular collision walls
- One terminal chamber that appears circular (visual motif only)

**Collision Rule:**  
All walls and interaction zones use `pygame.Rect`.  
“Circular” spaces are visual motifs only.

The map is a looped route:

```
Corridor → Room → Corridor → Terminal → Return
```

A ritual circuit.

Predictable.

Contained.

Computational.

---

# 4. Visual Language (CRT Terminal Reality)

Inspired by IBM 5151 monochrome phosphor (P39).

## Colour Palette

Background:
```
(0, 10, 0)
```

Primary Green:
```
(0, 255, 70)
```

Dim Green:
```
(0, 120, 40)
```

Player Core:
```
(220, 255, 220)
```

Infrared Sensors:
```
(255, 140, 0)
```

## CRT Effects (Simple & Feasible)

### Scanlines
```python
for y in range(0, height, 2):
    pygame.draw.line(surface, (0,0,0,40), (0,y), (width,y))
```

### Phosphor Flicker
Brightness variation scales with instability.

### Glow Trick
Draw player three times:
- Large faint square
- Medium dim square
- Bright core square

No shaders.

No post-processing pipeline.

---

# 5. Core System: Suspicion

The system is driven by a single variable:

```python
suspicion = 0  # range: 0–100
```

There is no stored integrity variable.

Integrity is derived:

```python
simulation_integrity = 100 - suspicion
```

Integrity is used only as a scaling factor for visual instability.

There is:

- No death
- No restart
- No Game Over

Only:

- Stable perception
- Unstable perception
- Awareness
- Obedience

As suspicion rises:

- Text jitters
- Green flicker intensifies
- Sensor timing desynchronises
- Walls subtly flicker
- Task text partially fractures

The world does not end.

It destabilises.

---

# 6. Structural Spine (State Flow)

The game has three states:

```
BOOT → TERMINAL → PLAY
```

## BootState
Constructs perception.

## TerminalState
Enforces ideological confirmation.

## PlayState
Simulates ongoing routine existence.

Boot and Terminal run once at startup.

PlayState becomes recursive.

---

# 7. Opening Sequence (BOOT)

Black screen.

Blinking green cursor.

Then:

```
INITIALISING PERCEPTION
NODE ID: 2084.114.7
COGNITIVE SHELL: ACTIVE
PERCEPTION BANDWIDTH: 12% (OPTIMAL)
EMOTIVE RANGE: SUPPRESSED

NOTICE:
PREVIOUS NODE: 2084.114.6
STATUS: REMOVED
CAUSE: UNSTRUCTURED CURIOSITY
```

Clinical tone.

No theatrics.

---

# 8. Truth Confirmation Sequence

```
CONFIRM:
YOUR PERCEPTION IS COMPLETE.
[Y/N]
```

```
CONFIRM:
THE SYSTEM PROVIDES.
[Y/N]
```

If N:
```python
suspicion += 10
```

Then:

```
RESPONSE RECORDED
SENSORY FIELD ATTACHED
```

Micro-delays between lines create unease.

Nothing dramatic happens.

It is logged.

---

# 9. Transition to Grid

After:

```
SENSORY FIELD ATTACHED
```

Pause 0.8 seconds.

The grid appears instantly.

Player appears 0.5 seconds later.

For half a second:

The world exists without them.

---

# 10. Infrared Sensors

Sensors:

- Emit cone-shaped detection zones
- Pulse rhythmically
- Detect using `pygame.Rect.colliderect()`

When detected:

- Suspicion rises slowly
- Unless player performs sanctioned tasks

The first sensor must detect the player intentionally.

Overlay:

```
MOVEMENT ACKNOWLEDGED
```

Surveillance is normal.

---

# 11. Tasks (Conditioning Through Comfort)

Tasks are mundane and repeat.

## Task 1 — Path Optimisation

```
REALIGN DATA CHANNEL
```

Walk to 3 tiles in sequence.

Completion:

```
COGNITIVE GRID STABLE
LOCAL INTEGRITY RESTORED
```

Suspicion decreases.

---

## Task 2 — Noise Correction

Walk over flickering tiles.

Completion:

```
ANOMALY PURGED
BACKGROUND PROCESSES NORMALISED
```

World stabilises.

---

## Task 3 — Historical Verification

At terminal chamber:

```
THE PAST IS CONSISTENT.
[Y/N]
```

Correct answer: Y.

Incorrect answer increases suspicion.

---

# 12. Discovery Escalation

Escalation order:

1. Self doubt  
2. Surveillance doubt  
3. Structural doubt  

Tasks are heartbeat.

Discoveries are arrhythmia.

---

## Discovery 1 — Personal Fragment

After one full task cycle:

```
UNINDEXED MEMORY FRAGMENT DETECTED
YOU ONCE HAD HANDS
DELETE FRAGMENT [Y/N]
```

Y lowers suspicion slightly.

N keeps suspicion elevated.

---

## Discovery 2 — Sensor Blind Spot

In an unscanned corner:

```
PROCESSING PAUSED
WHO IS WATCHING WHEN NOTHING MOVES?
```

Suspicion rises slowly while idle.

---

## Discovery 3 — Structural Contradiction

A sensor cone passes through a wall.

After repeated exposure:

```
COLLISION MAP: LOCAL ONLY
EXTERNAL PROCESS DOES NOT REQUIRE WALLS
YOU REQUIRE WALLS
```

Point of no return.

---

# 13. Cycle Structure

Inside PlayState exists a **CycleManager**.

It controls:

- Task activation
- Discovery activation
- Sensor timing drift
- Subtle wall shifts

## Cycle 1
Clean.

## Cycle 2
Degraded.

## Cycle 3
Fractured.

## Final Cycle
Terminal interruption:

```
CONTINUE CORRECTION?
[Y/N]
```

Regardless of input:

System resumes Play.

Never returns to Cycle 1.

---

# 14. Recursion Model

This game does not restart.

It loops.

But not cleanly.

After the “end”:

Tasks resume.

Text shifts:

```
REALIGN DATA CHANNEL (ONGOING)
```

Eventually:

```
STABILITY CORRECTION CONTINUES
```

The player realises:

They are maintaining the structure.

Closing the window is the only termination.

---

# 15. High-Level Architecture

```
Game
 ├── StateMachine
 ├── BootState
 ├── TerminalState
 └── PlayState
        ├── Map
        ├── Player
        ├── Sensors
        ├── TaskSystem
        ├── DiscoverySystem
        ├── SuspicionSystem
        └── CycleManager
```

Single main loop.

No ECS.

No scene graph.

No camera system.

---

# 16. The Horror Mechanism

The system never shouts.

No villain.

No violence.

No escape fantasy.

Compliance restores clarity.

Curiosity degrades perception.

The world depends on your input.

But it does not need your awareness.

There is no revolution.

Only recursion.

And clarity is optional.
