// PULL_OUT DASHBOARD

document.addEventListener("DOMContentLoaded", () => {
  const openDrawer = document.getElementById("openDrawer");
  const drawer = document.getElementById("mainDrawer");
  const overlay = document.getElementById("drawerOverlay");

  if (!openDrawer || !drawer || !overlay) return;

  function toggleDrawer(show) {
    if (show) {
      drawer.classList.remove("-translate-x-full"); // slide in
      drawer.classList.add("translate-x-0");
      overlay.classList.remove("hidden"); // show overlay
      document.body.style.overflow = "hidden"; // prevent scroll
    } else {
      drawer.classList.remove("translate-x-0"); // slide out
      drawer.classList.add("-translate-x-full");
      overlay.classList.add("hidden"); // hide overlay
      document.body.style.overflow = ""; // restore scroll
    }
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
  const resultsContainer = document.getElementById("searchResults");
  const micBtn = document.getElementById("micBtn");

  if (!searchInput || !resultsContainer) return;

  // Optional: Fetch all user resumes once for local filtering
/* let resumes = [];
  try {
    const res = await fetch("/api/user_resumes");
    if (res.ok) {
      resumes = await res.json();
    } else {
      const text = await res.text();
      console.error("Failed to fetch resumes:", res.status, text);
    }
  } catch (err) {
    console.error("Failed to fetch resumes:", err);
  }*/

  async function performSearch(query) {
    resultsContainer.innerHTML = "";

    if (!query) return;

    let data = [];
    try {
      const res = await fetch(`/resume/api/search_resumes?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        data = await res.json();
      } else {
        const text = await res.text();
        console.error("Search API error:", res.status, text);
      }
    } catch (err) {
      console.error("Search fetch error:", err);
    }

    if (!data.length) {
      resultsContainer.style.display = "none";
      return;
    }

    data.forEach(resume => {
      const div = document.createElement("div");
      div.className = "search-result-item";
      div.innerHTML = `<a href="/resume/resume/${resume.id}">${resume.title}</a>`;
      resultsContainer.appendChild(div);
    });
    resultsContainer.style.display = "block";
  }

  searchInput.addEventListener("input", (e) => {
    const query = searchInput.value.trim();
    performSearch(query);
  });

  // Mic voice input
  if (micBtn && "webkitSpeechRecognition" in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.lang = "en-US";

    micBtn.addEventListener("click", () => recognition.start());

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      searchInput.value = transcript;
      searchInput.dispatchEvent(new Event("input"));
    };
  } else if (micBtn) {
    micBtn.style.display = "none";
  }
});