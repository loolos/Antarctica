/**
 * Seagull sprite renderer - flying vs grounded have distinct visuals
 */

export interface SeagullSpriteOptions {
  x: number;
  y: number;
  energy: number;
  maxEnergy: number;
  state?: 'flying' | 'grounded';
  facing?: 'left' | 'right';
  animationTime?: number;
  behaviorState?: string; // idle, searching, targeting, fleeing
  carryingFish?: boolean;
}

function drawCarriedFishIcon(
  ctx: CanvasRenderingContext2D,
  beakX: number,
  beakY: number,
  rotation = 0,
  scale = 1
): void {
  ctx.save();
  ctx.translate(beakX, beakY);
  ctx.rotate(0.08 + rotation);
  ctx.scale(scale, scale);

  ctx.fillStyle = '#4a9eff';
  ctx.beginPath();
  ctx.ellipse(0, 0, 3.2, 1.8, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.beginPath();
  ctx.moveTo(3.2, 0);
  ctx.lineTo(5.6, -1.5);
  ctx.lineTo(5.6, 1.5);
  ctx.closePath();
  ctx.fill();

  // Bite notch to differentiate from intact fish.
  ctx.fillStyle = '#f5f7fa';
  ctx.beginPath();
  ctx.arc(-2.4, 0, 1.2, -Math.PI / 2, Math.PI / 2);
  ctx.fill();

  ctx.restore();
}

export function drawSeagull(ctx: CanvasRenderingContext2D, options: SeagullSpriteOptions): void {
  const {
    x,
    y,
    state = 'flying',
    facing = 'right',
    animationTime = 0,
    energy,
    maxEnergy,
    behaviorState = 'idle',
    carryingFish = false,
  } = options;
  const isFlying = state === 'flying';
  const isProcessingPrey = !isFlying && behaviorState === 'processing_prey' && carryingFish;
  const energyPercent = maxEnergy > 0 ? energy / maxEnergy : 1;

  ctx.save();
  ctx.translate(x, y);

  if (facing === 'left') {
    ctx.scale(-1, 1);
  }

  if (isFlying) {
    // ===== FLYING POSE =====
    const wingFlap = Math.sin(animationTime * Math.PI * 8) * 0.7;
    const bob = Math.sin(animationTime * Math.PI * 3) * -4;
    ctx.translate(0, bob);

    // body (horizontal, flying)
    ctx.fillStyle = '#f5f7fa';
    ctx.beginPath();
    ctx.ellipse(0, 0, 10, 5, 0, 0, Math.PI * 2);
    ctx.fill();

    // wings spread
    ctx.save();
    ctx.translate(-2, -1);
    ctx.rotate(-0.8 + wingFlap);
    ctx.fillStyle = '#dde4ef';
    ctx.beginPath();
    ctx.ellipse(-10, 0, 12, 2.3, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    ctx.save();
    ctx.translate(2, -1);
    ctx.rotate(0.8 - wingFlap);
    ctx.fillStyle = '#dde4ef';
    ctx.beginPath();
    ctx.ellipse(10, 0, 12, 2.3, 0, 0, Math.PI * 2);
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

    if (carryingFish) {
      drawCarriedFishIcon(ctx, -16.5, -1.6);
    }

    // eye (color by behavior: pink=searching, reddish-brown=targeting, green=fleeing, dark=idle)
    const flyingEyeColor =
      behaviorState === 'searching' ? '#ff69b4' :
      behaviorState === 'targeting' ? '#8b4513' :
      behaviorState === 'fleeing' ? '#22c55e' :
      '#1b1b1b';
    ctx.fillStyle = flyingEyeColor;
    ctx.beginPath();
    ctx.arc(-8.8, -2.4, 1, 0, Math.PI * 2);
    ctx.fill();
  } else {
    // ===== STANDING POSE (grounded on land) =====
    const idleBob = isProcessingPrey ? 0 : Math.sin(animationTime * Math.PI * 2) * 0.8;
    const peckCycle = (Math.sin(animationTime * Math.PI * 8) + 1) * 0.5;
    const peckDrop = isProcessingPrey ? peckCycle * 2.8 : 0;
    const bodyLean = isProcessingPrey ? 0.16 : 0;
    ctx.translate(0, idleBob);
    ctx.rotate(bodyLean);

    // body (more vertical/oval for standing bird)
    ctx.fillStyle = '#f5f7fa';
    ctx.beginPath();
    ctx.ellipse(0, 2, 6, 8, 0, 0, Math.PI * 2);
    ctx.fill();

    // wings folded at sides (small tucked wings)
    ctx.fillStyle = '#e6ebf2';
    ctx.beginPath();
    ctx.ellipse(-5, isProcessingPrey ? 0.6 : 0, 4, 6, 0.3, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(5, isProcessingPrey ? 0.6 : 0, 4, 6, -0.3, 0, Math.PI * 2);
    ctx.fill();

    // head (above body, more upright)
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(isProcessingPrey ? 1.2 : 0, -6 + peckDrop, 3.5, 0, Math.PI * 2);
    ctx.fill();

    // beak (pecking downward while processing prey)
    ctx.fillStyle = '#ffcc66';
    ctx.beginPath();
    if (isProcessingPrey) {
      ctx.moveTo(3.4, -5.5 + peckDrop);
      ctx.lineTo(8.8, -2.8 + peckDrop);
      ctx.lineTo(4.1, -3.8 + peckDrop);
    } else {
      ctx.moveTo(2, -6);
      ctx.lineTo(8, -5.5);
      ctx.lineTo(2, -5);
    }
    ctx.closePath();
    ctx.fill();

    if (carryingFish) {
      if (isProcessingPrey) {
        const fishWiggle = Math.sin(animationTime * Math.PI * 12) * 0.16;
        drawCarriedFishIcon(ctx, 9.2, -2.4 + peckDrop, 0.45 + fishWiggle, 0.95);

        // Tiny "crumb/bone" specks to make pecking more expressive.
        ctx.fillStyle = 'rgba(244, 247, 251, 0.7)';
        ctx.beginPath();
        ctx.arc(7.4, -0.4 + peckDrop, 0.55, 0, Math.PI * 2);
        ctx.arc(8.7, 0.4 + peckDrop, 0.45, 0, Math.PI * 2);
        ctx.fill();
      } else {
        drawCarriedFishIcon(ctx, 10.5, -5.5);
      }
    }

    // eye (color by behavior: pink=searching, reddish-brown=targeting, green=fleeing, dark=idle)
    const groundedEyeColor =
      behaviorState === 'searching' ? '#ff69b4' :
      behaviorState === 'targeting' ? '#8b4513' :
      behaviorState === 'fleeing' ? '#22c55e' :
      '#1b1b1b';
    ctx.fillStyle = groundedEyeColor;
    ctx.beginPath();
    ctx.arc(isProcessingPrey ? 2.2 : 1.2, -6.8 + peckDrop, 1.1, 0, Math.PI * 2);
    ctx.fill();

    // legs (standing)
    ctx.strokeStyle = '#d4a84b';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(-2.4, 9);
    ctx.lineTo(-2.8, isProcessingPrey ? 14.8 : 14);
    ctx.moveTo(2.2, 9);
    ctx.lineTo(2.8, isProcessingPrey ? 14.8 : 14);
    ctx.stroke();
  }

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
