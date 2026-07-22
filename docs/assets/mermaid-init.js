// Render Mermaid code fences to crisp, zoomable vector SVG (client-side).
(function () {
  function render() {
    if (!window.mermaid) return;
    mermaid.initialize({ startOnLoad: false, theme: "dark", securityLevel: "loose" });
    mermaid.run({ querySelector: "pre.mermaid, .mermaid" });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render);
  else render();
})();
