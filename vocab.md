# IOAI Training Platform — Controlled Vocabulary / Nền tảng luyện thi IOAI — Từ vựng kiểm soát

Status / Trạng thái: Draft for first release / Bản nháp cho phiên bản đầu tiên  
Purpose / Mục đích: Canonical vocabulary for tagging learning and competition tasks / Từ vựng chuẩn để gắn nhãn bài học và bài thi

## 1. General rules / Quy tắc chung

- Store stable uppercase codes in the database. Treat display labels as translatable content.
- The canonical identity of every controlled-vocabulary value is the composite key `(vocabulary_type, code)`, not `code` alone. Reusing a code in different vocabulary types is permitted only when the composite identities remain distinct.
- A task has exactly one pathway stage, one primary competency, one difficulty, and one task type.
- A task may have up to three secondary competencies, multiple topics, and multiple data modalities.
- Competencies describe assessable abilities. Topics describe narrower concepts, methods, tools, and techniques.
- Difficulty is relative to the pathway stage. Always display the two together, for example, **Competitive AI · Hard**.
- Prerequisites are references to competencies, topics, tasks, or learning units; they are not free-form tags.
- Expected time and compute limits are stored as exact numeric values. Categories are derived for filtering and display.
- Learning objectives are observable statements, not categorical values.

Example canonical references:

```json
{
  "vocabulary_type": "COMPETENCY",
  "code": "DL_TRANSFORMERS"
}
```

```json
{
  "vocabulary_type": "TOPIC",
  "code": "DL_TRANSFORMERS"
}
```

These values may share a human-readable code and label, but they are different records with different purposes. Database constraints, APIs, imports, and analytics must preserve `vocabulary_type`.

### Learner-facing presentation / Cách trình bày cho người học

- Stage answers **where the learner is in the pathway**; competency answers **what assessable ability the task develops or measures**; topic answers **which concepts, methods, or tools are involved**; prerequisite answers **what should be learned first**; difficulty answers **how demanding the task is within its stage**.
- Always present stage and difficulty together, for example, **Competition Foundations · Hard**.
- Use stages and topics as the primary learner-facing discovery controls. Competencies should mainly power recommendations, progress reports, and optional advanced filtering.
- On a problem row or card, show at most two topic labels and collapse the remainder. Put complete metadata in a details view.
- Do not render the entire topic vocabulary as a flat chip list. Show the top-level topic families and expose descendants through a searchable hierarchical picker.
- Topic selection should optionally include descendants. Search must recognize English labels, Vietnamese labels, and approved aliases while storing only canonical codes.
- Task completion status and learning evidence are separate dimensions. During the initial releases, use only `NOT_STARTED`, `ATTEMPTED`, and `COMPLETED` for task status; do not use `MASTERED`.
- Represent learning evidence with `INTRODUCED`, `PRACTICED`, `APPLIED`, and `PROFICIENT` as defined in Section 8. A completed task may contribute evidence without proving mastery of a topic or competency.

## 2. Pathway stage / Giai đoạn học tập

Cardinality: single-select, ordered.

| Code | English label | Vietnamese label |
|---|---|---|
| `AI_1_FOUNDATIONS` | AI Foundations | Nền tảng AI |
| `AI_2_COMPETITION_FOUNDATIONS` | Competition Foundations | Nền tảng thi đấu AI |
| `AI_3_HIGHSCHOOL` | High-school Competition | AI thi đấu mức THPT |
| `AI_4_STUDENT` | Collegiate Competition | AI thi đấu mức đại học |
| `AI_OPEN` | Open / Cross-level | Mở / Liên cấp độ |

`AI_OPEN` is for cross-level projects and events. It should not replace the most appropriate stage for ordinary problems.

## 3. Competency / Năng lực

Cardinality: one primary competency and zero to three secondary competencies.

### Mathematical foundations / Nền tảng toán học

| Code | English label | Vietnamese label |
|---|---|---|
| `MATH_LINEAR_ALGEBRA` | Linear Algebra | Đại số tuyến tính |
| `MATH_PROBABILITY` | Probability | Xác suất |
| `MATH_STATISTICS` | Statistics | Thống kê |
| `MATH_CALCULUS` | Calculus | Giải tích |
| `MATH_OPTIMIZATION` | Optimization | Tối ưu hóa |
| `MATH_DISCRETE` | Discrete Mathematics | Toán rời rạc |

### Programming / Lập trình

| Code | English label | Vietnamese label |
|---|---|---|
| `PROG_PYTHON` | Python Fundamentals | Nền tảng Python |
| `PROG_ALGORITHMIC_THINKING` | Algorithmic Thinking | Tư duy thuật toán |
| `PROG_DATA_STRUCTURES` | Data Structures | Cấu trúc dữ liệu |
| `PROG_NUMERICAL_COMPUTING` | Numerical Computing | Tính toán số |
| `PROG_SOFTWARE_ENGINEERING` | Software Engineering | Kỹ nghệ phần mềm |
| `PROG_DEBUGGING` | Debugging | Gỡ lỗi |

### Data / Dữ liệu

| Code | English label | Vietnamese label |
|---|---|---|
| `DATA_COLLECTION` | Data Collection | Thu thập dữ liệu |
| `DATA_CLEANING` | Data Cleaning | Làm sạch dữ liệu |
| `DATA_EXPLORATION` | Exploratory Data Analysis | Phân tích khám phá dữ liệu |
| `DATA_VISUALIZATION` | Data Visualization | Trực quan hóa dữ liệu |
| `DATA_FEATURE_ENGINEERING` | Feature Engineering | Kỹ thuật đặc trưng |
| `DATA_DATASET_DESIGN` | Dataset Design | Thiết kế tập dữ liệu |

### Machine-learning foundations / Nền tảng học máy

| Code | English label | Vietnamese label |
|---|---|---|
| `ML_PROBLEM_FORMULATION` | ML Problem Formulation | Xây dựng bài toán học máy |
| `ML_REGRESSION` | Regression | Hồi quy |
| `ML_CLASSIFICATION` | Classification | Phân loại |
| `ML_CLUSTERING` | Clustering | Phân cụm |
| `ML_DIMENSIONALITY_REDUCTION` | Dimensionality Reduction | Giảm chiều dữ liệu |
| `ML_ENSEMBLES` | Ensemble Methods | Phương pháp tổ hợp |

### Deep learning / Học sâu

| Code | English label | Vietnamese label |
|---|---|---|
| `DL_NEURAL_NETWORKS` | Neural Network Foundations | Nền tảng mạng nơ-ron |
| `DL_TRAINING_OPTIMIZATION` | Training and Optimization | Huấn luyện và tối ưu hóa |
| `DL_CONVOLUTIONAL_NETWORKS` | Convolutional Networks | Mạng tích chập |
| `DL_SEQUENCE_MODELS` | Sequence Models | Mô hình chuỗi |
| `DL_TRANSFORMERS` | Transformers | Mô hình Transformer |
| `DL_REPRESENTATION_LEARNING` | Representation Learning | Học biểu diễn |

