library(mirt)
# ============================================================================
##Step 1 Load the data
# ============================================================================
data <- read.csv("data/student_matrix_apr7_set.csv")

data <- data[,-1]


# ============================================================================
##Step 2: Define the dimensions 
# ============================================================================

# DIMENSION 1: Mathematical & Logical Reasoning (14)
# Linear Algebra: Q1, Q2, Q3, Q4, Q41, Q42, Q43
# Calculus: Q6, Q7, Q8, Q9
# Logic: Q37, Q39, Q40

dim1_items <- c(1, 2, 3, 4, 6, 7, 8, 9, 37, 39, 40, 41, 42, 43)

# DIMENSION 2: Statistical Reasoning (13)
# Q5, Q10, Q11, Q12, Q13, Q14, Q15, Q16, Q17, Q44, Q45, Q49, Q50

dim2_items <- c(5, 10, 11, 12, 13, 14, 15, 16, 17, 44, 45, 49, 50)

##We will combine them into one single dimension 


# DIMENSION 3: Computing & Programming (23)
# Python: Q18, Q19, Q20, Q21, Q22, Q23, Q24, Q25, Q26, Q27, Q48
# Data Structures: Q28, Q29, Q30, Q31, Q46, Q47
# Software Eng: Q32, Q33, Q34, Q35, Q36
# ML Vocabulary: Q38

dim3_items <- c(18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 
                32, 33, 34, 35, 36, 38, 46, 47, 48)

# ============================================================================
# MODEL SPECIFICATION
# ============================================================================
model_2d <- ('
  QUANT = Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10,
          Q11, Q12, Q13, Q14, Q15, Q16, Q17, Q37, Q39, Q40,Q41,
          Q42, Q43, Q44, Q45, Q50
  TECH = Q18, Q19, Q20, Q21, Q22, Q23, Q24, Q25, Q26, Q27,
         Q28, Q29, Q30, Q31, Q32, Q33, Q34, Q35, Q36,
         Q38, Q46, Q47, Q48,Q49
  COV = QUANT*TECH
')


#=============================================================================
# FIT THE MODEL
# ============================================================================
cat("Fitting 2D-MIRT model items...\n")
model_2pl <- mirt(data = data, 
                  model = model_2d,
                  itemtype = '2PL',
                  method = 'QMCEM',
                  verbose = TRUE)

# ============================================================================
# MODEL FIT
# ============================================================================
cat("\n=== MODEL FIT STATISTICS ===\n")
fit_stats <- M2(model_2pl, type = "C2")
print(fit_stats)


# ============================================================================
# EXTRACT PARAMETERS AND AVERAGE Q2 & Q41 (Duplicates)
# ============================================================================

# Extract item parameters
params_50 <- coef(model_2pl, IRTpars = TRUE, simplify = TRUE)
items_50 <- params_50$items

dim_cols <- grep("^a[0-9]", colnames(items_50), value = TRUE)
if(length(dim_cols) > 0) {
  items_50["Q2", dim_cols] <- 
    colMeans(items_50[c("Q2", "Q41"), dim_cols])
}

cat("\nAveraged Q2 parameters (Q2+Q41 combined):\n")
print(items_50["Q2", ])

# Remove Q41 from the parameter matrix
items_final <- items_50[!rownames(items_50) %in% "Q41", ]

cat("\nQ41 removed. Final item count:", nrow(items_final), "\n")

print(items_final)

# ============================================================================


df_2pl_7 = as.data.frame(items_final)
print(df_2pl_7)
df_2pl_7$b <- pmin(df_2pl_7$b, 3)


write.csv(df_2pl_7, "2_dimensional_set_7.csv", row.names = TRUE)
