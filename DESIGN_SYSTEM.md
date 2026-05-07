# GeekBrain AI Design System

## Mission
Create implementation-ready, token-driven UI guidance for GeekBrain AI chatbot that is optimized for consistency, accessibility, and fast delivery across dashboard web app.

## Brand
- **Product/brand**: GeekBrain AI - Internal System Assistant
- **Audience**: Authenticated users and operators
- **Product surface**: Dashboard web app
- **Visual style**: Clean, functional, implementation-oriented

---

## Design Tokens

### Typography
```css
--font-family-primary: 'Plus Jakarta Sans', -apple-system, sans-serif
--font-size-xs: 12px
--font-size-sm: 12.96px
--font-size-base: 12.96px
--font-size-md: 13.33px
--font-size-lg: 16px
--font-size-xl: 16.56px
--font-size-2xl: 19.2px
--font-size-3xl: 22.4px
--font-size-4xl: 25.6px
--font-weight-base: 400
--font-weight-semibold: 600
--font-weight-bold: 700
--line-height-base: normal
```

### Colors
```css
/* Text */
--color-text-primary: #1a1a1a
--color-text-secondary: #ffffff
--color-text-inverse: #1e293b
--color-text-muted: #6b7280

/* Surface */
--color-surface-base: #000000
--color-surface-strong: #0d1117
--color-surface-light: #ffffff
--color-surface-elevated: #f9fafb

/* Border */
--color-border-default: #e5e7eb
--color-border-strong: #c4d5dd

/* Accent */
--color-accent-primary: #7c83fd
--color-accent-hover: #6366f1

/* Semantic */
--color-success: #22c55e
--color-warning: #fcd34d
--color-error: #ef4444
```

### Spacing
```css
--space-1: 6.4px
--space-2: 8px
--space-3: 9.6px
--space-4: 13.6px
--space-5: 17.28px
--space-6: 57.6px
```

### Radius
```css
--radius-xs: 16px
--radius-sm: 50px
--radius-md: 12px
--radius-lg: 8px
```

### Shadow
```css
--shadow-1: rgba(29, 29, 29, 0.05) 0px 8px 17px 0px
--shadow-2: 0 1px 3px rgba(0, 0, 0, 0.08)
```

### Motion
```css
--motion-instant: 250ms
--motion-fast: 650ms
```

---

## Component Rules

### Tables (9 instances)

**Anatomy:**
- Header row with dark background (`--color-surface-base`)
- Body rows with light background (`--color-surface-light`)
- Hover state with elevated background (`--color-surface-elevated`)

**States:**
- **Default**: White background, subtle shadow
- **Hover**: Light gray background, smooth transition
- **Focus-visible**: 2px accent outline with 2px offset

**Typography:**
- Header: `--font-size-xs`, `--font-weight-semibold`, uppercase, 0.5px letter-spacing
- Body: `--font-size-md`, `--font-weight-base`

**Spacing:**
- Header padding: `--space-4` vertical, `--space-5` horizontal
- Body padding: `--space-3` vertical, `--space-5` horizontal
- Margin: `--space-4` top/bottom

**Accessibility:**
- ✅ Must use semantic `<table>`, `<thead>`, `<tbody>`, `<th>`, `<td>` elements
- ✅ Must have sufficient contrast (WCAG AA: 4.5:1 for text)
- ✅ Must support keyboard navigation
- ✅ Hover state must be visible and smooth

**Example:**
```html
<table class="md-table">
  <thead>
    <tr>
      <th>Service</th>
      <th>Status</th>
      <th>Cost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>PaymentGW</td>
      <td>Active</td>
      <td>$16,500</td>
    </tr>
  </tbody>
</table>
```

---

### Buttons (38 instances)

**Variants:**
1. **Primary**: Accent background, white text
2. **Secondary**: Light background, dark text
3. **Ghost**: Transparent background, accent text

**States:**
- **Default**: Base colors, no transform
- **Hover**: Darker shade, subtle lift (`translateY(-1px)`)
- **Focus-visible**: 2px accent outline, 2px offset
- **Active**: Pressed state (`translateY(0)`)
- **Disabled**: 50% opacity, no pointer events

**Typography:**
- Font size: `--font-size-xs`
- Font weight: `--font-weight-semibold`
- Font family: `--font-family-primary`

**Spacing:**
- Padding: `--space-1` vertical, `--space-4` horizontal
- Border radius: `--radius-sm` (pill shape)

**Accessibility:**
- ✅ Must have visible focus indicator
- ✅ Must support keyboard activation (Enter/Space)
- ✅ Must have descriptive text or aria-label
- ✅ Disabled state must have `disabled` attribute

---

### Citations (Enhanced Cards)

**Anatomy:**
- Index number badge (circular)
- File icon (📄)
- File name
- Confidence score badge
- Text snippet (150 chars)

