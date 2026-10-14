/* Lightweight, dependency-free interaction layer. Respects reduced-motion preferences. */
(() => {
  'use strict';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const canvas = document.getElementById('web-shooter');
  const cards = [...document.querySelectorAll('.project-card, .skill-group, .code-card, .floating-note, .contact-form, .detail-aside')];

  // Cursor-directed card tilt uses CSS variables, avoiding layout reads/writes per frame.
  if (finePointer && !reducedMotion) {
    cards.forEach((card) => {
      card.classList.add('magnetic-card');
      let rect;
      card.addEventListener('pointerenter', () => { rect = card.getBoundingClientRect(); }, { passive: true });
      card.addEventListener('pointermove', (event) => {
        rect = rect || card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width;
        const y = (event.clientY - rect.top) / rect.height;
        card.style.setProperty('--tilt-x', `${((0.5 - y) * 7).toFixed(2)}deg`);
        card.style.setProperty('--tilt-y', `${((x - 0.5) * 9).toFixed(2)}deg`);
        card.style.setProperty('--glow-x', `${(x * 100).toFixed(1)}%`);
        card.style.setProperty('--glow-y', `${(y * 100).toFixed(1)}%`);
      }, { passive: true });
      card.addEventListener('pointerleave', () => {
        rect = null;
        card.style.setProperty('--tilt-x', '0deg');
        card.style.setProperty('--tilt-y', '0deg');
        card.style.setProperty('--glow-x', '50%');
        card.style.setProperty('--glow-y', '50%');
      }, { passive: true });
    });
  }

  // A small canvas draws a subtle web lattice and short web-shooter strands near the pointer.
  // The canvas is decorative only; all content remains available without it.
  if (!canvas || reducedMotion || !finePointer) return;
  const ctx = canvas.getContext('2d', { alpha: true });
  if (!ctx) return;
  let width = 0, height = 0, raf = 0, lastDraw = 0, idleTimer = 0;
  const pointer = { x: -1000, y: -1000, active: false };
  const shots = [];
  const DPR_LIMIT = 1.5;
  const resize = () => {
    const dpr = Math.min(window.devicePixelRatio || 1, DPR_LIMIT);
    width = window.innerWidth; height = window.innerHeight;
    canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
    canvas.style.width = `${width}px`; canvas.style.height = `${height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  const shoot = (event) => {
    if (event.target.closest('a, button, input, textarea, select')) return;
    const originX = event.clientX, originY = event.clientY;
    const edgeX = originX < width / 2 ? width * 0.08 : width * 0.92;
    const edgeY = Math.max(24, Math.min(height - 24, originY - 120));
    shots.push({ x: originX, y: originY, ex: edgeX, ey: edgeY, born: performance.now(), life: 620 });
    if (shots.length > 3) shots.shift();
  };
  const draw = (now) => {
    raf = 0;
    if (now - lastDraw < 32) { raf = requestAnimationFrame(draw); return; } // cap near 30fps
    lastDraw = now;
    ctx.clearRect(0, 0, width, height);
    // Fine red connection lattice: sparse, low-contrast, and bounded by viewport size.
    const spacing = 74;
    ctx.lineWidth = 0.65;
    ctx.strokeStyle = 'rgba(255, 55, 75, 0.075)';
    for (let x = spacing; x < width; x += spacing) {
      for (let y = spacing; y < height; y += spacing) {
        const dx = x - pointer.x, dy = y - pointer.y;
        if (pointer.active && dx * dx + dy * dy < 210 * 210) continue;
        ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + spacing, y); ctx.lineTo(x + spacing, y + spacing); ctx.stroke();
      }
    }
    if (pointer.active) {
      const radius = 190;
      ctx.strokeStyle = 'rgba(255, 69, 88, 0.22)'; ctx.lineWidth = 0.8;
      for (let angle = 0; angle < Math.PI * 2; angle += Math.PI / 6) {
        const ex = pointer.x + Math.cos(angle) * radius;
        const ey = pointer.y + Math.sin(angle) * radius;
        ctx.beginPath(); ctx.moveTo(pointer.x, pointer.y); ctx.lineTo(ex, ey); ctx.stroke();
      }
      ctx.beginPath(); ctx.arc(pointer.x, pointer.y, 12 + Math.sin(now / 150) * 2, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(255, 80, 98, 0.7)'; ctx.lineWidth = 1.2; ctx.stroke();
      ctx.beginPath(); ctx.arc(pointer.x, pointer.y, 2.5, 0, Math.PI * 2); ctx.fillStyle = 'rgba(255, 95, 110, .9)'; ctx.fill();
    }
    for (let i = shots.length - 1; i >= 0; i--) {
      const shot = shots[i], progress = (now - shot.born) / shot.life;
      if (progress >= 1) { shots.splice(i, 1); continue; }
      const eased = 1 - Math.pow(1 - progress, 3);
      const x = shot.x + (shot.ex - shot.x) * eased;
      const y = shot.y + (shot.ey - shot.y) * eased;
      ctx.beginPath(); ctx.moveTo(shot.x, shot.y); ctx.lineTo(x, y);
      ctx.strokeStyle = `rgba(255, 80, 100, ${(1 - progress) * 0.9})`; ctx.lineWidth = 1.4; ctx.stroke();
      ctx.beginPath(); ctx.arc(x, y, 2.2 * (1 - progress), 0, Math.PI * 2); ctx.fillStyle = '#ff6678'; ctx.fill();
    }
    if (pointer.active || shots.length) raf = requestAnimationFrame(draw);
  };
  const wake = () => { if (!raf) raf = requestAnimationFrame(draw); };
  window.addEventListener('resize', resize, { passive: true });
  window.addEventListener('pointermove', (event) => {
    pointer.x = event.clientX; pointer.y = event.clientY; pointer.active = true;
    window.clearTimeout(idleTimer);
    idleTimer = window.setTimeout(() => { pointer.active = false; wake(); }, 900);
    wake();
  }, { passive: true });
  window.addEventListener('pointerleave', () => { pointer.active = false; wake(); }, { passive: true });
  window.addEventListener('pointerdown', shoot, { passive: true });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && raf) { cancelAnimationFrame(raf); raf = 0; }
    else if (!document.hidden) wake();
  });
  resize();
  // Do not animate continuously while idle: wake only for cursor activity or a web shot.
})();
