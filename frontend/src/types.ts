/**
 * Type definitions
 */

export interface Animal {
  id: string;
  x: number;
  y: number;
  energy: number;
  age: number;
  max_energy: number;
  state?: 'land' | 'sea' | 'flying' | 'grounded';
  behavior_state?: string; // idle, searching, targeting, fleeing
  is_juvenile?: boolean; // true if animal is still a juvenile
  carrying_fish?: boolean; // seagull-only: true when holding fish in beak
  prey_processing_ticks?: number; // seagull-only: ticks spent processing prey on floe
}

export interface FloeFish {
  id: string;
  x: number;
  y: number;
  ttl_ticks: number;
  age: number;
}

export interface IceFloe {
  x: number;
  y: number;
  radius: number; // Bounding circle radius
  shape?: 'circle' | 'ellipse' | 'irregular';
  radius_x?: number;
  radius_y?: number;
  rotation?: number;
  irregularity?: number;
}

export interface Environment {
  width: number;
  height: number;
  ice_coverage: number;
  temperature: number;
  sea_level: number;
  season: number;
  ice_floes?: IceFloe[];
}

export interface WorldState {
  tick: number;
  penguins: Animal[];
  seals: Animal[];
  fish: Animal[];
  seagulls?: Animal[];
  floe_fish?: FloeFish[];
  environment: Environment;
}

export interface AnimationState {
  x: number;
  y: number;
  targetX: number;
  targetY: number;
}

