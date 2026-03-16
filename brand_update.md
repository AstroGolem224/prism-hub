### 🔮 PRISM Hub — Brand Bible
**Clay Machine Games // Design System v2.0** *Neon Cyberpunk Edition — mit vollständiger Effekt-Dokumentation*

--------------------------------------------------------------------------------

#### 1. Brand Philosophy
PRISM Hub ist das Nervenzentrum von Clay Machine Games — ein internes Ops-Tool das sich anfühlt wie ein Cyberpunk-Terminal aus der Zukunft. Kein generisches Dashboard. Kein Clean-Corporate. **Dunkel, neon, lebendig.**

**Kernprinzipien & UI/UX Directives:**
*   **Dark First** — Augen schonen beim Nacht-Sprint.
*   **Neon Accent** — Farbe als Signal, nicht als Dekoration.
*   **Glass Morphism** — Tiefe durch Transparenz und Glow.
*   **Mono x Display** — Code-Ästhetik trifft Industrial Typography.
*   **Motion speaks** — Animationen kommunizieren Zustand.
*   **Layered Atmosphere** — 5 übereinanderliegende Schichten erzeugen Tiefe.
*   **Visual Hierarchy & Anti-Clutter (Update):** Etablierung einer strikten Texthierarchie und eines 8-Punkt-Grid-Systems für konsistente Abstände, um Information Overload zu vermeiden. Klare Ikonografie muss auf realen Objekten basieren.
*   **Thematic Eras (Update):** UI-Komponenten in architektonische Cyberpunk-Ären (Entropism, Kitsch, Neo Militarism, Neo Kitsch) unterteilen, ergänzt durch Retro-Futurismus (späte 90er Web-Layouts) für Sub-Seiten.

--------------------------------------------------------------------------------

#### 2. Color System
##### 2.1 Background Palette (Dark Foundation)
| Token | Hex | Verwendung |
| ------ | ------ | ------ |
| --bg-void | #080d13 | Tiefstes Schwarz — Body Background |
| --bg-base | #0c1214 | Seiten-Hintergrund |
| --bg-surface | #141b20 | Cards, Sidebar |
| --bg-elevated | #1c2830 | Hover States, raised Elements |

**Regel:** Immer von Void nach Elevated — niemals heller als #1c2830 für Flächen.

##### 2.2 Theme System — 3 Themen
PRISM Hub hat ein vollständiges Theme-System via data-theme auf `<html>`. Jedes Theme definiert den kompletten Token-Satz.

###### 🔥 Ember (Standard)
*Industrial. Glut. Forge-Ästhetik. Dunkel-warme Töne.*
| Token | Wert |
| ------ | ------ |
| --accent-primary | #d4520a (Ember Orange) |
| --accent-secondary | #c9972a (Ember Gold) |
| --accent-ember | #d4520a |
| --accent-gold | #c9972a |
| --rune-glow | #ff7b2e (Glow-Farbe für Animationen) |
| --bg-void | #080d13 |
| Particle-Colors | rgb(212,82,10), rgb(201,151,42), rgb(255,123,46), rgb(255,180,80) |

###### ⚡ Neon
*Cyberpunk. Electric. Klassisches Tron-Feeling.*
| Token | Wert |
| ------ | ------ |
| --accent-primary | #0de8f5 (Cyan) |
| --accent-secondary | #a855f7 (Violet) |
| --rune-glow | #0de8f5 |
| --neon-green | #22d3a0 |
| Particle-Colors | rgb(13,232,245), rgb(168,85,247), rgb(34,211,160) |

###### ☀️ Light
*Clean. Professional. Für Meetings und Screenshots.*
| Token | Wert |
| ------ | ------ |
| --accent-primary | #0891b2 |
| --accent-secondary | #7c3aed |
| --bg-void | #f1f5f9 |
| --bg-surface | #ffffff |
| Besonderheit | Glows reduziert, mix-blend-mode: multiply |

##### 2.3 Neon Accent Palette (Basis-Tokens)
| Token | Hex | Verwendung |
| ------ | ------ | ------ |
| --neon-cyan | #0de8f5 | Primär-Akzent (Neon-Theme), Links, Interactive |
| --neon-violet | #a855f7 | Secondary Accent, Tags, Badges |
| --neon-green | #4caf50 | Success, Online-Status, Bestätigung |
| --neon-amber | #f59e0b | Warnung, Pending |
| --neon-red | #ef4444 | Error, Offline, Danger |

**Regel:** Im Ember-Theme → `--accent-ember` für primäre Akzente. Im Neon-Theme → `--neon-cyan`. Niemals hart-coded Farben, immer CSS Tokens.
**Strikte Kontrastregeln (Update):** Schlechte Kontrastkombinationen (z. B. rote Standardschrift auf rotem Hintergrund) sind strengstens verboten.
**Dynamic State Feedback (Update):** Nutze semantische Farbzuordnung (Rot = Warnung, Blau = Ruhe, Pink = Spielerisch). Setze dynamisches visuelles Feedback ein, z.B. einen roten Blur-Effekt an den Bildschirmrändern für kritische Systemwarnungen.

