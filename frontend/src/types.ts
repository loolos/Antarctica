/**
 * 类型定义
 */

export interface Animal {
  id: string;
  x: number;
  y: number;
  energy: number;
  age: number;
  max_energy: number;
  state?: 'land' | 'sea';
}

export interface Environment {
  width: number;
  height: number;
  ice_coverage: number;
  temperature: number;
  sea_level: number;
  season: number;
  ice_floes?: { x: number; y: number; radius: number }[];
}

export interface WorldState {
  tick: number;
  penguins: Animal[];
  seals: Animal[];
  fish: Animal[];
  environment: Environment;
}

export interface AnimationState {
  x: number;
  y: number;
  targetX: number;
  targetY: number;
}

