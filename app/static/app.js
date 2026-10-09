/**
 * VeriSerp AI — Frontend Application Logic
 * Built for SerpApi India Hackathon 2026
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const queryInput = document.getElementById('search-query-input');
  const btnClearQuery = document.getElementById('btn-clear-query');
  const depthSelect = document.getElementById('depth-select');
  const toggleSimulation = document.getElementById('toggle-simulation');
  const btnLaunch = document.getElementById('btn-launch-search');
  const templateChips = document.querySelectorAll('.template-chip');

  // Stepper Elements
  const progressSection = document.getElementById('progress-section');
  const progressTitle = document.getElementById('progress-status-title');
  const progressDetail = document.getElementById('progress-status-detail');
  const progressTimer = document.getElementById('progress-timer');
  const stepItems = [
    document.getElementById('step-1'),
    document.getElementById('step-2'),
    document.getElementById('step-3'),
    document.getElementById('step-4'),
  ];
  const stepLines = [
    document.getElementById('step-line-1'),
    document.getElementById('step-line-2'),
    document.getElementById('step-line-3'),
  ];

  // Results Elements
  const resultsSection = document.getElementById('results-section');
  const consensusValue = document.getElementById('consensus-value');
  const gaugeCircle = document.getElementById('gauge-circle');
  const verdictTitle = document.getElementById('verdict-title');
  const verdictSummary = document.getElementById('verdict-summary');
  const confidenceBadge = document.getElementById('confidence-level-badge');
  const metricSources = document.getElementById('metric-sources-count');
  const metricDomains = document.getElementById('metric-domains-count');
  const metricLatency = document.getElementById('metric-latency');
  const metricSynthesizer = document.getElementById('metric-synthesizer');
  const enginePillsList = document.getElementById('engine-pills-list');

  // Dossier & Tabs
  const dossierMarkdownBody = document.getElementById('dossier-markdown-body');
  const btnCopyDossier = document.getElementById('btn-copy-dossier');
  const btnDownloadDossier = document.getElementById('btn-download-dossier');

  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');
  const evidenceList = document.getElementById('evidence-list');
  const filterChips = document.querySelectorAll('.filter-chip');
  const queryTraceList = document.getElementById('query-trace-list');
  const domainBarsContainer = document.getElementById('domain-bars-container');

  // Filter Counters
  const countAll = document.getElementById('count-all');
  const countSupporting = document.getElementById('count-supporting');
  const countCounter = document.getElementById('count-counter');
  const countNuanced = document.getElementById('count-nuanced');
  const evidenceTabCount = document.getElementById('evidence-tab-count');
  const queriesTabCount = document.getElementById('queries-tab-count');

  // Modals
  const modalKey = document.getElementById('modal-key');
  const btnKeyModal = document.getElementById('btn-key-modal');
  const btnCloseKeyModal = document.getElementById('btn-close-key-modal');
  const inputSerpapiKey = document.getElementById('input-serpapi-key');
  const btnToggleKeyVis = document.getElementById('btn-toggle-key-visibility');
  const btnTestKey = document.getElementById('btn-test-key');
  const btnSaveKey = document.getElementById('btn-save-key');
  const keyTestFeedback = document.getElementById('key-test-feedback');
  const keyStatusLabel = document.getElementById('key-status-label');

  const modalMcp = document.getElementById('modal-mcp');
  const btnMcpInfo = document.getElementById('btn-mcp-info');
  const btnCloseMcpModal = document.getElementById('btn-close-mcp-modal');
  const btnCloseMcpFooter = document.getElementById('btn-close-mcp-footer');
  const copyCodeButtons = document.querySelectorAll('.btn-copy-code');

  // State
  let currentResult = null;
  let timerInterval = null;
  let timerStartTime = 0;
  let activeFilter = 'all';

  // Retrieve stored API key if present
  let userApiKey = localStorage.getItem('veriserp_api_key') || '';
  if (userApiKey) {
    inputSerpapiKey.value = userApiKey;
    keyStatusLabel.textContent = 'Key Active';
    keyStatusLabel.style.color = '#38bdf8';
  }

  // Check system status on boot
  checkSystemStatus();

  // Search input events
  queryInput.addEventListener('input', () => {
    btnClearQuery.classList.toggle('hidden', !queryInput.value.trim());
  });

  btnClearQuery.addEventListener('click', () => {
    queryInput.value = '';
    btnClearQuery.classList.add('hidden');
    queryInput.focus();
  });

  queryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      launchInvestigation();
    }
  });

  btnLaunch.addEventListener('click', launchInvestigation);

  // Template prompt click
  templateChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const q = chip.getAttribute('data-query');
      if (q) {
        queryInput.value = q;
        btnClearQuery.classList.remove('hidden');
        launchInvestigation();
      }
    });
  });

  // Tab switching
  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      tabButtons.forEach((b) => b.classList.remove('active'));
      tabContents.forEach((c) => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.classList.add('active');
    });
  });

  // Evidence filter chips
  filterChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      filterChips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      activeFilter = chip.getAttribute('data-filter') || 'all';
      renderEvidenceItems();
    });
  });

  // Copy dossier
  btnCopyDossier.addEventListener('click', () => {
    if (!currentResult || !currentResult.dossier) return;
    navigator.clipboard.writeText(currentResult.dossier.markdown_report).then(() => {
      const original = btnCopyDossier.innerHTML;
      btnCopyDossier.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
      setTimeout(() => { btnCopyDossier.innerHTML = original; }, 2000);
    });
  });

  // Export dossier as Markdown file
  btnDownloadDossier.addEventListener('click', () => {
    if (!currentResult || !currentResult.dossier) return;
    const blob = new Blob([currentResult.dossier.markdown_report], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const safeTopic = (currentResult.query || 'investigation')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .slice(0, 30);
    a.href = url;
    a.download = `veriserp_${safeTopic}_dossier.md`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // Modals management
  btnKeyModal.addEventListener('click', () => modalKey.classList.remove('hidden'));
  btnCloseKeyModal.addEventListener('click', () => modalKey.classList.add('hidden'));

  btnMcpInfo.addEventListener('click', () => modalMcp.classList.remove('hidden'));
  btnCloseMcpModal.addEventListener('click', () => modalMcp.classList.add('hidden'));
  btnCloseMcpFooter.addEventListener('click', () => modalMcp.classList.add('hidden'));

  // Close modals on backdrop click
  [modalKey, modalMcp].forEach((m) => {
    m.addEventListener('click', (e) => {
      if (e.target === m) m.classList.add('hidden');
    });
  });

  // Toggle API key visibility
  btnToggleKeyVis.addEventListener('click', () => {
    const isPass = inputSerpapiKey.type === 'password';
    inputSerpapiKey.type = isPass ? 'text' : 'password';
    btnToggleKeyVis.innerHTML = isPass ? '<i class="fa-solid fa-eye-slash"></i>' : '<i class="fa-solid fa-eye"></i>';
  });

  // Test API Key
  btnTestKey.addEventListener('click', async () => {
    const key = inputSerpapiKey.value.trim();
    if (!key) {
      keyTestFeedback.innerHTML = '<span style="color:#f43f5e">Please paste a key first.</span>';
      return;
    }
    keyTestFeedback.innerHTML = '<span style="color:#38bdf8"><i class="fa-solid fa-spinner fa-spin"></i> Validating key with SerpApi...</span>';
    try {
      const res = await fetch('/api/test-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key })
      });
      const data = await res.json();
      if (data.valid) {
        keyTestFeedback.innerHTML = `<span style="color:#10b981"><i class="fa-solid fa-check"></i> ${data.message}</span>`;
      } else {
        keyTestFeedback.innerHTML = `<span style="color:#f43f5e"><i class="fa-solid fa-xmark"></i> ${data.message}</span>`;
      }
    } catch (e) {
      keyTestFeedback.innerHTML = `<span style="color:#f43f5e">Connection failed: ${e.message}</span>`;
    }
  });

  // Save API Key
  btnSaveKey.addEventListener('click', () => {
    const key = inputSerpapiKey.value.trim();
    userApiKey = key;
    if (key) {
      localStorage.setItem('veriserp_api_key', key);
      keyStatusLabel.textContent = 'Key Active';
      keyStatusLabel.style.color = '#38bdf8';
    } else {
      localStorage.removeItem('veriserp_api_key');
      keyStatusLabel.textContent = 'API Key';
      keyStatusLabel.style.color = '';
    }
    modalKey.classList.add('hidden');
  });

  // Copy code blocks in modal
  copyCodeButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const codeEl = document.getElementById(targetId);
      if (codeEl) {
        navigator.clipboard.writeText(codeEl.innerText).then(() => {
          const original = btn.innerHTML;
          btn.innerHTML = '<i class="fa-solid fa-check"></i>';
          setTimeout(() => { btn.innerHTML = original; }, 1800);
        });
      }
    });
  });

  // Check system status
  async function checkSystemStatus() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      if (data.serpapi_key_configured && !userApiKey) {
        keyStatusLabel.textContent = 'Env Key Ready';
        keyStatusLabel.style.color = '#10b981';
      }
    } catch (err) {
      console.warn('Status check notice:', err);
    }
  }

  // Core Investigation Runner
  async function launchInvestigation() {
    const query = queryInput.value.trim();
    if (!query) {
      queryInput.focus();
      return;
    }

    const depth = depthSelect.value;
    const forceSim = toggleSimulation.checked;

    // Reset and show progress
    btnLaunch.disabled = true;
    btnLaunch.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Investigating...';
    progressSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');

    startProgressStepper();

    try {
      const response = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          depth: depth,
          api_key: userApiKey || null,
          force_simulation: forceSim
        })
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server responded with ${response.status}`);
      }

      const data = await response.json();
      currentResult = data;

      stopProgressStepper();
      displayResults(data);
    } catch (err) {
      stopProgressStepper();
      progressTitle.textContent = 'Investigation Encountered An Error';
      progressDetail.innerHTML = `<span style="color:#f43f5e">${err.message}</span>`;
      console.error(err);
    } finally {
      btnLaunch.disabled = false;
      btnLaunch.innerHTML = '<i class="fa-solid fa-compass"></i> Launch Investigation';
    }
  }

  // Stepper animation logic
  function startProgressStepper() {
    timerStartTime = Date.now();
    updateTimer();
    timerInterval = setInterval(updateTimer, 100);

    // Step 1: Deconstruct
    setStep(1, 'Deconstructing Research Trajectory...', 'Formulating hypotheses and multi-engine query plans across Google Light, Bing, and News indexes.');

    setTimeout(() => {
      // Step 2: Multi-Engine Execution
      setStep(2, 'Executing Multi-Engine Searches...', 'Dispatching parallel queries using serpapi-search-tools across web and news indexes.');
    }, 700);

    setTimeout(() => {
      // Step 3: Corroborate
      setStep(3, 'Cross-Source Corroboration...', 'Analyzing domain authority, stance alignment, and computing consensus score.');
    }, 1500);

    setTimeout(() => {
      // Step 4: Synthesize
      setStep(4, 'Synthesizing Intelligence Dossier...', 'Generating executive findings, citations, and strategic assessment report.');
    }, 2200);
  }

  function setStep(stepNum, title, detail) {
    progressTitle.textContent = title;
    progressDetail.textContent = detail;

    stepItems.forEach((item, idx) => {
      if (idx + 1 < stepNum) {
        item.className = 'step-item completed';
      } else if (idx + 1 === stepNum) {
        item.className = 'step-item active';
      } else {
        item.className = 'step-item';
      }
    });

    stepLines.forEach((line, idx) => {
      line.classList.toggle('active', idx + 1 < stepNum);
    });
  }

  function stopProgressStepper() {
    clearInterval(timerInterval);
    progressSection.classList.add('hidden');
  }

  function updateTimer() {
    const elapsed = ((Date.now() - timerStartTime) / 1000).toFixed(1);
    progressTimer.textContent = `${elapsed}s`;
  }

  // Display Result Data in UI
  function displayResults(data) {
    resultsSection.classList.remove('hidden');

    const verif = data.verification || {};
    const dossier = data.dossier || {};
    const queries = data.queries_executed || [];

    // Consensus Gauge (Circumference: 2 * pi * 42 = 263.89)
    const score = Math.max(0, Math.min(100, verif.consensus_score || 0));
    consensusValue.textContent = `${score}%`;
    const circumference = 2 * Math.PI * 42;
    const offset = circumference - (score / 100) * circumference;
    gaugeCircle.style.strokeDashoffset = offset;

    // Badge and Verdict Color
    let colorHex = '#10b981'; // emerald
    if (verif.badge_color === 'rose') colorHex = '#f43f5e';
    else if (verif.badge_color === 'amber') colorHex = '#f59e0b';
    else if (verif.badge_color === 'blue') colorHex = '#38bdf8';
    else if (verif.badge_color === 'purple') colorHex = '#a855f7';

    gaugeCircle.style.stroke = colorHex;
    verdictTitle.textContent = verif.verdict_label || 'Evaluated';
    verdictTitle.style.color = colorHex;
    verdictSummary.textContent = verif.summary || '';

    confidenceBadge.textContent = `${verif.confidence_level || 'Moderate'} Confidence`;
    confidenceBadge.style.color = colorHex;
    confidenceBadge.style.borderColor = colorHex;

    // Telemetry Numbers
    metricSources.textContent = verif.total_sources_evaluated || 0;
    metricDomains.textContent = verif.unique_domains_count || 0;
    metricLatency.textContent = `${data.total_latency_ms || 0}ms`;
    metricSynthesizer.textContent = dossier.provider_used || 'Native';

    // Consulted Engines Pills
    if (verif.engine_coverage && verif.engine_coverage.length) {
      enginePillsList.innerHTML = verif.engine_coverage.map((eng) => {
        const icon = eng.includes('news') ? 'fa-newspaper' : (eng.includes('bing') ? 'fa-brands fa-microsoft' : 'fa-brands fa-google');
        return `<span class="pill-engine"><i class="fa-solid ${icon}"></i> ${eng}</span>`;
      }).join('');
    }

    // Render Dossier Markdown
    if (window.marked && dossier.markdown_report) {
      dossierMarkdownBody.innerHTML = marked.parse(dossier.markdown_report);
    } else {
      dossierMarkdownBody.innerHTML = `<pre>${dossier.markdown_report || ''}</pre>`;
    }

    // Update Counts
    const supCount = (data.evidence.supporting || []).length;
    const counterCount = (data.evidence.counter || []).length;
    const nuancedCount = (data.evidence.nuanced || []).length;
    const totalCount = supCount + counterCount + nuancedCount;

    countAll.textContent = totalCount;
    countSupporting.textContent = supCount;
    countCounter.textContent = counterCount;
    countNuanced.textContent = nuancedCount;
    evidenceTabCount.textContent = totalCount;
    queriesTabCount.textContent = queries.length;

    // Render Tabs
    renderEvidenceItems();
    renderQueryTraces(queries);
    renderDomainBars(verif.domain_distribution || {});

    // Smooth scroll into results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Render Evidence Cards
  function renderEvidenceItems() {
    if (!currentResult || !currentResult.evidence) return;
    const ev = currentResult.evidence;

    let items = [];
    if (activeFilter === 'all') {
      items = [...(ev.supporting || []), ...(ev.counter || []), ...(ev.nuanced || [])];
    } else if (activeFilter === 'supporting') {
      items = ev.supporting || [];
    } else if (activeFilter === 'counter') {
      items = ev.counter || [];
    } else if (activeFilter === 'nuanced') {
      items = ev.nuanced || [];
    }

    if (!items.length) {
      evidenceList.innerHTML = `
        <div style="text-align:center; padding: 2.5rem; color: var(--text-dim);">
          <i class="fa-solid fa-folder-open" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
          <p>No evidence records found under '${activeFilter}' filter.</p>
        </div>
      `;
      return;
    }

    evidenceList.innerHTML = items.map((it) => {
      const stanceClass = `tag-stance-${it.stance || 'neutral'}`;
      const tierClass = `tag-tier-${it.credibility_tier || 'medium'}`;

      return `
        <div class="evidence-card">
          <div class="evidence-card-header">
            <div class="evidence-source-info">
              <span class="evidence-domain">${escapeHtml(it.domain || 'source')}</span>
            </div>
            <div class="evidence-badges">
              <span class="tag ${tierClass}">${escapeHtml(it.credibility_tier)}</span>
              <span class="tag ${stanceClass}">${escapeHtml(it.stance)}</span>
            </div>
          </div>
          <h4 class="evidence-title">
            <a href="${escapeHtml(it.link)}" target="_blank" rel="noopener">
              ${escapeHtml(it.title || 'Untitled Source')}
              <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 0.75rem; margin-left: 4px;"></i>
            </a>
          </h4>
          <p class="evidence-snippet">${escapeHtml(it.snippet || 'No summary available.')}</p>
          <div class="evidence-footer">
            <span><i class="fa-solid fa-calendar-day"></i> ${escapeHtml(it.date || 'Recent')}</span>
            <span><i class="fa-solid fa-microchip"></i> Engine: ${escapeHtml(it.engine || 'google_light')}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  // Render Query Traces
  function renderQueryTraces(queries) {
    if (!queries.length) {
      queryTraceList.innerHTML = '<p style="color:var(--text-dim)">No queries recorded.</p>';
      return;
    }

    queryTraceList.innerHTML = queries.map((q) => {
      const isSim = q.is_simulated ? '<span style="color:#f59e0b; font-size:0.7rem; font-weight:700;">[DEMO]</span>' : '';
      return `
        <div class="query-trace-card">
          <div class="trace-top">
            <div class="trace-tool-engine">
              <span class="trace-engine-badge"><i class="fa-solid fa-magnifying-glass"></i> ${escapeHtml(q.engine)}</span>
              <span style="font-size: 0.75rem; color: var(--text-dim);">${escapeHtml(q.tool)}</span>
              ${isSim}
            </div>
            <div class="trace-latency"><i class="fa-solid fa-bolt"></i> ${q.latency_ms || 0}ms</div>
          </div>
          <div class="trace-query-text">"${escapeHtml(q.query)}"</div>
          <div class="trace-meta">
            <span>Purpose: ${escapeHtml(q.purpose || 'Verification')}</span>
            <span>Items: ${q.results_count || 0}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  // Render Domain Bars
  function renderDomainBars(domainDist) {
    const entries = Object.entries(domainDist);
    if (!entries.length) {
      domainBarsContainer.innerHTML = '<p style="color:var(--text-dim)">No domain data available.</p>';
      return;
    }

    const maxCount = Math.max(...entries.map(([, c]) => c), 1);

    domainBarsContainer.innerHTML = entries.map(([domain, count]) => {
      const pct = Math.round((count / maxCount) * 100);
      return `
        <div class="domain-bar-item">
          <div class="domain-bar-label">
            <span>${escapeHtml(domain)}</span>
            <span style="font-family: var(--font-mono); color: var(--accent-cyan);">${count} sources</span>
          </div>
          <div class="domain-bar-track">
            <div class="domain-bar-fill" style="width: ${pct}%;"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