### AI domains / Lĩnh vực AI

| Code | English label | Vietnamese label |
|---|---|---|
| `DOMAIN_COMPUTER_VISION` | Computer Vision | Thị giác máy tính |
| `DOMAIN_NLP` | Natural Language Processing | Xử lý ngôn ngữ tự nhiên |
| `DOMAIN_SPEECH_AUDIO` | Speech and Audio | Tiếng nói và âm thanh |
| `DOMAIN_TIME_SERIES` | Time Series | Chuỗi thời gian |
| `DOMAIN_RECOMMENDATION` | Recommendation Systems | Hệ gợi ý |
| `DOMAIN_MULTIMODAL` | Multimodal AI | AI đa phương thức |

### Evaluation / Đánh giá

| Code | English label | Vietnamese label |
|---|---|---|
| `EVAL_METRICS` | Metrics | Độ đo đánh giá |
| `EVAL_VALIDATION` | Validation Strategy | Chiến lược kiểm định |
| `EVAL_ERROR_ANALYSIS` | Error Analysis | Phân tích lỗi |
| `EVAL_DATA_LEAKAGE` | Data Leakage | Rò rỉ dữ liệu |
| `EVAL_ROBUSTNESS` | Robustness | Độ vững |
| `EVAL_FAIRNESS` | Fairness Evaluation | Đánh giá tính công bằng |
| `EVAL_STATISTICAL_SIGNIFICANCE` | Statistical Significance | Ý nghĩa thống kê |

### Experimentation / Thực nghiệm

| Code | English label | Vietnamese label |
|---|---|---|
| `EXP_BASELINES` | Baseline Construction | Xây dựng đường cơ sở |
| `EXP_DESIGN` | Experiment Design | Thiết kế thí nghiệm |
| `EXP_HYPERPARAMETER_TUNING` | Hyperparameter Tuning | Điều chỉnh siêu tham số |
| `EXP_ABLATION` | Ablation Studies | Nghiên cứu loại bỏ thành phần |
| `EXP_REPRODUCIBILITY` | Reproducibility | Khả năng tái lập |
| `EXP_RESOURCE_OPTIMIZATION` | Resource Optimization | Tối ưu tài nguyên |

### Responsible AI / AI có trách nhiệm

| Code | English label | Vietnamese label |
|---|---|---|
| `RAI_PRIVACY` | Privacy | Quyền riêng tư |
| `RAI_FAIRNESS_BIAS` | Fairness and Bias | Công bằng và thiên lệch |
| `RAI_SAFETY` | Safety | An toàn |
| `RAI_EXPLAINABILITY` | Explainability | Khả năng giải thích |
| `RAI_LICENSING` | Data and Model Licensing | Cấp phép dữ liệu và mô hình |
| `RAI_ENVIRONMENTAL_IMPACT` | Environmental Impact | Tác động môi trường |

### Research and communication / Nghiên cứu và truyền đạt

| Code | English label | Vietnamese label |
|---|---|---|
| `RESEARCH_LITERATURE_READING` | Literature Reading | Đọc tài liệu khoa học |
| `RESEARCH_TECHNICAL_WRITING` | Technical Writing | Viết kỹ thuật |
| `RESEARCH_RESULT_INTERPRETATION` | Result Interpretation | Diễn giải kết quả |
| `RESEARCH_PRESENTATION` | Visualization and Presentation | Trực quan hóa và trình bày |
| `RESEARCH_ARGUMENTATION` | Scientific Argumentation | Lập luận khoa học |

### Competition skills / Kỹ năng thi đấu

| Code | English label | Vietnamese label |
|---|---|---|
| `COMP_PROBLEM_ANALYSIS` | Problem Analysis | Phân tích bài toán |
| `COMP_TIME_MANAGEMENT` | Time Management | Quản lý thời gian |
| `COMP_SUBMISSION_STRATEGY` | Submission Strategy | Chiến lược nộp bài |
| `COMP_COMPUTE_MANAGEMENT` | Compute Management | Quản lý tài nguyên tính toán |
| `COMP_TEAM_COLLABORATION` | Team Collaboration | Hợp tác nhóm |
| `COMP_SOLUTION_DEFENSE` | Solution Defense | Bảo vệ lời giải |

## 4. Difficulty / Độ khó

Cardinality: single-select.

| Code | English label | Vietnamese label | Definition |
|---|---|---|---|
| `INTRODUCTORY` | Introductory | Nhập môn | Guided introduction with little transfer required |
| `EASY` | Easy | Dễ | Direct application of one competency |
| `MEDIUM` | Medium | Trung bình | Combines concepts or requires several decisions |
| `HARD` | Hard | Khó | Unfamiliar setting requiring substantial reasoning or experimentation |
| `CHALLENGE` | Challenge | Thử thách | Open-ended task with no obvious solution path |

### Task status / Trạng thái bài tập

Task status records learner interaction with a particular task. It is not a mastery judgment.

| Code | English label | Vietnamese label | Meaning |
|---|---|---|---|
| `NOT_STARTED` | Not started | Chưa bắt đầu | The learner has not made a recorded attempt |
| `ATTEMPTED` | Attempted | Đã thử | The learner has started or submitted without completing the task |
| `COMPLETED` | Completed | Đã hoàn thành | The learner has satisfied the task's completion rule |

`MASTERED` is not a valid task status for the initial releases. Use the learning-evidence scale in Section 8 when reporting progress toward a competency or topic.

## 5. Topic taxonomy / Phân loại chủ đề

Cardinality: multi-select. Topics are hierarchical records, not a hard-coded application enum or a flat list inferred from Markdown headings.

Every topic record must contain:

```json
{
  "vocabulary_type": "TOPIC",
  "code": "ML_LOGISTIC_REGRESSION",
  "parent_code": "ML_CLASSIFICATION_METHODS",
  "labels": {
    "en": "Logistic Regression",
    "vi": "Hồi quy logistic"
  },
  "status": "ACTIVE",
  "aliases": []
}
```

`parent_code` is `null` only for the top-level families below. Every other topic must store an explicit parent code. Section placement is for readability and must never be used as the database relationship. `status` is `ACTIVE` for all records in this draft unless explicitly marked otherwise. Aliases are optional, searchable labels and never replace the canonical code.

### Top-level topic families / Nhóm chủ đề cấp cao

| Code | English label | Vietnamese label | Parent code | Status |
|---|---|---|---|---|
| `TOPIC_MATHEMATICS` | Mathematics | Toán học | `null` | `ACTIVE` |
| `TOPIC_PYTHON_COMPUTING` | Python and Computing | Python và tính toán | `null` | `ACTIVE` |
| `TOPIC_DATA` | Data | Dữ liệu | `null` | `ACTIVE` |
| `TOPIC_MACHINE_LEARNING` | Machine Learning | Học máy | `null` | `ACTIVE` |
| `TOPIC_DEEP_LEARNING` | Deep Learning | Học sâu | `null` | `ACTIVE` |
| `TOPIC_EVALUATION` | Evaluation | Đánh giá | `null` | `ACTIVE` |
| `TOPIC_AI_DOMAINS` | AI Domains | Lĩnh vực AI | `null` | `ACTIVE` |
| `TOPIC_RESPONSIBLE_RESEARCH` | Responsible AI and Research | AI có trách nhiệm và nghiên cứu | `null` | `ACTIVE` |

