# Pixel Art Sprites

This directory contains pixel art sprite renderers for animals in the simulation.

## Sprites

### Penguin Sprite (`penguinSprite.ts`)
- **Features:**
  - Detailed penguin body with white belly
  - Black head with white face patch
  - Orange beak
  - Wings on both sides
  - Feet when on land
  - Color variation based on location (land vs sea)
  - Energy-based visual indicators

### Seal Sprite (`sealSprite.ts`)
- **Features:**
  - Detailed seal body with lighter belly
  - Head with snout and nose
  - Eyes with highlights
  - Flippers (front and back)
  - Tail when in sea
  - Color variation based on location (land vs sea)
  - Energy-based visual indicators

## Usage

```typescript
import { drawPenguin, drawSeal } from '../sprites';

// Draw a penguin
drawPenguin(ctx, {
  x: 100,
  y: 200,
  state: 'land', // or 'sea'
  energy: 120,
  maxEnergy: 150,
  facing: 'right', // or 'left'
});

// Draw a seal
drawSeal(ctx, {
  x: 300,
  y: 400,
  state: 'sea', // or 'land'
  energy: 180,
  maxEnergy: 200,
  facing: 'left', // or 'right'
});
```

## Sprite Features

### Direction Facing
- Sprites automatically flip based on `facing` parameter
- Direction is determined by movement direction in the simulation

### State-Based Appearance
- **Penguin:**
  - Land: White body
  - Sea: Light blue body
- **Seal:**
  - Land: Brown body
  - Sea: Darker brown body

### Energy Indicators
- Energy bars above each animal
- Color-coded: Green (>50%), Yellow (20-50%), Red (<20%)
- Low energy glow effect around animal

## Customization

To modify sprites, edit the respective sprite files:
- `penguinSprite.ts` - Penguin appearance
- `sealSprite.ts` - Seal appearance

You can adjust:
- Colors
- Sizes (via `scale` parameter)
- Shapes and proportions
- Additional details (eyes, beaks, etc.)