**States:**
- **Default**: Green background (#f0fdf4), left border
- **Hover**: Darker green (#dcfce7), shadow, slight translate
- **Focus-visible**: Accent outline
- **Active**: Modal opens with full content

**Typography:**
- File name: `--font-size-xs`, `--font-weight-semibold`
- Snippet: `--font-size-xs`, italic, 90% opacity

**Spacing:**
- Padding: `--space-3` vertical, `--space-4` horizontal
- Gap between items: `--space-2`

**Accessibility:**
- ✅ Must be keyboard accessible (Tab to focus, Enter to open)
- ✅ Must have role="button" or be a `<button>` element
- ✅ Must announce content to screen readers

---

### Modal (Citation Detail)

**Anatomy:**
- Dark overlay (70% opacity black)
- White content card with rounded corners
- Header with file name and close button
- Scrollable body with full document content
- Footer with metadata

**States:**
- **Hidden**: `display: none`
- **Active**: `display: flex`, centered
- **Closing**: Fade out animation

**Keyboard behavior:**
- **Escape**: Close modal
- **Tab**: Trap focus within modal
- **Enter on close button**: Close modal

**Accessibility:**
- ✅ Must trap focus when open
- ✅ Must restore focus to trigger element when closed
- ✅ Must have `role="dialog"` and `aria-modal="true"`
- ✅ Must have `aria-labelledby` pointing to title
- ✅ Must close on Escape key
- ✅ Must close on outside click

---

## Accessibility Requirements

### WCAG 2.2 AA Compliance

**Contrast:**
- ✅ Text on background: Minimum 4.5:1 ratio
- ✅ Large text (18px+): Minimum 3:1 ratio
- ✅ UI components: Minimum 3:1 ratio

**Keyboard:**
- ✅ All interactive elements must be keyboard accessible
- ✅ Focus order must be logical
- ✅ Focus indicators must be visible (2px outline, 2px offset)
- ✅ No keyboard traps

**Screen Readers:**
- ✅ Semantic HTML elements preferred
- ✅ ARIA labels for non-semantic elements
- ✅ Status messages announced with `aria-live`
- ✅ Loading states announced

**Motion:**
- ✅ Respect `prefers-reduced-motion` media query
- ✅ Animations must be subtle and purposeful
- ✅ No auto-playing animations over 5 seconds

---

## Content & Tone

**Writing Style:**
- Concise, confident, implementation-focused
- Use active voice
- Avoid jargon unless necessary
- Be specific with numbers and names

**Button Labels:**
- ✅ "Send message" (descriptive)
- ✅ "New chat" (clear action)
- ❌ "Go" (ambiguous)
- ❌ "Click here" (non-descriptive)

**Error Messages:**
- ✅ "Failed to load chat history. Please refresh the page."
- ❌ "Error 500"

---

## Anti-Patterns

### ❌ Don't Do This:

1. **Low contrast text**
   ```css
   /* Bad: #aaa on #fff = 2.3:1 ratio */
   color: #aaa;
   background: #fff;
   ```

2. **Hidden focus indicators**
   ```css
   /* Bad: Removes focus outline */
   button:focus {
     outline: none;
   }
   ```

3. **One-off spacing**
   ```css
   /* Bad: Random spacing value */
   padding: 13px;
   
   /* Good: Use design token */
   padding: var(--space-4);
   ```

4. **Non-semantic HTML**
   ```html
   <!-- Bad: div as button -->
   <div onclick="submit()">Submit</div>
   
   <!-- Good: Semantic button -->
   <button onclick="submit()">Submit</button>
   ```

5. **Ambiguous labels**
   ```html
   <!-- Bad: Non-descriptive -->
   <button>OK</button>
   
   <!-- Good: Descriptive -->
   <button>Save changes</button>
   ```

---

## QA Checklist

### Before Shipping:

**Visual:**
- [ ] All colors use design tokens (no raw hex values)
- [ ] All spacing uses design tokens
- [ ] All typography uses design tokens
- [ ] Consistent border radius across components
- [ ] Shadows applied consistently

**Accessibility:**
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible on all focusable elements
- [ ] Contrast ratios meet WCAG AA (4.5:1 for text)
- [ ] Screen reader tested with NVDA/JAWS
- [ ] No keyboard traps
- [ ] Semantic HTML used where possible

**Functionality:**
- [ ] All states defined (default, hover, focus, active, disabled)
- [ ] Loading states implemented
- [ ] Error states implemented
- [ ] Empty states implemented
- [ ] Long content handled gracefully
- [ ] Responsive behavior tested

**Content:**
- [ ] All labels descriptive and clear
- [ ] Error messages helpful and actionable
- [ ] No jargon or ambiguous terms
- [ ] Consistent tone throughout

**Performance:**
- [ ] Animations smooth (60fps)
- [ ] No layout shifts
- [ ] Fast load times (<3s)
- [ ] Optimized images and assets

---

## Migration Notes

### From Old Design to New Design System:

1. **Replace all hardcoded colors with tokens**
   ```css
   /* Before */
   background: #7c83fd;
   
   /* After */
   background: var(--color-accent-primary);
   ```

2. **Replace all hardcoded spacing with tokens**
   ```css
   /* Before */
   padding: 12px 16px;
   
   /* After */
   padding: var(--space-4) var(--space-5);
   ```

3. **Add focus-visible states to all interactive elements**
   ```css
   button:focus-visible {
     outline: 2px solid var(--color-accent-primary);
     outline-offset: 2px;
   }
   ```

4. **Import Plus Jakarta Sans font**
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
   ```

---

## Component Density

Current page component usage:
- **Cards**: 141 instances (citations, history items, messages)
- **Buttons**: 38 instances (send, level selector, nav)
- **Tables**: 9 instances (AI responses with structured data)
- **Lists**: 6 instances (questions sidebar, history)
- **Links**: 1 instance (navigation)
- **Navigation**: 1 instance (top nav)

---

## Success Metrics

**Consistency:**
- 100% of components use design tokens
- 0 one-off spacing or color values
- 0 accessibility violations

**Performance:**
- Page load < 3 seconds
- Time to interactive < 5 seconds
- 60fps animations

**Accessibility:**
- WCAG 2.2 AA compliant
- 0 critical accessibility issues
- Keyboard navigation fully functional

---

**Last Updated**: 2026-05-07
**Version**: 1.0.0
**Status**: ✅ Implemented