### Intermediate topic categories / Nhóm chủ đề trung gian

Intermediate categories organize the searchable topic tree. They are navigational records and should not normally be assigned directly to a task when a more specific descendant applies.

| Code | English label | Vietnamese label | Parent code | Status |
|---|---|---|---|---|
| `MATH_LINEAR_ALGEBRA_TOPICS` | Linear Algebra | Đại số tuyến tính | `TOPIC_MATHEMATICS` | `ACTIVE` |
| `MATH_CALCULUS_TOPICS` | Calculus | Giải tích | `TOPIC_MATHEMATICS` | `ACTIVE` |
| `MATH_PROBABILITY_STATISTICS_TOPICS` | Probability and Statistics | Xác suất và thống kê | `TOPIC_MATHEMATICS` | `ACTIVE` |
| `MATH_OPTIMIZATION_TOPICS` | Optimization | Tối ưu hóa | `TOPIC_MATHEMATICS` | `ACTIVE` |
| `PYTHON_LANGUAGE` | Python Language | Ngôn ngữ Python | `TOPIC_PYTHON_COMPUTING` | `ACTIVE` |
| `PYTHON_LIBRARIES` | Python Libraries | Thư viện Python | `TOPIC_PYTHON_COMPUTING` | `ACTIVE` |
| `COMPUTING_ALGORITHMS_STRUCTURES` | Algorithms and Data Structures | Thuật toán và cấu trúc dữ liệu | `TOPIC_PYTHON_COMPUTING` | `ACTIVE` |
| `COMPUTING_PERFORMANCE` | Computing Performance | Hiệu năng tính toán | `TOPIC_PYTHON_COMPUTING` | `ACTIVE` |
| `COMPUTING_ENGINEERING` | Computing Practice | Thực hành kỹ thuật tính toán | `TOPIC_PYTHON_COMPUTING` | `ACTIVE` |
| `DATA_INGESTION_REPRESENTATION` | Data Ingestion and Representation | Nạp và biểu diễn dữ liệu | `TOPIC_DATA` | `ACTIVE` |
| `DATA_CLEANING_PREPROCESSING` | Data Cleaning and Preprocessing | Làm sạch và tiền xử lý dữ liệu | `TOPIC_DATA` | `ACTIVE` |
| `DATA_FEATURES_AUGMENTATION` | Features and Augmentation | Đặc trưng và tăng cường dữ liệu | `TOPIC_DATA` | `ACTIVE` |
| `DATA_DATASET_DESIGN_QUALITY` | Dataset Design and Quality | Thiết kế và chất lượng tập dữ liệu | `TOPIC_DATA` | `ACTIVE` |
| `ML_REGRESSION_METHODS` | Regression Methods | Các phương pháp hồi quy | `TOPIC_MACHINE_LEARNING` | `ACTIVE` |
| `ML_CLASSIFICATION_METHODS` | Classification Methods | Các phương pháp phân loại | `TOPIC_MACHINE_LEARNING` | `ACTIVE` |
| `ML_TREE_ENSEMBLE_METHODS` | Tree and Ensemble Methods | Phương pháp cây và tổ hợp | `TOPIC_MACHINE_LEARNING` | `ACTIVE` |
| `ML_UNSUPERVISED_METHODS` | Unsupervised Methods | Phương pháp học không giám sát | `TOPIC_MACHINE_LEARNING` | `ACTIVE` |
| `ML_MODEL_OPTIMIZATION` | Model Optimization | Tối ưu hóa mô hình | `TOPIC_MACHINE_LEARNING` | `ACTIVE` |
| `DL_NETWORK_FOUNDATIONS` | Neural-network Foundations | Nền tảng mạng nơ-ron | `TOPIC_DEEP_LEARNING` | `ACTIVE` |
| `DL_TRAINING_METHODS` | Training Methods | Phương pháp huấn luyện | `TOPIC_DEEP_LEARNING` | `ACTIVE` |
| `DL_ARCHITECTURES` | Neural Architectures | Kiến trúc mạng nơ-ron | `TOPIC_DEEP_LEARNING` | `ACTIVE` |
| `DL_REPRESENTATION_ADAPTATION` | Representation and Adaptation | Biểu diễn và thích nghi | `TOPIC_DEEP_LEARNING` | `ACTIVE` |
| `EVAL_CLASSIFICATION_METRICS` | Classification Metrics | Độ đo phân loại | `TOPIC_EVALUATION` | `ACTIVE` |
| `EVAL_REGRESSION_METRICS` | Regression Metrics | Độ đo hồi quy | `TOPIC_EVALUATION` | `ACTIVE` |
| `EVAL_DOMAIN_METRICS` | Domain-specific Metrics | Độ đo chuyên biệt theo lĩnh vực | `TOPIC_EVALUATION` | `ACTIVE` |
| `EVAL_VALIDATION_STRATEGIES` | Validation Strategies | Chiến lược kiểm định | `TOPIC_EVALUATION` | `ACTIVE` |
| `EVAL_ANALYSIS_DECISIONS` | Evaluation Analysis and Decisions | Phân tích và quyết định đánh giá | `TOPIC_EVALUATION` | `ACTIVE` |
| `DOMAIN_COMPUTER_VISION_TOPICS` | Computer Vision | Thị giác máy tính | `TOPIC_AI_DOMAINS` | `ACTIVE` |
| `DOMAIN_NLP_TOPICS` | Natural Language Processing | Xử lý ngôn ngữ tự nhiên | `TOPIC_AI_DOMAINS` | `ACTIVE` |
| `DOMAIN_AUDIO_TOPICS` | Speech and Audio | Tiếng nói và âm thanh | `TOPIC_AI_DOMAINS` | `ACTIVE` |
| `DOMAIN_OTHER_AI_TOPICS` | Other AI Domains | Các lĩnh vực AI khác | `TOPIC_AI_DOMAINS` | `ACTIVE` |
| `RAI_GOVERNANCE_SAFETY_TOPICS` | Responsible AI, Governance, and Safety | AI có trách nhiệm, quản trị và an toàn | `TOPIC_RESPONSIBLE_RESEARCH` | `ACTIVE` |
| `RESEARCH_PRACTICE_TOPICS` | Research Practice | Thực hành nghiên cứu | `TOPIC_RESPONSIBLE_RESEARCH` | `ACTIVE` |

The leaf records below serialize the parent relationship on each line as `Parent: <code>`. This repeated field is normative; the headings are only visual grouping.

### Mathematics / Toán học

