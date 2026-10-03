/**
 * Mathematical generators for classic 2D ML classification toy datasets.
 * Coordinates are normalized in [0.05, 0.95] for optimal canvas rendering.
 */

// Simple pseudo-random gaussian generator (Box-Muller)
function randomGaussian(mean = 0, stdev = 1) {
  const u = 1 - Math.random();
  const v = Math.random();
  const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  return mean + z * stdev;
}

export const DATASET_PRESETS = {
  moons: {
    id: 'moons',
    name: 'Two Moons',
    tagline: 'Non-linear interlocking semicircles',
    generate: (n = 60, noise = 0.04) => {
      const points = [];
      const nEach = Math.floor(n / 2);

      // Upper moon (Class 0 - Blue)
      for (let i = 0; i < nEach; i++) {
        const theta = (Math.PI * i) / (nEach - 1);
        const x = 0.5 + 0.28 * Math.cos(theta) + randomGaussian(0, noise);
        const y = 0.42 - 0.28 * Math.sin(theta) + randomGaussian(0, noise);
        points.push({
          x: Math.max(0.05, Math.min(0.95, x)),
          y: Math.max(0.05, Math.min(0.95, y)),
          label: 0
        });
      }

      // Lower moon (Class 1 - Orange)
      for (let i = 0; i < nEach; i++) {
        const theta = (Math.PI * i) / (nEach - 1);
        const x = 0.5 + 0.28 * (1 - Math.cos(theta)) - 0.14 + randomGaussian(0, noise);
        const y = 0.58 + 0.28 * Math.sin(theta) - 0.14 + randomGaussian(0, noise);
        points.push({
          x: Math.max(0.05, Math.min(0.95, x)),
          y: Math.max(0.05, Math.min(0.95, y)),
          label: 1
        });
      }

      return points;
    }
  },

  circles: {
    id: 'circles',
    name: 'Concentric Circles',
    tagline: 'Radial non-linear boundary test',
    generate: (n = 70, noise = 0.035) => {
      const points = [];
      const nEach = Math.floor(n / 2);

      // Inner circle (Class 0 - Blue)
      for (let i = 0; i < nEach; i++) {
        const theta = (2 * Math.PI * i) / nEach;
        const r = 0.16 + randomGaussian(0, noise);
        const x = 0.5 + r * Math.cos(theta);
        const y = 0.5 + r * Math.sin(theta);
        points.push({
          x: Math.max(0.05, Math.min(0.95, x)),
          y: Math.max(0.05, Math.min(0.95, y)),
          label: 0
        });
      }

      // Outer circle (Class 1 - Orange)
      for (let i = 0; i < nEach; i++) {
        const theta = (2 * Math.PI * i) / nEach;
        const r = 0.36 + randomGaussian(0, noise);
        const x = 0.5 + r * Math.cos(theta);
        const y = 0.5 + r * Math.sin(theta);
        points.push({
          x: Math.max(0.05, Math.min(0.95, x)),
          y: Math.max(0.05, Math.min(0.95, y)),
          label: 1
        });
      }

      return points;
    }
  },

  linear: {
    id: 'linear',
    name: 'Linearly Separable',
    tagline: 'Two distinct gaussian clusters',
    generate: (n = 50, noise = 0.06) => {
      const points = [];
      const nEach = Math.floor(n / 2);

      // Top-Left Cluster (Class 0 - Blue)
      for (let i = 0; i < nEach; i++) {
        const x = randomGaussian(0.32, noise);
        const y = randomGaussian(0.32, noise);
        points.push({
          x: Math.max(0.05, Math.min(0.95, x)),
          y: Math.max(0.05, Math.min(0.95, y)),
          label: 0
        });
      }

      // Bottom-Right Cluster (Class 1 - Orange)
      for (let i = 0; i < nEach; i++) {
        const x = randomGaussian(0.68, noise);
        const y = randomGaussian(0.68, noise);
        points.push({
          x: Math.max(0.05, Math.min(0.95, x)),
          y: Math.max(0.05, Math.min(0.95, y)),
          label: 1
        });
      }

      return points;
    }
  },

  xor: {
    id: 'xor',
    name: 'XOR Problem',
    tagline: 'Classic 4-quadrant non-linear benchmark',
    generate: (n = 60, noise = 0.05) => {
      const points = [];
      const nPerQuadrant = Math.floor(n / 4);

      // Top-Left: Class 0
      for (let i = 0; i < nPerQuadrant; i++) {
        points.push({
          x: Math.max(0.05, Math.min(0.95, randomGaussian(0.3, noise))),
          y: Math.max(0.05, Math.min(0.95, randomGaussian(0.3, noise))),
          label: 0
        });
      }

      // Bottom-Right: Class 0
      for (let i = 0; i < nPerQuadrant; i++) {
        points.push({
          x: Math.max(0.05, Math.min(0.95, randomGaussian(0.7, noise))),
          y: Math.max(0.05, Math.min(0.95, randomGaussian(0.7, noise))),
          label: 0
        });
      }

      // Top-Right: Class 1
      for (let i = 0; i < nPerQuadrant; i++) {
        points.push({
          x: Math.max(0.05, Math.min(0.95, randomGaussian(0.7, noise))),
          y: Math.max(0.05, Math.min(0.95, randomGaussian(0.3, noise))),
          label: 1
        });
      }

      // Bottom-Left: Class 1
      for (let i = 0; i < nPerQuadrant; i++) {
        points.push({
          x: Math.max(0.05, Math.min(0.95, randomGaussian(0.3, noise))),
          y: Math.max(0.05, Math.min(0.95, randomGaussian(0.7, noise))),
          label: 1
        });
      }

      return points;
    }
  }
};
