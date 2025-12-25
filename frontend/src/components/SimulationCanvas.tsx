import React, { useRef, useEffect } from 'react';
import { WorldState, AnimationState } from '../types';

interface SimulationCanvasProps {
  worldState: WorldState | null;
  width?: number;
  height?: number;
}

export const SimulationCanvas: React.FC<SimulationCanvasProps> = ({
  worldState,
  width = 800,
  height = 600,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();
  const animationsRef = useRef<Map<string, AnimationState>>(new Map());
  const worldStateRef = useRef<WorldState | null>(null);

  // Update worldState reference
  useEffect(() => {
    worldStateRef.current = worldState;
  }, [worldState]);

  // Update animation target positions
  useEffect(() => {
    if (!worldState) return;

    const animations = animationsRef.current;

    // Update penguin animations
    worldState.penguins.forEach((penguin) => {
      const existing = animations.get(penguin.id);
      if (existing) {
        animations.set(penguin.id, {
          ...existing,
          targetX: penguin.x,
          targetY: penguin.y,
        });
      } else {
        animations.set(penguin.id, {
          x: penguin.x,
          y: penguin.y,
          targetX: penguin.x,
          targetY: penguin.y,
        });
      }
    });

    // Update seal animations
    worldState.seals.forEach((seal) => {
      const existing = animations.get(seal.id);
      if (existing) {
        animations.set(seal.id, {
          ...existing,
          targetX: seal.x,
          targetY: seal.y,
        });
      } else {
        animations.set(seal.id, {
          x: seal.x,
          y: seal.y,
          targetX: seal.x,
          targetY: seal.y,
        });
      }
    });

    // Update fish animations
    worldState.fish.forEach((fish) => {
      const existing = animations.get(fish.id);
      if (existing) {
        animations.set(fish.id, {
          ...existing,
          targetX: fish.x,
          targetY: fish.y,
        });
      } else {
        animations.set(fish.id, {
          x: fish.x,
          y: fish.y,
          targetX: fish.x,
          targetY: fish.y,
        });
      }
    });

    // Remove animals that no longer exist
    const allIds = new Set([
      ...worldState.penguins.map((p) => p.id),
      ...worldState.seals.map((s) => s.id),
      ...worldState.fish.map((f) => f.id),
    ]);

    for (const [id] of animations) {
      if (!allIds.has(id)) {
        animations.delete(id);
      }
    }
  }, [worldState]);

  // Animation loop (60fps interpolation)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let lastTime = performance.now();

    const animate = (currentTime: number) => {
      const deltaTime = Math.min((currentTime - lastTime) / 1000, 0.1); // Limit max delta
      lastTime = currentTime;

      const animations = animationsRef.current;
      const worldState = worldStateRef.current;

      // Update animation state (smooth interpolation)
      const lerpSpeed = 10; // Interpolation speed
      for (const [id, anim] of animations) {
        const dx = anim.targetX - anim.x;
        const dy = anim.targetY - anim.y;
        animations.set(id, {
          x: anim.x + dx * lerpSpeed * deltaTime,
          y: anim.y + dy * lerpSpeed * deltaTime,
          targetX: anim.targetX,
          targetY: anim.targetY,
        });
      }

      // Render
      if (worldState) {
        render(ctx, worldState, animations);
      }

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const render = (
    ctx: CanvasRenderingContext2D,
    state: WorldState,
    anims: Map<string, AnimationState>
  ) => {
    // Clear canvas
    ctx.fillStyle = '#0a0a1a';
    ctx.fillRect(0, 0, width, height);

    const env = state.environment;

    // Draw sea (background)
    ctx.fillStyle = '#1a3a5a';
    ctx.fillRect(0, 0, width, height);

    // Draw Ice Floes (Islands)
    if (env.ice_floes) {
      env.ice_floes.forEach(floe => {
        ctx.fillStyle = '#eef4ff'; // White-ish ice color
        ctx.beginPath();
        ctx.arc(floe.x, floe.y, floe.radius, 0, Math.PI * 2);
        ctx.fill();

        // Optional: nice stroke
        ctx.strokeStyle = '#cce0ff';
        ctx.lineWidth = 2;
        ctx.stroke();
      });
    }

    // Draw global ice layer (if extremely cold, maybe overlay everywhere?)
    // For now, let's keep the scene clear to see the islands
    if (env.temperature < -20) {
      ctx.fillStyle = `rgba(255, 255, 255, 0.2)`;
      ctx.fillRect(0, 0, width, height);
    }

    // Draw fish
    state.fish.forEach((fish) => {
      const anim = anims.get(fish.id);
      if (!anim) return;

      ctx.fillStyle = '#4a9eff';
      ctx.beginPath();
      ctx.arc(anim.x, anim.y, 3, 0, Math.PI * 2);
      ctx.fill();
    });

    // 绘制企鹅
    state.penguins.forEach((penguin) => {
      const anim = anims.get(penguin.id);
      if (!anim) return;

      const isOnLand = penguin.state === 'land';
      ctx.fillStyle = isOnLand ? '#ffffff' : '#aaccff';
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 1;

      // Draw penguin body
      ctx.beginPath();
      ctx.arc(anim.x, anim.y, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Draw penguin head
      ctx.beginPath();
      ctx.arc(anim.x, anim.y - 10, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Energy bar
      const energyPercent = penguin.energy / penguin.max_energy;
      ctx.fillStyle = energyPercent > 0.5 ? '#00ff00' : energyPercent > 0.2 ? '#ffff00' : '#ff0000';
      ctx.fillRect(anim.x - 10, anim.y - 20, 20 * energyPercent, 2);
    });

    // Draw seals
    state.seals.forEach((seal) => {
      const anim = anims.get(seal.id);
      if (!anim) return;

      const isOnLand = seal.state === 'land';
      ctx.fillStyle = isOnLand ? '#8b7355' : '#6b5b4a';
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 1;

      // Draw seal body (ellipse)
      ctx.beginPath();
      ctx.ellipse(anim.x, anim.y, 12, 8, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Energy bar
      const energyPercent = seal.energy / seal.max_energy;
      ctx.fillStyle = energyPercent > 0.5 ? '#00ff00' : energyPercent > 0.2 ? '#ffff00' : '#ff0000';
      ctx.fillRect(anim.x - 12, anim.y - 18, 24 * energyPercent, 2);
    });

    // Draw info text
    ctx.fillStyle = '#ffffff';
    ctx.font = '14px Arial';
    ctx.fillText(`Tick: ${state.tick}`, 10, 20);
    ctx.fillText(`Penguins: ${state.penguins.length}`, 10, 40);
    ctx.fillText(`Seals: ${state.seals.length}`, 10, 60);
    ctx.fillText(`Fish: ${state.fish.length}`, 10, 80);
    ctx.fillText(`Temperature: ${state.environment.temperature.toFixed(1)}°C`, 10, 100);
    ctx.fillText(`Season: ${(state.environment.season / 1000).toFixed(1)}`, 10, 120);
  };

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        border: '2px solid #444',
        borderRadius: '8px',
        display: 'block',
      }}
    />
  );
};

