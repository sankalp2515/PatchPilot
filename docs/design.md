# PatchPilot experience and design rationale

## Direction
The product is an inspection bench for integration engineers. Warm paper (#f6f5ef), graphite ink (#242621), safety orange (#e65224), muted olive (#686c60), rule gray (#dddfd4), and success green make the interface feel like a working engineering dossier. Orange belongs to primary actions and the brand, not every metric. The decisive visual is the repair dossier: contract, diff, evidence chain, review outcome.

The visual identity uses real adapter syntax, historical Stripe version context, protected tests and explicit scope boundaries. The dossier illustration helps engineers understand the review workflow before opening an investigation. Trust comes from inspectable results and clear limitations.

## Typography and layout
Georgia carries the large editorial landing headlines and workspace page headings. Trebuchet MS gives utility text a human, slightly technical voice without requiring network fonts. Consolas/monospace is reserved for code and hashes. Native font fallbacks keep offline replay self-contained. Heading scale is 83/52/25 px at desktop and 60/42/23 px on mobile; body text is 12â€“17 px with 1.65 line height and constrained line length.

The landing uses a two-column hero, asymmetric editorial sections, a dark proof section, and a quiet footer. All text is left aligned except the tool-role strip. Desktop content caps at 1440 px; 64 px side gutters become 24 px on mobile. Sections collapse to a single reading column, including the proof and pricing layouts. The workspace retains a persistent navigation rail, responsive investigation cards, searchable history, inspection tabs, and a modal incident editor.

## Section decisions
- Navigation: anchor links explain the product; opening `/app` is an ordinary link so direct navigation and browser history work without a router dependency.
- Hero: the value is contract preservation, not autonomous production repair. The sample dossier is explicitly labeled as an illustration and directs readers to the actual replay.
- Tool roles: SerpApi, neatlogs, Entire and cfo.ai describe their role. They are neither customer endorsements nor a claim that the current machine has all accounts connected.
- Workflow: three ordered steps are an actual sequenceâ€”intake, evidence-led repair, independent verification and export.
- Proof story: a historical Stripe invoice migration provides a concrete narrative. Baseline, source evidence and post-repair scope have different jobs and remain distinct.
- Benefits: explain review quality, useful refusal, portable evidence and bounded execution. No fabricated savings or testimonials.
- Pricing: local prototype is free; the $79 team amount and $19 individual concept match the saved financial hypotheses and are clearly planning assumptions with no checkout or billing. Provider usage remains separate.
- FAQ: native `details` gives keyboard-accessible disclosure for scope, keys, data handling and verification limits.
- Install: verified repository URL, combined Windows setup/start command and Docker Compose alternative; a workspace CTA helps people already running the server.
- Workspace: preserve editable incident intake, replay/live selection, polling, recovery, cancellation, evidence, adapter download, protected case review and report export. Configuration states show which providers are available on the current installation. Historical runs without proof remain readable with an explicit absence message.

## Components and tokens
Primary orange buttons, neutral outline secondary buttons, a compact workflow mark, 5 px control radii, 9 px document-panel radii, 1 px rules and restrained layered paper shadow establish hierarchy. The sample dossier alone is slightly tilted on desktop; the mobile document is upright. Proof hashes wrap at arbitrary character boundaries so real SHA256 values never create horizontal overflow. Acceptance counts and independent audit counts remain separate.

## Motion and accessibility
No background animation or section entrance effects. User-triggered disclosure and focus states carry interaction. Reduced-motion disables animation and transition globally. Native links and buttons, visible orange focus rings, a landing skip link, semantic navigation and main landmarks, explicit form labels, and the existing modal keyboard handling support keyboard use. Mobile breakpoints remove nonessential navigation links while preserving the primary workspace route. Code samples scroll within their panel.

## Verification
Unit tests cover landing routing without backend requests, workspace intake/recovery, actual integration states, proof rendering and old-run compatibility. Playwright exercises landing-to-workspace navigation, no mobile document overflow, replay recovery, exports, editable invalid JSON and credential rejection. Production build validates the TypeScript boundary.
