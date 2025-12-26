library(mirt)
# ============================================================================
##Step 1 Load the data
# ============================================================================
data <- read.csv("D:/Internship/IRT/adaptive-exam/data/student_matrix_apr5_set.csv")
data <- data[,-1]


# ============================================================================
# MODEL SPECIFICATION
# ============================================================================
model_2d <- ('
  MATH = Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10,
         Q11, Q12, Q13, Q14, Q15, Q16, Q17, Q37, 
         Q41,  Q50
  
  TECH = Q18, Q19, Q20, Q21, Q22, Q23, Q24, Q25, Q26, Q27,
         Q28, Q29, Q30, Q31, Q32, Q33,  Q34, Q35,Q36, Q38, Q39, Q40,
         Q42, Q43, Q44, Q45, Q46,Q47, Q48, Q49
  
  COV = MATH*TECH
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


# Extract item parameters
params_50 <- coef(model_2pl, IRTpars = TRUE, simplify = TRUE)
items_50 <- params_50$items

# Identify dimension columns
dim_cols <- grep("^a[0-9]", colnames(items_50), value = TRUE)

# Handle first duplicate pair: Q17 and Q41 (A/B testing/hypothesis testing)
if(length(dim_cols) > 0) {
  items_50["Q17", dim_cols] <- 
    colMeans(items_50[c("Q17", "Q41"), dim_cols])
}
cat("\nAveraged Q17 parameters (Q17+Q41 combined):\n")
print(items_50["Q17", ])

# Handle second duplicate pair: Q26 and Q47 (Matplotlib subplot)
if(length(dim_cols) > 0) {
  items_50["Q26", dim_cols] <- 
    colMeans(items_50[c("Q26", "Q47"), dim_cols])
}
cat("\nAveraged Q26 parameters (Q26+Q47 combined):\n")
print(items_50["Q26", ])

# Remove both duplicate items (Q41 and Q48)
items_final <- items_50[!rownames(items_50) %in% c("Q41", "Q47"), ]

cat("\nQ41 and Q47 removed. Final item count:", nrow(items_final), "\n")
print(items_final)

# ============================================================================


df_2pl_5 = as.data.frame(items_final)
print(df_2pl_5)
df_2pl_5$b <- pmin(df_2pl_5$b, 3)


write.csv(df_2pl_5, "2_dimensional_set_5.csv", row.names = TRUE)
