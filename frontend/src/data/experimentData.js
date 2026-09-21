export const experimentInfo = {

    aim: "Experiment 1: choose the UCI Adult Income dataset and apply advanced categorical encoding strategies beyond one-hot encoding — One-Hot, Target, Leave-One-Out and Embedding-Based Encoding — then compare their impact on model performance for predicting whether annual income is <=50K or >50K.",

    introduction: "Machine Learning is the process of teaching computers to find patterns in data without being explicitly programmed. This virtual lab walks through the complete supervised learning pipeline: from raw data ingestion to model evaluation. The two fundamental supervised problems are Classification (predicting a discrete label) and Regression (predicting a continuous value). An essential step in any pipeline is handling categorical features, which machine learning algorithms cannot consume directly, and must therefore be converted to numbers using encoding techniques.",

    dataset: {
        title: "UCI Adult Income Dataset",
        description: "The Adult dataset (UCI id=2, 48842 rows) predicts whether annual income exceeds $50K. Categorical columns include workclass, education, marital-status, occupation, relationship, race, sex and native-country. Numerical columns include age, education-num, capital-gain, capital-loss and hours-per-week. Target: income (<=50K / >50K). It is the primary experiment dataset; the app remains generic and can load other UCI ids.",
        defaultCode: "from ucimlrepo import fetch_ucirepo\n\nadult = fetch_ucirepo(id=2)",
    },

    classification: {

        title: "Classification",

        theory: "Classification is a supervised learning task where the target variable is a discrete class label (for example: spam / not spam, malignant / benign, or species of flower). The model learns a decision boundary that separates one class from another. Logistic Regression, despite its name, is a classification algorithm. It applies the logistic (sigmoid) function to a linear combination of the features, producing a probability between 0 and 1 that the sample belongs to a given class, and then thresholds that probability into class predictions. The model is trained by maximizing the likelihood of the observed labels, a process called Maximum Likelihood Estimation, typically implemented via gradient descent.",

        model: "Logistic Regression",

        advantages: [
            "Simple, fast, and highly interpretable - coefficients directly show feature influence.",
            "Works well on linearly separable data and provides probabilistic outputs.",
            "Easily regularized to prevent overfitting and handles multiclass via softmax.",
            "Performs well on small and medium sized datasets."
        ]

    },

    regression: {

        title: "Regression",

        theory: "Regression is a supervised learning task where the target variable is a continuous numeric value (for example: house price, temperature, or stock value). Linear Regression models the relationship between the features and the target as a straight line: y = w·x + b. The model learns the weights w and bias b that minimize the sum of squared differences between predicted and actual values, a procedure called Ordinary Least Squares. Linear Regression assumes a roughly linear relationship, independence of errors, and homoscedasticity, but remains one of the most widely used, interpretable models in machine learning.",

        model: "Linear Regression",

        advantages: [
            "Extremely fast to train and scale with even millions of samples.",
            "Highly interpretable - weights show the direction and strength of each feature.",
            "Closed-form solution via Ordinary Least Squares requires no iterative tuning.",
            "Excellent baseline model that most other regressors are compared against."
        ]

    },

    cleaning: {

        theory: "Raw datasets are almost never ready for modelling. Data cleaning (or data wrangling) is the process of correcting or removing incorrect, incomplete, irrelevant, or duplicated data. This lab normalises unicode text, neutralises placeholder tokens (., ?, NA, null), recovers numbers hidden as strings ($, %, commas), converts datetime-like columns, handles sentinel values (-999, inf), drops sparse/constant columns, imputes feature gaps (median/mode), groups rare categories into 'other', caps outliers (IQR) and removes duplicates. Missing targets are never imputed — those rows are dropped. Every operation is reported so no information is silently destroyed.",

        steps: [
            "Normalising string values (unicode NFKC, whitespace, case) and neutralising placeholder tokens.",
            "Recovering numeric/datetime columns hidden as strings; handling sentinel values.",
            "Dropping sparse (>50% missing) and constant columns; median/mode imputation for features.",
            "Grouping rare categories, capping outliers, dropping duplicates and missing-target rows."
        ]

    },

    one_hot: {
        title: "One-Hot Encoding",
        what: "Each category becomes its own binary (0/1) feature. City {Mumbai, Pune, Delhi} becomes City_Mumbai, City_Pune, City_Delhi.",
        why: "Provides a neutral numerical representation with no false ordering between categories.",
        how: "sklearn OneHotEncoder with handle_unknown='ignore'. Fit on train, transform train/test. Original categorical columns replaced by N binary columns.",
        advantages: ["No false ordinality.", "No target leakage (unsupervised).", "Works with any model."],
        disadvantages: ["Dimensionality explodes for high-cardinality features (native-country).", "Sparse matrix; many zeros."],
        leakage: "Safe from target leakage — it never looks at the target.",
        when: "Low-cardinality features (sex, race) or linear models where interpretability matters.",
    },

    target_encoding: {
        title: "Target Encoding",
        what: "Replaces each category with a statistic derived from the target — e.g. mean P(income>50K) for each occupation.",
        why: "Compact: one number per categorical column regardless of cardinality.",
        how: "category_encoders.TargetEncoder fitted ONLY on training data, then applied to test. Never compute means on the full dataset before splitting.",
        advantages: ["Compact representation.", "Captures category-target relationship directly."],
        disadvantages: ["Prone to overfitting on rare categories.", "Leaks if fitted before the split."],
        leakage: "WARNING: fitting on full data before splitting leaks test labels into training features. This lab splits FIRST, then fits on train only.",
        when: "High-cardinality features with enough samples per category and proper regularisation.",
    },

    leave_one_out: {
        title: "Leave-One-Out Encoding",
        what: "Like target encoding, but each training row's own target is excluded when computing its category statistic.",
        why: "Reduces the optimistic bias of naive target encoding on training data.",
        how: "category_encoders.LeaveOneOutEncoder fitted only on train. Test rows use full train statistics (their labels are unknown).",
        advantages: ["Less overfit than naive target encoding.", "Still compact."],
        disadvantages: ["Still uses targets — leakage possible if misapplied.", "Noisier for rare categories."],
        leakage: "Same rule: fit on train only. Excluding the current row helps, but does not excuse fitting on test.",
        when: "When target encoding overfits; a safer default for small categories.",
    },

    embedding_encoding: {
        title: "Embedding-Based Encoding",
        what: "Each category maps to an index, then to a trainable dense vector (embedding). Occupation -> index -> Embedding(dim=8) -> [0.21, -0.13, 0.72, ...].",
        why: "Learns similarity between categories from data while keeping representation dense and compact.",
        how: "PyTorch: per-feature nn.Embedding vocab built from TRAIN only (<UNK>=0 for unseen test categories) + scaled numericals -> Dense(64) -> ReLU -> Dropout -> output. Trained with validation split from train; test untouched until evaluation.",
        advantages: ["Dense, compact, learns category similarity.", "Handles high cardinality gracefully."],
        disadvantages: ["Requires more data/compute; less interpretable; training stochasticity."],
        leakage: "Vocabulary and weights come from train only. Test categories map through the frozen train vocabulary.",
        when: "High-cardinality data with enough rows (like Adult) where linear encodings underfit.",
    },

    mini_example: {
        title: "Mini example (City -> Placement)",
        rows: [
            { city: "Mumbai", y: 1 }, { city: "Mumbai", y: 1 }, { city: "Mumbai", y: 0 },
            { city: "Pune", y: 0 }, { city: "Pune", y: 0 }, { city: "Pune", y: 1 },
        ],
        note: "One-Hot: Mumbai->[1,0], Pune->[0,1]. Target: Mumbai->0.667, Pune->0.333 (train means). LOO: first Mumbai row -> mean of other Mumbais (1,0)=0.5. Embedding: Mumbai->index 1->[learned 8-dim vector].",
    },

    train_test_split: {
        theory: "Split BEFORE any target-based encoding. For classification use stratified splitting so train/test preserve class ratios. Test size 20% with random_state=42 is the default; the same indices are reused for all four encodings so comparison is fair.",
    },

    evaluation: {
        theory: "For binary classification report Accuracy, Precision, Recall and F1 (zero_division=0), plus the confusion matrix (TP/TN/FP/FN). Adult is imbalanced, so prefer F1 over raw accuracy.",
    },

    comparison_note: "Performance differences indicate how each representation affects the selected model. Same train/test split and same model configuration were used. Do not read small gaps as proof of universal superiority.",

    conclusion: "This experiment demonstrates a complete supervised machine learning workflow. A real UCI dataset was loaded, its problem type (classification or regression) was automatically detected, the data was cleaned, and multiple categorical encoding strategies were applied. By comparing the evaluation metrics (Accuracy/Precision/Recall/F1 for classification, or R2/MSE/RMSE/MAE for regression) across encoding techniques, we observe how the choice of encoding influences downstream model performance - proving that data representation is just as important as the choice of algorithm."
};
