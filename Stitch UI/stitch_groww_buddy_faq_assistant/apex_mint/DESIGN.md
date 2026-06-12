---
name: Apex Mint
colors:
  surface: '#0d1511'
  surface-dim: '#0d1511'
  surface-bright: '#333b37'
  surface-container-lowest: '#08100c'
  surface-container-low: '#161d19'
  surface-container: '#1a211d'
  surface-container-high: '#242c28'
  surface-container-highest: '#2f3732'
  on-surface: '#dce5de'
  on-surface-variant: '#bacac1'
  inverse-surface: '#dce5de'
  inverse-on-surface: '#2a322e'
  outline: '#85948c'
  outline-variant: '#3c4a43'
  surface-tint: '#2fe0aa'
  primary: '#44edb7'
  on-primary: '#003828'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#006c4f'
  secondary: '#c2c7d0'
  on-secondary: '#2c3138'
  secondary-container: '#42474f'
  on-secondary-container: '#b1b5be'
  tertiary: '#c7d5e2'
  on-tertiary: '#25323c'
  tertiary-container: '#acb9c6'
  on-tertiary-container: '#3d4a55'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#dee2ec'
  secondary-fixed-dim: '#c2c7d0'
  on-secondary-fixed: '#171c23'
  on-secondary-fixed-variant: '#42474f'
  tertiary-fixed: '#d7e4f2'
  tertiary-fixed-dim: '#bbc8d6'
  on-tertiary-fixed: '#101d27'
  on-tertiary-fixed-variant: '#3c4853'
  background: '#0d1511'
  on-background: '#dce5de'
  surface-variant: '#2f3732'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-max-width: 1200px
  gutter: 1.5rem
  margin-mobile: 1rem
  margin-desktop: 2.5rem
  stack-sm: 0.5rem
  stack-md: 1rem
  stack-lg: 2rem
---

## Brand & Style

The design system is engineered for a premium fintech experience, focusing on high-performance investment and financial clarity. The brand personality is professional, modern, and high-energy, evoking a sense of growth and precision.

The style is a sophisticated **Modern-Minimalist Dark Mode**. It utilizes a deep charcoal foundation to reduce eye strain during long trading sessions, while leveraging high-contrast mint accents to direct user focus toward critical actions. The interface avoids unnecessary decorative elements, favoring clean lines, generous whitespace (negative space), and a systematic approach to data visualization that makes complex financial information feel approachable and breathable.

## Colors

The palette is optimized for a dark-first environment.

- **Primary (#00D09C):** Reserved exclusively for "success" states, growth indicators, and primary call-to-action buttons. 
- **Background (#0C0F12):** A deep, neutral charcoal that provides the foundation for the entire application.
- **Surface (#1D2229):** Used for cards and modals to create a clear visual hierarchy against the background.
- **Status Colors:** Use the primary mint for gains/positive movement and the warning red (#FF5A5A) for losses/negative movement or errors.
- **Text:** High-contrast white is used for readability of data, while muted slate-gray handles secondary labels and metadata to prevent visual noise.

## Typography

This design system uses **Inter** for its exceptional legibility in data-heavy environments. 

- **Weight Strategy:** Use Bold (700) for primary headers to create a strong anchor. Use Medium (500) for interactive labels and Semibold (600) for sub-headers.
- **Numerical Data:** For stock prices and balances, use `headline-md` or `headline-lg` with a slight tabular-nums setting if available to ensure digits align vertically in lists.
- **Secondary Text:** All labels for data fields (e.g., "Market Cap," "P/E Ratio") should use `label-md` with the Text Secondary color.

## Layout & Spacing

The layout follows a **Fluid Grid** model with a max-width of 1200px for desktop.

- **Grid:** A 12-column grid is used for desktop, collapsing to 4 columns on mobile.
- **Rhythm:** An 8px base grid drives all spacing. 
- **Desktop:** Use 2.5rem (40px) outer margins to give the content a "premium" centered feel.
- **Mobile:** Margins reduce to 1rem (16px). Cards should generally be full-width on mobile with 12px internal padding.
- **Vertical Spacing:** Use `stack-lg` to separate major sections (e.g., "Your Investments" vs "Market News") and `stack-sm` for internal card elements.

## Elevation & Depth

This design system avoids heavy shadows to maintain a clean, modern aesthetic. Depth is communicated through **Tonal Layering**:

1.  **Level 0 (Floor):** Background (#0C0F12) - The base layer.
2.  **Level 1 (Card/Surface):** Surface (#1D2229) - Used for primary content containers. These should have a subtle 1px border (#2A323D) to define edges.
3.  **Level 2 (Modals/Popovers):** Surface (#1D2229) but with a soft ambient shadow (0px 8px 24px rgba(0,0,0,0.5)) and a slightly lighter border (#3A4450).

**Glassmorphism** may be used sparingly for sticky navigation bars (Background color at 80% opacity with a 12px blur) to maintain context while scrolling.

## Shapes

The shape language balances approachability with professional structure.

- **Cards:** Use `rounded-lg` (16px) for major dashboard cards and containers.
- **Interactive Elements:** Buttons and Input fields use a **Pill-shaped** (full radius) style to make them feel distinct from the structural containers and highly touch-friendly.
- **Small Elements:** Chips and Tags use a 4px or 8px radius depending on size.

## Components

- **Buttons:** 
  - *Primary:* Pill-shaped, Primary Mint background, black or very dark green text for maximum contrast.
  - *Secondary:* Pill-shaped, Surface color background, 1px border (#2A323D), White text.
- **Input Fields:** Pill-shaped, Surface color background, 1px border (#2A323D). On focus, the border transitions to the Primary Mint color.
- **Cards:** 16px corner radius, #1D2229 background, #2A323D 1px border. No shadow for standard state.
- **Chips/Filters:** Small pill shapes. Active state uses a subtle Primary Mint tint (10% opacity) with a solid Primary Mint border.
- **List Items:** Use a 1px bottom border (#2A323D) for list separation. Items should have a subtle hover state that lightens the background to #242B33.
- **Stock Tickers:** Positive values always use Primary Mint; Negative values use Warning Red. Use a small up/down arrow icon alongside the value.