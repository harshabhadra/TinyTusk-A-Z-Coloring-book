(() => {
  "use strict";

  /* ---------- Amazon links ----------
     Paste each book's Amazon link once it is live, e.g.
     "https://www.amazon.com/dp/XXXXXXXXXX". That book's card then switches
     from its "In review" / "Coming soon" badge to "Now on Amazon" and shows
     a "Buy on Amazon" button. */
  const BOOK_LINKS = {
    "az-coloring": "",       // My First A to Z Animals Copy Coloring Book
    "color-by-number": "",   // TinyTusk A to Z Animals Color by Number
    "abc-tracing": "",       // TinyTusk ABC Letter Tracing Workbook
    "trace-write": "",       // Trace & Write the Alphabet
  };

  document.querySelectorAll("[data-book]").forEach((card) => {
    const url = BOOK_LINKS[card.dataset.book];
    if (!url) return;
    card.querySelectorAll("[data-buy]").forEach((a) => { a.href = url; a.hidden = false; });
    card.querySelectorAll("[data-status-soon]").forEach((el) => { el.hidden = true; });
    card.querySelectorAll("[data-status-live]").forEach((el) => { el.hidden = false; });
  });

  const ANIMALS = {
    A: "Alligator", B: "Bear", C: "Camel", D: "Dolphin", E: "Elephant", F: "Frog",
    G: "Giraffe", H: "Hippo", I: "Iguana", J: "Jellyfish", K: "Koala", L: "Lion",
    M: "Monkey", N: "Narwhal", O: "Owl", P: "Panda", Q: "Quail", R: "Rabbit",
    S: "Sloth", T: "Tiger", U: "Urial", V: "Vulture", W: "Whale", X: "X-ray fish",
    Y: "Yak", Z: "Zebra",
  };
  const LETTERS = Object.keys(ANIMALS);
  const article = (name) => (/^[AEIOU]/i.test(name) && !/^U[a-z]/.test(name) ? "an" : "a");

  /* ---------- Mobile menu ---------- */
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.getElementById("site-nav");
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  nav.addEventListener("click", (e) => {
    if (e.target.closest("a")) { nav.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); }
  });

  /* ---------- Gallery + viewer ---------- */
  const gallery = document.getElementById("gallery");
  const frag = document.createDocumentFragment();
  LETTERS.forEach((l) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "card";
    btn.dataset.letter = l;
    btn.setAttribute("aria-label", `${l} is for ${ANIMALS[l]}. View the coloring page`);
    btn.innerHTML =
      `<span class="letter" aria-hidden="true">${l}</span>` +
      `<img src="assets/animals/${l}.webp" alt="" width="420" height="420" loading="lazy" decoding="async">` +
      `<span class="name" aria-hidden="true">${ANIMALS[l]}</span>`;
    li.appendChild(btn);
    frag.appendChild(li);
  });
  gallery.appendChild(frag);

  /* Page viewer: one list of pages per "group" (the A-Z gallery, or a book's preview strip). */
  const GROUPS = {
    az: LETTERS.map((l) => ({
      src: `assets/pages/${l}.webp`,
      title: `${l} is for ${ANIMALS[l]}`,
      short: `${l} · ${ANIMALS[l]}`,
      alt: `Coloring page for the letter ${l}: ${ANIMALS[l]}`,
    })),
  };
  const BOOK_TITLES = {
    "az-coloring": "A to Z Animals Copy Coloring Book",
    "color-by-number": "TinyTusk A to Z Animals Color by Number",
    "abc-tracing": "TinyTusk ABC Letter Tracing Workbook",
    "trace-write": "Trace & Write the Alphabet",
  };
  document.querySelectorAll(".peek").forEach((btn) => {
    const g = btn.dataset.group;
    const title = btn.getAttribute("aria-label").replace(/^View page: /, "");
    (GROUPS[g] ||= [])[Number(btn.dataset.index)] = {
      src: btn.querySelector("img").getAttribute("src"),
      title,
      short: title,
      alt: `${BOOK_TITLES[g] || "TinyTusk"} sample page: ${title}`,
    };
  });

  const viewer = document.getElementById("viewer");
  const vImg = document.getElementById("viewer-img");
  const vTitle = document.getElementById("viewer-title");
  const vPrevLabel = document.getElementById("viewer-prev-label");
  const vNextLabel = document.getElementById("viewer-next-label");
  let group = GROUPS.az;
  let current = 0;
  let opener = null;

  function showPage(i) {
    const n = group.length;
    current = (i + n) % n;
    const pg = group[current];
    vImg.src = pg.src;
    vImg.alt = pg.alt;
    vTitle.textContent = pg.title;
    vPrevLabel.textContent = group[(current - 1 + n) % n].short;
    vNextLabel.textContent = group[(current + 1) % n].short;
  }
  function openViewer(g, i, from) {
    group = GROUPS[g];
    opener = from;
    showPage(i);
    viewer.showModal();
  }
  gallery.addEventListener("click", (e) => {
    const card = e.target.closest(".card");
    if (card) openViewer("az", LETTERS.indexOf(card.dataset.letter), card);
  });
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".peek");
    if (btn) openViewer(btn.dataset.group, Number(btn.dataset.index), btn);
  });
  document.getElementById("viewer-prev").addEventListener("click", () => showPage(current - 1));
  document.getElementById("viewer-next").addEventListener("click", () => showPage(current + 1));
  document.getElementById("viewer-close").addEventListener("click", () => viewer.close());
  viewer.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") showPage(current - 1);
    if (e.key === "ArrowRight") showPage(current + 1);
  });
  viewer.addEventListener("click", (e) => { if (e.target === viewer) viewer.close(); });
  viewer.addEventListener("close", () => { if (opener) opener.focus(); });

  /* ---------- Coloring studio ---------- */
  const PALETTE = [
    ["Red", "#E53935"], ["Orange", "#FB8C00"], ["Yellow", "#FDD835"],
    ["Light green", "#7CB342"], ["Dark green", "#2E7D32"], ["Light blue", "#4FC3F7"],
    ["Dark blue", "#1E5AA8"], ["Purple", "#8E24AA"], ["Pink", "#F48FB1"],
    ["Brown", "#8D5524"], ["Grey", "#9E9E9E"], ["White", "#FFFFFF"],
  ];
  const STUDIO = ["A", "E", "L", "P", "O", "Z"];

  const canvas = document.getElementById("paint");
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const tabs = document.getElementById("studio-tabs");
  const swatches = document.getElementById("swatches");
  const undoBtn = document.getElementById("undo");
  const refImg = document.getElementById("ref-img");
  const refTitle = document.getElementById("ref-title");

  let color = PALETTE[3][1];
  let base = null;      // original line art ImageData
  let history = [];
  let letter = "A";

  // swatches (radio group semantics)
  const swatchName = document.createElement("span");
  swatchName.className = "swatch-name";
  swatchName.setAttribute("aria-live", "polite");
  PALETTE.forEach(([name, hex], i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "swatch";
    b.style.setProperty("--c", hex);
    b.setAttribute("role", "radio");
    b.setAttribute("aria-label", name);
    b.setAttribute("aria-checked", String(i === 3));
    b.tabIndex = i === 3 ? 0 : -1;
    b.dataset.hex = hex;
    b.dataset.name = name;
    swatches.appendChild(b);
  });
  swatches.setAttribute("role", "radiogroup");
  swatches.setAttribute("aria-label", "Crayon color");
  swatches.after(swatchName);

  function pickSwatch(b, focus) {
    swatches.querySelectorAll(".swatch").forEach((s) => { s.setAttribute("aria-checked", "false"); s.tabIndex = -1; });
    b.setAttribute("aria-checked", "true");
    b.tabIndex = 0;
    if (focus) b.focus();
    color = b.dataset.hex;
    swatchName.textContent = `Crayon: ${b.dataset.name}`;
  }
  pickSwatch(swatches.children[3], false);
  swatches.addEventListener("click", (e) => { const b = e.target.closest(".swatch"); if (b) pickSwatch(b, false); });
  swatches.addEventListener("keydown", (e) => {
    const list = [...swatches.querySelectorAll(".swatch")];
    const i = list.indexOf(document.activeElement);
    if (i < 0) return;
    const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
    if (step) { e.preventDefault(); pickSwatch(list[(i + step + list.length) % list.length], true); }
  });

  // animal tabs
  STUDIO.forEach((l, i) => {
    const t = document.createElement("button");
    t.type = "button";
    t.className = "tab";
    t.setAttribute("role", "tab");
    t.setAttribute("aria-selected", String(i === 0));
    t.tabIndex = i === 0 ? 0 : -1;
    t.dataset.letter = l;
    t.innerHTML = `<img src="assets/animals/${l}.webp" alt="" width="36" height="36" loading="lazy">${ANIMALS[l]}`;
    tabs.appendChild(t);
  });
  function selectTab(t, focus) {
    tabs.querySelectorAll(".tab").forEach((x) => { x.setAttribute("aria-selected", "false"); x.tabIndex = -1; });
    t.setAttribute("aria-selected", "true");
    t.tabIndex = 0;
    if (focus) t.focus();
    loadArt(t.dataset.letter);
  }
  tabs.addEventListener("click", (e) => { const t = e.target.closest(".tab"); if (t) selectTab(t, false); });
  tabs.addEventListener("keydown", (e) => {
    const list = [...tabs.querySelectorAll(".tab")];
    const i = list.indexOf(document.activeElement);
    const step = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
    if (i >= 0 && step) { e.preventDefault(); selectTab(list[(i + step + list.length) % list.length], true); }
  });

  function loadArt(l) {
    letter = l;
    const name = ANIMALS[l];
    refImg.src = `assets/animals/${l}.webp`;
    refImg.alt = `Colored ${name.toLowerCase()} to copy`;
    refTitle.innerHTML = `${l} is for <strong>${name}</strong>`;
    canvas.setAttribute("aria-label", `Coloring page: ${article(name)} ${name.toLowerCase()}. Tap or click a shape to fill it with the chosen color.`);
    const img = new Image();
    img.onload = () => {
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      ctx.fillStyle = "#fff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      base = ctx.getImageData(0, 0, canvas.width, canvas.height);
      // snap to pure black/white so fills never leak through soft pixels
      const d = base.data;
      for (let i = 0; i < d.length; i += 4) {
        const v = d[i] < 160 ? 0 : 255;
        d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255;
      }
      ctx.putImageData(base, 0, 0);
      history = [];
      undoBtn.disabled = true;
    };
    img.src = `assets/lineart/${l}.png`;
  }

  function hexToRgb(hex) {
    const n = parseInt(hex.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }

  function fill(x, y) {
    const w = canvas.width, h = canvas.height;
    const img = ctx.getImageData(0, 0, w, h);
    const d = img.data;
    const start = (y * w + x) * 4;
    const isLine = (i) => base.data[i] === 0;
    if (isLine(start)) return false;
    const [r, g, b] = hexToRgb(color);
    const tr = d[start], tg = d[start + 1], tb = d[start + 2];
    if (tr === r && tg === g && tb === b) return false;

    history.push(img.data.slice());
    if (history.length > 25) history.shift();

    const match = (i) => !isLine(i) && d[i] === tr && d[i + 1] === tg && d[i + 2] === tb;
    const stack = [[x, y]];
    while (stack.length) {
      let [cx, cy] = stack.pop();
      let i = (cy * w + cx) * 4;
      while (cx >= 0 && match(i)) { cx--; i -= 4; }
      cx++; i += 4;
      let up = false, down = false;
      while (cx < w && match(i)) {
        d[i] = r; d[i + 1] = g; d[i + 2] = b;
        if (cy > 0) {
          const u = i - w * 4;
          if (match(u)) { if (!up) { stack.push([cx, cy - 1]); up = true; } } else up = false;
        }
        if (cy < h - 1) {
          const dn = i + w * 4;
          if (match(dn)) { if (!down) { stack.push([cx, cy + 1]); down = true; } } else down = false;
        }
        cx++; i += 4;
      }
    }
    ctx.putImageData(img, 0, 0);
    undoBtn.disabled = false;
    return true;
  }

  canvas.addEventListener("pointerup", (e) => {
    if (!base) return;
    const rect = canvas.getBoundingClientRect();
    let x = Math.floor(((e.clientX - rect.left) / rect.width) * canvas.width);
    let y = Math.floor(((e.clientY - rect.top) / rect.height) * canvas.height);
    x = Math.max(0, Math.min(canvas.width - 1, x));
    y = Math.max(0, Math.min(canvas.height - 1, y));
    // if the tap lands on a line, nudge to the nearest open pixel
    if (base.data[(y * canvas.width + x) * 4] === 0) {
      outer: for (let rad = 1; rad <= 6; rad++) {
        for (let dy = -rad; dy <= rad; dy++) for (let dx = -rad; dx <= rad; dx++) {
          const nx = x + dx, ny = y + dy;
          if (nx >= 0 && ny >= 0 && nx < canvas.width && ny < canvas.height && base.data[(ny * canvas.width + nx) * 4] !== 0) { x = nx; y = ny; break outer; }
        }
      }
    }
    fill(x, y);
  });

  undoBtn.addEventListener("click", () => {
    const prev = history.pop();
    if (!prev) return;
    const img = ctx.createImageData(canvas.width, canvas.height);
    img.data.set(prev);
    ctx.putImageData(img, 0, 0);
    undoBtn.disabled = history.length === 0;
  });
  document.getElementById("clear").addEventListener("click", () => {
    if (!base) return;
    ctx.putImageData(base, 0, 0);
    history = [];
    undoBtn.disabled = true;
  });
  document.getElementById("save").addEventListener("click", () => {
    const a = document.createElement("a");
    a.download = `tinytusk-${ANIMALS[letter].toLowerCase().replace(/\W+/g, "-")}.png`;
    a.href = canvas.toDataURL("image/png");
    a.click();
  });

  loadArt("A");

  /* ---------- Launch sign-up ---------- */
  const form = document.getElementById("notify-form");
  const email = document.getElementById("email");
  const err = document.getElementById("email-error");
  const ok = document.getElementById("email-success");
  const showErr = (msg) => { err.textContent = msg; err.hidden = !msg; email.setAttribute("aria-invalid", msg ? "true" : "false"); };
  email.addEventListener("blur", () => { if (email.value && !email.validity.valid) showErr("Please check your email address, for example name@example.com."); });
  email.addEventListener("input", () => { if (!err.hidden && email.validity.valid) showErr(""); });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    ok.hidden = true;
    if (!email.value.trim()) { showErr("Please type your email address."); email.focus(); return; }
    if (!email.validity.valid) { showErr("Please check your email address, for example name@example.com."); email.focus(); return; }
    showErr("");
    const action = form.dataset.action || "";
    const btn = form.querySelector("button[type=submit]");
    if (!action || action.startsWith("YOUR_")) {
      // No mailing service connected yet (see website/README.md).
      ok.textContent = "Thanks! Sign-ups open very soon. Please check back on launch day.";
      ok.hidden = false;
      return;
    }
    btn.disabled = true;
    btn.textContent = "Sending…";
    try {
      const res = await fetch(action, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } });
      if (!res.ok) throw new Error(String(res.status));
      form.reset();
      ok.textContent = "You're on the list! We'll email you on launch day.";
      ok.hidden = false;
    } catch {
      showErr("Sorry, that didn't go through. Please try again in a moment.");
    } finally {
      btn.disabled = false;
      btn.textContent = "Notify me";
    }
  });

  document.getElementById("year").textContent = String(new Date().getFullYear());
})();
