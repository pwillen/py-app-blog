document.addEventListener("DOMContentLoaded", () => {
    const slides = document.querySelectorAll(".album-slide");
    const currentRank = document.querySelector(".current-rank");

    if (!slides.length || !currentRank) {
        return;
    }

    // Track the visibility of every slide.
    const visibility = new Map(
        [...slides].map((slide) => [slide, 0])
    );

    let activeSlide = null;

    const observer = new IntersectionObserver(
        (entries) => {
            // Update visibility for slides that changed.
            entries.forEach((entry) => {
                visibility.set(
                    entry.target,
                    entry.isIntersecting ? entry.intersectionRatio : 0
                );
            });

            // Find the most visible slide overall.
            let mostVisible = null;
            let highestRatio = 0;

            visibility.forEach((ratio, slide) => {
                if (ratio > highestRatio) {
                    highestRatio = ratio;
                    mostVisible = slide;
                }
            });

            if (!mostVisible || mostVisible === activeSlide) {
                return;
            }

            // Update the active slide.
            activeSlide?.classList.remove("is-active");
            mostVisible.classList.add("is-active");
            activeSlide = mostVisible;

            // Update the progress indicator.
            currentRank.textContent =
                activeSlide.dataset.rank.padStart(2, "0");
        },
        {
            threshold: [
                0, 0.05, 0.1, 0.15, 0.2,
                0.25, 0.3, 0.35, 0.4, 0.45,
                0.5, 0.55, 0.6, 0.65, 0.7,
                0.75, 0.8, 0.85, 0.9, 0.95, 1
            ],
        }
    );

    slides.forEach((slide) => {
        observer.observe(slide);
    });
});