- `MATH_VECTORS_MATRICES` — Vectors and Matrices — Vectơ và ma trận — Parent: `MATH_LINEAR_ALGEBRA_TOPICS`
- `MATH_MATRIX_MULTIPLICATION` — Matrix Multiplication — Phép nhân ma trận — Parent: `MATH_LINEAR_ALGEBRA_TOPICS`
- `MATH_EIGENVALUES_EIGENVECTORS` — Eigenvalues and Eigenvectors — Trị riêng và vectơ riêng — Parent: `MATH_LINEAR_ALGEBRA_TOPICS`
- `MATH_DERIVATIVES` — Derivatives — Đạo hàm — Parent: `MATH_CALCULUS_TOPICS`
- `MATH_PARTIAL_DERIVATIVES` — Partial Derivatives — Đạo hàm riêng — Parent: `MATH_CALCULUS_TOPICS`
- `MATH_GRADIENTS` — Gradients — Gradient — Parent: `MATH_CALCULUS_TOPICS`
- `MATH_CHAIN_RULE` — Chain Rule — Quy tắc dây chuyền — Parent: `MATH_CALCULUS_TOPICS`
- `MATH_PROBABILITY_DISTRIBUTIONS` — Probability Distributions — Phân phối xác suất — Parent: `MATH_PROBABILITY_STATISTICS_TOPICS`
- `MATH_CONDITIONAL_PROBABILITY` — Conditional Probability — Xác suất có điều kiện — Parent: `MATH_PROBABILITY_STATISTICS_TOPICS`
- `MATH_BAYES_THEOREM` — Bayes' Theorem — Định lý Bayes — Parent: `MATH_PROBABILITY_STATISTICS_TOPICS`
- `MATH_EXPECTATION_VARIANCE` — Expectation and Variance — Kỳ vọng và phương sai — Parent: `MATH_PROBABILITY_STATISTICS_TOPICS`
- `MATH_HYPOTHESIS_TESTING` — Hypothesis Testing — Kiểm định giả thuyết — Parent: `MATH_PROBABILITY_STATISTICS_TOPICS`
- `MATH_CONFIDENCE_INTERVALS` — Confidence Intervals — Khoảng tin cậy — Parent: `MATH_PROBABILITY_STATISTICS_TOPICS`
- `MATH_INFORMATION_THEORY` — Information Theory — Lý thuyết thông tin — Parent: `MATH_PROBABILITY_STATISTICS_TOPICS`
- `MATH_CONVEXITY` — Convexity — Tính lồi — Parent: `MATH_OPTIMIZATION_TOPICS`

### Python and computing / Python và tính toán

- `PYTHON_SYNTAX` — Python Syntax — Cú pháp Python — Parent: `PYTHON_LANGUAGE`
- `PYTHON_FUNCTIONS` — Functions — Hàm — Parent: `PYTHON_LANGUAGE`
- `PYTHON_COLLECTIONS` — Collections — Kiểu dữ liệu tập hợp — Parent: `PYTHON_LANGUAGE`
- `PYTHON_OOP` — Object-oriented Programming — Lập trình hướng đối tượng — Parent: `PYTHON_LANGUAGE`
- `LIB_NUMPY` — NumPy — NumPy — Parent: `PYTHON_LIBRARIES`
- `LIB_PANDAS` — pandas — pandas — Parent: `PYTHON_LIBRARIES`
- `LIB_MATPLOTLIB` — Matplotlib — Matplotlib — Parent: `PYTHON_LIBRARIES`
- `LIB_SCIKIT_LEARN` — scikit-learn — scikit-learn — Parent: `PYTHON_LIBRARIES`
- `LIB_PYTORCH` — PyTorch — PyTorch — Parent: `PYTHON_LIBRARIES`
- `COMPUTING_ALGORITHMS` — Algorithms — Thuật toán — Parent: `COMPUTING_ALGORITHMS_STRUCTURES`
- `COMPUTING_DATA_STRUCTURES` — Data Structures — Cấu trúc dữ liệu — Parent: `COMPUTING_ALGORITHMS_STRUCTURES`
- `COMPUTING_VECTORIZATION` — Vectorization — Vectơ hóa — Parent: `COMPUTING_PERFORMANCE`
- `COMPUTING_MEMORY_OPTIMIZATION` — Memory Optimization — Tối ưu bộ nhớ — Parent: `COMPUTING_PERFORMANCE`
- `COMPUTING_RUNTIME_OPTIMIZATION` — Runtime Optimization — Tối ưu thời gian chạy — Parent: `COMPUTING_PERFORMANCE`
- `COMPUTING_DEBUGGING` — Debugging — Gỡ lỗi — Parent: `COMPUTING_ENGINEERING`
- `COMPUTING_TESTING` — Testing — Kiểm thử — Parent: `COMPUTING_ENGINEERING`
- `COMPUTING_GIT` — Git — Git — Parent: `COMPUTING_ENGINEERING`
- `COMPUTING_REPRODUCIBLE_ENV` — Reproducible Environments — Môi trường có thể tái lập — Parent: `COMPUTING_ENGINEERING`

Only libraries supported by the platform may be assigned to tasks.

### Data / Dữ liệu

- `DATA_LOADING` — Data Loading — Nạp dữ liệu — Parent: `DATA_INGESTION_REPRESENTATION`
- `DATA_TYPES` — Data Types — Kiểu dữ liệu — Parent: `DATA_INGESTION_REPRESENTATION`
- `DATA_MISSING_VALUES` — Missing Values — Giá trị thiếu — Parent: `DATA_CLEANING_PREPROCESSING`
- `DATA_OUTLIERS` — Outliers — Giá trị ngoại lai — Parent: `DATA_CLEANING_PREPROCESSING`
- `DATA_DUPLICATES` — Duplicate Records — Bản ghi trùng lặp — Parent: `DATA_CLEANING_PREPROCESSING`
- `DATA_NORMALIZATION` — Normalization — Chuẩn hóa về miền giá trị — Parent: `DATA_CLEANING_PREPROCESSING`
- `DATA_STANDARDIZATION` — Standardization — Chuẩn hóa theo phân phối — Parent: `DATA_CLEANING_PREPROCESSING`
- `DATA_CATEGORICAL_ENCODING` — Categorical Encoding — Mã hóa biến phân loại — Parent: `DATA_CLEANING_PREPROCESSING`
- `DATA_TOKENIZATION` — Tokenization — Tách token — Parent: `DATA_CLEANING_PREPROCESSING`
- `DATA_AUGMENTATION` — Data Augmentation — Tăng cường dữ liệu — Parent: `DATA_FEATURES_AUGMENTATION`
- `DATA_FEATURE_SELECTION` — Feature Selection — Lựa chọn đặc trưng — Parent: `DATA_FEATURES_AUGMENTATION`
- `DATA_FEATURE_EXTRACTION` — Feature Extraction — Trích xuất đặc trưng — Parent: `DATA_FEATURES_AUGMENTATION`
- `DATA_SPLITTING` — Train-validation-test Split — Chia tập huấn luyện–kiểm định–kiểm thử — Parent: `DATA_DATASET_DESIGN_QUALITY`
- `DATA_SAMPLING` — Sampling — Lấy mẫu — Parent: `DATA_DATASET_DESIGN_QUALITY`
- `DATA_CLASS_IMBALANCE` — Class Imbalance — Mất cân bằng lớp — Parent: `DATA_DATASET_DESIGN_QUALITY`
- `DATA_DATASET_SHIFT` — Dataset Shift — Dịch chuyển phân phối dữ liệu — Parent: `DATA_DATASET_DESIGN_QUALITY`
- `DATA_LEAKAGE` — Data Leakage — Rò rỉ dữ liệu — Parent: `DATA_DATASET_DESIGN_QUALITY`
- `DATA_LABEL_QUALITY` — Label Quality — Chất lượng nhãn — Parent: `DATA_DATASET_DESIGN_QUALITY`
- `DATA_ANNOTATION` — Annotation — Gán nhãn dữ liệu — Parent: `DATA_DATASET_DESIGN_QUALITY`

