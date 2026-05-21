(() => {
    const body = document.body;
    const sidebar = document.getElementById("sidebar-menu");
    const toggles = document.querySelectorAll("[data-sidebar-toggle]");
    const closers = document.querySelectorAll("[data-sidebar-close]");

    if (!sidebar || !toggles.length) {
        return;
    }

    const isOpen = () => body.classList.contains("sidebar-open");

    const setOpen = (open) => {
        body.classList.toggle("sidebar-open", open);
        sidebar.setAttribute("aria-hidden", String(!open));

        toggles.forEach((toggle) => {
            toggle.setAttribute("aria-expanded", String(open));
        });

        if (open) {
            const firstItem = sidebar.querySelector("a, button");

            if (firstItem) {
                firstItem.focus({ preventScroll: true });
            }
        }
    };

    toggles.forEach((toggle) => {
        toggle.addEventListener("click", () => {
            setOpen(!isOpen());
        });
    });

    closers.forEach((closer) => {
        closer.addEventListener("click", () => {
            setOpen(false);
        });
    });

    sidebar.addEventListener("click", (event) => {
        if (event.target.closest("a")) {
            setOpen(false);
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && isOpen()) {
            setOpen(false);
            toggles[0].focus({ preventScroll: true });
        }
    });
})();
