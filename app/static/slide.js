// PULL_OUT DASHBOARD

document.addEventListener("DOMContentLoaded", () => {
        const openDrawer = document.getElementById("openDrawer");
        const drawer = document.getElementById("mainDrawer");
        const overlay = document.getElementById("drawerOverlay");

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
});

const btn = document.getElementById("btn");

window.onscroll = () => {
    btn.style.display = window.scrollY > 300 ? "block" : "none";
};

btn.onclick = () => window.scrollTo({ top:0, behavior: "smooth"});

window.addEventListener('load', () => {
  document.body.classList.add('ready');
});

// SHARE BUTTON

function copyLink() {
  const input = document.getElementById("shareLink");
  input.select();
  input.setSelectionRange(0, 99999);
  document.execCommand("copy");
  alert("Link copied to clipboard!");
}

function shareApp() {
  const link = document.getElementById("shareLink").value;
  if (navigator.share) {
    navigator.share({
      title: "Superior CV",
      text: "Build professional resumes easily with Superior CV",
      url: link
    });
  } else {
    copyLink();
  }
}

function shareWhatsApp() {
  window.open(
    "https://wa.me/?text=" + encodeURIComponent(
      "Check out Superior CV Resume App: " + document.getElementById("shareLink").value
    ),
    "_blank"
  );
}

function shareFacebook() {
  window.open(
    "https://www.facebook.com/sharer/sharer.php?u=" +
      encodeURIComponent(document.getElementById("shareLink").value),
    "_blank"
  );
}

function shareTwitter() {
  window.open(
    "https://twitter.com/intent/tweet?text=" +
      encodeURIComponent(
        "Build professional resumes easily with Superior CV " +
        document.getElementById("shareLink").value
      ),
    "_blank"
  );
}

// SEARCH BUTTON


document.addEventListener("DOMContentLoaded", async () => {
  const searchInput = document.getElementById("searchInput");
  const searchResults = document.getElementById("searchResults");

  // Fetch user's resumes from backend
  let resumes = [];
  try {
    const res = await fetch("/api/user_resumes");
    resumes = await res.json();
  } catch (err) {
    console.error("Failed to fetch resumes:", err);
  }

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.toLowerCase();
    searchResults.innerHTML = "";

    if (query) {
      const filtered = resumes.filter(r => r.title.toLowerCase().includes(query));
      filtered.forEach(r => {
        const div = document.createElement("div");
        div.className = "search-result-item";
        div.textContent = r.title;
        div.addEventListener("click", () => {
          // Redirect to resume view/edit page
          window.location.href = `/resume/edit/${r.id}`;
        });
        searchResults.appendChild(div);
      });
      searchResults.style.display = filtered.length ? "block" : "none";
    } else {
      searchResults.style.display = "none";
    }
  });

  // Optional: Search button
  document.getElementById("searchBtn").addEventListener("click", () => {
    alert(`Searching for: ${searchInput.value}`);
  });

  // Optional: Mic button
  const micBtn = document.getElementById("micBtn");
  if ("webkitSpeechRecognition" in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.lang = "en-US";

    micBtn.addEventListener("click", () => recognition.start());

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      searchInput.value = transcript;
      searchInput.dispatchEvent(new Event("input"));
    };
  } else {
    micBtn.style.display = "none";
  }
});