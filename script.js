const year = document.getElementById('year');
const highlightButton = document.getElementById('highlight-btn');
const nextSection = document.getElementById('features');

year.textContent = new Date().getFullYear();

highlightButton.addEventListener('click', () => {
  nextSection.classList.add('highlight');
  setTimeout(() => nextSection.classList.remove('highlight'), 1400);
  nextSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
});
