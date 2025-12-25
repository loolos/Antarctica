/**
 * Fish pixel art sprite renderer with animations
 */

export interface FishSpriteOptions {
  x: number;
  y: number;
  energy: number;
  maxEnergy: number;
  facing?: 'left' | 'right';
  animationTime?: number; // Time for animation (0-1)
}

/**
 * Draw an animated pixel art fish
 */
export function drawFish(ctx: CanvasRenderingContext2D, options: FishSpriteOptions): void {
  const { x, y, facing = 'right', animationTime = 0 } = options;
  const scale = 1.0;
  
  // Calculate swimming animation
  const tailAngle = Math.sin(animationTime * Math.PI * 4) * 0.3; // Tail wagging
  const bodyOffset = Math.sin(animationTime * Math.PI * 2) * 1; // Body undulation
  const finAngle = Math.sin(animationTime * Math.PI * 3) * 0.2; // Fin movement
  
  // Save context
  ctx.save();
  ctx.translate(x, y + bodyOffset);
  
  // Flip if facing left
  if (facing === 'left') {
    ctx.scale(-1, 1);
  }
  
  // Fish colors (fixed, no energy-based variation)
  const bodyColor = '#4a9eff';
  const bellyColor = '#e0f0ff';
  const finColor = '#3a8aef';
  const eyeColor = '#000000';
  const eyeHighlight = '#ffffff';
  
  // Draw main body (ellipse)
  ctx.fillStyle = bodyColor;
  ctx.beginPath();
  ctx.ellipse(0, 0, 6 * scale, 3 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw belly (lighter front)
  ctx.fillStyle = bellyColor;
  ctx.beginPath();
  ctx.ellipse(-1 * scale, 0, 4 * scale, 2.5 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw head
  ctx.fillStyle = bodyColor;
  ctx.beginPath();
  ctx.ellipse(-4 * scale, 0, 3 * scale, 2.5 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw eye
  ctx.fillStyle = eyeColor;
  ctx.beginPath();
  ctx.arc(-4.5 * scale, -0.5 * scale, 1 * scale, 0, Math.PI * 2);
  ctx.fill();
  
  // Eye highlight
  ctx.fillStyle = eyeHighlight;
  ctx.beginPath();
  ctx.arc(-4.2 * scale, -0.7 * scale, 0.4 * scale, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw tail (animated, wagging)
  ctx.save();
  ctx.translate(6 * scale, 0);
  ctx.rotate(tailAngle);
  ctx.fillStyle = bodyColor;
  ctx.beginPath();
  // Tail shape (triangle-like)
  ctx.moveTo(0, 0);
  ctx.lineTo(4 * scale, -2 * scale);
  ctx.lineTo(4 * scale, 2 * scale);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
  
  // Draw top fin (dorsal fin, animated)
  ctx.save();
  ctx.translate(-1 * scale, -2.5 * scale);
  ctx.rotate(finAngle);
  ctx.fillStyle = finColor;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(1 * scale, -2 * scale);
  ctx.lineTo(2 * scale, -1 * scale);
  ctx.lineTo(1 * scale, 0);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
  
  // Draw bottom fin (anal fin, animated)
  ctx.save();
  ctx.translate(-1 * scale, 2.5 * scale);
  ctx.rotate(-finAngle);
  ctx.fillStyle = finColor;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(1 * scale, 2 * scale);
  ctx.lineTo(2 * scale, 1 * scale);
  ctx.lineTo(1 * scale, 0);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
  
  // Draw side fins (pectoral fins, animated)
  ctx.save();
  ctx.translate(-2 * scale, 0);
  ctx.rotate(finAngle * 0.5);
  // Left fin
  ctx.fillStyle = finColor;
  ctx.beginPath();
  ctx.ellipse(0, -1.5 * scale, 1.5 * scale, 1 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  // Right fin
  ctx.beginPath();
  ctx.ellipse(0, 1.5 * scale, 1.5 * scale, 1 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  
  // Restore context (no energy bar for fish)
  ctx.restore();
}