### Machine learning / Học máy

- `ML_LINEAR_REGRESSION` — Linear Regression — Hồi quy tuyến tính — Parent: `ML_REGRESSION_METHODS`
- `ML_LOGISTIC_REGRESSION` — Logistic Regression — Hồi quy logistic — Parent: `ML_CLASSIFICATION_METHODS`
- `ML_KNN` — k-nearest Neighbours — k láng giềng gần nhất — Parent: `ML_CLASSIFICATION_METHODS`
- `ML_NAIVE_BAYES` — Naive Bayes — Bayes ngây thơ — Parent: `ML_CLASSIFICATION_METHODS`
- `ML_DECISION_TREES` — Decision Trees — Cây quyết định — Parent: `ML_TREE_ENSEMBLE_METHODS`
- `ML_RANDOM_FORESTS` — Random Forests — Rừng ngẫu nhiên — Parent: `ML_TREE_ENSEMBLE_METHODS`
- `ML_GRADIENT_BOOSTING` — Gradient Boosting — Tăng cường gradient — Parent: `ML_TREE_ENSEMBLE_METHODS`
- `ML_SVM` — Support Vector Machines — Máy vectơ hỗ trợ — Parent: `ML_CLASSIFICATION_METHODS`
- `ML_KMEANS` — k-means — Phân cụm k-means — Parent: `ML_UNSUPERVISED_METHODS`
- `ML_PCA` — Principal Component Analysis — Phân tích thành phần chính — Parent: `ML_UNSUPERVISED_METHODS`
- `ML_ENSEMBLE_LEARNING` — Ensemble Learning — Học tổ hợp — Parent: `ML_TREE_ENSEMBLE_METHODS`
- `ML_BAGGING` — Bagging — Bagging — Parent: `ML_TREE_ENSEMBLE_METHODS`
- `ML_BOOSTING` — Boosting — Boosting — Parent: `ML_TREE_ENSEMBLE_METHODS`
- `ML_CALIBRATION` — Calibration — Hiệu chỉnh xác suất — Parent: `ML_MODEL_OPTIMIZATION`
- `ML_REGULARIZATION` — Regularization — Chính quy hóa — Parent: `ML_MODEL_OPTIMIZATION`
- `ML_HYPERPARAMETER_OPTIMIZATION` — Hyperparameter Optimization — Tối ưu siêu tham số — Parent: `ML_MODEL_OPTIMIZATION`

### Deep learning / Học sâu

- `DL_PERCEPTRONS` — Perceptrons — Perceptron — Parent: `DL_NETWORK_FOUNDATIONS`
- `DL_MLP` — Multilayer Neural Networks — Mạng nơ-ron nhiều lớp — Parent: `DL_NETWORK_FOUNDATIONS`
- `DL_ACTIVATIONS` — Activation Functions — Hàm kích hoạt — Parent: `DL_NETWORK_FOUNDATIONS`
- `DL_LOSS_FUNCTIONS` — Loss Functions — Hàm mất mát — Parent: `DL_NETWORK_FOUNDATIONS`
- `DL_BACKPROPAGATION` — Backpropagation — Lan truyền ngược — Parent: `DL_NETWORK_FOUNDATIONS`
- `DL_GRADIENT_DESCENT` — Gradient Descent — Hạ gradient — Parent: `DL_TRAINING_METHODS`
- `DL_OPTIMIZERS` — Optimizers — Thuật toán tối ưu — Parent: `DL_TRAINING_METHODS`
- `DL_LR_SCHEDULING` — Learning-rate Scheduling — Lập lịch tốc độ học — Parent: `DL_TRAINING_METHODS`
- `DL_BATCH_NORMALIZATION` — Batch Normalization — Chuẩn hóa theo lô — Parent: `DL_TRAINING_METHODS`
- `DL_DROPOUT` — Dropout — Dropout — Parent: `DL_TRAINING_METHODS`
- `DL_WEIGHT_INITIALIZATION` — Weight Initialization — Khởi tạo trọng số — Parent: `DL_TRAINING_METHODS`
- `DL_CNN` — Convolutional Neural Networks — Mạng nơ-ron tích chập — Parent: `DL_ARCHITECTURES`
- `DL_RNN` — Recurrent Neural Networks — Mạng nơ-ron hồi quy — Parent: `DL_ARCHITECTURES`
- `DL_LSTM` — Long Short-term Memory Networks — Mạng bộ nhớ dài–ngắn hạn — Parent: `DL_ARCHITECTURES`
- `DL_ATTENTION` — Attention — Cơ chế chú ý — Parent: `DL_ARCHITECTURES`
- `DL_TRANSFORMERS` — Transformers — Mô hình Transformer — Parent: `DL_ARCHITECTURES`
- `DL_EMBEDDINGS` — Embeddings — Biểu diễn nhúng — Parent: `DL_REPRESENTATION_ADAPTATION`
- `DL_TRANSFER_LEARNING` — Transfer Learning — Học chuyển giao — Parent: `DL_REPRESENTATION_ADAPTATION`
- `DL_FINE_TUNING` — Fine-tuning — Tinh chỉnh — Parent: `DL_REPRESENTATION_ADAPTATION`
- `DL_SELF_SUPERVISED` — Self-supervised Learning — Học tự giám sát — Parent: `DL_REPRESENTATION_ADAPTATION`
- `DL_CONTRASTIVE_LEARNING` — Contrastive Learning — Học tương phản — Parent: `DL_REPRESENTATION_ADAPTATION`

### Evaluation / Đánh giá

