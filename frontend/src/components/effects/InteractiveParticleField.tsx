"use client";

import { useEffect, useRef } from "react";

interface Particle {
  // Original/ambient position
  ox: number;
  oy: number;
  // Current position
  x: number;
  y: number;
  // Velocity
  vx: number;
  vy: number;
  // Visual properties (set once)
  radius: number;
  baseOpacity: number;
  // Current opacity (animated)
  opacity: number;
  // Ambient drift phase offsets
  phaseX: number;
  phaseY: number;
  // Ambient drift speed
  driftSpeed: number;
  // Drift amplitude (pixels)
  driftAmplitude: number;
}

interface InteractiveParticleFieldProps {
  /** Particle density as particles per 1000 px² — default 0.25 */
  density?: number;
  /** Primary particle hue (HSL, degrees) — default 240 (indigo) */
  hue?: number;
  /** Secondary particle hue for variety — default 270 (purple) */
  hueAlt?: number;
  /** Repulsion radius in px — default 120 */
  repelRadius?: number;
  /** Maximum repulsion displacement in px — default 60 */
  repelStrength?: number;
  /** Spring return constant (higher = snappier) — default 0.04 */
  springK?: number;
  /** Friction factor per frame (0..1, higher = more drag) — default 0.85 */
  friction?: number;
  className?: string;
}

export default function InteractiveParticleField({
  density = 0.25,
  hue = 240,
  hueAlt = 270,
  repelRadius = 120,
  repelStrength = 60,
  springK = 0.04,
  friction = 0.85,
  className = "",
}: InteractiveParticleFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let rafId: number;
    let particles: Particle[] = [];
    let mouseX = -9999;
    let mouseY = -9999;
    let reducedMotion = false;
    let width = 0;
    let height = 0;
    let dpr = 1;

    // ─── Reduced motion ───────────────────────────────────────────────────────
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    reducedMotion = mediaQuery.matches;
    const onMotionChange = (e: MediaQueryListEvent) => {
      reducedMotion = e.matches;
    };
    mediaQuery.addEventListener("change", onMotionChange);

    // ─── Resize ───────────────────────────────────────────────────────────────
    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      const rect = canvas.getBoundingClientRect();
      width = rect.width;
      height = rect.height;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.scale(dpr, dpr);
      buildParticles();
    };

    // ─── Build particle list ───────────────────────────────────────────────────
    const buildParticles = () => {
      const isMobile = width < 768;
      const effectiveDensity = isMobile ? density * 0.5 : density;
      const area = width * height;
      const count = Math.round((area / 1000) * effectiveDensity);

      particles = [];
      for (let i = 0; i < count; i++) {
        const ox = Math.random() * width;
        const oy = Math.random() * height;
        particles.push({
          ox,
          oy,
          x: ox,
          y: oy,
          vx: 0,
          vy: 0,
          radius: 0.8 + Math.random() * 1.8,
          baseOpacity: 0.15 + Math.random() * 0.45,
          opacity: 0.15 + Math.random() * 0.45,
          phaseX: Math.random() * Math.PI * 2,
          phaseY: Math.random() * Math.PI * 2,
          driftSpeed: 0.0003 + Math.random() * 0.0005,
          driftAmplitude: 6 + Math.random() * 12,
        });
      }
    };

    // ─── Mouse/touch tracking ─────────────────────────────────────────────────
    const onMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
    };
    const onMouseLeave = () => {
      mouseX = -9999;
      mouseY = -9999;
    };
    // Use window-level mouse tracking so cursor works even in mixed-content parent
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseleave", onMouseLeave);

    // ─── Animation loop ────────────────────────────────────────────────────────
    const repelRadiusSq = repelRadius * repelRadius;
    let lastTime = 0;

    const tick = (timestamp: number) => {
      const dt = Math.min(timestamp - lastTime, 50); // cap at 50ms (20fps min)
      lastTime = timestamp;

      ctx.clearRect(0, 0, width, height);

      const time = timestamp;
      const isCursorNearby = mouseX > -9000;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        if (reducedMotion) {
          // Static render only — no physics, no drift
          ctx.beginPath();
          ctx.arc(p.ox, p.oy, p.radius, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${i % 2 === 0 ? hue : hueAlt}, 80%, 75%, ${p.baseOpacity * 0.5})`;
          ctx.fill();
          continue;
        }

        // ── Ambient drift (smooth sine oscillation around origin) ──────────────
        const driftX = Math.sin(time * p.driftSpeed + p.phaseX) * p.driftAmplitude;
        const driftY = Math.cos(time * p.driftSpeed * 0.7 + p.phaseY) * p.driftAmplitude;
        const targetX = p.ox + driftX;
        const targetY = p.oy + driftY;

        // ── Cursor repulsion ───────────────────────────────────────────────────
        let repelX = 0;
        let repelY = 0;
        let proximity = 0; // 0..1 for opacity boost

        if (isCursorNearby) {
          const dx = p.x - mouseX;
          const dy = p.y - mouseY;
          const distSq = dx * dx + dy * dy;

          if (distSq < repelRadiusSq && distSq > 0.01) {
            const dist = Math.sqrt(distSq);
            const factor = 1 - dist / repelRadius; // 0..1 (stronger when closer)
            const smoothFactor = factor * factor; // quadratic falloff
            const pushMag = smoothFactor * repelStrength;
            repelX = (dx / dist) * pushMag;
            repelY = (dy / dist) * pushMag;
            proximity = factor;
          }
        }

        // ── Spring toward (target + repel offset) ─────────────────────────────
        const goalX = targetX + repelX;
        const goalY = targetY + repelY;

        const ax = (goalX - p.x) * springK;
        const ay = (goalY - p.y) * springK;

        p.vx = (p.vx + ax) * friction;
        p.vy = (p.vy + ay) * friction;
        p.x += p.vx;
        p.y += p.vy;

        // ── Opacity: boost near cursor ─────────────────────────────────────────
        const targetOpacity = p.baseOpacity + proximity * 0.35;
        p.opacity += (targetOpacity - p.opacity) * 0.1;

        // ── Draw ───────────────────────────────────────────────────────────────
        const particleHue = i % 3 === 0 ? hueAlt : hue;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${particleHue}, 75%, 72%, ${p.opacity})`;
        ctx.fill();
      }

      rafId = requestAnimationFrame(tick);
    };

    // ─── Init ─────────────────────────────────────────────────────────────────
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);
    resize();
    rafId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(rafId);
      ro.disconnect();
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseleave", onMouseLeave);
      mediaQuery.removeEventListener("change", onMotionChange);
    };
  }, [density, hue, hueAlt, repelRadius, repelStrength, springK, friction]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`}
      style={{ zIndex: 0 }}
    />
  );
}
