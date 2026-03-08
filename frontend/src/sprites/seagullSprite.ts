/**
 * Seagull sprite renderer
 */

export interface SeagullSpriteOptions {
  x: number;
  y: number;
  energy: number;
  maxEnergy: number;
  facing?: 'left' | 'right';
  animationTime?: number;
}

export function drawSeagull(ctx: CanvasRenderingContext2D, options: SeagullSpriteOptions): void {
  const { x, y, facing = 'right', animationTime = 0, energy, maxEnergy } = options;
  const wingFlap = Math.sin(animationTime * Math.PI * 6) * 0.5;
  const bob = Math.sin(animationTime * Math.PI * 2) * 1.2;
  const energyPercent = maxEnergy > 0 ? energy / maxEnergy : 1;

  ctx.save();
  ctx.translate(x, y + bob);

  if (facing === 'left') {
    ctx.scale(-1, 1);
  }

  // body
  ctx.fillStyle = '#f5f7fa';
  ctx.beginPath();
  ctx.ellipse(0, 0, 10, 5, 0, 0, Math.PI * 2);
  ctx.fill();

  // wing left
  ctx.save();
  ctx.translate(-2, -1);
  ctx.rotate(-0.8 + wingFlap);
  ctx.fillStyle = '#e6ebf2';
  ctx.beginPath();
  ctx.ellipse(-10, 0, 10, 2.3, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // wing right
  ctx.save();
  ctx.translate(2, -1);
  ctx.rotate(0.8 - wingFlap);
  ctx.fillStyle = '#e6ebf2';
  ctx.beginPath();
  ctx.ellipse(10, 0, 10, 2.3, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // head
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.arc(-8, -2, 3, 0, Math.PI * 2);
  ctx.fill();

  // beak
  ctx.fillStyle = '#ffcc66';
  ctx.beginPath();
  ctx.moveTo(-10, -2);
  ctx.lineTo(-14, -1.5);
  ctx.lineTo(-10, -0.8);
  ctx.closePath();
  ctx.fill();

  // eye
  ctx.fillStyle = '#1b1b1b';
  ctx.beginPath();
  ctx.arc(-8.8, -2.4, 0.7, 0, Math.PI * 2);
  ctx.fill();

  // energy bar
  const barWidth = 18;
  const barX = -barWidth / 2;
  const barY = -14;
  ctx.fillStyle = 'rgba(0, 0, 0, 0.45)';
  ctx.fillRect(barX, barY, barWidth, 2.5);
  ctx.fillStyle = energyPercent > 0.5 ? '#67ff7a' : energyPercent > 0.25 ? '#ffd166' : '#ff5d5d';
  ctx.fillRect(barX, barY, barWidth * Math.max(0, Math.min(1, energyPercent)), 2.5);

  ctx.restore();
}
