Schema = [
    {
        "domain": "math",
        "units": [
            {
                "unit": "Linear Algebra",
                "topics": [
                    {
                        "topic": "Scalars and Vectors",
                        "concept": "scalar_vector",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Feature vector", "Force component", "State vector"],
                            "context": [
                                        "Representing the magnitude and direction of wind velocity at various points in a weather model.",
                                        "Encoding RGB color values for individual pixels in a digital image.",
                                        "Organizing inventory levels for multiple products across various warehouse locations.",
                                        "Calculating stress distribution within a structural beam during finite element analysis."
                                        ],
                            "constraint": ["linear scaling", "dimensional consistency"]
                        },
                        "templates": [
    {
        "level": 1,
        "type": "define",
        "stem": "Define the [OBJECT_TYPE] and describe its fundamental mathematical properties."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In the context of [CONTEXT], explain the significance and role of a [OBJECT_TYPE] within the system."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Given raw inputs in [CONTEXT], compute the resulting [OBJECT_TYPE] and verify that it satisfies the required [CONSTRAINT]."
    }
]
                    },
                    {
                        "topic": "Vector Norms, Dot Product and Orthogonal Vectors",
                        "concept": "vector_norm_dot_product_and_orthogonal",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Euclidean distance (L2)", "Cosine similarity", "Power intensity vector"],
                            "context": [
                                        "Calculation of mechanical work performed by a constant force vector along a linear displacement vector.",
                                        "Calculating the total path length traversed along grid lines in urban navigation and robotics.",
                                        "Propagating system states over discrete time steps using a state transition matrix in control systems."
                                        ],
                            "constraint": ["orthogonality (zero interference)", "unit magnitude", "minimal error variance"]
                        },
                        "templates": [
    {
        "level": 1,
        "type": "define",
        "stem": "Define the [OBJECT_TYPE] and describe its fundamental mathematical properties."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In the context of [CONTEXT], explain the significance and role of a [OBJECT_TYPE] within the system."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Given raw inputs in [CONTEXT], compute the resulting [OBJECT_TYPE] and verify that it satisfies the required [CONSTRAINT]."
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
        "stem": "Define the [OBJECT_TYPE] and state its key algebraic properties."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] transforms inputs within the system."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Apply the specified [OBJECT_TYPE] in [CONTEXT] and compute the output to verify preservation of the [CONSTRAINT]."
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
        "stem": "Define the [OBJECT_TYPE] and describe the mathematical principle it is based on."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] improves system accuracy or stability."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Using parameters from [CONTEXT], compute the [OBJECT_TYPE] and verify that it satisfies the [CONSTRAINT]."
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
        "stem": "Define the [OBJECT_TYPE] and describe its role in matrix decomposition."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] helps analyze structural or data patterns."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Given data from [CONTEXT], compute the [OBJECT_TYPE] and determine whether the resulting model maintains the [CONSTRAINT]."
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
                            "context": ["Deep Learning", "Chemical Kinetics", "Financial Option Pricing"],
                            "constraint": ["local extrema (Optimization)", "Steepest descent", "Constraint satisfaction"]
                        },
                        "templates": [
    {
        "level": 1,
        "type": "define",
        "stem": "Define the [OBJECT_TYPE] for a multivariable function."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] determines system sensitivity."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "For a function in [CONTEXT], compute the [OBJECT_TYPE] and verify whether the system satisfies the [CONSTRAINT]."
    }
]
                    },
                    {
                        "topic": "Ordinary Derivatives",
                        "concept": "ordinary_derivatives",
                        "bloom_levels": [1, 2, 3],
                        "variation_axes": {
                            "object_type": ["Normal derivative (flux rate)", "Unit normal vector", "Boundary conditions"],
                            "context": ["Local rate of heat transfer through a material given a temperature gradient.",
                                        "Instantaneous rate of change of reactant concentration during a chemical reaction.",
                                        "Marginal cost of producing an additional unit of a manufactured good.",
                                        "Instantaneous rate of change of displacement of a moving object."],
                            "constraint": ["No-flux (insulation)", "Tangential flow", "Isothermal boundary"]
                        },
                        "templates": [
    {
        "level": 1,
        "type": "define",
        "stem": "Define the [OBJECT_TYPE] for a multivariable function."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain how the [OBJECT_TYPE] determines system sensitivity."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "For a function in [CONTEXT], compute the [OBJECT_TYPE] and verify whether the system satisfies the [CONSTRAINT]."
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
        "stem": "Define [OBJECT_TYPE] and describe its structural representation."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain how [OBJECT_TYPE] functions within the system."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Given input in [CONTEXT], determine the output of [OBJECT_TYPE] and verify whether it satisfies [CONSTRAINT]."
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
        "stem": "Define [OBJECT_TYPE] and describe its role in computer systems."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In a [CONTEXT], explain how [OBJECT_TYPE] improves system efficiency."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Analyze [OBJECT_TYPE] in a [CONTEXT] and estimate its impact under [CONSTRAINT]."
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
        "stem": "Define [OBJECT_TYPE] in Python and describe its core characteristics."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain how [OBJECT_TYPE] improves modularity and structure."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Write or trace code in [CONTEXT] demonstrating [OBJECT_TYPE] while ensuring adherence to [CONSTRAINT]."
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
        "stem": "Define [OBJECT_TYPE] in numerical computing."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain why [OBJECT_TYPE] improves performance."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Perform a [OBJECT_TYPE] operation in [CONTEXT] and verify that it avoids [CONSTRAINT]."
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
        "stem": "Define the time or space complexity of [OBJECT_TYPE]."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain why [OBJECT_TYPE] may impact system performance."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Compute the asymptotic complexity of [OBJECT_TYPE] in [CONTEXT] and determine whether it exceeds [CONSTRAINT]."
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
        "stem": "Define the time or space complexity of [OBJECT_TYPE]."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain why [OBJECT_TYPE] may impact system performance."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Compute the asymptotic complexity of [OBJECT_TYPE] in [CONTEXT] and determine whether it exceeds [CONSTRAINT]."
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
        "stem": "Define [OBJECT_TYPE] in relational databases."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In a [CONTEXT] database, explain how [OBJECT_TYPE] operates."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Construct a query using [OBJECT_TYPE] in [CONTEXT] and verify compliance with [CONSTRAINT]."
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
        "stem": "Define [OBJECT_TYPE] in distributed databases."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain why [OBJECT_TYPE] is selected."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Design a [OBJECT_TYPE] model for [CONTEXT] and demonstrate how it handles [CONSTRAINT]."
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
        "stem": "Define [OBJECT_TYPE] in distributed databases."
    },
    {
        "level": 2,
        "type": "explain",
        "stem": "In [CONTEXT], explain why [OBJECT_TYPE] is selected."
    },
    {
        "level": 3,
        "type": "compute",
        "stem": "Design a [OBJECT_TYPE] model for [CONTEXT] and demonstrate how it handles [CONSTRAINT]."
    }
]
                    }
                ]
            }
        ]
    }

    
    
]