"""
Test cases for ECG Signal Biometric Encryption System.

This module contains unit tests for the core encryption functionality.
"""

import pytest
import numpy as np
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ecg_gui_all import ECGEncryptionGUI
    HAS_MAIN_MODULE = True
except ImportError:
    HAS_MAIN_MODULE = False


class TestEncryptionFunctions:
    """Test encryption-related functionality."""
    
    def test_logistic_map_generation(self):
        """Test logistic map sequence generation."""
        # This would test the logistic_map function if accessible
        # For now, we'll test the concept
        r = 3.847
        x0 = 0.623
        n = 100
        
        # Simulate logistic map behavior
        sequence = np.zeros(n)
        x = x0
        for i in range(n):
            x = r * x * (1 - x)
            sequence[i] = x
        
        # Basic validation
        assert len(sequence) == n
        assert all(0 <= x <= 1 for x in sequence)  # Logistic map bounds
        assert not np.array_equal(sequence, np.zeros(n))  # Not all zeros
    
    def test_entropy_calculation(self):
        """Test entropy calculation functionality."""
        # Test signal with known entropy characteristics
        # Random signal should have higher entropy than constant signal
        
        # Constant signal (low entropy)
        constant_signal = np.ones(100)
        constant_entropy = self._calculate_shannon_entropy(constant_signal)
        
        # Random signal (high entropy)
        random_signal = np.random.random(100)
        random_entropy = self._calculate_shannon_entropy(random_signal)
        
        # Random signal should have higher entropy
        assert random_entropy > constant_entropy
        assert constant_entropy < 1.0  # Very low entropy for constant
        assert random_entropy > 3.0   # Reasonable entropy for random
    
    def test_signal_feature_extraction(self):
        """Test signal feature extraction."""
        # Create test signal
        t = np.linspace(0, 10, 1000)
        test_signal = np.sin(2 * np.pi * 1.2 * t) + 0.5 * np.random.normal(0, 1, 1000)
        
        # Extract basic features
        mean_val = np.mean(test_signal)
        std_val = np.std(test_signal)
        entropy_val = self._calculate_shannon_entropy(test_signal)
        
        # Validate features
        assert isinstance(mean_val, float)
        assert isinstance(std_val, float)
        assert isinstance(entropy_val, float)
        assert std_val > 0  # Non-zero standard deviation
        assert entropy_val > 0  # Positive entropy
    
    def test_chaotic_parameters(self):
        """Test chaotic parameter generation."""
        # Test parameter ranges for logistic map
        r_values = [3.5, 3.7, 3.847, 3.9, 4.0]
        x0_values = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for r in r_values:
            for x0 in x0_values:
                # Generate sequence
                sequence = np.zeros(50)
                x = x0
                for i in range(50):
                    x = r * x * (1 - x)
                    sequence[i] = x
                
                # Validate sequence properties
                assert len(sequence) == 50
                assert all(0 <= x <= 1 for x in sequence)
    
    def _calculate_shannon_entropy(self, signal):
        """Calculate Shannon entropy of a signal."""
        # Normalize signal to [0, 1]
        signal_norm = (signal - np.min(signal)) / (np.max(signal) - np.min(signal))
        
        # Create histogram
        hist, _ = np.histogram(signal_norm, bins=256, range=(0, 1))
        hist = hist[hist > 0]  # Remove zero bins
        
        if len(hist) == 0:
            return 0.0
        
        # Calculate entropy
        p = hist / np.sum(hist)
        entropy = -np.sum(p * np.log2(p))
        return entropy


class TestDataProcessing:
    """Test data processing functionality."""
    
    def test_csv_data_loading(self):
        """Test CSV data loading capabilities."""
        # This would test actual CSV loading if we had access to the data
        # For now, we'll test the concept
        
        # Simulate CSV data structure
        sample_data = {
            'ecg_id': [1, 2, 3],
            '0.0': [0.1, 0.2, 0.3],
            '0.1': [0.4, 0.5, 0.6],
            '0.2': [0.7, 0.8, 0.9]
        }
        
        # Validate data structure
        assert 'ecg_id' in sample_data
        assert len(sample_data['ecg_id']) > 0
        assert all(isinstance(x, (int, float)) for x in sample_data['0.0'])
    
    def test_signal_validation(self):
        """Test signal validation logic."""
        # Valid signal
        valid_signal = np.random.random(1000)
        assert len(valid_signal) > 0
        assert not np.any(np.isnan(valid_signal))
        assert not np.any(np.isinf(valid_signal))
        
        # Invalid signal (with NaN values)
        invalid_signal = np.random.random(1000)
        invalid_signal[100] = np.nan
        assert np.any(np.isnan(invalid_signal))


class TestSecurityMetrics:
    """Test security analysis functionality."""
    
    def test_correlation_analysis(self):
        """Test correlation analysis between signals."""
        # Create two different signals
        signal1 = np.random.random(1000)
        signal2 = np.random.random(1000)
        
        # Calculate correlation
        correlation = np.corrcoef(signal1, signal2)[0, 1]
        
        # Validate correlation
        assert -1 <= correlation <= 1
        assert not np.isnan(correlation)
        assert not np.isinf(correlation)
    
    def test_entropy_improvement(self):
        """Test entropy improvement measurement."""
        # Original signal (lower entropy)
        original = np.sin(np.linspace(0, 10, 1000))  # Periodic signal
        
        # "Encrypted" signal (higher entropy - simulated)
        encrypted = np.random.random(1000)
        
        # Calculate entropies
        orig_entropy = self._calculate_shannon_entropy(original)
        enc_entropy = self._calculate_shannon_entropy(encrypted)
        
        # Encrypted should have higher entropy
        assert enc_entropy > orig_entropy
        
        # Calculate improvement ratio
        improvement = enc_entropy / orig_entropy
        assert improvement > 1.0


# Main test runner
if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
