# Simple MIRT Guide

## What are 2PL and 3PL Models?

### 2PL (2-Parameter Logistic) Model

**Parameters**:
- **a (discrimination)**: How well the item separates high and low ability students
  - Higher value = better at distinguishing ability levels
  - Range: typically 0.3 to 2.5
- **b (difficulty)**: How hard the item is
  - Higher value = harder item
  - Range: typically -3 to +3

### 3PL (3-Parameter Logistic) Model

**Parameters**:
- **a (discrimination)**: Same as 2PL
- **b (difficulty)**: Same as 2PL  
- **g (guessing)**: Probability of getting it right by random guessing
  - Range: 0 to 0.35 (typically around 0.25 for 4-option MCQ)

---

## Data Requirements

### Required Format

Your data must be in **binary format** (0/1):
```csv
Q1,Q2,Q3,Q4,Q5,...,Q50
1,0,1,1,0,...,1
0,1,1,0,1,...,0
1,1,1,1,1,...,1
```

Where:
- **1** = Correct answer
- **0** = Incorrect answer

### Sample Size Requirements

**Minimum recommended**: 450-500 responses (students)

- **For 2PL model**: At least 10 responses per item (e.g., 50 items × 10 = 500 responses)
- **For reliable parameter estimates**: 500+ responses preferred
- **For multidimensional models**: Larger samples provide more stable estimates

**Rule of thumb**: More responses = more reliable parameter estimates

---

## We Used 2PL for Your Data
```r
model_2pl <- mirt(data = data, 
                  model = model_2d,
                  itemtype = '2PL',  # <-- 2PL chosen
                  method = 'QMCEM',
                  verbose = TRUE)
```

---

## The 2-Dimensional Model

We split the items into **two dimensions**:

For example, for a 50 question dataset:
```r
model_2d <- ('
  MATH = Q1, Q2, Q3, ..., Q17, Q37, Q41, Q50        # 20 math items
  TECHNICAL = Q18, Q19, Q20, ..., Q49               # 30 technical items
  
  COV = MATH*TECHNICAL                              # Allow correlation
')
```

This means:
- Items Q1-Q17, Q37, Q41, Q50 measure **MATH ability**
- Items Q18-Q49 (except Q37, Q41, Q50) measure **TECHNICAL ability**
- The two abilities can correlate (students good at math might be good at technical skills)

---

## What We Got: Parameters

After fitting the model, we extracted parameters for each dimension:
```r
# Get all parameters
params <- coef(model_2pl, IRTpars = TRUE, simplify = TRUE)
items <- params$items
```

### MATH Dimension Parameters

Each MATH item has:
- **a1**: Discrimination on MATH dimension (should be high)
- **a2**: Discrimination on TECHNICAL dimension (0)
- **b**: Difficulty

Example output:
```
     a1    a2      b
Q1   1.2   0    0.5    # Good MATH item 
Q2   1.5   0   -0.3    # Good MATH item, easier than Q1
Q3   0.8   0    1.2    # Weaker MATH item 
```

### TECHNICAL Dimension Parameters

Each TECHNICAL item has:
- **a1**: Discrimination on MATH dimension (0)
- **a2**: Discrimination on TECHNICAL dimension (should be high)
- **b**: Difficulty

Example output:
```
      a1    a2      b
Q18   0   1.4   -0.2    # Good TECHNICAL item 
Q19   0   1.6    0.8    # Good TECHNICAL item, harder than Q18
Q20   0   1.1    0.3    # Decent TECHNICAL item
```

---

## Quick Checklist

Before running MIRT analysis:

✅ **Data Format**: Binary (0/1) responses  
✅ **Sample Size**: At least 450-500 students  
✅ **Missing Data**: Less than 5% missing responses preferred  
✅ **Item Quality**: Remove items with >95% or <5% correct responses  
✅ **Dimensions**: Clearly define which items belong to which dimension

---

## Loading Your Data
```r
# Load binary response data
data <- read.csv("student_responses.csv")

# Remove ID column if present
data <- data[, -1]

# Verify format
cat("Students:", nrow(data), "\n")        # Should be 450+
cat("Items:", ncol(data), "\n")           # Number of questions
cat("Values:", unique(unlist(data)), "\n") # Should show: 0, 1 
```