# Engineering Command Center V1.0

Review branch only. Do not merge or publish without owner approval.

- The four public engineering projects are linked. VOLTEACH card is prepared at assets/projects/volteach.svg but intentionally not shown or linked: the existing portfolio review requires a security review before adding it. No private project is included.
- Project SVGs are custom illustrations, not screenshots or measurements. The GitHub-rendered profile supports image links, not arbitrary dashboard HTML/CSS. Check desktop and mobile plus light and dark themes.
- Local banner, technology fallback and animated SVG work without an external graphics service. Skill Icons and LinkedIn badge are optional external images with text fallback.
- Telemetry is generated from public owned non-fork repositories via REST and GitHub contribution aggregate via GraphQL. No private repo names, code or secrets are output. Calendar aggregate may include private activity according to visibility settings. No synthetic counts are displayed.
- Preview workflow is read-only and tests offline fixtures; scheduled refresh only runs on the default branch after separate merge approval. No current main modification. Generated placeholders remain until a successful refresh. GitHub scheduled runs are not guaranteed at exact times.
- Spotify deliberately disconnected. No token, app, workflow or secret added. After separate authorization: review current Spotify API requirements, decide public music visibility, store secrets in repository Actions secrets, and implement narrowly scoped integration. Never paste credentials into the README or chat.
- Review checklist: inspect README on branch, test links and mobile wrapping, confirm project claims, inspect workflow permissions and CI results, confirm animation rendering; then separately decide whether to merge.
