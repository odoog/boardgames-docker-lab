const $ = (id) => document.getElementById(id);

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function api(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

// Кнопка 1: данные из БД через backend
async function loadCollection() {
  const out = $("collection-out");
  out.innerHTML = '<p class="muted">Загрузка…</p>';
  try {
    const rows = await api("/api/collection");
    if (!rows.length) { out.innerHTML = '<p class="muted">Коллекция пуста</p>'; return; }
    out.innerHTML = `<table>
      <tr><th>Название</th><th>Игроки</th><th>Время</th><th>Жанр</th><th>Копий</th><th></th></tr>
      ${rows.map((g) => `<tr>
        <td>${esc(g.title)}</td><td>${g.min_players}–${g.max_players}</td><td>${g.play_time} мин</td>
        <td>${esc(g.genre)}</td><td>${g.copies}</td>
        <td><button class="del" data-id="${g.id}">✕</button></td></tr>`).join("")}
    </table>`;
  } catch (e) {
    out.innerHTML = `<p class="error">Ошибка: ${esc(e.message)}</p>`;
  }
}

// Кнопка 2: данные от web-сервиса через backend
async function searchGames() {
  const out = $("search-out");
  const params = new URLSearchParams();
  if ($("players").value) params.set("players", $("players").value);
  if ($("max-time").value) params.set("max_time", $("max-time").value);
  out.innerHTML = '<p class="muted">Поиск…</p>';
  try {
    const data = await api(`/api/search?${params}`);
    if (!data.count) { out.innerHTML = '<p class="muted">Ничего не найдено</p>'; return; }
    out.innerHTML = `<p>Найдено игр: <b>${data.count}</b></p><table>
      <tr><th>Название</th><th>Игроки</th><th>Время</th><th>Жанр</th><th>Рейтинг</th><th></th></tr>
      ${data.games.map((g) => `<tr>
        <td>${esc(g.title)}</td><td>${g.min_players}–${g.max_players}</td><td>${g.play_time} мин</td>
        <td>${esc(g.genre)}</td><td>${g.rating}</td>
        <td>${g.in_collection ? '<span class="badge">в клубе</span>' :
          `<button class="add" data-game='${esc(JSON.stringify(g))}'>+ в коллекцию</button>`}</td></tr>`).join("")}
    </table>`;
  } catch (e) {
    out.innerHTML = `<p class="error">Ошибка: ${esc(e.message)}</p>`;
  }
}

async function addGame(game) {
  await api("/api/collection", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(game),
  });
}

$("btn-collection").addEventListener("click", loadCollection);
$("btn-search").addEventListener("click", searchGames);

$("add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  try {
    await addGame({
      title: f.get("title"),
      min_players: +f.get("min_players"),
      max_players: +f.get("max_players"),
      play_time: +f.get("play_time"),
      genre: f.get("genre") || null,
    });
    e.target.reset();
    loadCollection();
  } catch (err) {
    alert(err.message);
  }
});

$("collection-out").addEventListener("click", async (e) => {
  if (!e.target.matches("button.del")) return;
  await api(`/api/collection/${e.target.dataset.id}`, { method: "DELETE" });
  loadCollection();
});

$("search-out").addEventListener("click", async (e) => {
  if (!e.target.matches("button.add")) return;
  const g = JSON.parse(e.target.dataset.game);
  await addGame({ title: g.title, min_players: g.min_players, max_players: g.max_players, play_time: g.play_time, genre: g.genre });
  searchGames();
  loadCollection();
});
