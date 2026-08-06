# Accessibility Requirements

Accessibility is part of the core acceptance criteria. The target for the demo path is WCAG 2.2 AA, tested with keyboard and macOS VoiceOver.

## Interaction

- Every action is available by keyboard without timing-dependent gestures.
- Focus order follows the visual and semantic order.
- Focus is visible and moves intentionally after upload, errors, modal actions, and quiz feedback.
- Touch targets are comfortably sized and do not require precision.
- No important meaning depends only on color, position, sound, or animation.

## Content

- Use semantic headings, lists, tables, buttons, labels, and landmarks.
- Prefer short sentences and explain financial terminology on first use.
- Display numbers with units, currency, period, and comparison basis.
- Keep severity wording visible next to icons and colors.
- Mark assumptions and `needs_review` in direct language.
- Avoid countdowns and unnecessary auto-advancing content.

## Visual

- Support browser zoom and text resizing to 200% without loss of content or action.
- Maintain sufficient text, control, focus, and non-text contrast.
- Reflow on mobile without horizontal scrolling except genuinely tabular content.
- Respect reduced-motion preferences.
- Do not place essential evidence only inside an image highlight; provide equivalent text.

## Screen Reader

- Give uploaded documents, findings, evidence links, formula results, and quiz feedback descriptive names.
- Announce processing-state changes through a restrained live region.
- Associate validation messages with the relevant input.
- Treat decorative severity graphics as hidden and expose the severity in text.
- Provide a text list of source excerpts even when visual bounding boxes are available.

## Explanation Modes

- Modes are user-selected preferences, not inferred diagnoses.
- Changing mode must announce the new mode and preserve current position when possible.
- Number-First must pronounce rates and currencies unambiguously.
- Example-First must label examples as examples, not guaranteed outcomes.
- Optional text-to-speech must have pause, resume, stop, and visible current section.

## Release Checks

- Complete the P0 flow with keyboard only.
- Complete the P0 flow with macOS VoiceOver.
- Check 200% zoom and narrow mobile viewport.
- Verify error, loading, `needs_review`, and wrong-answer feedback.
- Run automated accessibility checks, then perform manual checks; automation alone is insufficient.
