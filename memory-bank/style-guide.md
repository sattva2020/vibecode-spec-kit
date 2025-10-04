# Style Guide - RAG-Powered Code Assistant

**Version**: 1.0  
**Date**: 04.01.2025  
**Target**: Developer-focused AI interface design

## 🎨 DESIGN PHILOSOPHY

### Core Principles
- **Developer-Centric**: Designed for developers, by developers
- **Minimal Cognitive Load**: Reduce mental overhead in AI interactions
- **Context-Aware**: Visual design adapts to coding context
- **Privacy-First**: Visual indicators of local processing
- **Performance-Oriented**: Fast, responsive interface elements

### Design Language
- **Modern & Clean**: Contemporary design with developer aesthetics
- **Functional Beauty**: Form follows function, beauty through utility
- **Consistent Patterns**: Predictable interaction patterns
- **Accessible**: WCAG 2.1 AA compliance

---

## 🎨 COLOR PALETTE

### Primary Colors
```css
/* Primary Blue - Trust, Intelligence, Technology */
--primary-50: #eff6ff;
--primary-100: #dbeafe;
--primary-200: #bfdbfe;
--primary-300: #93c5fd;
--primary-400: #60a5fa;
--primary-500: #3b82f6;  /* Main Primary */
--primary-600: #2563eb;
--primary-700: #1d4ed8;
--primary-800: #1e40af;
--primary-900: #1e3a8a;
```

### Secondary Colors
```css
/* Secondary Green - Success, Learning, Growth */
--secondary-50: #f0fdf4;
--secondary-100: #dcfce7;
--secondary-200: #bbf7d0;
--secondary-300: #86efac;
--secondary-400: #4ade80;
--secondary-500: #22c55e;  /* Main Secondary */
--secondary-600: #16a34a;
--secondary-700: #15803d;
--secondary-800: #166534;
--secondary-900: #14532d;
```

### Neutral Colors
```css
/* Neutral Grays - Text, Backgrounds, Borders */
--neutral-50: #fafafa;
--neutral-100: #f5f5f5;
--neutral-200: #e5e5e5;
--neutral-300: #d4d4d4;
--neutral-400: #a3a3a3;
--neutral-500: #737373;
--neutral-600: #525252;
--neutral-700: #404040;
--neutral-800: #262626;
--neutral-900: #171717;
```

### Status Colors
```css
/* Success */
--success-50: #f0fdf4;
--success-500: #22c55e;
--success-600: #16a34a;

/* Warning */
--warning-50: #fffbeb;
--warning-500: #f59e0b;
--warning-600: #d97706;

/* Error */
--error-50: #fef2f2;
--error-500: #ef4444;
--error-600: #dc2626;

/* Info */
--info-50: #eff6ff;
--info-500: #3b82f6;
--info-600: #2563eb;
```

### AI-Specific Colors
```css
/* AI Processing - Purple for AI operations */
--ai-50: #faf5ff;
--ai-100: #f3e8ff;
--ai-500: #a855f7;
--ai-600: #9333ea;

/* Learning Indicator - Gradient for active learning */
--learning-start: #22c55e;
--learning-end: #3b82f6;

/* Local Processing - Teal for privacy/local */
--local-50: #f0fdfa;
--local-500: #14b8a6;
--local-600: #0d9488;
```

---

## 📝 TYPOGRAPHY

### Font Families
```css
/* Primary Font - Inter (Modern, Developer-friendly) */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Code Font - JetBrains Mono (Excellent for code) */
--font-code: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

/* Monospace - For UI elements requiring fixed width */
--font-mono: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
```

### Font Sizes
```css
/* Headings */
--text-xs: 0.75rem;    /* 12px - Labels, captions */
--text-sm: 0.875rem;   /* 14px - Small text, metadata */
--text-base: 1rem;     /* 16px - Body text */
--text-lg: 1.125rem;   /* 18px - Large body text */
--text-xl: 1.25rem;    /* 20px - Small headings */
--text-2xl: 1.5rem;    /* 24px - Medium headings */
--text-3xl: 1.875rem;  /* 30px - Large headings */
--text-4xl: 2.25rem;   /* 36px - Display headings */

/* Code-specific sizes */
--code-xs: 0.75rem;    /* 12px - Inline code */
--code-sm: 0.875rem;   /* 14px - Code blocks */
--code-base: 1rem;     /* 16px - Primary code */
--code-lg: 1.125rem;   /* 18px - Large code */
```

### Font Weights
```css
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Line Heights
```css
--leading-tight: 1.25;
--leading-snug: 1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose: 2;
```

---

## 📏 SPACING SYSTEM

### Base Unit
```css
--space-unit: 0.25rem; /* 4px base unit */
```

### Spacing Scale
```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

### Component Spacing
```css
/* Component internal spacing */
--component-padding-sm: var(--space-2) var(--space-3);
--component-padding-md: var(--space-3) var(--space-4);
--component-padding-lg: var(--space-4) var(--space-6);

/* Component external spacing */
--component-margin-sm: var(--space-2);
--component-margin-md: var(--space-4);
--component-margin-lg: var(--space-6);
```

---

## 🔲 COMPONENT STYLES

### Buttons

#### Primary Button
```css
.btn-primary {
  background: var(--primary-500);
  color: white;
  border: none;
  padding: var(--component-padding-md);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--primary-600);
  transform: translateY(-1px);
}

.btn-primary:active {
  background: var(--primary-700);
  transform: translateY(0);
}
```

#### Secondary Button
```css
.btn-secondary {
  background: transparent;
  color: var(--primary-500);
  border: 1px solid var(--primary-500);
  padding: var(--component-padding-md);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--primary-50);
  border-color: var(--primary-600);
}
```

