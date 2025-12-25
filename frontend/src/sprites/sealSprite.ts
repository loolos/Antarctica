/**
 * Seal pixel art sprite renderer
 */

export interface SpriteOptions {
  x: number;
  y: number;
  state: 'land' | 'sea';
  energy: number;
  maxEnergy: number;
  facing?: 'left' | 'right';
}

/**
 * Draw a pixel art seal
 */
export function drawSeal(ctx: CanvasRenderingContext2D, options: SpriteOptions): void {
  const { x, y, state, energy, maxEnergy, facing = 'right' } = options;
  const isOnLand = state === 'land';
  const scale = 1.2; // Scale factor for sprite size
  
  // Energy-based color variation
  const energyPercent = energy / maxEnergy;
  const isHealthy = energyPercent > 0.5;
  
  // Save context
  ctx.save();
  ctx.translate(x, y);
  
  // Flip if facing left
  if (facing === 'left') {
    ctx.scale(-1, 1);
  }
  
  // Seal colors
  const bodyColor = isOnLand ? '#a08060' : '#6b5b4a'; // Brown on land, darker in sea
  const bellyColor = '#d4c4a8'; // Lighter belly
  const headColor = '#8b7355';
  const noseColor = '#000000';
  const eyeColor = '#ffffff';
  
  // Draw main body (large ellipse)
  ctx.fillStyle = bodyColor;
  ctx.beginPath();
  ctx.ellipse(0, 0, 14 * scale, 10 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw belly (lighter front)
  ctx.fillStyle = bellyColor;
  ctx.beginPath();
  ctx.ellipse(-3 * scale, 0, 8 * scale, 8 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw head
  ctx.fillStyle = headColor;
  ctx.beginPath();
  ctx.ellipse(-10 * scale, -2 * scale, 7 * scale, 6 * scale, -0.2, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw snout
  ctx.fillStyle = headColor;
  ctx.beginPath();
  ctx.ellipse(-14 * scale, -1 * scale, 4 * scale, 3 * scale, -0.3, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw nose
  ctx.fillStyle = noseColor;
  ctx.beginPath();
  ctx.arc(-15 * scale, -1 * scale, 1.5 * scale, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw eyes
  ctx.fillStyle = '#000000';
  ctx.beginPath();
  ctx.arc(-12 * scale, -4 * scale, 2 * scale, 0, Math.PI * 2);
  ctx.fill();
  
  // Eye highlight
  ctx.fillStyle = eyeColor;
  ctx.beginPath();
  ctx.arc(-11.5 * scale, -4.5 * scale, 0.8 * scale, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw flippers
  ctx.fillStyle = bodyColor;
  // Front flipper (left)
  ctx.beginPath();
  ctx.ellipse(8 * scale, -4 * scale, 4 * scale, 7 * scale, -0.4, 0, Math.PI * 2);
  ctx.fill();
  // Front flipper (right)
  ctx.beginPath();
  ctx.ellipse(8 * scale, 4 * scale, 4 * scale, 7 * scale, 0.4, 0, Math.PI * 2);
  ctx.fill();
  // Back flipper (left)
  ctx.beginPath();
  ctx.ellipse(12 * scale, -3 * scale, 3 * scale, 6 * scale, 0.2, 0, Math.PI * 2);
  ctx.fill();
  // Back flipper (right)
  ctx.beginPath();
  ctx.ellipse(12 * scale, 3 * scale, 3 * scale, 6 * scale, -0.2, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw tail (if in sea)
  if (!isOnLand) {
    ctx.fillStyle = bodyColor;
    ctx.beginPath();
    ctx.ellipse(14 * scale, 0, 3 * scale, 5 * scale, 0, 0, Math.PI * 2);
    ctx.fill();
  }
  
  // Energy indicator
  if (!isHealthy) {
    ctx.strokeStyle = energyPercent > 0.2 ? '#ffff00' : '#ff0000';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(0, 0, 18 * scale, 0, Math.PI * 2);
    ctx.stroke();
  }
  
  // Restore context
  ctx.restore();
  
  // Draw energy bar above seal
  const barWidth = 24;
  const barHeight = 3;
  const barX = x - barWidth / 2;
  const barY = y - 22;
  
  // Bar background
  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
  ctx.fillRect(barX, barY, barWidth, barHeight);
  
  // Bar fill
  const barColor = energyPercent > 0.5 ? '#00ff00' : energyPercent > 0.2 ? '#ffff00' : '#ff0000';
  ctx.fillStyle = barColor;
  ctx.fillRect(barX, barY, barWidth * energyPercent, barHeight);
  
  // Bar border
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 1;
  ctx.strokeRect(barX, barY, barWidth, barHeight);
}

