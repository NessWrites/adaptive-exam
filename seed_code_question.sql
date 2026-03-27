-- =============================================================================
-- SEED DATA: Coding Questions for code-grader compatibility
-- Inserts into 'questions' (base) + 'code_questions' (child) tables
-- =============================================================================

-- 1. Two Sum (No data_type - simple built-in types)
INSERT INTO questions (domain, concept_tag, question_text, question_type, a_values, b_value, calibration_status)
VALUES (
    'DSA', 'Arrays',
    'Write a function `two_sum(nums, target)` that returns the indices of two numbers in the list that add up to the target. You may assume each input has exactly one solution.',
    'code', ARRAY[0.0, 0.0], 0.0, 'operational'
);
INSERT INTO code_questions (id, placeholder, function_name, configurations, markscheme, total_marks, timeout, memory_limit, bloom_level)
VALUES (
    currval('questions_unique_id_seq'),
    E'def two_sum(nums, target):\n    # Return indices of two numbers that add up to target\n    pass',
    'two_sum',
    '{"allowed_imports": [], "data_type": null}',
    '[
        {"input": [[2, 7, 11, 15], 9], "expected": [0, 1], "hidden": false},
        {"input": [[3, 2, 4], 6], "expected": [1, 2], "hidden": false},
        {"input": [[3, 3], 6], "expected": [0, 1], "hidden": true},
        {"input": [[1, 5, 3, 7, 2], 9], "expected": [1, 4], "hidden": true}
    ]',
    4, 5, '128m', 2.0
);


-- 2. Reverse Linked List (data_type: linked_list)
INSERT INTO questions (domain, concept_tag, question_text, question_type, a_values, b_value, calibration_status)
VALUES (
    'DSA', 'Linked List',
    'Write a function `reverse_linked_list(head)` that reverses a singly linked list and returns the new head.',
    'code', ARRAY[0.0, 0.0], 0.0, 'operational'
);
INSERT INTO code_questions (id, placeholder, function_name, configurations, markscheme, total_marks, timeout, memory_limit, bloom_level)
VALUES (
    currval('questions_unique_id_seq'),
    E'def reverse_linked_list(head):\n    # Reverse the linked list and return the new head\n    pass',
    'reverse_linked_list',
    '{"allowed_imports": [], "data_type": "linked_list"}',
    '[
        {"input": [[1, 2, 3, 4, 5]], "expected": [5, 4, 3, 2, 1], "hidden": false},
        {"input": [[1, 2]], "expected": [2, 1], "hidden": false},
        {"input": [[1]], "expected": [1], "hidden": true},
        {"input": [[]], "expected": [], "hidden": true}
    ]',
    4, 5, '128m', 2.0
);


-- 3. Maximum Depth of Binary Tree (data_type: binary_tree)
INSERT INTO questions (domain, concept_tag, question_text, question_type, a_values, b_value, calibration_status)
VALUES (
    'DSA', 'Binary Tree',
    'Write a function `max_depth(root)` that returns the maximum depth (height) of a binary tree. The maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.',
    'code', ARRAY[0.0, 0.0], 0.0, 'operational'
);
INSERT INTO code_questions (id, placeholder, function_name, configurations, markscheme, total_marks, timeout, memory_limit, bloom_level)
VALUES (
    currval('questions_unique_id_seq'),
    E'def max_depth(root):\n    # Return the maximum depth of the binary tree\n    pass',
    'max_depth',
    '{"allowed_imports": [], "data_type": "binary_tree"}',
    '[
        {"input": [[3, 9, 20, null, null, 15, 7]], "expected": 3, "hidden": false},
        {"input": [[1, null, 2]], "expected": 2, "hidden": false},
        {"input": [[]], "expected": 0, "hidden": true},
        {"input": [[1]], "expected": 1, "hidden": true},
        {"input": [[1, 2, 3, 4, 5, null, null, 6]], "expected": 4, "hidden": true}
    ]',
    5, 5, '128m', 2.0
);