- `METRIC_ACCURACY` — Accuracy — Độ chính xác — Parent: `EVAL_CLASSIFICATION_METRICS`
- `METRIC_PRECISION` — Precision — Độ chuẩn xác — Parent: `EVAL_CLASSIFICATION_METRICS`
- `METRIC_RECALL` — Recall — Độ phủ — Parent: `EVAL_CLASSIFICATION_METRICS`
- `METRIC_F1` — F1-score — Điểm F1 — Parent: `EVAL_CLASSIFICATION_METRICS`
- `METRIC_SPECIFICITY` — Specificity — Độ đặc hiệu — Parent: `EVAL_CLASSIFICATION_METRICS`
- `METRIC_ROC_AUC` — ROC-AUC — Diện tích dưới đường cong ROC — Parent: `EVAL_CLASSIFICATION_METRICS`
- `METRIC_PR_AUC` — PR-AUC — Diện tích dưới đường cong precision–recall — Parent: `EVAL_CLASSIFICATION_METRICS`
- `METRIC_LOG_LOSS` — Log Loss — Mất mát logarit — Parent: `EVAL_CLASSIFICATION_METRICS`
- `METRIC_MAE` — Mean Absolute Error — Sai số tuyệt đối trung bình — Parent: `EVAL_REGRESSION_METRICS`
- `METRIC_MSE` — Mean Squared Error — Sai số bình phương trung bình — Parent: `EVAL_REGRESSION_METRICS`
- `METRIC_RMSE` — Root Mean Squared Error — Căn sai số bình phương trung bình — Parent: `EVAL_REGRESSION_METRICS`
- `METRIC_R2` — R-squared — Hệ số xác định R bình phương — Parent: `EVAL_REGRESSION_METRICS`
- `METRIC_IOU` — Intersection over Union — Tỷ lệ giao trên hợp — Parent: `EVAL_DOMAIN_METRICS`
- `METRIC_MAP` — Mean Average Precision — Độ chuẩn xác trung bình bình quân — Parent: `EVAL_DOMAIN_METRICS`
- `METRIC_BLEU` — BLEU — Điểm BLEU — Parent: `EVAL_DOMAIN_METRICS`
- `METRIC_ROUGE` — ROUGE — Điểm ROUGE — Parent: `EVAL_DOMAIN_METRICS`
- `METRIC_PERPLEXITY` — Perplexity — Độ hỗn loạn — Parent: `EVAL_DOMAIN_METRICS`
- `EVAL_CROSS_VALIDATION` — Cross-validation — Kiểm định chéo — Parent: `EVAL_VALIDATION_STRATEGIES`
- `EVAL_STRATIFIED_VALIDATION` — Stratified Validation — Kiểm định phân tầng — Parent: `EVAL_VALIDATION_STRATEGIES`
- `EVAL_GROUPED_VALIDATION` — Grouped Validation — Kiểm định theo nhóm — Parent: `EVAL_VALIDATION_STRATEGIES`
- `EVAL_TIME_SERIES_VALIDATION` — Time-series Validation — Kiểm định chuỗi thời gian — Parent: `EVAL_VALIDATION_STRATEGIES`
- `EVAL_LEADERBOARD_SPLIT` — Public-private Leaderboard Split — Chia bảng xếp hạng công khai–riêng tư — Parent: `EVAL_VALIDATION_STRATEGIES`
- `EVAL_THRESHOLD_SELECTION` — Threshold Selection — Lựa chọn ngưỡng — Parent: `EVAL_ANALYSIS_DECISIONS`
- `EVAL_CONFUSION_MATRIX` — Confusion Matrix — Ma trận nhầm lẫn — Parent: `EVAL_ANALYSIS_DECISIONS`
- `EVAL_ERROR_ANALYSIS` — Error Analysis — Phân tích lỗi — Parent: `EVAL_ANALYSIS_DECISIONS`
- `EVAL_STATISTICAL_SIGNIFICANCE` — Statistical Significance — Ý nghĩa thống kê — Parent: `EVAL_ANALYSIS_DECISIONS`

### AI domains / Lĩnh vực AI

- `CV_IMAGE_CLASSIFICATION` — Image Classification — Phân loại ảnh — Parent: `DOMAIN_COMPUTER_VISION_TOPICS`
- `CV_OBJECT_DETECTION` — Object Detection — Phát hiện đối tượng — Parent: `DOMAIN_COMPUTER_VISION_TOPICS`
- `CV_IMAGE_SEGMENTATION` — Image Segmentation — Phân đoạn ảnh — Parent: `DOMAIN_COMPUTER_VISION_TOPICS`
- `CV_IMAGE_GENERATION` — Image Generation — Sinh ảnh — Parent: `DOMAIN_COMPUTER_VISION_TOPICS`
- `NLP_TEXT_CLASSIFICATION` — Text Classification — Phân loại văn bản — Parent: `DOMAIN_NLP_TOPICS`
- `NLP_NER` — Named Entity Recognition — Nhận dạng thực thể có tên — Parent: `DOMAIN_NLP_TOPICS`
- `NLP_INFORMATION_RETRIEVAL` — Information Retrieval — Truy hồi thông tin — Parent: `DOMAIN_NLP_TOPICS`
- `NLP_QUESTION_ANSWERING` — Question Answering — Hỏi đáp — Parent: `DOMAIN_NLP_TOPICS`
- `NLP_LANGUAGE_MODELING` — Language Modelling — Mô hình hóa ngôn ngữ — Parent: `DOMAIN_NLP_TOPICS`
- `NLP_MACHINE_TRANSLATION` — Machine Translation — Dịch máy — Parent: `DOMAIN_NLP_TOPICS`
- `AUDIO_SPEECH_RECOGNITION` — Speech Recognition — Nhận dạng tiếng nói — Parent: `DOMAIN_AUDIO_TOPICS`
- `AUDIO_CLASSIFICATION` — Audio Classification — Phân loại âm thanh — Parent: `DOMAIN_AUDIO_TOPICS`
- `TS_FORECASTING` — Forecasting — Dự báo — Parent: `DOMAIN_OTHER_AI_TOPICS`
- `REC_RECOMMENDATION` — Recommendation — Gợi ý — Parent: `DOMAIN_OTHER_AI_TOPICS`
- `GRAPH_LEARNING` — Graph Learning — Học trên đồ thị — Parent: `DOMAIN_OTHER_AI_TOPICS`
- `MULTIMODAL_LEARNING` — Multimodal Learning — Học đa phương thức — Parent: `DOMAIN_OTHER_AI_TOPICS`

### Responsible AI and research / AI có trách nhiệm và nghiên cứu

