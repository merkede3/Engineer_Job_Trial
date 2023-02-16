import mlflow
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.regression import MultilayerPerceptronRegressor
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.pipeline import Pipeline
from pyspark.sql.functions import col

# Assemble features into a single vector and standardize them
vector_assembler = VectorAssembler(inputCols=feature_cols, outputCol='unscaled_features')
scaler = StandardScaler(inputCol='unscaled_features', outputCol='features')

# Create an instance of the Deep Learning regression model
mlp = MultilayerPerceptronRegressor(featuresCol='features', layers=[len(feature_cols), 20, 10, 1], maxIter=200, seed=123)

# Define a parameter grid for hyperparameter tuning
param_grid = ParamGridBuilder() \
    .addGrid(mlp.layers, [[len(feature_cols), 10, 5, 1], [len(feature_cols), 20, 10, 5, 1]]) \
    .addGrid(mlp.blockSize, [128, 256, 512]) \
    .addGrid(mlp.solver, ['l-bfgs', 'gd']) \
    .build()

# Create an instance of the Deep Learning model with cross-validation
mlp_cv = CrossValidator(estimator=mlp, estimatorParamMaps=param_grid, evaluator=RegressionEvaluator(metricName='rmse'), numFolds=5, parallelism=4)

# Create the pipeline
pipeline = Pipeline(stages=[vector_assembler, scaler, mlp_cv])

# Fit the pipeline on the training data
model_fit = pipeline.fit(training_data.repartition(4))

# Make predictions on the test data
predictions = model_fit.transform(test_data.repartition(4))
