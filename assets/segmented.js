/* assets/segmented.js
   Auto-repositions the segmented-control pill on window resize.
   The clientside Dash callback handles tab-change events; this file only
   covers layout reflows (resize, font-loading, container width changes). */

(function () {
  const reposition = (instant) => {
    const container = document.getElementById("map-segmented");
    if (!container) return;
    const pill = container.querySelector(".map-seg-pill");
    const active = container.querySelector("label.map-seg-btn.active");
    if (!pill || !active) return;
    const cRect = container.getBoundingClientRect();
    const lRect = active.getBoundingClientRect();
    if (instant) {
      const prev = pill.style.transition;
      pill.style.transition = "none";
      pill.style.transform = `translateX(${lRect.left - cRect.left}px)`;
      pill.style.width = `${lRect.width}px`;
      requestAnimationFrame(() => { pill.style.transition = prev; });
    } else {
      pill.style.transform = `translateX(${lRect.left - cRect.left}px)`;
      pill.style.width = `${lRect.width}px`;
    }
  };

  const clearMapHover = () => {
    const container = document.getElementById("unified-map");
    if (!container || !window.Plotly || !window.Plotly.Fx) return;
    const plot = container.querySelector(".js-plotly-plot");
    if (plot) window.Plotly.Fx.unhover(plot);
  };

  const bindMapHoverClear = () => {
    const container = document.getElementById("unified-map");
    if (!container || container.dataset.hoverClearBound === "true") return;
    container.dataset.hoverClearBound = "true";
    container.addEventListener("mouseleave", clearMapHover);
    container.addEventListener("pointerleave", clearMapHover);
  };

  window.addEventListener("resize", () => reposition(true));

  // Re-run after web-fonts finish loading so pill width matches final text
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(() => reposition(true));
  }

  bindMapHoverClear();
  new MutationObserver(bindMapHoverClear).observe(document.body, {
    childList: true,
    subtree: true,
  });
})();