- `RAI_BIAS` — Bias — Thiên lệch — Parent: `RAI_GOVERNANCE_SAFETY_TOPICS`
- `RAI_FAIRNESS` — Fairness — Tính công bằng — Parent: `RAI_GOVERNANCE_SAFETY_TOPICS`
- `RAI_PRIVACY` — Privacy — Quyền riêng tư — Parent: `RAI_GOVERNANCE_SAFETY_TOPICS`
- `RAI_EXPLAINABILITY` — Explainability — Khả năng giải thích — Parent: `RAI_GOVERNANCE_SAFETY_TOPICS`
- `RAI_MODEL_SAFETY` — Model Safety — An toàn mô hình — Parent: `RAI_GOVERNANCE_SAFETY_TOPICS`
- `RAI_ADVERSARIAL_ROBUSTNESS` — Adversarial Robustness — Độ vững trước tấn công đối nghịch — Parent: `RAI_GOVERNANCE_SAFETY_TOPICS`
- `RAI_COPYRIGHT` — Copyright — Bản quyền — Parent: `RAI_GOVERNANCE_SAFETY_TOPICS`
- `RAI_DATA_LICENSING` — Data Licensing — Cấp phép dữ liệu — Parent: `RAI_GOVERNANCE_SAFETY_TOPICS`
- `RAI_MODEL_CARDS` — Model Cards — Thẻ mô hình — Parent: `RAI_GOVERNANCE_SAFETY_TOPICS`
- `RAI_DATASET_DOCUMENTATION` — Dataset Documentation — Tài liệu tập dữ liệu — Parent: `RAI_GOVERNANCE_SAFETY_TOPICS`
- `RESEARCH_BASELINES` — Baselines — Đường cơ sở — Parent: `RESEARCH_PRACTICE_TOPICS`
- `RESEARCH_ABLATIONS` — Ablations — Thí nghiệm loại bỏ thành phần — Parent: `RESEARCH_PRACTICE_TOPICS`
- `RESEARCH_REPRODUCIBILITY` — Reproducibility — Khả năng tái lập — Parent: `RESEARCH_PRACTICE_TOPICS`
- `RESEARCH_SCIENTIFIC_REPORTING` — Scientific Reporting — Báo cáo khoa học — Parent: `RESEARCH_PRACTICE_TOPICS`

## 6. Task type / Loại bài tập

Cardinality: single-select.

| Code | English label | Vietnamese label |
|---|---|---|
| `QUIZ_SINGLE` | Single-answer Quiz | Câu hỏi một đáp án |
| `QUIZ_MULTIPLE` | Multiple-answer Quiz | Câu hỏi nhiều đáp án |
| `NUMERIC_ANSWER` | Numeric Answer | Câu trả lời dạng số |
| `SHORT_ANSWER` | Short Written Answer | Câu trả lời ngắn |
| `CODE_FUNCTION` | Function Implementation | Cài đặt hàm |
| `CODE_PROGRAM` | Complete Program | Chương trình hoàn chỉnh |
| `CODE_DEBUGGING` | Debugging Task | Bài tập gỡ lỗi |
| `CODE_COMPLETION` | Code Completion | Hoàn thiện mã nguồn |
| `DATA_ANALYSIS` | Data Analysis | Phân tích dữ liệu |
| `MODEL_TRAINING` | Model-training Task | Bài tập huấn luyện mô hình |
| `PREDICTION_CHALLENGE` | Prediction Challenge | Thử thách dự đoán |
| `EXPERIMENT` | Controlled Experiment | Thí nghiệm có kiểm soát |
| `ERROR_ANALYSIS` | Model Error Analysis | Phân tích lỗi mô hình |
| `SYSTEM_DESIGN` | AI System Design | Thiết kế hệ thống AI |
| `REPRODUCTION` | Result Reproduction | Tái lập kết quả |
| `OPEN_PROJECT` | Open-ended Project | Dự án mở |
| `TECHNICAL_REPORT` | Technical Report | Báo cáo kỹ thuật |
| `ORAL_DEFENSE` | Presentation or Oral Defense | Thuyết trình hoặc bảo vệ vấn đáp |
| `TEAM_CHALLENGE` | Team Challenge | Thử thách đồng đội |

## 7. Data modality / Phương thức dữ liệu

Cardinality: multi-select. Use `NONE` alone or one or more actual modalities.

| Code | English label | Vietnamese label |
|---|---|---|
| `NONE` | No Dataset | Không sử dụng tập dữ liệu |
| `TABULAR` | Tabular Data | Dữ liệu dạng bảng |
| `TIME_SERIES` | Time-series Data | Dữ liệu chuỗi thời gian |
| `TEXT` | Text | Văn bản |
| `IMAGE` | Image | Hình ảnh |
| `VIDEO` | Video | Video |
| `AUDIO` | Audio or Speech | Âm thanh hoặc tiếng nói |
| `GRAPH` | Graph or Network | Đồ thị hoặc mạng lưới |
| `GEOSPATIAL` | Geospatial Data | Dữ liệu không gian địa lý |
| `SENSOR` | Sensor Data | Dữ liệu cảm biến |
| `CODE` | Source Code | Mã nguồn |
| `MULTIMODAL` | Multimodal Data | Dữ liệu đa phương thức |

Store data origin separately:

| Code | English label | Vietnamese label |
|---|---|---|
| `REAL_PUBLIC` | Real, Public Data | Dữ liệu thực, công khai |
| `REAL_RESTRICTED` | Real, Restricted Data | Dữ liệu thực, hạn chế truy cập |
| `SYNTHETIC` | Synthetic or Simulated Data | Dữ liệu tổng hợp hoặc mô phỏng |
| `MIXED` | Mixed-origin Data | Dữ liệu hỗn hợp nhiều nguồn gốc |

## 8. Prerequisites / Điều kiện tiên quyết

Prerequisites are typed references.

### Relationship type / Loại quan hệ

| Code | English meaning | Vietnamese label |
|---|---|---|
| `REQUIRED` | Required learning evidence must be met first | Bắt buộc |
| `RECOMMENDED` | Helpful but not mandatory | Khuyến nghị |
| `CO_REQUISITE` | May be learned concurrently | Học đồng thời |
| `UNLOCKED_BY` | Completion of the target unlocks this task | Được mở khóa bởi |

### Target type / Loại đối tượng

| Code | English meaning | Vietnamese label |
|---|---|---|
| `COMPETENCY` | Competency reference | Năng lực |
| `TOPIC` | Topic reference | Chủ đề |
| `TASK` | Task reference | Bài tập |
| `LEARNING_UNIT` | Course or learning-unit reference | Đơn vị học tập |

Example:

```json
{
  "relationship": "REQUIRED",
  "target_type": "COMPETENCY",
  "target_id": "ML_CLASSIFICATION",
  "minimum_evidence": "APPLIED"
}
```

### Learning evidence level / Mức độ bằng chứng học tập

The optional `minimum_evidence` prerequisite field uses the following ordered learning-evidence scale. These values describe accumulated evidence rather than a definitive mastery judgment:

| Code | English label | Vietnamese label | Meaning |
|---|---|---|---|
| `INTRODUCED` | Introduced | Đã làm quen | Recognizes the main concept with guidance |
| `PRACTICED` | Practiced | Đã luyện tập | Completes direct applications with limited support |
| `APPLIED` | Applied | Vận dụng được | Applies the competency independently in a familiar setting |
| `PROFICIENT` | Proficient | Thành thạo | Transfers the competency to unfamiliar or integrated tasks |

During the initial releases, report these values as learning evidence and keep them separate from task status. Do not add or infer a `MASTERED` task status.

## 9. Expected time / Thời gian dự kiến

Store `expected_minutes` as a positive integer. Derive the following display category:

| Code | English label | Vietnamese label | Duration |
|---|---|---|---|
| `MICRO` | Micro | Siêu ngắn | 1–10 minutes |
| `SHORT` | Short | Ngắn | 11–30 minutes |
| `STANDARD` | Standard | Tiêu chuẩn | 31–60 minutes |
| `EXTENDED` | Extended | Mở rộng | 61–180 minutes |
| `LONG` | Long | Dài | 181–480 minutes |
| `PROJECT` | Project | Dự án | More than 480 minutes |

## 10. Compute requirement / Yêu cầu tính toán

### Compute tier / Cấp tài nguyên tính toán

| Code | English label | Vietnamese label | Typical capacity |
|---|---|---|---|
| `NONE` | None | Không cần tính toán | No execution required |
| `BROWSER` | Browser | Trình duyệt | Runs locally in the browser |
| `CPU_LIGHT` | Light CPU | CPU nhẹ | 1–2 CPU cores and less than 2 GB RAM |
| `CPU_STANDARD` | Standard CPU | CPU tiêu chuẩn | 2–4 CPU cores and 2–8 GB RAM |
| `CPU_HIGH` | High CPU | CPU cao | More than 4 cores or more than 8 GB RAM |
| `GPU_LIGHT` | Light GPU | GPU nhẹ | GPU with less than 4 GB VRAM |
| `GPU_STANDARD` | Standard GPU | GPU tiêu chuẩn | GPU with 4–16 GB VRAM |
| `GPU_HIGH` | High GPU | GPU cao | GPU with more than 16 GB VRAM |
| `DISTRIBUTED` | Distributed | Phân tán | Multiple accelerators or machines |

### Runtime class / Nhóm thời gian chạy

| Code | English label | Vietnamese label | Limit |
|---|---|---|---|
| `INSTANT` | Instant | Tức thời | Under 10 seconds |
| `SHORT` | Short | Ngắn | 10 seconds to 2 minutes |
| `MEDIUM` | Medium | Trung bình | More than 2 and up to 15 minutes |
| `LONG` | Long | Dài | More than 15 minutes and up to 2 hours |
| `EXTENDED` | Extended | Mở rộng | More than 2 hours |

Store exact resource constraints alongside the categories:

```text
cpu_cores
ram_mb
gpu_count
gpu_vram_mb
storage_mb
runtime_seconds
network_access
```

`network_access` is a Boolean and should normally be `false` during assessed tasks.

## 11. Scoring method / Phương thức chấm điểm

Cardinality: one or more weighted scoring components.

| Code | English label | Vietnamese label |
|---|---|---|
| `EXACT_MATCH` | Exact Answer | Khớp đáp án chính xác |
| `UNIT_TESTS` | Public and Hidden Unit Tests | Kiểm thử đơn vị công khai và ẩn |
| `PARTIAL_TESTS` | Weighted Test Groups | Nhóm kiểm thử có trọng số |
| `OUTPUT_SCORE` | Generated-output Quality | Chất lượng đầu ra |
| `PREDICTION_METRIC` | Metric Calculated from Hidden Labels | Độ đo dự đoán trên nhãn ẩn |
| `THRESHOLD_PASS` | Pass after Reaching a Threshold | Đạt khi vượt ngưỡng |
| `RANK_BASED` | Leaderboard-rank Score | Điểm theo thứ hạng |
| `RUBRIC_AUTOMATED` | Automated Structured Rubric | Tiêu chí chấm tự động |
| `RUBRIC_HUMAN` | Human-assessed Rubric | Tiêu chí do người chấm |
| `PEER_REVIEW` | Peer Assessment | Đánh giá đồng cấp |
| `ORAL_EVALUATION` | Presentation or Defense | Đánh giá thuyết trình hoặc vấn đáp |

Do not store `HYBRID` as a scoring method. A hybrid assessment is represented by multiple weighted components.

Example:

```json
[
  {
    "method": "PREDICTION_METRIC",
    "metric": "F1_MACRO",
    "weight": 0.7
  },
  {
    "method": "RUBRIC_HUMAN",
    "rubric_id": "EXPERIMENT_JUSTIFICATION_V1",
    "weight": 0.3
  }
]
```

Weights must total `1.0`.

## 12. Learning objective / Mục tiêu học tập

Learning objectives are concise authored statements, not categorical values. Use this pattern:

> Observable verb + knowledge or skill + conditions or constraints

Preferred observable verbs / Các động từ quan sát được ưu tiên:

- Define — Định nghĩa
- Describe — Mô tả
- Explain — Giải thích
- Calculate — Tính toán
- Implement — Cài đặt
- Apply — Áp dụng
- Compare — So sánh
- Select — Lựa chọn
- Interpret — Diễn giải
- Diagnose — Chẩn đoán
- Evaluate — Đánh giá
- Design — Thiết kế
- Optimize — Tối ưu hóa
- Justify — Lập luận và biện minh
- Reproduce — Tái lập
- Defend — Bảo vệ

Avoid vague verbs such as *know*, *learn*, *understand*, and *be familiar with*.

Examples:

- Calculate precision, recall, and F1-score from a confusion matrix. / Tính precision, recall và điểm F1 từ ma trận nhầm lẫn.
- Select and justify a metric for an imbalanced classification task. / Lựa chọn và lập luận cho một độ đo phù hợp với bài toán phân loại mất cân bằng.
- Design a validation strategy that prevents group leakage. / Thiết kế chiến lược kiểm định ngăn rò rỉ dữ liệu giữa các nhóm.
- Diagnose overfitting using training and validation curves. / Chẩn đoán quá khớp bằng đường cong huấn luyện và kiểm định.

## 13. Canonical Release 1 task example / Ví dụ bài tập chuẩn cho phiên bản 1

```json
{
  "pathway_stage": "AI_1_FOUNDATIONS",
  "primary_competency": "EVAL_METRICS",
  "secondary_competencies": [
    "PROG_PYTHON"
  ],
  "difficulty": "EASY",
  "topics": [
    "EVAL_CONFUSION_MATRIX",
    "METRIC_PRECISION",
    "METRIC_RECALL",
    "METRIC_F1"
  ],
  "task_type": "CODE_FUNCTION",
  "data_modalities": [
    "NONE"
  ],
  "prerequisites": [
    {
      "relationship": "RECOMMENDED",
      "target_type": "COMPETENCY",
      "target_id": "PROG_PYTHON",
      "minimum_evidence": "PRACTICED"
    },
    {
      "relationship": "REQUIRED",
      "target_type": "TOPIC",
      "target_id": "EVAL_CONFUSION_MATRIX"
    }
  ],
  "expected_minutes": 25,
  "compute_tier": "BROWSER",
  "runtime_class": "INSTANT",
  "resource_limits": {
    "cpu_cores": 1,
    "ram_mb": 512,
    "gpu_count": 0,
    "gpu_vram_mb": 0,
    "storage_mb": 64,
    "runtime_seconds": 10,
    "network_access": false
  },
  "scoring_components": [
    {
      "method": "UNIT_TESTS",
      "weight": 1.0
    }
  ],
  "learning_objectives": [
    "Implement a Python function that calculates precision, recall, and F1-score from confusion-matrix counts."
  ]
}
```