##### 2.4 Glow System
**Intensitäten:**
*  0.06–0.10 → Ambient Glow (immer vorhanden)
*  0.25–0.40 → Active / Hover Glow
*  0.60–0.80 → Focus / Selected State

##### 2.5 Text Palette
| Token | Hex (Ember) | Verwendung |
| ------ | ------ | ------ |
| --text-primary | #e0ddd5 | Haupttext, Headlines |
| --text-secondary | #8a8578 | Subtitles, Labels |
| --text-muted | #5a5548 | Hints, Timestamps, Disabled |

##### 2.6 Glass Morphism
**Card-Basis:**
**Formgebung (Update):** Anstelle von fragilen SVG-Masken oder simplen `border-radius`-Hacks MUSS die moderne CSS-Eigenschaft `corner-shape` für abgeschrägte (beveled) oder squircle Ecken verwendet werden, um die harte Sci-Fi-Terminal-Ästhetik nativ und performant zu realisieren.

--------------------------------------------------------------------------------

#### 3. Typography
##### 3.1 Font Stack
| Role | Font | Weight | Verwendung |
| ------ | ------ | ------ | ------ |
| **Display** | Barlow Condensed | 700–900 | Page Titles, Hero Text, Nav Labels |
| **Body** | Inter | 400–600 | Fließtext, Descriptions, UI-Labels |
| **Mono** | JetBrains Mono | 400–700 | Code, IDs, Timestamps, Werte, Tags |
| **Display (Public)** | Orbitron | 400–900 | Public-Seite Hero Text |

*Wichtig (Update):* Definiere strikte Fallback-Font-Stacks (z.B. `Orbitron, sans-serif`), um die typografische Hierarchie bei eventuellen Font-Ladeverzögerungen nicht zu brechen.

##### 3.2 Type Scale
| Element | Font | Size | Weight | Styling |
| ------ | ------ | ------ | ------ | ------ |
| Page Title | Barlow Condensed | 2.8rem | 800 | UPPERCASE, gold glow + accent-bar |
| Section Header | Barlow Condensed | 1.6rem | 700 | UPPERCASE |
| Card Title | Inter | 1rem | 600 | — |
| Body | Inter | 0.95rem | 400 | line-height: 1.7 |
| Label/Badge | JetBrains Mono | 0.75rem | 500 | UPPERCASE, letter-spacing: 0.08em |
| Code/Value | JetBrains Mono | 0.85rem | 400 | --neon-cyan color |

--------------------------------------------------------------------------------

#### 4. Background Effects — Das Atmosphären-System
PRISM Hub nutzt **5 übereinanderliegende Schichten** für die Hintergrundatmosphäre:
*Accessibility Directive (Update):* Implementiere zwingend `@media (prefers-reduced-motion: reduce)`, um die driftenden 25s-Animationen für Nutzer mit Bewegungsempfindlichkeit zu pausieren und auf organisches, statisches Noise zurückzufallen.

##### 4.1 Radial Ambient Glows (body::before)
Sanfte, sich bewegende Farbblobs erzeugen ein lebendiges Gefühl.
**Regel:** `color-mix(in srgb, ...)` macht die Glows automatisch theme-sensitiv.

##### 4.2 Hex Grid (body::after)
Das Hexagon-Grid ist das visuelle Signature-Element. SVG-basiert, animiert driftend, theme-farbig.
**SVG-Hexagon-Pattern** (theme-farbig, einmal pro Theme):
*  Ember: `stroke="#f59e0b"` (Amber)
*  Neon: `stroke="#0de8f5"` (Cyan)
*  Light: `stroke="#0891b2"` (Blue), opacity: 0.14, mix-blend-mode: multiply

Jedes Tile enthält 5 überlappende Hexagons für nahtloses Tiling. Grid-Zelle: 172×148px, stroke-width: 3.

##### 4.3 Ember Particle System (Canvas)
Das Herzstück der Atmosphäre. Ein `<canvas id="ember-canvas">` über dem gesamten Viewport.
**Specs:**
*   **Count:** 120 Partikel
*   **Deaktiviert** auf Mobilgeräten (`max-width: 768px`) zur Performance
*   **Theme-aware:** Farben wechseln mit Theme-Switcher in Echtzeit

##### 4.4 Scanlines Overlay
Klassischer CRT-Effekt. Extrem subtil — kaum wahrnehmbar aber atmosphärisch.
*   **Zeilenhöhe:** 4px (2px transparent + 2px dunkel)
*   **Dunkel-Intensität:** 0.03 (kaum sichtbar, nur der Hauch)
*   **Deaktiviert** auf Mobilgeräten

##### 4.5 SVG Noise / Film Grain
Organische Textur über allem. Verhindert den "zu digital" Look.
*  SVG `<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4">`
*  Tile-Größe: 256×256px
*  Opacity: 0.03 (subtiles Grain)

