// ─── Character counter ───────────────────────────────────────────────────────
const textInput = document.getElementById('textInput');
const charCount = document.getElementById('charCount');

textInput.addEventListener('input', () => {
  charCount.textContent = `${textInput.value.length} characters`;
});

// ─── Analyze ─────────────────────────────────────────────────────────────────
async function analyze() {
  const text = textInput.value.trim();
  if (!text) { alert('Please paste some text first!'); return; }

  document.getElementById('resultSection').style.display = 'none';
  document.getElementById('loader').style.display = 'block';

  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    const data = await response.json();
    if (data.error) throw new Error(data.error);

    renderResults(data);
  } catch (err) {
    alert('Error: ' + err.message);
  } finally {
    document.getElementById('loader').style.display = 'none';
  }
}

// ─── Render results ───────────────────────────────────────────────────────────
function renderResults(data) {
  const section = document.getElementById('resultSection');
  section.style.display = 'block';

  // --- Score ring ---
  const score = Math.round(data.toxicity_score * 100);
  const ringFill = document.getElementById('ringFill');
  const circumference = 314;
  const offset = circumference - (score / 100) * circumference;

  document.getElementById('scoreNumber').textContent = score;
  ringFill.style.strokeDashoffset = offset;

  // Color based on score
  if (score < 30) {
    ringFill.style.stroke = '#00f5a0';
    document.getElementById('scoreLabel').textContent = '✅ Pretty clean!';
  } else if (score < 60) {
    ringFill.style.stroke = '#ffd166';
    document.getElementById('scoreLabel').textContent = '⚠️ Somewhat toxic';
  } else {
    ringFill.style.stroke = '#ff3c6e';
    document.getElementById('scoreLabel').textContent = '🔥 Highly toxic!';
  }

  // --- Emotion bars ---
  const emotionColors = {
    anger: '#ff3c6e',
    joy: '#00f5a0',
    sadness: '#6a9cf8',
    fear: '#b88fff',
    surprise: '#ffd166',
    disgust: '#ff8c42',
    neutral: '#6b6b80'
  };

  const emotionContainer = document.getElementById('emotionBars');
  emotionContainer.innerHTML = '';

  Object.entries(data.emotions).forEach(([emotion, value]) => {
    const pct = Math.round(value * 100);
    const color = emotionColors[emotion] || '#888';

    const row = document.createElement('div');
    row.className = 'emotion-row';
    row.innerHTML = `
      <div class="emotion-meta">
        <span class="emotion-name">${emotion}</span>
        <span>${pct}%</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="background:${color}; width:0%"
             data-target="${pct}"></div>
      </div>`;
    emotionContainer.appendChild(row);
  });

  // Animate bars after render
  setTimeout(() => {
    document.querySelectorAll('.bar-fill').forEach(bar => {
      bar.style.width = bar.dataset.target + '%';
    });
  }, 100);

  // --- Verdict ---
  document.getElementById('verdictIcon').textContent = data.verdict_icon;
  document.getElementById('verdictText').textContent = data.verdict;

  // --- Rewrite ---
  document.getElementById('rewriteText').textContent = data.rewrite || 'No rewrite needed — text looks healthy!';
}

// ─── Copy rewrite ─────────────────────────────────────────────────────────────
function copyRewrite() {
  const text = document.getElementById('rewriteText').textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector('.copy-btn');
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 2000);
  });
}

// ─── Reset ────────────────────────────────────────────────────────────────────
function reset() {
  document.getElementById('resultSection').style.display = 'none';
  textInput.value = '';
  charCount.textContent = '0 characters';
  textInput.focus();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
