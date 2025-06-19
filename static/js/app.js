document.addEventListener('DOMContentLoaded', () => {
  const teamSelect     = document.getElementById('team-select');
  const loader         = document.getElementById('stats-loader');
  const statsContainer = document.getElementById('stats-container');

  // Adapt this to your own data‐structure if needed
  function renderStatsTable(data) {
    let html = `
      <table>
        <thead>
          <tr>
            <th>#</th><th>Name</th><th>Pos</th><th>G</th><th>A</th>
          </tr>
        </thead>
        <tbody>
    `;
    data.players.forEach(p => {
      html += `
        <tr>
          <td>${p.jerseyNumber}</td>
          <td>${p.fullName}</td>
          <td>${p.primaryPosition.abbreviation}</td>
          <td>${p.stats.goals}</td>
          <td>${p.stats.assists}</td>
        </tr>`;
    });
    html += `</tbody></table>`;
    return html;
  }

  teamSelect.addEventListener('change', async (e) => {
    const team = e.target.value;
    // clear old stats & show spinner
    statsContainer.innerHTML = '';
    loader.style.display = 'block';

    try {
      const res  = await fetch(`/stats?team=${encodeURIComponent(team)}`);
      const json = await res.json();
      loader.style.display = 'none';
      statsContainer.innerHTML = renderStatsTable(json);
    } catch (err) {
      loader.style.display = 'none';
      statsContainer.innerHTML = '<p class="error">Failed to load stats.</p>';
      console.error(err);
    }
  });
});
