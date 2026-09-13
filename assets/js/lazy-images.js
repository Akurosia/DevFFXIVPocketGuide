(() => {
  "use strict";

  function markLoaded(image) {
    image.classList.add("is-loaded");
  }

  function prepareImage(image) {
    if (image.complete && image.naturalWidth > 0) {
      markLoaded(image);
      return;
    }
    image.addEventListener("load", () => markLoaded(image), { once: true });
  }

  const images = Array.from(
    document.querySelectorAll(".index-item__background-image")
  );

  images.forEach(prepareImage);

  if (!("IntersectionObserver" in window)) {
    images.forEach(image => image.setAttribute("fetchpriority", "auto"));
    return;
  }

  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const image = entry.target;
        image.setAttribute("fetchpriority", "auto");
        observer.unobserve(image);
      });
    },
    { rootMargin: "700px 0px" }
  );

  images.forEach(image => observer.observe(image));
})();
