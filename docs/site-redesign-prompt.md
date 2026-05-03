# Whole Site Redesign Prompt

Use this prompt when you want another project to adopt the same overall visual direction as the current Bestiarium-inspired Pocket Guide redesign.

## Prompt

Redesign the entire site as a cohesive dark fantasy MMO codex interface inspired by FFXIV UI language.

Visual direction:
- Use a cool charcoal, slate, steel-blue, and ice palette.
- Avoid brown, brass, amber, or gold as dominant colors.
- The site should feel like layered lacquered panels, glass overlays, and engraved in-universe navigation.
- Keep the result atmospheric and game-like, not SaaS-like.

Global shell:
- Build the entire project around a shared shell with a strong sidebar, a framed hero header, and content panels that all belong to the same system.
- The sidebar should feel like a navigation console with grouped sections, compact icons, subtle active states, and dark inset surfaces.
- The page header should feel like a mission board or codex banner with artwork, title, subtitle, and utility links inside one framed surface.
- The footer should look like another system panel, not plain text floating on the page.

Content styling:
- Search bars, filters, counters, cards, accordions, and tables should all share the same material language.
- Use compact spacing, 8-14px radii, soft internal highlights, and restrained glow.
- Cards should feel layered and slightly inset rather than flat.
- Tables should be readable on dark surfaces and use cool-toned headers.
- Forms and buttons should use dark panel fills with blue focus and hover states.

Index/list pages:
- Expansion dividers or section headers should look like framed category bars.
- Item cards should use dark image overlays, framed icons, and strong title contrast.
- Hover states should feel precise and tactile, not overly animated.

Guide/detail pages:
- Side metadata should live in a dedicated panel with the same shell language as the sidebar.
- Main content should render as a sequence of codex modules or combat dossier panels.
- Accordions, alerts, and embedded content blocks should inherit the same surface treatment.

Mood and texture:
- Use layered gradients, subtle scanline/noise overlays, light inner borders, and controlled shadow depth.
- Favor restrained atmospheric depth over glossy or neon effects.
- Preserve readability first, but let the interface still feel immersive and authored.

Do not:
- Default back to Bootstrap white cards or plain gray admin surfaces.
- Use warm metallic palettes as the main theme.
- Use oversized pills, generic dashboard widgets, or modern app-store aesthetics.

## Transfer Recipe

When porting this to another project, keep these layers separate:

1. Base tokens
   Define the site-wide palette, border, text, and shadow tokens in one place.
2. Shell layer
   Apply the design to the global wrappers: body, sidebar, header, footer, page frame.
3. Component layer
   Skin shared primitives: cards, tables, forms, buttons, accordions, tabs, search bars.
4. Feature layer
   Let specialist pages keep their own CSS, but make them inherit the shell and token system.

## Suggested Token Set

```css
:root {
  --bg-deep: #1c2128;
  --bg-surface: #242a31;
  --bg-panel: #2c333b;
  --bg-panel-strong: #313942;
  --line-soft: rgba(178, 196, 206, 0.08);
  --line-strong: rgba(131, 176, 209, 0.22);
  --text-main: #e5edf5;
  --text-muted: #aebcc9;
  --text-soft: #8f9baa;
  --accent: #83b0d1;
  --accent-soft: #96bdb9;
  --accent-deep: #2f5889;
  --shadow-panel: 0 18px 42px rgba(0, 0, 0, 0.32);
}
```

## Short Prompt

Redesign this whole site as a dark fantasy MMO codex with a cool charcoal, slate, steel-blue, and ice palette. Give the project a unified sidebar, framed hero header, panel-based content system, dark search and filter surfaces, codex-style cards, and readable dark tables. Make it feel like an in-universe FFXIV field manual instead of a Bootstrap site.
