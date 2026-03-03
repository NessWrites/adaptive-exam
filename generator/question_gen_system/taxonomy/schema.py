Schema = [
    {
        "domain": "math",
        "units": [
            {
  "unit": "Linear Algebra",
  "topics": [
    {
      "topic": "Transformations",
      "concept": "linear_and_affine_transformations",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Linear Transformation", "Scaling Transformation", "Shear Transformation"],
        "context": [
          "Applying geometric transformations to 2D objects in computer graphics.",
          "Resizing and skewing architectural blueprints in CAD software.",
          "Coordinate frame changes in basic robotic arm motion."
        ],
        "constraint": ["Linearity (additivity and homogeneity)", "Area scaling factor", "Invertibility"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and state its fundamental algebraic properties."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] modifies vectors and preserves or alters geometric structure."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given a transformation matrix in [CONTEXT], compute the transformed output and verify whether it satisfies the specified [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Rank, Spaces and Span",
      "concept": "rank_column_row_space_span",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Column Space", "Row Space", "Matrix Rank"],
        "context": [
          "Determining independent features in a dataset for regression modeling.",
          "Analyzing connectivity patterns in a transportation network matrix.",
          "Checking solvability of a system of linear equations in engineering calculations."
        ],
        "constraint": ["Linear independence", "Full rank condition", "Dimensional consistency"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and explain its relationship to linear independence and span."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] determines the effective dimensionality of the system."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given a matrix from [CONTEXT], compute the [OBJECT_TYPE] and verify whether it satisfies the stated [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Orthogonality & Projections",
      "concept": "orthogonal_vectors_and_projection_matrices",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Orthogonal Projection Matrix", "Orthogonal Basis", "Projection Vector"],
        "context": [
          "Projecting measured sensor data onto a reference calibration axis.",
          "Separating noise from signal components in audio processing.",
          "Computing perpendicular distance from a point to a line in 2D geometry."
        ],
        "constraint": ["Orthogonality condition", "Idempotent property", "Minimum distance property"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and describe the mathematical principle of orthogonality it relies on."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] isolates components along specific directions."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Using data from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the required [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "SVD and Eigen Decomposition",
      "concept": "svd_and_eigendecomposition",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Eigenvalues", "Eigenvectors", "Singular Values"],
        "context": [
          "Analyzing vibration modes of a mechanical structure.",
          "Reducing dimensionality of image data using principal component analysis.",
          "Studying stability of a discrete-time linear dynamical system."
        ],
        "constraint": ["Spectral decomposition accuracy", "Orthogonality of eigenvectors", "Energy preservation"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and explain its role in matrix factorization."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] reveals structural or stability properties of the system."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given a matrix from [CONTEXT], compute the [OBJECT_TYPE] and verify whether the result satisfies the specified [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Least Squares",
      "concept": "least_squares_estimation",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Normal Equation", "Residual Vector", "Best Fit Line"],
        "context": [
          "Fitting a straight line to experimental physics data.",
          "Estimating demand trends from historical sales records.",
          "Calibrating a linear sensor model using observed measurements."
        ],
        "constraint": ["Minimization of squared error", "Orthogonality of residuals", "Uniqueness of solution"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and describe the optimization principle it is based on."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] ensures optimal approximation of observed data."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given sample data from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the stated [CONSTRAINT]."
        }
      ]
    }
  ]
},
            {
  "unit": "Calculus",
  "topics": [
    {
      "topic": "Limit, Series, and Basic Derivatives",
      "concept": "limits_series_basic_derivatives",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Limit of a function", "Taylor Series Approximation", "First Derivative"],
        "context": [
          "Estimating instantaneous velocity from position-time data of a moving vehicle.",
          "Approximating exponential growth in population models using polynomial expansion.",
          "Analyzing marginal revenue from a cost-revenue function in economics."
        ],
        "constraint": ["Continuity at a point", "Convergence of series", "Differentiability"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and state its fundamental mathematical properties."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] models instantaneous change or approximation."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given a function from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the required [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Minima & Maxima",
      "concept": "optimization_extrema",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Critical Point", "Second Derivative Test", "Optimal Value"],
        "context": [
          "Maximizing profit based on a production cost function.",
          "Minimizing material usage in packaging design.",
          "Finding peak height of a projectile in basic physics."
        ],
        "constraint": ["First-order optimality condition", "Concavity/Convexity", "Global optimality"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and explain its role in identifying extrema."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] determines whether a solution is a minimum or maximum."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "For a function in [CONTEXT], compute the [OBJECT_TYPE] and verify whether it satisfies the stated [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Multivariate",
      "concept": "multivariable_calculus",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Partial Derivative", "Gradient Vector", "Directional Derivative"],
        "context": [
          "Modeling temperature variation across a metal plate.",
          "Analyzing how sales depend on both price and advertising budget.",
          "Evaluating terrain elevation changes on a geographic map."
        ],
        "constraint": ["Mixed partial consistency", "Steepest ascent direction", "Local linear approximation"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] for a function of multiple variables."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] captures sensitivity to multiple inputs."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given a multivariable function from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the required [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Integral and Numerical Optimization",
      "concept": "integration_numerical_methods",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Definite Integral", "Trapezoidal Rule Approximation", "Gradient Descent Update"],
        "context": [
          "Calculating total distance traveled from a velocity-time graph.",
          "Estimating area under experimental data points.",
          "Minimizing a cost function in parameter tuning."
        ],
        "constraint": ["Area interpretation", "Approximation accuracy", "Convergence criterion"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and describe its computational purpose."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] is used to compute accumulation or optimization."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Using data from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the specified [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Matrix Calculus",
      "concept": "matrix_differentiation",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Jacobian Matrix", "Hessian Matrix", "Matrix Gradient"],
        "context": [
          "Computing gradients in multivariable regression models.",
          "Analyzing curvature of a multivariate cost function.",
          "Optimizing parameters in a linear transformation model."
        ],
        "constraint": ["Symmetry of Hessian", "Positive definiteness", "Dimensional consistency"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and explain its structure in matrix differentiation."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] supports multivariate optimization."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given a matrix-valued function from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the required [CONSTRAINT]."
        }
      ]
    }
  ]
},
{
  "unit": "Probability",
  "topics": [
    {
      "topic": "Basic Probability",
      "concept": "axioms_sample_space_events",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Sample Space", "Event", "Probability Measure"],
        "context": [
          "Determining the probability of drawing a red card from a standard deck of cards.",
          "Calculating the likelihood of a defective item in a batch of manufactured products.",
          "Estimating the probability of heads when tossing a fair coin."
        ],
        "constraint": ["Non-negativity", "Normalization (total probability equals 1)", "Additivity for disjoint events"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and state its role in a probabilistic model."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] is constructed and interpreted."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given the scenario in [CONTEXT], compute the relevant [OBJECT_TYPE] and verify that it satisfies the stated [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Bayes Theorem and Conditional Probability",
      "concept": "conditional_probability_bayes_rule",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Conditional Probability", "Posterior Probability", "Likelihood Function"],
        "context": [
          "Updating the probability of a disease given a positive medical test result.",
          "Revising the probability of rain given updated weather forecast information.",
          "Evaluating spam detection based on observed keywords in an email."
        ],
        "constraint": ["Bayes' rule consistency", "Law of total probability", "Proper normalization"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and explain its mathematical formulation."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] updates prior beliefs."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Using data from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the required [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Probability Distributions",
      "concept": "discrete_continuous_distributions",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Probability Mass Function (PMF)", "Probability Density Function (PDF)", "Cumulative Distribution Function (CDF)"],
        "context": [
          "Modeling the number of customer arrivals at a store per hour.",
          "Describing the distribution of heights in a population.",
          "Analyzing the lifetime of electronic components."
        ],
        "constraint": ["Non-negativity", "Total probability equals 1", "Monotonicity of CDF"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and describe its mathematical properties."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] models uncertainty."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given parameters from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the stated [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Random Variables, Expectations and Variance",
      "concept": "random_variables_expectation_variance",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Random Variable", "Expected Value", "Variance"],
        "context": [
          "Calculating the expected profit from a simple investment.",
          "Estimating the average waiting time in a queueing system.",
          "Measuring variability in daily stock returns."
        ],
        "constraint": ["Linearity of expectation", "Non-negative variance", "Finite expectation condition"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and explain its role in quantifying uncertainty."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] summarizes central tendency or variability."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Using data from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the required [CONSTRAINT]."
        }
      ]
    }
  ]
},
{
  "unit": "Statistics",
  "topics": [
    {
      "topic": "Moments",
      "concept": "statistical_moments",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Mean (First Moment)", "Variance (Second Central Moment)", "Skewness (Third Standardized Moment)"],
        "context": [
          "Analyzing the average and variability of students' exam scores.",
          "Measuring dispersion in daily household electricity consumption.",
          "Evaluating asymmetry in income distribution within a population."
        ],
        "constraint": ["Non-negative variance", "Zero skewness for symmetric data", "Finite moment existence"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and explain its statistical interpretation."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] characterizes the distribution of the data."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given sample data from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the stated [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Central Limit Theorem",
      "concept": "central_limit_theorem_sampling_distribution",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Sampling Distribution of the Mean", "Standard Error", "Z-score Approximation"],
        "context": [
          "Estimating the average height of a population using random samples.",
          "Approximating average customer waiting time in a service center.",
          "Analyzing mean daily sales from repeated random samples."
        ],
        "constraint": ["Large sample condition", "Independence assumption", "Normal approximation validity"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] in the context of the Central Limit Theorem."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] justifies normal approximation."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Using sample information from [CONTEXT], compute the [OBJECT_TYPE] and verify that the stated [CONSTRAINT] holds."
        }
      ]
    },
    {
      "topic": "Statistical Models: Regression, ANOVA",
      "concept": "regression_and_anova_models",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Linear Regression Coefficient", "ANOVA F-Statistic", "Coefficient of Determination (R^2)"],
        "context": [
          "Modeling the relationship between advertising budget and sales revenue.",
          "Comparing average test scores across multiple classrooms.",
          "Evaluating the effect of training hours on employee productivity."
        ],
        "constraint": ["Linearity assumption", "Homogeneity of variance", "Statistical significance threshold"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and describe its role in statistical modeling."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] measures relationship or group differences."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Given data from [CONTEXT], compute the [OBJECT_TYPE] and verify whether it satisfies the specified [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Hypothesis Testing, P-value, Chi-square",
      "concept": "hypothesis_testing_and_chi_square",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Null Hypothesis", "P-value", "Chi-Square Test Statistic"],
        "context": [
          "Testing whether a new drug has a different recovery rate than a standard treatment.",
          "Evaluating whether customer preferences differ across product categories.",
          "Assessing independence between gender and voting preference in a survey."
        ],
        "constraint": ["Significance level (alpha)", "Expected frequency condition", "Type I error control"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the [OBJECT_TYPE] and explain its role in hypothesis testing."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] guides decision-making."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Using observed data from [CONTEXT], compute the [OBJECT_TYPE] and determine whether the stated [CONSTRAINT] is satisfied."
        }
      ]
    }
  ]
}
        ]
    },
    {
        "domain": "cs",
        "units": [
            {
  "unit": "Python Programming",
  "topics": [
    {
      "topic": "Core Programming Concepts",
      "concept": "python_core_programming_fundamentals",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Variable Assignment", "Conditional Statement", "Loop Structure", "Function Definition"],
        "context": [
          "Building a simple command-line calculator.",
          "Validating and processing user registration input.",
          "Automating repetitive numeric computations."
        ],
        "constraint": ["Correct indentation", "Logical correctness", "Termination condition"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in Python and describe its syntax and purpose."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] controls program flow and execution."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Write or trace Python code in [CONTEXT] using [OBJECT_TYPE] and verify that it satisfies the specified [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Python Data Structure",
      "concept": "python_builtin_data_structures",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["List", "Dictionary", "Tuple", "Set"],
        "context": [
          "Storing and updating inventory records in a small store system.",
          "Counting word frequencies in a paragraph of text.",
          "Removing duplicate user IDs from a dataset."
        ],
        "constraint": ["Mutability rules", "Key uniqueness", "Efficient membership testing"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define the Python [OBJECT_TYPE] and describe its key characteristics."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain why the [OBJECT_TYPE] is appropriate for managing the data."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Implement a solution in [CONTEXT] using a [OBJECT_TYPE] and verify that it adheres to the required [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Error Handling in Python Code",
      "concept": "exception_handling_mechanisms",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Try-Except Block", "Finally Clause", "Custom Exception"],
        "context": [
          "Handling invalid numeric input in a user-driven calculator.",
          "Managing file-not-found errors while reading a configuration file.",
          "Validating data types in a simple data processing script."
        ],
        "constraint": ["Graceful failure", "Resource cleanup", "Specific exception handling"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in Python and explain its role in exception handling."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] improves program robustness."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Write Python code for [CONTEXT] demonstrating [OBJECT_TYPE] and verify that it satisfies the specified [CONSTRAINT]."
        }
      ]
    }
  ]
},{
  "unit": "OOP & Functional Programming",
  "topics": [
    {
      "topic": "OOP",
      "concept": "object_oriented_programming_principles",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Class Definition", "Object Instance", "Encapsulation", "Method"],
        "context": [
          "Designing a simple banking account system.",
          "Modeling products in an e-commerce application.",
          "Creating a student management system."
        ],
        "constraint": ["Data hiding", "Single responsibility principle", "Proper attribute access"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in object-oriented programming and describe its core characteristics."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] helps structure the program logically."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Write or trace code in [CONTEXT] demonstrating [OBJECT_TYPE] while ensuring adherence to [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Inheritance",
      "concept": "class_inheritance_mechanism",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Base Class", "Derived Class", "Method Overriding"],
        "context": [
          "Extending a general Vehicle class into Car and Bike subclasses.",
          "Creating specialized employee roles from a common Employee class.",
          "Customizing behavior in a graphical user interface component."
        ],
        "constraint": ["Method resolution order", "Code reusability", "Correct override behavior"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in the context of inheritance and describe its purpose."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] promotes reuse and extensibility."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Implement [OBJECT_TYPE] in [CONTEXT] and verify that it satisfies the specified [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Polymorphism",
      "concept": "polymorphic_behavior",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Method Overloading", "Method Overriding", "Duck Typing"],
        "context": [
          "Processing different payment methods through a common interface.",
          "Rendering various shapes using a shared draw method.",
          "Handling multiple file types with a unified processing function."
        ],
        "constraint": ["Interface consistency", "Substitutability", "Behavioral correctness"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] and explain how it enables polymorphic behavior."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] allows flexible method invocation."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Write code in [CONTEXT] demonstrating [OBJECT_TYPE] and verify compliance with the stated [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "List & Dictionary Comprehension",
      "concept": "comprehension_expressions",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["List Comprehension", "Dictionary Comprehension", "Conditional Expression"],
        "context": [
          "Filtering even numbers from a list of integers.",
          "Creating a mapping of words to their lengths in a sentence.",
          "Transforming raw numeric data into normalized values."
        ],
        "constraint": ["Readable syntax", "Efficient iteration", "Correct filtering logic"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in Python and describe its syntax structure."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] simplifies data transformation."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Write a Python expression in [CONTEXT] using [OBJECT_TYPE] and verify that it satisfies the required [CONSTRAINT]."
        }
      ]
    }
  ]
},
{
  "unit": "Python Libraries",
  "topics": [
    {
      "topic": "Regex",
      "concept": "regular_expressions_pattern_matching",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Regex Pattern", "Match Object", "Capture Group", "Substitution Operation"],
        "context": [
          "Validating email addresses in a user registration form.",
          "Extracting phone numbers from a text document.",
          "Cleaning log files by removing unwanted patterns."
        ],
        "constraint": ["Correct pattern syntax", "Greedy vs non-greedy matching", "Accurate group extraction"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in the context of Python regular expressions and describe its purpose."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] enables pattern detection or text transformation."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Write Python code in [CONTEXT] using [OBJECT_TYPE] and verify that it satisfies the specified [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Numpy",
      "concept": "numpy_numerical_computing",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["NumPy Array", "Broadcasting Operation", "Vectorized Function", "Matrix Multiplication"],
        "context": [
          "Performing element-wise normalization on sensor data.",
          "Computing statistical measures on large numerical datasets.",
          "Applying matrix operations in a simple linear algebra problem."
        ],
        "constraint": ["Shape compatibility", "Memory efficiency", "Vectorization without explicit loops"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in NumPy and describe its computational role."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] improves numerical performance."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Perform a computation in [CONTEXT] using [OBJECT_TYPE] and verify that it adheres to the required [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Pandas",
      "concept": "pandas_data_manipulation",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["DataFrame", "Series", "GroupBy Operation", "Merge Operation"],
        "context": [
          "Analyzing monthly sales records stored in a CSV file.",
          "Aggregating customer purchase data by region.",
          "Combining two datasets based on a common key."
        ],
        "constraint": ["Index alignment", "Handling missing values", "Efficient aggregation"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in Pandas and describe its structural properties."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] supports data manipulation and analysis."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Using a dataset in [CONTEXT], apply [OBJECT_TYPE] and verify that it satisfies the specified [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Matplotlib",
      "concept": "matplotlib_visualization",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Line Plot", "Bar Chart", "Scatter Plot", "Figure Object"],
        "context": [
          "Visualizing monthly revenue trends.",
          "Comparing category-wise sales performance.",
          "Plotting the relationship between study hours and exam scores."
        ],
        "constraint": ["Correct axis labeling", "Clear legend usage", "Accurate data representation"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in Matplotlib and describe its visualization purpose."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] communicates data insights effectively."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Write Python code in [CONTEXT] to generate a [OBJECT_TYPE] and verify compliance with the stated [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Virtual Environment and PIP",
      "concept": "environment_and_dependency_management",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Virtual Environment", "PIP Install Command", "Requirements File"],
        "context": [
          "Setting up dependencies for a new data analysis project.",
          "Managing library versions for a collaborative software project.",
          "Deploying a Python application to a new system."
        ],
        "constraint": ["Dependency isolation", "Version compatibility", "Reproducible environment setup"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] and explain its role in Python environment management."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] ensures stable and reproducible development."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Demonstrate the use of [OBJECT_TYPE] in [CONTEXT] and verify that it satisfies the required [CONSTRAINT]."
        }
      ]
    }
  ]
},{
  "unit": "CS & Algorithms",
  "topics": [
    {
      "topic": "Linux, Git and Version Control",
      "concept": "system_operations_and_version_control",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Linux Command", "Git Repository", "Branching Strategy", "Commit Operation"],
        "context": [
          "Managing source code for a collaborative software project.",
          "Tracking changes during feature development.",
          "Deploying code updates to a production server."
        ],
        "constraint": ["Correct command syntax", "Merge conflict resolution", "Version history integrity"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in the context of Linux or Git and describe its primary function."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] supports collaboration and system management."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Demonstrate the use of [OBJECT_TYPE] in [CONTEXT] and verify adherence to the required [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "SDLC and Agile",
      "concept": "software_development_lifecycle_models",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["SDLC Phase", "Sprint", "User Story", "Scrum Ceremony"],
        "context": [
          "Developing a web application from requirement gathering to deployment.",
          "Managing iterative product releases.",
          "Coordinating a cross-functional development team."
        ],
        "constraint": ["Requirement traceability", "Iterative feedback incorporation", "Time-boxed delivery"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] within SDLC or Agile methodology."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain the role of [OBJECT_TYPE] in structured software delivery."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Design a scenario in [CONTEXT] applying [OBJECT_TYPE] while satisfying the specified [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Big-O Notation",
      "concept": "algorithmic_time_and_space_complexity",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Time Complexity", "Space Complexity", "Worst-case Analysis", "Average-case Analysis"],
        "context": [
          "Analyzing nested loop algorithms.",
          "Comparing sorting algorithms.",
          "Evaluating recursive function performance."
        ],
        "constraint": ["Asymptotic growth rate", "Input size scalability", "Upper bound justification"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in the context of Big-O notation."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] determines algorithm efficiency."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Analyze the algorithm in [CONTEXT] and determine its [OBJECT_TYPE], justifying based on [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Tree and Graphs",
      "concept": "hierarchical_and_network_data_structures",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Binary Tree", "Binary Search Tree", "Graph Traversal", "Adjacency List"],
        "context": [
          "Representing hierarchical file systems.",
          "Modeling social network connections.",
          "Searching paths in a transportation network."
        ],
        "constraint": ["Traversal correctness", "Cycle detection", "Time complexity analysis"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] and describe its structural properties."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] organizes and processes data."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Implement or trace [OBJECT_TYPE] in [CONTEXT] ensuring compliance with [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Stack, Queue, Hash and Heaps",
      "concept": "linear_and_priority_data_structures",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Stack", "Queue", "Hash Table", "Heap"],
        "context": [
          "Managing function calls in recursion.",
          "Scheduling tasks based on priority.",
          "Implementing caching mechanisms."
        ],
        "constraint": ["Correct ordering principle", "Collision handling", "Heap property maintenance"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] and describe its operational principle."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain why [OBJECT_TYPE] is appropriate for the given scenario."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Design or trace an example in [CONTEXT] using [OBJECT_TYPE] while ensuring adherence to [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Sorting and Searching",
      "concept": "algorithmic_search_and_ordering",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Binary Search", "Merge Sort", "Quick Sort", "Linear Search"],
        "context": [
          "Searching in a sorted database record.",
          "Ordering large datasets for analytics.",
          "Optimizing lookup operations."
        ],
        "constraint": ["Correct partitioning logic", "Sorted input requirement", "Time complexity comparison"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] and describe its algorithmic approach."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] improves efficiency."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Apply [OBJECT_TYPE] in [CONTEXT] and analyze its performance based on [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Database Concept",
      "concept": "database_fundamentals",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Primary Key", "Normalization", "Transaction", "Index"],
        "context": [
          "Designing a relational database schema.",
          "Ensuring data integrity in financial records.",
          "Optimizing query performance."
        ],
        "constraint": ["ACID properties", "Referential integrity", "Redundancy reduction"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in database systems."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] ensures structured data management."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Design a solution in [CONTEXT] applying [OBJECT_TYPE] while maintaining [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "SQL",
      "concept": "structured_query_language_operations",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["SELECT Query", "JOIN Operation", "GROUP BY Clause", "Subquery"],
        "context": [
          "Retrieving sales data from multiple tables.",
          "Aggregating performance metrics by department.",
          "Filtering records based on nested conditions."
        ],
        "constraint": ["Correct join condition", "Aggregation accuracy", "Query optimization"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in SQL and describe its function."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] enables structured data retrieval."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Write an SQL example in [CONTEXT] using [OBJECT_TYPE] and ensure compliance with [CONSTRAINT]."
        }
      ]
    }
  ]
},{
  "unit": "Basic ML",
  "topics": [
    {
      "topic": "Supervised ML Concepts",
      "concept": "supervised_learning_principles",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Linear Regression", "Decision Tree", "Classification Model", "Target Variable"],
        "context": [
          "Predicting house prices based on historical features.",
          "Classifying emails as spam or not spam.",
          "Estimating customer churn from usage patterns."
        ],
        "constraint": ["Label availability", "Input-output mapping", "Minimization of prediction error"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] and describe its role in supervised learning."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] predicts outcomes from labeled data."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Apply [OBJECT_TYPE] to data in [CONTEXT] and verify that predictions minimize error under [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Unsupervised ML Concepts",
      "concept": "unsupervised_learning_principles",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Clustering", "Dimensionality Reduction", "Anomaly Detection", "Feature Extraction"],
        "context": [
          "Grouping customers by purchasing behavior.",
          "Detecting unusual network activity.",
          "Reducing dimensionality of image data for visualization."
        ],
        "constraint": ["No labeled data", "Pattern discovery", "Separation between clusters or components"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in unsupervised learning and describe its purpose."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] uncovers hidden structure in data."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Apply [OBJECT_TYPE] to [CONTEXT] and verify the separation or grouping satisfies [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Overfitting",
      "concept": "model_overfitting",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["High Complexity Model", "Regularization Technique", "Training Error vs Test Error"],
        "context": [
          "Fitting a polynomial regression to noisy data.",
          "Training a deep neural network on a small dataset.",
          "Building a decision tree without pruning."
        ],
        "constraint": ["Poor generalization", "Regularization requirement", "Avoid memorization of noise"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] in the context of machine learning."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] affects model performance on unseen data."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Analyze a model in [CONTEXT] and apply [OBJECT_TYPE] strategies to reduce overfitting while respecting [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Bias and Variance",
      "concept": "bias_variance_tradeoff",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Bias Error", "Variance Error", "Tradeoff Management"],
        "context": [
          "Evaluating linear vs nonlinear models on training and test data.",
          "Comparing underfitted vs overfitted model behaviors.",
          "Tuning model complexity in supervised learning tasks."
        ],
        "constraint": ["Minimization of total error", "Balance between bias and variance", "Model generalization"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] and describe its impact on model prediction."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] contributes to the bias-variance tradeoff."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Measure [OBJECT_TYPE] in [CONTEXT] and adjust model parameters to achieve optimal [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Validation",
      "concept": "model_validation_techniques",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Train-Test Split", "Cross-Validation", "Holdout Set", "K-Fold CV"],
        "context": [
          "Evaluating predictive performance of a regression model.",
          "Selecting the best hyperparameters for a classification model.",
          "Ensuring robust assessment of model generalization."
        ],
        "constraint": ["Data leakage avoidance", "Balanced folds", "Accurate performance estimation"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] and explain its role in model validation."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] ensures reliable performance evaluation."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Implement [OBJECT_TYPE] in [CONTEXT] and verify that it satisfies [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Metrics",
      "concept": "model_evaluation_metrics",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Accuracy", "Precision and Recall", "F1 Score", "Mean Squared Error"],
        "context": [
          "Evaluating a binary classification model for spam detection.",
          "Assessing regression predictions for housing prices.",
          "Comparing multiple models on a test dataset."
        ],
        "constraint": ["Appropriate metric selection", "Interpretability", "Consistency across datasets"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] and describe its significance in model evaluation."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] reflects model performance."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Compute [OBJECT_TYPE] in [CONTEXT] and verify it satisfies the specified [CONSTRAINT]."
        }
      ]
    },
    {
      "topic": "Data Handling",
      "concept": "data_preprocessing_and_transformation",
      "bloom_levels": [1, 2, 3],
      "variation_axes": {
        "object_type": ["Missing Value Imputation", "Normalization", "Encoding Categorical Data", "Feature Scaling"],
        "context": [
          "Handling incomplete survey responses.",
          "Scaling features for a regression model.",
          "Encoding categorical variables for classification tasks."
        ],
        "constraint": ["Preserve data integrity", "Consistent scaling", "Avoid introducing bias"]
      },
      "templates": [
        {
          "level": 1,
          "type": "define",
          "stem": "Define [OBJECT_TYPE] and explain its role in preparing data for ML models."
        },
        {
          "level": 2,
          "type": "explain",
          "stem": "In [CONTEXT], explain how [OBJECT_TYPE] improves model input quality."
        },
        {
          "level": 3,
          "type": "compute",
          "stem": "Apply [OBJECT_TYPE] in [CONTEXT] and verify that it satisfies [CONSTRAINT]."
        }
      ]
    }
  ]
},
        ]
    }

    
    
]