-- 4. Mean Squared Error (No data_type - math/statistics)
INSERT INTO questions (domain, concept_tag, question_text, question_type, a_values, b_value, calibration_status)
VALUES (
    'Mathematics', 'Statistics',
    'Write a function `mean_squared_error(y_true, y_pred)` that calculates the Mean Squared Error between two lists of values. MSE = (1/n) * sum((y_true_i - y_pred_i)^2).',
    'code', ARRAY[0.0, 0.0], 0.0, 'operational'
);
INSERT INTO code_questions (id, placeholder, function_name, configurations, markscheme, total_marks, timeout, memory_limit, bloom_level)
VALUES (
    currval('questions_unique_id_seq'),
    E'def mean_squared_error(y_true, y_pred):\n    # Calculate and return the MSE\n    pass',
    'mean_squared_error',
    '{"allowed_imports": ["import math"], "data_type": null}',
    '[
        {"input": [[1, 2, 3], [1, 2, 3]], "expected": 0.0, "hidden": false},
        {"input": [[1, 2, 3], [4, 5, 6]], "expected": 9.0, "hidden": false},
        {"input": [[0, 0, 0], [1, 1, 1]], "expected": 1.0, "hidden": true},
        {"input": [[2.5, 3.5], [3.0, 4.0]], "expected": 0.25, "hidden": true}
    ]',
    4, 5, '128m', 1.0
);


-- 5. Fibonacci (No data_type - recursion/DP)
INSERT INTO questions (domain, concept_tag, question_text, question_type, a_values, b_value, calibration_status)
VALUES (
    'DSA', 'Dynamic Programming',
    'Write a function `fibonacci(n)` that returns the nth Fibonacci number. The sequence starts with F(0) = 0 and F(1) = 1.',
    'code', ARRAY[0.0, 0.0], 0.0, 'operational'
);
INSERT INTO code_questions (id, placeholder, function_name, configurations, markscheme, total_marks, timeout, memory_limit, bloom_level)
VALUES (
    currval('questions_unique_id_seq'),
    E'def fibonacci(n):\n    # Return the nth Fibonacci number\n    pass',
    'fibonacci',
    '{"allowed_imports": [], "data_type": null}',
    '[
        {"input": [0], "expected": 0, "hidden": false},
        {"input": [1], "expected": 1, "hidden": false},
        {"input": [10], "expected": 55, "hidden": false},
        {"input": [20], "expected": 6765, "hidden": true},
        {"input": [30], "expected": 832040, "hidden": true}
    ]',
    5, 5, '128m', 2.0
);


-- 6. Invert Binary Tree (data_type: binary_tree)
INSERT INTO questions (domain, concept_tag, question_text, question_type, a_values, b_value, calibration_status)
VALUES (
    'DSA', 'Binary Tree',
    'Write a function `invert_tree(root)` that inverts a binary tree (mirror image) and returns the root of the inverted tree.',
    'code', ARRAY[0.0, 0.0], 0.0, 'operational'
);
INSERT INTO code_questions (id, placeholder, function_name, configurations, markscheme, total_marks, timeout, memory_limit, bloom_level)
VALUES (
    currval('questions_unique_id_seq'),
    E'def invert_tree(root):\n    # Invert the binary tree and return root\n    pass',
    'invert_tree',
    '{"allowed_imports": [], "data_type": "binary_tree"}',
    '[
        {"input": [[4, 2, 7, 1, 3, 6, 9]], "expected": [4, 7, 2, 9, 6, 3, 1], "hidden": false},
        {"input": [[2, 1, 3]], "expected": [2, 3, 1], "hidden": false},
        {"input": [[]], "expected": [], "hidden": true},
        {"input": [[1]], "expected": [1], "hidden": true}
    ]',
    4, 5, '128m', 3.0
);


-- 7. Detect Cycle in Linked List (data_type: linked_list_with_cycle)
INSERT INTO questions (domain, concept_tag, question_text, question_type, a_values, b_value, calibration_status)
VALUES (
    'DSA', 'Linked List',
    'Write a function `has_cycle(head)` that returns True if a linked list has a cycle, False otherwise.',
    'code', ARRAY[0.0, 0.0], 0.0, 'operational'
);
INSERT INTO code_questions (id, placeholder, function_name, configurations, markscheme, total_marks, timeout, memory_limit, bloom_level)
VALUES (
    currval('questions_unique_id_seq'),
    E'def has_cycle(head):\n    # Return True if the linked list has a cycle\n    pass',
    'has_cycle',
    '{"allowed_imports": [], "data_type": "linked_list_with_cycle"}',
    '[
        {"input": [[3, 2, 0, -4], 1], "expected": true, "hidden": false},
        {"input": [[1, 2], 0], "expected": true, "hidden": false},
        {"input": [[1], -1], "expected": false, "hidden": true},
        {"input": [[1, 2, 3, 4, 5], -1], "expected": false, "hidden": true}
    ]',
    4, 5, '128m', 3.0
);


