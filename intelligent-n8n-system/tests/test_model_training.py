"""
Integration tests for ML model training pipeline
"""

import pytest
import asyncio
import tempfile
import json
import numpy as np
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
import pandas as pd


@pytest.mark.integration
@pytest.mark.slow
class TestModelTraining:
    """Integration tests for ML model training"""

    @pytest.fixture
    def training_data(self):
        """Generate mock training data"""
        return [
            {
                "project_analysis": {
                    "languages": {"python": 2, "javascript": 1},
                    "technologies": [
                        {"name": "fastapi", "type": "framework", "confidence": 0.9},
                        {"name": "postgresql", "type": "database", "confidence": 0.8},
                    ],
                    "architecture_type": "api",
                    "complexity_score": 0.6,
                    "automation_potential": 0.8,
                },
                "knowledge_context": {
                    "nodes": ["httpRequest", "postgres"],
                    "patterns": ["API Integration", "Database Backup"],
                    "confidence": 0.85,
                },
                "expected_workflows": [
                    {
                        "name": "API Monitoring Workflow",
                        "category": "monitoring",
                        "confidence": 0.9,
                    },
                    {
                        "name": "Database Backup Workflow",
                        "category": "maintenance",
                        "confidence": 0.8,
                    },
                ],
                "user_feedback": {
                    "rating": 5,
                    "useful": True,
                    "comments": "Very helpful workflows",
                },
            },
            {
                "project_analysis": {
                    "languages": {"python": 1},
                    "technologies": [
                        {"name": "django", "type": "framework", "confidence": 0.95}
                    ],
                    "architecture_type": "web",
                    "complexity_score": 0.4,
                    "automation_potential": 0.6,
                },
                "knowledge_context": {
                    "nodes": ["scheduleTrigger", "httpRequest"],
                    "patterns": ["Scheduled Tasks"],
                    "confidence": 0.7,
                },
                "expected_workflows": [
                    {
                        "name": "Scheduled Health Check",
                        "category": "monitoring",
                        "confidence": 0.7,
                    }
                ],
                "user_feedback": {
                    "rating": 4,
                    "useful": True,
                    "comments": "Good for basic monitoring",
                },
            },
        ]

    @pytest.fixture
    def mock_models(self):
        """Mock ML models for testing"""
        from unittest.mock import MagicMock

        models = {}

        # Mock Random Forest
        rf_model = MagicMock()
        rf_model.fit = MagicMock()
        rf_model.predict_proba = MagicMock(
            return_value=np.array([[0.2, 0.8], [0.9, 0.1]])
        )
        rf_model.score = MagicMock(return_value=0.85)
        models["random_forest"] = rf_model

        # Mock Neural Network
        nn_model = MagicMock()
        nn_model.fit = MagicMock()
        nn_model.predict_proba = MagicMock(
            return_value=np.array([[0.3, 0.7], [0.8, 0.2]])
        )
        nn_model.evaluate = MagicMock(return_value=0.82)
        models["neural_network"] = nn_model

        # Mock SVM
        svm_model = MagicMock()
        svm_model.fit = MagicMock()
        svm_model.predict_proba = MagicMock(
            return_value=np.array([[0.1, 0.9], [0.7, 0.3]])
        )
        svm_model.score = MagicMock(return_value=0.78)
        models["svm"] = svm_model

        return models

    @pytest.mark.asyncio
    async def test_training_data_preparation(self, training_data, test_config):
        """Test training data preparation and feature extraction"""
        from src.ml.training_pipeline import TrainingPipeline

        pipeline = TrainingPipeline()

        # Test data preparation
        prepared_data = await pipeline.prepare_training_data(training_data)

        # Verify data structure
        assert "features" in prepared_data
        assert "labels" in prepared_data
        assert "metadata" in prepared_data

        # Verify feature extraction
        features = prepared_data["features"]
        assert len(features) == len(training_data)
        assert len(features[0]) > 0  # Should have extracted features

        # Verify labels
        labels = prepared_data["labels"]
        assert len(labels) == len(training_data)

        # Verify metadata
        metadata = prepared_data["metadata"]
        assert "feature_names" in metadata
        assert "label_encoder" in metadata

    @pytest.mark.asyncio
    async def test_model_training_pipeline(
        self, training_data, mock_models, test_config
    ):
        """Test complete model training pipeline"""
        from src.ml.training_pipeline import TrainingPipeline

        with tempfile.TemporaryDirectory() as temp_dir:
            # Update config to use temp directory
            test_config.ml.model_path = temp_dir

            pipeline = TrainingPipeline()

            # Mock the model creation
            with patch.object(pipeline, "_create_models") as mock_create:
                mock_create.return_value = mock_models

                # Test training pipeline
                results = await pipeline.train_models(training_data)

                # Verify training results
                assert "random_forest" in results
                assert "neural_network" in results
                assert "svm" in results

                # Verify each model was trained
                for model_name, result in results.items():
                    assert hasattr(result, 'accuracy') or "accuracy" in result
                    assert hasattr(result, 'training_time') or "training_time" in result
                    assert hasattr(result, 'model_path') or "model_path" in result
                    
                    # Handle both object and dict formats
                    if hasattr(result, 'accuracy'):
                        assert result.accuracy > 0.0
                        assert result.training_time > 0.0
                    else:
                        assert result["accuracy"] > 0.0
                        assert result["training_time"] > 0.0

    @pytest.mark.asyncio
    async def test_model_evaluation(self, training_data, mock_models, test_config):
        """Test model evaluation and validation"""
        from src.ml.training_pipeline import TrainingPipeline

        pipeline = TrainingPipeline()

        # Prepare test data
        prepared_data = await pipeline.prepare_training_data(training_data)

        # Split data for evaluation
        train_size = int(0.8 * len(prepared_data["features"]))
        X_train = prepared_data["features"][:train_size]
        X_test = prepared_data["features"][train_size:]
        y_train = prepared_data["labels"][:train_size]
        y_test = prepared_data["labels"][train_size:]

        # Test model evaluation
        with patch.object(pipeline, "_create_models") as mock_create:
            mock_create.return_value = mock_models

            evaluation_results = await pipeline.evaluate_models(
                X_train, X_test, y_train, y_test
            )

            # Verify evaluation results
            assert "random_forest" in evaluation_results
            assert "neural_network" in evaluation_results
            assert "svm" in evaluation_results

            for model_name, results in evaluation_results.items():
                assert "accuracy" in results
                assert "precision" in results
                assert "recall" in results
                assert "f1_score" in results
                assert "confusion_matrix" in results

    @pytest.mark.asyncio
    async def test_model_persistence(self, mock_models, test_config):
        """Test model saving and loading"""
        from src.ml.training_pipeline import TrainingPipeline

        with tempfile.TemporaryDirectory() as temp_dir:
            test_config.ml.model_path = temp_dir

            pipeline = TrainingPipeline()

            # Test model saving
            with patch.object(pipeline, "_create_models") as mock_create:
                mock_create.return_value = mock_models

                # Save models
                saved_paths = await pipeline.save_models(mock_models)

                # Verify models were saved
                assert len(saved_paths) == len(mock_models)
                for model_name, path in saved_paths.items():
                    assert Path(path).exists()
                    assert model_name in path

                # Test model loading
                loaded_models = await pipeline.load_models(saved_paths)

                # Verify models were loaded
                assert len(loaded_models) == len(mock_models)
                for model_name in mock_models.keys():
                    assert model_name in loaded_models

    @pytest.mark.asyncio
    async def test_hyperparameter_tuning(self, training_data, test_config):
        """Test hyperparameter tuning for models"""
        from src.ml.training_pipeline import TrainingPipeline

        pipeline = TrainingPipeline()

        # Prepare training data
        prepared_data = await pipeline.prepare_training_data(training_data)

        # Test hyperparameter tuning
        with patch("sklearn.model_selection.GridSearchCV") as mock_grid_search:
            # Mock grid search results
            mock_best_model = MagicMock()
            mock_best_model.best_score_ = 0.88
            mock_best_model.best_params_ = {"n_estimators": 100, "max_depth": 10}

            mock_grid_search.return_value.fit = MagicMock()
            mock_grid_search.return_value.best_estimator_ = mock_best_model
            mock_grid_search.return_value.best_score_ = 0.88
            mock_grid_search.return_value.best_params_ = {
                "n_estimators": 100,
                "max_depth": 10,
            }

            tuning_results = await pipeline.tune_hyperparameters(
                prepared_data["features"], prepared_data["labels"]
            )

            # Verify tuning results
            assert "best_params" in tuning_results
            assert "best_score" in tuning_results
            assert "tuning_time" in tuning_results
            assert tuning_results["best_score"] > 0.0

    @pytest.mark.asyncio
    async def test_incremental_learning(self, training_data, test_config):
        """Test incremental learning with new data"""
        from src.ml.training_pipeline import TrainingPipeline

        pipeline = TrainingPipeline()

        # Initial training data
        initial_data = training_data[:1]
        new_data = training_data[1:]

        # Prepare initial data
        initial_prepared = await pipeline.prepare_training_data(initial_data)

        # Mock models for incremental learning
        mock_model = MagicMock()
        mock_model.partial_fit = MagicMock()
        mock_model.score = MagicMock(return_value=0.85)

        # Test incremental learning
        with patch.object(pipeline, "_create_models") as mock_create:
            mock_create.return_value = {"test_model": mock_model}

            # Initial training
            initial_results = await pipeline.train_models(initial_data)

            # Prepare new data
            new_prepared = await pipeline.prepare_training_data(new_data)

            # Incremental learning
            updated_results = await pipeline.incremental_learn(
                initial_results, new_prepared
            )

            # Verify incremental learning
            assert "test_model" in updated_results
            assert "updated_accuracy" in updated_results["test_model"]
            assert updated_results["test_model"]["updated_accuracy"] > 0.0

    @pytest.mark.asyncio
    async def test_model_ensemble_training(self, training_data, test_config):
        """Test ensemble model training"""
        from src.ml.training_pipeline import TrainingPipeline

        pipeline = TrainingPipeline()

        # Prepare training data
        prepared_data = await pipeline.prepare_training_data(training_data)

        # Mock ensemble models
        mock_ensemble = MagicMock()
        mock_ensemble.fit = MagicMock()
        mock_ensemble.predict_proba = MagicMock(
            return_value=np.array([[0.25, 0.75], [0.8, 0.2]])
        )
        mock_ensemble.score = MagicMock(return_value=0.90)

        # Test ensemble training
        with patch.object(pipeline, "_create_ensemble_model") as mock_create:
            mock_create.return_value = mock_ensemble

            ensemble_results = await pipeline.train_ensemble_model(
                prepared_data["features"], prepared_data["labels"]
            )

            # Verify ensemble training
            assert "ensemble_accuracy" in ensemble_results
            assert "individual_scores" in ensemble_results
            assert "training_time" in ensemble_results
            assert ensemble_results["ensemble_accuracy"] > 0.0

    @pytest.mark.asyncio
    async def test_training_monitoring(self, training_data, test_config):
        """Test training monitoring and logging"""
        from src.ml.training_pipeline import TrainingPipeline

        pipeline = TrainingPipeline()

        # Test training with monitoring
        with (
            patch.object(pipeline, "_create_models") as mock_create,
            patch.object(pipeline, "_log_training_metrics") as mock_log,
        ):
            mock_models = {"test_model": MagicMock()}
            mock_create.return_value = mock_models

            # Train with monitoring
            results = await pipeline.train_models_with_monitoring(training_data)

            # Verify monitoring was called
            assert mock_log.called
            assert "training_metrics" in results
            assert "monitoring_data" in results

    @pytest.mark.asyncio
    async def test_model_performance_comparison(self, training_data, test_config):
        """Test model performance comparison"""
        from src.ml.training_pipeline import TrainingPipeline

        pipeline = TrainingPipeline()

        # Prepare training data
        prepared_data = await pipeline.prepare_training_data(training_data)

        # Test performance comparison
        comparison_results = await pipeline.compare_model_performance(
            prepared_data["features"], prepared_data["labels"]
        )

        # Verify comparison results
        assert "model_scores" in comparison_results
        assert "best_model" in comparison_results
        assert "performance_metrics" in comparison_results

        # Verify model scores
        model_scores = comparison_results["model_scores"]
        assert len(model_scores) > 0

        # Verify best model selection
        best_model = comparison_results["best_model"]
        assert "name" in best_model
        assert "score" in best_model
        assert best_model["score"] > 0.0
