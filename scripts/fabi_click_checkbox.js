(() => {
  // ===== SETTINGS: change these =====
  const minAmount    = 1;                   // price >= this (null = no limit)
  const maxAmount    = null;                // price <= this (null = no limit)
  const timeColumn   = 'Thời gian vào';     // or 'Thời gian ra'
  const timeFrom     = null;                // dd/mm/yyyy hh:mm (null = no limit)
  const timeTo       = null;                // dd/mm/yyyy hh:mm (null = no limit)
  const timeRanges   = [                    // time of day, any date ([] or null = no limit)
    ['09:00', '11:31'],
    ['12:00', '12:16'],
    ['13:30', '16:31'],
    ['17:00', '17:31'],
    ['18:00', '18:31'],
  ];
  const source       = null;                // e.g. 'GRAB FOOD', 'TẠI CHỖ', 'MANG VỀ', 'SHOPEE FOOD' (null = any)
  const clickDelayMs = 100;                 // delay in ms after each click
  // ==================================

  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

  const parseTime = s => {
    const m = s && s.match(/(\d+)\/(\d+)\/(\d+)\s+(\d+):(\d+)/);
    return m ? new Date(m[3], m[2] - 1, m[1], m[4], m[5]) : null;
  };
  const parsePrice = s => parseInt((s || '').replace(/\D/g, ''), 10) || 0;

  // --- time-of-day ranges ---
  const toMin = s => { const [h, m] = s.split(':').map(Number); return h * 60 + m; };
  const ranges = (timeRanges || []).map(([a, b]) => [toMin(a), toMin(b)]);
  const inRanges = d => {
    if (!ranges.length) return true;      // no ranges set = no limit
    if (!d) return false;
    const t = d.getHours() * 60 + d.getMinutes();
    return ranges.some(([s, e]) => s <= e ? (t >= s && t <= e) : (t >= s || t <= e));
  };

  const table   = document.querySelectorAll('table.p-datatable-table')[1];
  const headers = [...table.querySelectorAll('thead th')].map(th => th.innerText.trim());
  const iAmount = headers.indexOf('Tổng tiền');
  const iTime   = headers.indexOf(timeColumn);
  const iSource = headers.indexOf('Nguồn');

  const from = timeFrom ? parseTime(timeFrom) : null;
  const to   = timeTo   ? parseTime(timeTo)   : null;

  (async () => {
    let count = 0;
    let totalAmount = 0;
    const rows = [...table.querySelectorAll('tbody tr')];

    for (const tr of rows) {
      const cells = tr.querySelectorAll('td');
      if (cells.length < headers.length) continue;

      const amount = parsePrice(cells[iAmount].innerText);
      const time   = parseTime(cells[iTime].innerText);
      const src    = cells[iSource].innerText.trim();

      const ok =
        (minAmount == null || amount >= minAmount) &&
        (maxAmount == null || amount <= maxAmount) &&
        (from == null || (time && time >= from)) &&
        (to   == null || (time && time <= to)) &&
        inRanges(time) &&
        (source == null || src === source);

      const cb = tr.querySelector('input[type="checkbox"]');
      if (ok && cb && !cb.checked) {
        cb.click();
        count++;
        totalAmount += amount;
        await sleep(clickDelayMs);
      }
    }

    console.log(`Checked ${count} rows`);
    console.log(`Total Amount: ${totalAmount}`);
  })();
})();