-- 8. Matrix Transpose (No data_type)
INSERT INTO questions (domain, concept_tag, question_text, question_type, a_values, b_value, calibration_status)
VALUES (
    'Mathematics', 'Linear Algebra',
    'Write a function `transpose(matrix)` that returns the transpose of a given 2D matrix.',
    'code', ARRAY[0.0, 0.0], 0.0, 'operational'
);
INSERT INTO code_questions (id, placeholder, function_name, configurations, markscheme, total_marks, timeout, memory_limit, bloom_level)
VALUES (
    currval('questions_unique_id_seq'),
    E'def transpose(matrix):\n    # Return the transpose of the matrix\n    pass',
    'transpose',
    '{"allowed_imports": [], "data_type": null}',
    '[
        {"input": [[[1, 2, 3], [4, 5, 6]]], "expected": [[1, 4], [2, 5], [3, 6]], "hidden": false},
        {"input": [[[1, 2], [3, 4], [5, 6]]], "expected": [[1, 3, 5], [2, 4, 6]], "hidden": false},
        {"input": [[[1]]], "expected": [[1]], "hidden": true},
        {"input": [[[1, 2, 3, 4]]], "expected": [[1], [2], [3], [4]], "hidden": true}
    ]',
    4, 5, '128m', 1.0
);


-- 9. Binary Search (No data_type - searching)
INSERT INTO questions (domain, concept_tag, question_text, question_type, a_values, b_value, calibration_status)
VALUES (
    'DSA', 'Searching',
    'Write a function `binary_search(nums, target)` that returns the index of the target in a sorted list, or -1 if not found.',
    'code', ARRAY[0.0, 0.0], 0.0, 'operational'
);
INSERT INTO code_questions (id, placeholder, function_name, configurations, markscheme, total_marks, timeout, memory_limit, bloom_level)
VALUES (
    currval('questions_unique_id_seq'),
    E'def binary_search(nums, target):\n    # Return the index of target or -1 if not found\n    pass',
    'binary_search',
    '{"allowed_imports": [], "data_type": null}',
    '[
        {"input": [[-1, 0, 3, 5, 9, 12], 9], "expected": 4, "hidden": false},
        {"input": [[-1, 0, 3, 5, 9, 12], 2], "expected": -1, "hidden": false},
        {"input": [[5], 5], "expected": 0, "hidden": true},
        {"input": [[1, 3, 5, 7, 9], 7], "expected": 3, "hidden": true},
        {"input": [[], 1], "expected": -1, "hidden": true}
    ]',
    5, 5, '128m', 2.0
);


-- 10. Linear Regression (No data_type - math/ML)
INSERT INTO questions (domain, concept_tag, question_text, question_type, a_values, b_value, calibration_status)
VALUES (
    'Mathematics', 'Machine Learning',
    'Write a function `linear_regression(X, Y)` that computes the slope (m) and intercept (b) of the best-fit line using the least squares method. Return [m, b].',
    'code', ARRAY[0.0, 0.0], 0.0, 'operational'
);
INSERT INTO code_questions (id, placeholder, function_name, configurations, markscheme, total_marks, timeout, memory_limit, bloom_level)
VALUES (
    currval('questions_unique_id_seq'),
    E'def linear_regression(X, Y):\n    # Return [slope, intercept]\n    pass',
    'linear_regression',
    '{"allowed_imports": ["import math"], "data_type": null}',
    '[
        {"input": [[1, 2, 3], [2, 4, 6]], "expected": [2.0, 0.0], "hidden": false},
        {"input": [[1, 2, 3, 4, 5], [2, 4, 5, 4, 5]], "expected": [0.6, 2.2], "hidden": false},
        {"input": [[0, 1, 2], [1, 1, 1]], "expected": [0.0, 1.0], "hidden": true},
        {"input": [[1, 2, 3, 4], [1, 3, 5, 7]], "expected": [2.0, -1.0], "hidden": true}
    ]',
    4, 5, '128m', 3.0
);
