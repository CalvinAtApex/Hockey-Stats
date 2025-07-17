<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Hockey Roster</title>

  <!-- Tabulator CSS -->
  <link
    href="https://unpkg.com/tabulator-tables@5.5.3/dist/css/tabulator.min.css"
    rel="stylesheet"
  />

  <style>
    body {
      font-family: sans-serif;
      padding: 1rem;
    }
    #controls {
      margin-bottom: 1rem;
      display: flex;
      gap: 0.5rem;
      align-items: center;
    }
    #stats-table {
      margin-top: 0.5rem;
    }
  </style>
</head>
<body>
  <h1>Hockey Roster</h1>

  <div id="controls">
    <label for="team-select">Select a team:</label>
    <select id="team-select"></select>
    <button id="add-col-btn">Add Your Own Column</button>
  </div>

  <div id="stats-table"></div>

  <!-- Tabulator JS -->
  <script src="https://unpkg.com/tabulator-tables@5.5.3/dist/js/tabulator.min.js"></script>

  <script>
    document.addEventListener('DOMContentLoaded', () => {
      let table; // Tabulator instance

      // 1) Load teams and populate the selector
      fetch('/teams')
        .then(res => res.json())
        .then(divisions => {
          const select = document.getElementById('team-select');
          // flatten divisions → [ { abbrev, name, logo }, … ]
          const teams = Object.values(divisions).flat();
          teams.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.abbrev;
            opt.textContent = t.name;
            select.appendChild(opt);
          });

          // when user changes team, reload roster
          select.addEventListener('change', () => loadRoster(select.value));

          // initial load
          if (select.value) loadRoster(select.value);
        });

      // 2) Fetch roster and (re)create/update Tabulator
      function loadRoster(team) {
        fetch(`/roster/${team}`)
          .then(res => res.json())
          .then(({ players }) => {
            // base columns pulled from server data
            const baseCols = [
              { title: "Name",        field: "name",         headerFilter: "input", editor: "input" },
              { title: "#",           field: "number",       headerFilter: "input", editor: "input" },
              { title: "Pos",         field: "position",     headerFilter: "input", editor: "input" },
              { title: "GP",          field: "gamesPlayed",  headerFilter: "input", editor: "input" },
              { title: "G",           field: "goals",        headerFilter: "input", editor: "input" },
              { title: "A",           field: "assists",      headerFilter: "input", editor: "input" },
              { title: "P",           field: "points",       headerFilter: "input", editor: "input" },
              { title: "Playoff GP",  field: "playoffGames", headerFilter: "input", editor: "input" },
              { title: "Playoff G",   field: "playoffGoals", headerFilter: "input", editor: "input" },
              { title: "Playoff A",   field: "playoffAssists", headerFilter: "input", editor: "input" },
              { title: "Playoff P",   field: "playoffPoints",  headerFilter: "input", editor: "input" },
            ];

            if (table) {
              // reset columns to base, then load new data
              table.setColumns(baseCols);
              table.replaceData(players);
            } else {
              // first-time instantiation
              table = new Tabulator("#stats-table", {
                data: players,
                layout: "fitDataStretch",
                columns: baseCols,
                movableColumns: true,          // drag‑and‑drop columns
                persistence: {
                  columns: true,               // remember order & visibility
                  sort:    true,
                  filter:  true,
                },
              });
            }
          });
      }

      // 3) “Add Your Own Column” button
      document.getElementById('add-col-btn').addEventListener('click', () => {
        if (!table) return alert("Please select a team first!");

        const title = prompt("Enter new column title:");
        if (!title) return;

        // Create a unique field key (no spaces)
        const field = title.replace(/\s+/g, '_');

        // Append new column definition
        const cols = table.getColumns().map(col => col.getDefinition());
        cols.push({ title, field, editor: "input", headerFilter: "input" });

        table.setColumns(cols);
      });
    });
  </script>
</body>
</html>