#### AI Action Button
```css
.btn-ai {
  background: linear-gradient(135deg, var(--ai-500), var(--primary-500));
  color: white;
  border: none;
  padding: var(--component-padding-md);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  font-size: var(--text-sm);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.btn-ai::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.btn-ai:hover::before {
  left: 100%;
}
```

### Input Fields

#### Text Input
```css
.input-text {
  background: var(--neutral-50);
  border: 1px solid var(--neutral-300);
  border-radius: var(--radius-md);
  padding: var(--component-padding-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--neutral-900);
  transition: all 0.2s ease;
}

.input-text:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-100);
  background: white;
}

.input-text::placeholder {
  color: var(--neutral-500);
}
```

#### Code Input
```css
.input-code {
  background: var(--neutral-900);
  border: 1px solid var(--neutral-700);
  border-radius: var(--radius-md);
  padding: var(--component-padding-md);
  font-family: var(--font-code);
  font-size: var(--code-sm);
  color: var(--neutral-100);
  line-height: var(--leading-relaxed);
  transition: all 0.2s ease;
}

.input-code:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-900);
}
```

### Cards & Containers

#### Basic Card
```css
.card {
  background: white;
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}
```

#### AI Suggestion Card
```css
.card-ai-suggestion {
  background: linear-gradient(135deg, var(--ai-50), var(--primary-50));
  border: 1px solid var(--ai-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  position: relative;
  overflow: hidden;
}

.card-ai-suggestion::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, var(--ai-500), var(--primary-500));
}
```

#### Code Block Card
```css
.card-code {
  background: var(--neutral-900);
  border: 1px solid var(--neutral-700);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  font-family: var(--font-code);
  font-size: var(--code-sm);
  color: var(--neutral-100);
  overflow-x: auto;
}
```

---

## 🎭 BORDER RADIUS

```css
--radius-none: 0;
--radius-sm: 0.125rem;   /* 2px */
--radius-md: 0.375rem;   /* 6px */
--radius-lg: 0.5rem;     /* 8px */
--radius-xl: 0.75rem;    /* 12px */
--radius-2xl: 1rem;      /* 16px */
--radius-full: 9999px;
```

---

## 🌊 SHADOWS

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
--shadow-2xl: 0 25px 50px rgba(0, 0, 0, 0.25);

/* AI-specific shadows */
--shadow-ai: 0 4px 12px rgba(168, 85, 247, 0.15);
--shadow-learning: 0 4px 12px rgba(34, 197, 94, 0.15);
```

---

## 🎯 AI-SPECIFIC COMPONENTS

### Learning Indicator
```css
.learning-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  background: linear-gradient(90deg, var(--learning-start), var(--learning-end));
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
```

### Context Badge
```css
.context-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  background: var(--local-100);
  color: var(--local-700);
  border: 1px solid var(--local-200);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}
```

### Suggestion Confidence
```css
.confidence-meter {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.confidence-bar {
  width: 60px;
  height: 4px;
  background: var(--neutral-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--error-500), var(--warning-500), var(--success-500));
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}
```

---

## 📱 RESPONSIVE BREAKPOINTS

```css
/* Mobile First Approach */
--breakpoint-sm: 640px;   /* Small devices */
--breakpoint-md: 768px;   /* Medium devices */
--breakpoint-lg: 1024px;  /* Large devices */
--breakpoint-xl: 1280px;  /* Extra large devices */
--breakpoint-2xl: 1536px; /* 2X large devices */

/* Usage in media queries */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

---

## 🎨 ANIMATIONS & TRANSITIONS

### Standard Transitions
```css
--transition-fast: 0.15s ease;
--transition-normal: 0.2s ease;
--transition-slow: 0.3s ease;

/* Usage */
.element {
  transition: all var(--transition-normal);
}
```

### AI-Specific Animations
```css
/* Thinking animation for AI processing */
@keyframes thinking {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}

.thinking {
  animation: thinking 1.5s infinite;
}

/* Learning pulse for active learning */
@keyframes learning-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.learning-active {
  animation: learning-pulse 2s infinite;
}
```

---

## ♿ ACCESSIBILITY GUIDELINES

### Color Contrast
- **Text**: Minimum 4.5:1 contrast ratio
- **Large Text**: Minimum 3:1 contrast ratio
- **Interactive Elements**: Minimum 3:1 contrast ratio

### Focus States
```css
.focusable:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* Remove default focus for custom styled elements */
.custom-focusable:focus {
  outline: none;
  box-shadow: 0 0 0 3px var(--primary-100);
}
```

### ARIA Labels
- All interactive elements must have proper ARIA labels
- Status changes must be announced to screen readers
- Form validation messages must be properly associated

---

## 🎯 USAGE GUIDELINES

### Do's ✅
- Use semantic HTML elements
- Maintain consistent spacing using the spacing scale
- Apply hover and focus states to interactive elements
- Use the defined color palette consistently
- Ensure proper contrast ratios for accessibility
- Use AI-specific colors for AI-related functionality

### Don'ts ❌
- Don't use colors outside the defined palette
- Don't create custom spacing values
- Don't ignore accessibility requirements
- Don't use AI colors for non-AI functionality
- Don't mix different design patterns without purpose

---

## 🔧 IMPLEMENTATION NOTES

### Tailwind CSS Classes
This style guide is designed to work seamlessly with Tailwind CSS. Most values correspond to Tailwind's default scale with custom extensions for AI-specific components.

### CSS Custom Properties
All design tokens are defined as CSS custom properties for easy theming and customization.

### Component Library
This style guide serves as the foundation for a component library that can be built using React, Vue, or any other framework.

---

**Version**: 1.0  
**Last Updated**: 04.01.2025  
**Maintained By**: RAG-Powered Code Assistant Design Team
