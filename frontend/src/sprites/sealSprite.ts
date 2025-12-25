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
  behaviorState?: string; // idle, searching, targeting, fleeing
  animationTime?: number; // Time for animation (0-1)
  isJuvenile?: boolean; // true if seal is a juvenile
}

/**
 * Draw a pixel art seal
 */
export function drawSeal(ctx: CanvasRenderingContext2D, options: SpriteOptions): void {
  const { x, y, state, energy, maxEnergy, facing = 'right', behaviorState = 'idle', animationTime = 0, isJuvenile = false } = options;
  const isOnLand = state === 'land';
  // Juveniles are smaller (60% size)
  const baseScale = 1.2;
  const scale = isJuvenile ? baseScale * 0.6 : baseScale;
  
  // Energy-based color variation
  const energyPercent = energy / maxEnergy;
  
  // Calculate animation offsets based on state and animation time
  let verticalOffset = 0;
  let bodyRotation = 0;
  let flipperAngle = 0;
  let bodyStretch = 1;
  
  if (behaviorState === 'fleeing') {
    // Fast swimming/crawling motion when fleeing
    verticalOffset = Math.sin(animationTime * Math.PI * 5) * 2;
    flipperAngle = Math.sin(animationTime * Math.PI * 6) * 0.4;
    bodyStretch = 1 + Math.sin(animationTime * Math.PI * 5) * 0.1;
  } else if (behaviorState === 'targeting') {
    // Forward lean and focused movement when targeting
    bodyRotation = 0.15;
    flipperAngle = Math.sin(animationTime * Math.PI * 4) * 0.3;
    bodyStretch = 1.05;
  } else if (behaviorState === 'searching') {
    // Gentle movement when searching
    verticalOffset = Math.sin(animationTime * Math.PI * 2) * 1;
    flipperAngle = Math.sin(animationTime * Math.PI * 2) * 0.2;
  } else if (isOnLand) {
    // Crawling animation on land
    verticalOffset = Math.sin(animationTime * Math.PI * 2) * 1;
    bodyRotation = Math.sin(animationTime * Math.PI * 2) * 0.1;
  } else {
    // Swimming animation in sea
    verticalOffset = Math.sin(animationTime * Math.PI * 2) * 1.5;
    flipperAngle = Math.sin(animationTime * Math.PI * 2) * 0.3;
    bodyStretch = 1 + Math.sin(animationTime * Math.PI * 2) * 0.05;
  }
  
  // Save context
  ctx.save();
  ctx.translate(x, y + verticalOffset);
  ctx.rotate(bodyRotation);
  
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
  
  // Draw main body (large ellipse) with stretch animation
  ctx.fillStyle = bodyColor;
  ctx.beginPath();
  ctx.ellipse(0, 0, 14 * scale * bodyStretch, 10 * scale, 0, 0, Math.PI * 2);
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
  
  // Draw flippers with animation
  ctx.fillStyle = bodyColor;
  // Front flipper (left, animated)
  ctx.save();
  ctx.translate(8 * scale, -4 * scale);
  ctx.rotate(-0.4 + flipperAngle);
  ctx.beginPath();
  ctx.ellipse(0, 0, 4 * scale, 7 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  // Front flipper (right, animated)
  ctx.save();
  ctx.translate(8 * scale, 4 * scale);
  ctx.rotate(0.4 - flipperAngle);
  ctx.beginPath();
  ctx.ellipse(0, 0, 4 * scale, 7 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  // Back flipper (left, animated)
  ctx.save();
  ctx.translate(12 * scale, -3 * scale);
  ctx.rotate(0.2 + flipperAngle * 0.5);
  ctx.beginPath();
  ctx.ellipse(0, 0, 3 * scale, 6 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  // Back flipper (right, animated)
  ctx.save();
  ctx.translate(12 * scale, 3 * scale);
  ctx.rotate(-0.2 - flipperAngle * 0.5);
  ctx.beginPath();
  ctx.ellipse(0, 0, 3 * scale, 6 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  
  // Draw tail (if in sea)
  if (!isOnLand) {
    ctx.fillStyle = bodyColor;
    ctx.beginPath();
    ctx.ellipse(14 * scale, 0, 3 * scale, 5 * scale, 0, 0, Math.PI * 2);
    ctx.fill();
  }
  
  // Restore context (no energy warning circle)
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

