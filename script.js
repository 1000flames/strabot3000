const year = document.getElementById('year');
const highlightButton = document.getElementById('highlight-btn');
const liveSection = document.getElementById('live');
const liveFeed = document.getElementById('live-feed');
const docCount = document.getElementById('doc-count');
const pageCount = document.getElementById('page-count');
const latestDate = document.getElementById('latest-date');
const sourceCount = document.getElementById('source-count');

year.textContent = new Date().getFullYear();

highlightButton.addEventListener('click', () => {
  liveSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

function formatDate(dateString) {
  const date = new Date(`${dateString}T00:00:00Z`);
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date);
}

function renderFeed(results) {
  liveFeed.innerHTML = results
    .slice(0, 6)
    .map(
      (item) => `
        <article class="result-card">
          <div class="result-top">
            <span class="source-badge">${item.procedure}</span>
            <span class="result-deadline">Deadline ${item.deadline}</span>
          </div>
          <h3 class="result-title">${item.title}</h3>
          <p class="result-authority">${item.authority}</p>
          <div class="result-meta">
            <span class="result-deadline">Published ${item.publishedAt}</span>
            <a class="result-link" href="${item.url}" target="_blank" rel="noreferrer">Open document</a>
          </div>
        </article>
      `,
    )
    .join('');
}

async function loadFeed() {
  try {
    const response = await fetch('data/autobahn_tenders.json');
    if (!response.ok) {
      throw new Error(`Failed to load feed: ${response.status}`);
    }
    const payload = await response.json();
    const results = payload.results || [];
    const pages = new Set(results.map((item) => item.pageStart));

    docCount.textContent = payload.count ?? results.length;
    pageCount.textContent = pages.size;
    latestDate.textContent = formatDate((payload.scrapedAt || '').slice(0, 10) || '2026-04-15');
    sourceCount.textContent = '1 portal';

    renderFeed(results);
  } catch (error) {
    liveFeed.innerHTML = `
      <div class="loading-card">
        Live feed unavailable right now. The scraper still works, but the demo JSON could not be loaded.
      </div>
    `;
    docCount.textContent = '182';
    pageCount.textContent = '4';
    latestDate.textContent = '15/04/2026';
    sourceCount.textContent = '1 portal';
    console.error(error);
  }
}

loadFeed();
