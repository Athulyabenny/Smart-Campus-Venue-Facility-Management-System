# ==============================================================================
# Smart Campus Venue & Facility Management: R Data Analytics & Modeling
# File: analytics/campus_analytics.R
# MCA Data Structures & Analytics Project Deliverable
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. LOAD AND PREPROCESS DATASET
# ------------------------------------------------------------------------------

cat("\n[STEP 1] Loading and Preprocessing Campus Venue Analytics Dataset...\n")

csv_path <- file.path("data", "venue_analytics_dataset.csv")
if (!file.exists(csv_path)) {
  csv_path <- file.path("..", "data", "venue_analytics_dataset.csv")
}

if (!file.exists(csv_path)) {
  stop(paste("Dataset file not found at:", csv_path))
}

venue_data <- read.csv(csv_path, header = TRUE, stringsAsFactors = FALSE)
cat(sprintf("Loaded %d venue records with %d attributes.\n", nrow(venue_data), ncol(venue_data)))

cat("\n--- Dataset Structure ---\n")
str(venue_data)

# Preprocessing & Data Cleaning
venue_data$category <- as.factor(venue_data$category)
venue_data$efficiency_grade <- as.factor(venue_data$efficiency_grade)
venue_data$capacity <- as.integer(venue_data$capacity)
venue_data$duration_hours <- as.numeric(venue_data$duration_hours)
venue_data$attendees <- as.integer(venue_data$attendees)
venue_data$utilization_pct <- as.numeric(venue_data$utilization_pct)
venue_data$satisfaction_score <- as.numeric(venue_data$satisfaction_score)

# Handle potential missing values
if (any(is.na(venue_data))) {
  cat("Warning: Missing values detected. Imputing with column medians...\n")
  venue_data$utilization_pct[is.na(venue_data$utilization_pct)] <- median(venue_data$utilization_pct, na.rm = TRUE)
}

# Create binary classification label: High Efficiency (Utilization >= 75%)
venue_data$is_high_efficiency <- as.factor(ifelse(venue_data$utilization_pct >= 75.0, 1, 0))

cat("\n--- Descriptive Summary Statistics ---\n")
summary(venue_data[, c("capacity", "duration_hours", "attendees", "utilization_pct", "satisfaction_score")])

# ------------------------------------------------------------------------------
# 2. STATISTICAL MODELING
# ------------------------------------------------------------------------------

cat("\n[STEP 2] Fitting Multiple Linear Regression (Venue Utilization)...\n")
# Model: Utilization % ~ Duration Hours + Attendees + Venue Capacity
lm_model <- lm(utilization_pct ~ duration_hours + attendees + capacity, data = venue_data)
cat("\n--- Multiple Linear Regression Model Summary ---\n")
print(summary(lm_model))

cat("\n[STEP 3] Fitting Binary Logistic Regression (High Efficiency Probability)...\n")
# Model: High Efficiency ~ Duration Hours + Satisfaction Score
glm_model <- glm(is_high_efficiency ~ duration_hours + satisfaction_score, data = venue_data, family = binomial)
cat("\n--- Binary Logistic Regression Model Summary ---\n")
print(summary(glm_model))

cat("\n[COMPLETE] Campus Venue Analytics executed successfully.\n")
