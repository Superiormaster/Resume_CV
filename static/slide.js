document.addEventListener("DOMContentLoaded", () => {
        const openDrawer = document.getElementById("openDrawer");
        const drawer = document.getElementById("mainDrawer");
        const overlay = document.getElementById("drawerOverlay");
        const toggleBtn = document.getElementById("toggle-btn");

        if (!openDrawer || !drawer || !overlay) return;

        function toggleDrawer(show) {
            const isVisible = show ?? drawer.getAttribute("aria-hidden") === "true";
            drawer.setAttribute("aria-hidden", !isVisible);
            overlay.dataset.hidden = !isVisible;
            openDrawer.setAttribute("aria-expanded", isVisible);
            document.body.style.overflow = isVisible ? "hidden" : "";
        }

        openDrawer.addEventListener("click", () => toggleDrawer(true));
        overlay.addEventListener("click", () => toggleDrawer(false));

        let darkMode = localStorage.getItem("darkMode") === "true";

        if (darkMode) {
            document.body.classList.add("dark-mode");
            toggleBtn.textContent = "Light Mode";
        }

        toggleBtn.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode", darkMode);
            darkMode = !darkMode;
            toggleBtn.textContent = darkMode ? "Light Mode" : "Dark Mode";
        });

});