--------------------------------------------------------------------------------

#### 5. Component Tokens
##### 5.1 Badges
##### 5.2 Buttons
##### 5.3 Status Indicators
##### 5.4 Stat Cards
**Stat Counter:** Zahlen animieren beim Laden von 0 auf Zielwert (800ms, cubic ease-out).
##### 5.5 Active Nav Indicator

--------------------------------------------------------------------------------

#### 6. Animation Tokens
| Name | Duration | Easing | Verwendung |
| ------ | ------ | ------ | ------ |
| drift | 25s | ease-in-out alternate | Ambient Radial Glows |
| hex-drift | 25s | linear infinite | Hex Grid Scroll |
| rune-pulse | — | ease-in-out | Rune/Icon-Elemente |
| ember-shimmer | 3s | linear infinite | Shimmer-Text, Hero |
| pulse | 2.5s | ease-in-out | Status Dots |
| fade-in | 0.3s | ease-out | Page Transitions |

**Hover-Transitions:** immer 0.2s ease — nicht langsamer. **Theme-Switch:** background-color 0.3s, border-color 0.3s, color 0.2s — alles smooth.

--------------------------------------------------------------------------------

#### 7. Editions — Intern vs. Public
##### 7.1 Internal Hub (`server.py`)
*  Vollständige Atmosphäre (alle 5 Background-Layer)
*  Ember / Neon / Light Theme Switcher
*  Mission Control, Cron Jobs, Terminal, Cameras, PRISM-Docs
*  Sidebar mit Theme-Switcher + Status-Dot
*  Barlow Condensed als Display Font

##### 7.2 Public Site (`build.py` → Cloudflare Pages)
*  Reduzierte Features (kein Terminal, keine Cameras, keine privaten Docs)
*  Eigenes CSS-Set: `--neon-cyan: #00f0ff` (etwas heller)
*  **Orbitron** als Display Font (statt Barlow Condensed)
*  Square CSS Grid statt Hex Grid
*  Hamburger-Menu für Mobile
*  Öffentlich: Docs, News, Research

--------------------------------------------------------------------------------

#### 8. Logo & Identity
##### PRISM Hub Wordmark
*  Font: **Barlow Condensed 800** (intern) / **Orbitron 700** (public)
*  Color: `var(--accent-primary)` (theme-adaptiv)
*  Tracking: 0.15em
*  UPPERCASE: ja
*  Glow: `text-shadow: 0 0 20px var(--rune-glow, rgba(13,232,245,0.6))`

##### Icon
*  Emoji: 🔮 (Crystal Ball / Prism)
*  Animation: rune-pulse loop
*  Filter: `drop-shadow(0 0 8px var(--accent-primary))`

##### Tagline
*  Font: JetBrains Mono, 0.8rem
*  Color: `--text-secondary`
*  Prefix `//` in `--accent-ember`

--------------------------------------------------------------------------------

#### 9. Voice & Tone (UI Copy)
| Element | Stil | Beispiel |
| ------ | ------ | ------ |
| Page Title | Kurz, CAPS, direkt | MISSION CONTROL |
| Subtitle | Slash-Style, lowercase | // live feed // auto-refresh aktiv |
| Empty State | Nüchtern, technisch | no active sessions detected |
| Error | Präzise, kein Drama | connection refused — cam offline |
| Success | Knapp | synced ✓ |

**Verboten:** Ausrufezeichen, Marketing-Sprache, „Großartig!", Emojis im UI-Flow (nur in Navicons).

--------------------------------------------------------------------------------

#### 10. Do's & Don'ts
##### ✅ Do
*  Schwarzes Hintergrund als Basis.
*  `var(--accent-primary)` als primären Akzent (nicht hard-coded).
*  Alle 5 Atmosphären-Layer aktiv halten.
*  Glassmorphism für Cards.
*  Mono-Font für alle Datenwerte.
*  Glows sparsam aber bewusst einsetzen.
*  Hex Grid + Partikel für lebendige Atmosphäre.
*  Scanlines + Noise für subtile CRT-Textur.
*  **Update:** Ein 8-Punkt-Grid-System verwenden und klare Texthierarchien aufbauen.
*  **Update:** Modernes CSS (`corner-shape`) für authentische Sci-Fi Ecken nutzen.

##### ❌ Don't
*  Weiße oder helle Hintergründe (außer Light Theme).
*  Mehr als 2 Neon-Farben gleichzeitig prominent.
*  Fette Farbflächen (nur Akzente).
*  Hard-coded Farb-Hex-Codes — immer `var(--...)` nutzen.
*  Partikel-Canvas auf Mobile (Performance).
*  Serifenschriften.
*  Schatten ohne Farbe (nur Glow, kein grauer Box-Shadow).
*  **Update:** Identische Schriftgrößen für Haupt- und Unterkategorien verwenden.
*  **Update:** Schlechte Kontrastkombinationen (z. B. roter Text auf rotem Panel) zulassen.
