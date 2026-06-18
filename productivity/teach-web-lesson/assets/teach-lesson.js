// Teach Web Lesson JS
(function () {
  function renderKatex() {
    if (!window.renderMathInElement) return;
    window.renderMathInElement(document.body, {
      delimiters: [
        { left: "\\[", right: "\\]", display: true },
        { left: "\\(", right: "\\)", display: false }
      ],
      throwOnError: false
    });
  }

  function setupProgress() {
    const bar = document.querySelector('.progress-bar');
    if (!bar) return;
    const update = () => {
      const doc = document.documentElement;
      const max = doc.scrollHeight - window.innerHeight;
      const pct = max <= 0 ? 0 : Math.min(100, Math.max(0, window.scrollY / max * 100));
      bar.style.width = pct + '%';
    };
    update();
    window.addEventListener('scroll', update, { passive: true });
  }

  function setupActiveToc() {
    const links = Array.from(document.querySelectorAll('.toc a[href^="#"]'));
    const sections = links.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
    if (!links.length || !sections.length || !('IntersectionObserver' in window)) return;
    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        links.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + entry.target.id));
      });
    }, { rootMargin: '-35% 0px -55% 0px', threshold: 0.01 });
    sections.forEach(s => obs.observe(s));
  }

  function setupQuizzes() {
    document.querySelectorAll('.quiz-card').forEach(card => {
      const feedback = card.querySelector('.feedback');
      card.querySelectorAll('.choice').forEach(btn => {
        btn.addEventListener('click', () => {
          card.querySelectorAll('.choice').forEach(b => b.classList.remove('correct', 'wrong'));
          const ok = btn.dataset.correct === 'true';
          btn.classList.add(ok ? 'correct' : 'wrong');
          const correct = card.querySelector('.choice[data-correct="true"]');
          if (!ok && correct) correct.classList.add('correct');
          if (feedback) {
            feedback.classList.add('show');
            feedback.textContent = ok
              ? (card.dataset.feedbackCorrect || '对，继续保持这个判断。')
              : (card.dataset.feedbackWrong || '先别急，回看上面的识别条件再判断一次。');
          }
        });
      });
    });
  }

  function setupCopyButtons() {
    document.querySelectorAll('[data-copy]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const selector = btn.getAttribute('data-copy');
        const target = selector ? document.querySelector(selector) : null;
        const text = target ? target.innerText : '';
        if (!text) return;
        try {
          await navigator.clipboard.writeText(text);
          const old = btn.textContent;
          btn.textContent = '已复制';
          setTimeout(() => (btn.textContent = old), 1100);
        } catch (_) {}
      });
    });
  }

  function setupSidebarToggle() {
    const toggle = document.getElementById('sidebar-toggle');
    const layout = document.querySelector('.layout');
    if (!toggle || !layout) return;

    const setToggleState = (collapsed) => {
      toggle.textContent = collapsed ? '→' : '←';
      toggle.setAttribute('aria-label', collapsed ? '展开侧边栏' : '折叠侧边栏');
      toggle.setAttribute('title', collapsed ? '展开侧边栏' : '折叠侧边栏');
      toggle.setAttribute('aria-expanded', String(!collapsed));
    };

    layout.setAttribute('data-sidebar', layout.getAttribute('data-sidebar') || 'expanded');
    setToggleState(layout.getAttribute('data-sidebar') === 'collapsed');

    toggle.addEventListener('click', () => {
      const collapsed = layout.getAttribute('data-sidebar') === 'collapsed';
      const nextCollapsed = !collapsed;
      layout.setAttribute('data-sidebar', nextCollapsed ? 'collapsed' : 'expanded');
      setToggleState(nextCollapsed);
    });
  }

  function initLesson() {
    renderKatex();
    setupProgress();
    setupActiveToc();
    setupQuizzes();
    setupCopyButtons();
    setupSidebarToggle();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLesson);
  } else {
    initLesson();
  }
})();
