/**
 * Shared ML Algorithm Definitions, Hyperparameters & Metadata
 * Central registry for KNN, SVM, and Decision Tree
 */

export const ALGORITHMS = {
  knn: {
    id: 'knn',
    name: 'K-Nearest Neighbors',
    shortName: 'KNN',
    category: 'Instance-Based / Non-parametric',
    themeColor: 'var(--algo-knn)',
    bgColor: 'var(--algo-knn-bg)',
    borderColor: 'var(--algo-knn-border)',
    badgeText: 'Lazy Learner',
    summary: 'Classifies points based on the majority class among their K closest Euclidean neighbors.',
    defaultParams: {
      k: 3,
      metric: 'euclidean',
      weights: 'uniform'
    },
    controls: [
      {
        id: 'k',
        label: 'Number of Neighbors (K)',
        type: 'slider',
        min: 1,
        max: 25,
        step: 2, // Odd numbers prevent ties in binary classification
        description: 'Lower K = complex, wiggly boundary (high variance). Higher K = smoother boundary (high bias).'
      },
      {
        id: 'weights',
        label: 'Weighting Function',
        type: 'select',
        options: [
          { value: 'uniform', label: 'Uniform (All neighbors equal)' },
          { value: 'distance', label: 'Distance (Closer = higher weight)' }
        ],
        description: 'Distance weighting gives closer neighbors more influence over the prediction.'
      },
      {
        id: 'metric',
        label: 'Distance Metric',
        type: 'select',
        options: [
          { value: 'euclidean', label: 'Euclidean (L2 Norm)' },
          { value: 'manhattan', label: 'Manhattan (L1 Norm)' }
        ],
        description: 'Determines how geometric proximity between sample points is computed.'
      }
    ],
    mathFormula: 'y = \\operatorname{mode}(\\{y_i : x_i \\in N_K(x)\\})'
  },

  svm: {
    id: 'svm',
    name: 'Support Vector Machine',
    shortName: 'SVM',
    category: 'Max-Margin Separator',
    themeColor: 'var(--algo-svm)',
    bgColor: 'var(--algo-svm-bg)',
    borderColor: 'var(--algo-svm-border)',
    badgeText: 'Kernel Trick',
    summary: 'Finds optimal hyperplane with maximal margin between classes, optionally projecting with kernels.',
    defaultParams: {
      kernel: 'rbf',
      c: 1.0,
      gamma: 0.5
    },
    controls: [
      {
        id: 'kernel',
        label: 'Kernel Function',
        type: 'select',
        options: [
          { value: 'rbf', label: 'RBF (Gaussian Radial Basis)' },
          { value: 'linear', label: 'Linear (Straight hyperplane)' },
          { value: 'poly', label: 'Polynomial (Degree 3)' }
        ],
        description: 'Projects points into higher-dimensional space where they can be linearly separated.'
      },
      {
        id: 'c',
        label: 'Regularization Parameter (C)',
        type: 'slider',
        min: 0.05,
        max: 10.0,
        step: 0.05,
        description: 'Low C = soft margin (allows misclassifications). High C = hard margin (penalizes mistakes heavily).'
      },
      {
        id: 'gamma',
        label: 'Kernel Coefficient (Gamma)',
        type: 'slider',
        min: 0.05,
        max: 5.0,
        step: 0.05,
        showIf: (params) => params.kernel === 'rbf' || params.kernel === 'poly',
        description: 'Defines radius of influence of support vectors. High gamma = narrow bell curves (risk of overfitting).'
      }
    ],
    mathFormula: '\\min_{w,b} \\frac{1}{2}\\|w\\|^2 + C \\sum \\xi_i'
  },

  dt: {
    id: 'dt',
    name: 'Decision Tree',
    shortName: 'Decision Tree',
    category: 'Tree-Based Partitioning',
    themeColor: 'var(--algo-dt)',
    bgColor: 'var(--algo-dt-bg)',
    borderColor: 'var(--algo-dt-border)',
    badgeText: 'Orthogonal Cuts',
    summary: 'Recursively splits feature space with axis-parallel orthogonal decision boundaries.',
    defaultParams: {
      max_depth: 4,
      criterion: 'gini',
      min_samples_split: 2
    },
    controls: [
      {
        id: 'max_depth',
        label: 'Maximum Depth',
        type: 'slider',
        min: 1,
        max: 12,
        step: 1,
        description: 'Tree depth limit. Depth 1 = single orthogonal decision stump. High depth = axis-aligned overfitting.'
      },
      {
        id: 'criterion',
        label: 'Splitting Criterion',
        type: 'select',
        options: [
          { value: 'gini', label: 'Gini Impurity' },
          { value: 'entropy', label: 'Information Gain (Entropy)' }
        ],
        description: 'Purity metric used to evaluate each orthogonal candidate split across X and Y.'
      },
      {
        id: 'min_samples_split',
        label: 'Min Samples to Split',
        type: 'slider',
        min: 2,
        max: 10,
        step: 1,
        description: 'Minimum number of sample points required to split an internal node.'
      }
    ],
    mathFormula: 'Gini = 1 - \\sum_{k=1}^C p_k^2'
  }
};
