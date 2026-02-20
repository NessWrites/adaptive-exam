Schema = [
    {
        "domain": "math",
        "units": [
            {
                "unit": "Linear Algebra",
                "topics": [
                    {
                        "topic": "Scalar and Vectors",
                        "concept": "scalar_vector",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Feature vector", "Force component", "State vector"],
                            "context": ["Predictive Analytics", "Structural Engineering", "Quantum Computing"],
                            "constraint": ["linear scaling", "dimensional consistency"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "In the development of a [CONTEXT] model, define the [OBJECT_TYPE] and explain the formula used to ensure [CONSTRAINT] when adjusting global parameters."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Using the requirements of [CONTEXT], explain the physical or logical significance of a zero-magnitude [OBJECT_TYPE] and how it impacts the system's ability to maintain [CONSTRAINT]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Given a set of raw data inputs in [CONTEXT], compute the resulting [OBJECT_TYPE] and verify if the scaling factor satisfies the [CONSTRAINT] required for system stability."
                            }
                        ]
                    },
                    {
                        "topic": "Vector Norms, Dot Product and Orthogonal Vectors",
                        "concept": "vector_norm_dot_product_and_orthogonal",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Euclidean distance (L2)", "Cosine similarity", "Power intensity vector"],
                            "context": ["Search Engine Ranking", "Renewable Energy (Solar)", "Autonomous Navigation"],
                            "constraint": ["orthogonality (zero interference)", "unit magnitude", "minimal error variance"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "For a [CONTEXT] algorithm, define the [OBJECT_TYPE] and describe how it is used to satisfy the [CONSTRAINT] between two competing signals."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "In a [CONTEXT] setup, explain why the [OBJECT_TYPE] must be maximized or minimized to ensure that the system meets the [CONSTRAINT] for efficient operation."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "An array in [CONTEXT] provides vectors $u$ and $v$. Calculate the [OBJECT_TYPE] to determine the effective alignment and verify if the [CONSTRAINT] is met within a 5% tolerance."
                            }
                        ]
                    },
                    {
                        "topic": "Linear Transformation and Matrix",
                        "concept": "linear_transformation_and_matrix",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Rotation Matrix", "Projection Operator", "Adjacency Matrix"],
                            "context": ["Computer Graphics (CGI)", "Robotic Kinematics", "Social Network Analysis"],
                            "constraint": ["Invariance (Shape preservation)", "Rank-deficiency (Information loss)", "Orthogonal transformation"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "In [CONTEXT] workflows, define the [OBJECT_TYPE] and state the mathematical condition required to preserve the [CONSTRAINT] during data processing."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "A transformation using [OBJECT_TYPE] is applied to a model in [CONTEXT]. Explain how the [CONSTRAINT] prevents or causes the collapse of specific dimensions in the output."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Apply the specified [OBJECT_TYPE] to the input coordinates of a [CONTEXT] system and compute the output to prove that the [CONSTRAINT] has been successfully maintained."
                            }
                        ]
                    },
                    {
                        "topic": "Orthogonality",
                        "concept": "orthogonality",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Gram-Schmidt Process", "Least Squares Estimator", "Orthogonal Basis"],
                            "context": ["Signal De-noising", "Market Trend Forecasting", "Acoustic Engineering"],
                            "constraint": ["Minimization of residuals", "Signal-to-noise optimization", "Normalization"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "When optimizing a [CONTEXT] system, define the [OBJECT_TYPE] and state the condition necessary to achieve the [CONSTRAINT]."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Given the use of [OBJECT_TYPE] in [CONTEXT], explain how the [CONSTRAINT] ensures that the resulting model does not overfit the data or lose signal clarity."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Using real-world parameters from [CONTEXT], compute the [OBJECT_TYPE] and verify that the output successfully satisfies the [CONSTRAINT] for the predicted values."
                            }
                        ]
                    },
                    {
                        "topic": "Eigen and Singular Value Decomposition",
                        "concept": "svd",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Principal Components", "Singular Values", "Eigenvectors"],
                            "context": ["Facial Recognition Systems", "Bridge Vibration Analysis", "Recommendation Engines"],
                            "constraint": ["Data compression ratio", "Directional invariance", "Spectral stability"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "In the context of [CONTEXT], define the [OBJECT_TYPE] and explain its role in satisfying the [CONSTRAINT] during high-dimensional data reduction."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Explain how the [OBJECT_TYPE] allows an engineer in [CONTEXT] to identify the most critical points of failure while maintaining the [CONSTRAINT] of the overall structure."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Given a covariance matrix from a [CONTEXT] study, compute the [OBJECT_TYPE] and determine if the resulting [CONSTRAINT] allows for a 90% reduction in data storage."
                            }
                        ]
                    }
                ]
            },
            {
                "unit": "Calculus",
                "topics": [
                    {
                        "topic": "Partial Derivatives",
                        "concept": "partial_derivatives",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Gradient vector", "Rate of change (Sensitivity)", "Jacobian Matrix"],
                            "context": ["Deep Learning (Backpropagation)", "Chemical Kinetics", "Financial Option Pricing"],
                            "constraint": ["local extrema (Optimization)", "Steepest descent", "Constraint satisfaction"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "In [CONTEXT] training, define the [OBJECT_TYPE] and state how it is used to satisfy the [CONSTRAINT] of the loss function."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Consider a multi-variable process in [CONTEXT]. Explain how the [OBJECT_TYPE] determines the system's sensitivity to small changes while under the [CONSTRAINT]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "A model in [CONTEXT] uses the function $f(x, y, z)$. Compute the [OBJECT_TYPE] at the current operating point and verify if the system has reached the [CONSTRAINT] required for equilibrium."
                            }
                        ]
                    },
                    {
                        "topic": "Ordinary Derivatives",
                        "concept": "ordinary_derivatives",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Normal derivative (flux rate)", "Unit normal vector", "Boundary conditions"],
                            "context": ["Thermal Management", "Fluid Dynamics", "Structural Geology"],
                            "constraint": ["No-flux (insulation)", "Tangential flow", "Isothermal boundary"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "In a [CONTEXT] scenario, define the [OBJECT_TYPE] and explain how the dot product is used to ensure the [CONSTRAINT] is physically maintained at the surface."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "You are designing a system in [CONTEXT]. Explain the physical significance of the [OBJECT_TYPE] regarding how energy/material moves across the boundary when satisfying a [CONSTRAINT]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "A sensor in a [CONTEXT] system measures a field modeled by $f(x, y)$. Compute the [OBJECT_TYPE] at $(x_0, y_0)$ and determine if the current flow satisfies the [CONSTRAINT] for stability."
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
                "unit": "Basics of Computer Systems",
                "topics": [
                    {
                        "topic": "Digital Information and Logic",
                        "concept": "digital_logic_and_representation",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Floating-point number", "XOR Gate", "Two's Complement", "Bitmapped Image"],
                            "context": ["circuit design", "data compression", "cryptography", "error checking"],
                            "constraint": ["precision loss", "overflow", "truth table validity", "DeMorgan's Law"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "In the context of [CONTEXT], define a [OBJECT_TYPE] and state the rules regarding [CONSTRAINT]."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Using the principles of [CONTEXT], explain why [CONSTRAINT] occurs when manipulating a [OBJECT_TYPE]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Given a specific input in [CONTEXT], determine the output of the [OBJECT_TYPE] and verify if the result suffers from [CONSTRAINT]."
                            }
                        ]
                    },
                    {
                        "topic": "Architecture and OS",
                        "concept": "arch_and_os_fundamentals",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Cache Memory", "Process Control Block", "Instruction Set (RISC)", "Thread"],
                            "context": ["multitasking environment", "high-performance computing", "embedded systems"],
                            "constraint": ["Von-Neumann bottleneck", "Deadlock", "Context Switching overhead"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "Define the role of [OBJECT_TYPE] in a [CONTEXT] and describe the phenomenon of [CONSTRAINT]."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Explain how the design of [OBJECT_TYPE] improves efficiency in [CONTEXT] despite the limitations imposed by [CONSTRAINT]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Analyze a scenario involving [OBJECT_TYPE] in [CONTEXT] and calculate/estimate the performance impact caused by [CONSTRAINT]."
                            }
                        ]
                    }
                ]
            },
            {
                "unit": "Python Programming",
                "topics": [
                    {
                        "topic": "Object-Oriented Programming",
                        "concept": "oop_concepts",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Inheritance", "Polymorphism", "Decorator", "Class Method"],
                            "context": ["game development", "API design", "library extension"],
                            "constraint": ["Method Resolution Order (MRO)", "Encapsulation", "Liskov Substitution Principle"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "In Python [CONTEXT], define [OBJECT_TYPE] and explain the syntax rules regarding [CONSTRAINT]."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Explain how using [OBJECT_TYPE] in [CONTEXT] promotes code reusability while adhering to [CONSTRAINT]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Write or trace a Python code snippet demonstrating [OBJECT_TYPE] in [CONTEXT] that specifically handles [CONSTRAINT]."
                            }
                        ]
                    },
                    {
                        "topic": "Numpy and Data Analysis",
                        "concept": "numpy_vectorization",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Numpy Array", "Broadcasting", "Slicing", "Dot Product"],
                            "context": ["image processing", "statistical analysis", "financial modeling"],
                            "constraint": ["Shape mismatch", "Memory efficiency", "Vectorization"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "Define [OBJECT_TYPE] in the context of [CONTEXT] and state the condition required to avoid [CONSTRAINT]."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Explain why [OBJECT_TYPE] is preferred over standard lists in [CONTEXT] regarding [CONSTRAINT]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Given two datasets in [CONTEXT], perform a [OBJECT_TYPE] operation and determine the resulting dimensions, ensuring [CONSTRAINT] is satisfied."
                            }
                        ]
                    }
                ]
            },
            {
                "unit": "Data Structures and Algorithms",
                "topics": [
                    {
                        "topic": "Algorithm Analysis",
                        "concept": "time_space_complexity",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Binary Search", "Merge Sort", "Recursion", "Hash Map Lookup"],
                            "context": ["large-scale database", "real-time systems", "memory-constrained device"],
                            "constraint": ["Worst-case O(n^2)", "Space Complexity O(n)", "Stack Overflow"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "Define the Big-O notation for [OBJECT_TYPE] and identify the scenario that triggers [CONSTRAINT]."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "In the context of [CONTEXT], explain why [OBJECT_TYPE] might be unsuitable due to [CONSTRAINT]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Calculate the asymptotic complexity of [OBJECT_TYPE] applied to [CONTEXT] and verify if it exceeds [CONSTRAINT]."
                            }
                        ]
                    },
                    {
                        "topic": "Data Structures",
                        "concept": "linear_and_non_linear_ds",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Stack (LIFO)", "Binary Search Tree", "Adjacency Matrix", "Queue (FIFO)"],
                            "context": ["browser history", "task scheduling", "social network graph"],
                            "constraint": ["Collision resolution", "Unbalanced tree height", "Memory contiguity"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "Define the structure of [OBJECT_TYPE] used in [CONTEXT] and describe the method for handling [CONSTRAINT]."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Explain how the properties of [OBJECT_TYPE] make it ideal for [CONTEXT], specifically addressing [CONSTRAINT]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Simulate the insertion/deletion of elements in [OBJECT_TYPE] for [CONTEXT] and show the state of the structure under [CONSTRAINT]."
                            }
                        ]
                    }
                ]
            },
            {
                "unit": "Database Systems",
                "topics": [
                    {
                        "topic": "SQL and Relational Design",
                        "concept": "rdbms_fundamentals",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Foreign Key", "Inner Join", "Group By Clause", "Subquery"],
                            "context": ["e-commerce inventory", "student records", "banking transactions"],
                            "constraint": ["Referential Integrity", "ACID properties", "Normalization (3NF)"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "In the context of [CONTEXT], define [OBJECT_TYPE] and state how it enforces [CONSTRAINT]."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Explain the result of applying [OBJECT_TYPE] on a [CONTEXT] database and how it helps maintain [CONSTRAINT]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Construct a SQL query using [OBJECT_TYPE] for a [CONTEXT] schema and verify that the design satisfies [CONSTRAINT]."
                            }
                        ]
                    },
                    {
                        "topic": "NoSQL",
                        "concept": "nosql_properties",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Document Store (MongoDB)", "Sharding", "Key-Value Pair"],
                            "context": ["content management system", "big data analytics", "real-time feed"],
                            "constraint": ["CAP Theorem", "Eventual Consistency", "Schema flexibility"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "Define [OBJECT_TYPE] in [CONTEXT] and state its relationship to the [CONSTRAINT]."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Explain why [OBJECT_TYPE] is chosen for [CONTEXT] over relational models, specifically regarding the trade-off presented by [CONSTRAINT]."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Design a data model using [OBJECT_TYPE] for [CONTEXT] and demonstrate how it handles a failure scenario based on [CONSTRAINT]."
                            }
                        ]
                    }
                ]
            },
            {
                "unit": "Application Development",
                "topics": [
                    {
                        "topic": "Web Frameworks",
                        "concept": "web_architecture",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["REST API", "MVC Pattern", "HTTP Request (POST/GET)", "DOM Manipulation"],
                            "context": ["social media feed", "user authentication", "dynamic dashboard"],
                            "constraint": ["Statelessness", "Separation of Concerns", "Same-origin policy"]
                        },
                        "templates": [
                            {
                                "level": 1,
                                "type": "define",
                                "stem": "Define [OBJECT_TYPE] in [CONTEXT] and explain the importance of [CONSTRAINT]."
                            },
                            {
                                "level": 2,
                                "type": "explain",
                                "stem": "Explain the flow of data when using [OBJECT_TYPE] in [CONTEXT] and how [CONSTRAINT] influences the architecture."
                            },
                            {
                                "level": 3,
                                "type": "compute",
                                "stem": "Design or trace a request cycle using [OBJECT_TYPE] for [CONTEXT] ensuring it adheres to [CONSTRAINT]."
                            }
                        ]
                    }
                ]
            }
        ]
    }

    
    
]