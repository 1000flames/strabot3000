const year = document.getElementById('year');
const highlightButton = document.getElementById('highlight-btn');
const integration = document.getElementById('integration');

year.textContent = new Date().getFullYear();

highlightButton.addEventListener('click', () => {
  integration.classList.add('highlight');
  integration.scrollIntoView({ behavior: 'smooth', block: 'center' });
  window.setTimeout(() => integration.classList.remove('highlight'), 1600);
});
