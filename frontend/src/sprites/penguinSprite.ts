/**
 * Penguin pixel art sprite renderer
 */

export interface SpriteOptions {
  x: number;
  y: number;
  state: 'land' | 'sea';
  energy: number;
  maxEnergy: number;
  facing?: 'left' | 'right'; // Direction penguin is facing
  behaviorState?: string; // idle, searching, targeting, fleeing
  animationTime?: number; // Time for animation (0-1)
  isJuvenile?: boolean; // true if penguin is a juvenile
}

/**
 * Draw a pixel art penguin
 */
export function drawPenguin(ctx: CanvasRenderingContext2D, options: SpriteOptions): void {
  const { x, y, state, energy, maxEnergy, facing = 'right', behaviorState = 'idle', animationTime = 0, isJuvenile = false } = options;
  const isOnLand = state === 'land';
  // Juveniles are smaller (60% size)
  // Overall penguin size reduced
  const baseScale = 0.9;
  const scale = isJuvenile ? baseScale * 0.6 : baseScale;
  
  // Energy-based color variation
  const energyPercent = energy / maxEnergy;
  
  // Check if penguin should be horizontal (in water and hunting or fleeing)
  const isHorizontal = !isOnLand && (behaviorState === 'searching' || behaviorState === 'targeting' || behaviorState === 'fleeing');
  
  // Calculate animation offsets based on state and animation time
  let verticalOffset = 0;
  let wingAngle = 0;
  let bodyRotation = 0;
  
  if (behaviorState === 'fleeing') {
    if (isHorizontal) {
      // Fast horizontal swimming when fleeing in water
      verticalOffset = Math.sin(animationTime * Math.PI * 5) * 1;
      wingAngle = Math.sin(animationTime * Math.PI * 8) * 0.4;
    } else {
      // Fast bobbing motion when fleeing on land
      verticalOffset = Math.sin(animationTime * Math.PI * 4) * 2;
      wingAngle = Math.sin(animationTime * Math.PI * 6) * 0.3;
    }
  } else if (behaviorState === 'targeting') {
    if (isHorizontal) {
      // Horizontal swimming when targeting in water
      verticalOffset = Math.sin(animationTime * Math.PI * 2) * 1;
      wingAngle = Math.sin(animationTime * Math.PI * 4) * 0.3;
    } else {
      // Slight forward lean when targeting on land
      bodyRotation = 0.1;
      wingAngle = Math.sin(animationTime * Math.PI * 3) * 0.2;
    }
  } else if (behaviorState === 'searching') {
    if (isHorizontal) {
      // Horizontal swimming when searching in water
      verticalOffset = Math.sin(animationTime * Math.PI * 2) * 1;
      wingAngle = Math.sin(animationTime * Math.PI * 3) * 0.25;
    } else {
      // Gentle bobbing when searching on land
      verticalOffset = Math.sin(animationTime * Math.PI * 2) * 1;
      wingAngle = Math.sin(animationTime * Math.PI * 2) * 0.15;
    }
  } else if (isOnLand) {
    // Walking animation on land
    verticalOffset = Math.sin(animationTime * Math.PI * 3) * 1.5;
    bodyRotation = Math.sin(animationTime * Math.PI * 3) * 0.05;
  } else {
    // Swimming animation in sea (idle)
    verticalOffset = Math.sin(animationTime * Math.PI * 2) * 1;
    wingAngle = Math.sin(animationTime * Math.PI * 2) * 0.2;
  }
  
  // Save context
  ctx.save();
  ctx.translate(x, y + verticalOffset);
  
  // Rotate body to horizontal if in water and hunting
  if (isHorizontal) {
    // Rotate 90 degrees to make penguin horizontal
    ctx.rotate(Math.PI / 2);
    // Adjust facing: if facing right, head should be to the right (no flip needed)
    // If facing left, we need to flip vertically to make head point left
    if (facing === 'left') {
      ctx.scale(1, -1); // Flip vertically to reverse head direction
    }
  } else {
    // Normal vertical orientation
    ctx.rotate(bodyRotation);
    // Flip if facing left
    if (facing === 'left') {
      ctx.scale(-1, 1);
    }
  }
  
  // Penguin colors
  const bodyColor = isOnLand ? '#ffffff' : '#e0f0ff'; // White on land, lighter blue in sea
  const bellyColor = '#ffffff';
  const headColor = '#000000'; // Black head
  const beakColor = '#ffaa00'; // Orange beak
  const wingColor = '#000000';
  
  // Draw penguin body (main oval)
  ctx.fillStyle = bodyColor;
  ctx.beginPath();
  ctx.ellipse(0, 0, 10 * scale, 12 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw white belly (front part)
  ctx.fillStyle = bellyColor;
  ctx.beginPath();
  ctx.ellipse(-2 * scale, 0, 6 * scale, 10 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw head
  ctx.fillStyle = headColor;
  ctx.beginPath();
  ctx.arc(0, -14 * scale, 7 * scale, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw white face patch
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.ellipse(-2 * scale, -14 * scale, 4 * scale, 5 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw eyes
  ctx.fillStyle = '#000000';
  ctx.beginPath();
  ctx.arc(-3 * scale, -16 * scale, 1.5 * scale, 0, Math.PI * 2);
  ctx.arc(1 * scale, -16 * scale, 1.5 * scale, 0, Math.PI * 2);
  ctx.fill();
  
  // Draw beak
  ctx.fillStyle = beakColor;
  ctx.beginPath();
  ctx.moveTo(0, -12 * scale);
  ctx.lineTo(3 * scale, -11 * scale);
  ctx.lineTo(0, -10 * scale);
  ctx.closePath();
  ctx.fill();
  
  // Draw wings with animation
  ctx.fillStyle = wingColor;
  // Left wing (animated)
  ctx.save();
  ctx.translate(-8 * scale, 0);
  ctx.rotate(-0.3 + wingAngle);
  ctx.beginPath();
  ctx.ellipse(0, 0, 3 * scale, 8 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  // Right wing (back, animated)
  ctx.save();
  ctx.translate(8 * scale, 2 * scale);
  ctx.rotate(0.3 - wingAngle);
  ctx.beginPath();
  ctx.ellipse(0, 0, 3 * scale, 6 * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  
  // Draw feet (if on land)
  if (isOnLand) {
    ctx.fillStyle = '#ffaa00';
    // Left foot
    ctx.beginPath();
    ctx.ellipse(-4 * scale, 12 * scale, 3 * scale, 2 * scale, 0, 0, Math.PI * 2);
    ctx.fill();
    // Right foot
    ctx.beginPath();
    ctx.ellipse(4 * scale, 12 * scale, 3 * scale, 2 * scale, 0, 0, Math.PI * 2);
    ctx.fill();
  }
  
  // Restore context (no energy warning circle)
  ctx.restore();
  
  // Draw energy bar above penguin
  const barWidth = 20;
  const barHeight = 3;
  const barX = x - barWidth / 2;
  const barY = y - 25;
  
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

