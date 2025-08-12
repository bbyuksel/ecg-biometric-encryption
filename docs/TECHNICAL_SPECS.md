# Technical Specifications - ECG Signal Biometric Encryption System

## 🏗️ System Architecture

### Overview
The ECG Signal Biometric Encryption System is a modular, real-time processing platform that combines signal processing, chaotic encryption, and machine learning optimization.

### Core Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Input    │───▶│  Signal Process │───▶│   Encryption    │
│                 │    │                 │    │                 │
│ • CSV Files     │    │ • Feature Ext.  │    │ • Chaotic Maps  │
│ • Serial Port   │    │ • Filtering     │    │ • Permutation   │
│ • Real-time     │    │ • Normalization │    │ • XOR Operations│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   ML Engine     │    │   Security      │
                       │                 │    │   Analysis      │
                       │ • Optimization  │    │ • Entropy       │
                       │ • Learning      │    │ • Correlation   │
                       │ • Adaptation    │    │ • Attack Tests  │
                       └─────────────────┘    └─────────────────┘
```

## 💻 Software Requirements

### Operating Systems
- **Windows**: 10/11 (64-bit)
- **Linux**: Ubuntu 18.04+, CentOS 7+
- **macOS**: 10.15+ (Catalina)

### Python Environment
- **Python Version**: 3.8 - 3.11
- **Package Manager**: pip 21.0+
- **Virtual Environment**: Recommended (venv/conda)

### Hardware Requirements
- **CPU**: Intel i5/AMD Ryzen 5 or equivalent
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB free space
- **Display**: 1366x768 minimum resolution

## 📦 Dependencies

### Core Dependencies
```python
# Numerical Computing
numpy>=1.21.0          # Array operations, mathematical functions
pandas>=1.3.0          # Data manipulation and analysis
matplotlib>=3.5.0      # Data visualization and plotting

# GUI Framework
tkinter                 # Built-in Python GUI (no installation needed)

# Serial Communication
pyserial>=3.5          # Serial port communication
```

### Optional Dependencies
```python
# Signal Processing
scipy>=1.7.0           # Scientific computing and signal processing

# Machine Learning
tensorflow>=2.8.0      # Deep learning framework
scikit-learn>=1.0.0    # Machine learning algorithms

# Additional Utilities
pillow>=8.3.0          # Image processing
seaborn>=0.11.0        # Statistical data visualization
```

### Development Dependencies
```python
# Testing
pytest>=6.2.0          # Unit testing framework

# Code Quality
black>=21.0.0          # Code formatter
flake8>=3.9.0          # Linter

# Documentation
sphinx>=4.0.0          # Documentation generator
sphinx-rtd-theme>=0.5.0 # ReadTheDocs theme
```

## 🔧 Installation Guide

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ecg-biometric-encryption.git
cd ecg-biometric-encryption
```

### 2. Create Virtual Environment
```bash
# Using venv (recommended)
python -m venv ecg_env
source ecg_env/bin/activate  # Linux/macOS
ecg_env\Scripts\activate     # Windows

# Using conda
conda create -n ecg_env python=3.9
conda activate ecg_env
```

### 3. Install Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install core dependencies only
pip install numpy pandas matplotlib pyserial
```

### 4. Verify Installation
```bash
python -c "import numpy, pandas, matplotlib; print('Core dependencies installed successfully')"
```

## 🚀 Usage Instructions

### Basic Usage
```bash
# Run the main application
python src/ecg_gui_all.py

# Run security analysis
python src/brute_force_attack_comparison.py
```

### Configuration
1. **Data Loading**: Place `processed_data.csv` in the `data/` directory
2. **Serial Port**: Configure COM port settings in the GUI
3. **Parameters**: Adjust chaotic parameters in the encryption tab

### GUI Navigation
- **Dashboard**: System status and overview
- **Encryption**: Signal encryption/decryption controls
- **Security Analysis**: Security metrics and testing
- **Real-time Monitoring**: Live signal processing
- **Serial Communication**: Hardware interface

## 📊 Data Format Specifications

### Input Data Format
```csv
ecg_id,0.0,0.1,0.2,0.3,0.4,0.5,...
1,0.123,0.456,0.789,0.321,0.654,0.987,...
2,0.234,0.567,0.890,0.432,0.765,0.098,...
```

**Columns**:
- `ecg_id`: Unique identifier for each ECG recording
- `0.0, 0.1, 0.2, ...`: Time-sampled signal values (seconds)
- Signal values: Floating-point numbers representing amplitude

### Output Data Format
```json
{
  "encryption_results": {
    "method": "ML-Enhanced",
    "parameters": {
      "r": 3.847,
      "x0": 0.623,
      "alpha": 0.85,
      "eta": 0.01
    },
    "performance": {
      "encryption_time": 0.023,
      "entropy_improvement": 2.3,
      "security_score": 98.5
    }
  }
}
```

## 🔐 Security Specifications

### Encryption Algorithms
1. **Logistic Map**: Chaotic sequence generation
2. **Permutation**: Sample reordering using chaotic indices
3. **XOR Operation**: Signal modification with chaotic values

### Key Generation
- **Source**: ECG signal features (entropy, mean, std, peaks)
- **Length**: 128-bit equivalent
- **Uniqueness**: Each signal generates distinct keys
- **Randomness**: Validated through entropy analysis

### Security Metrics
- **Entropy**: Shannon entropy measurement
- **Correlation**: Pearson correlation coefficient
- **Uniformity**: Histogram distribution analysis
- **Attack Resistance**: Brute force and CPA testing

## 📈 Performance Specifications

### Processing Capabilities
- **Sampling Rate**: 500 Hz real-time processing
- **Latency**: < 50ms end-to-end encryption
- **Throughput**: 1000+ samples per second
- **Memory Usage**: < 100MB for 10-minute recordings

### Scalability
- **Signal Length**: 1000 - 100,000 samples
- **Batch Processing**: Up to 100 signals simultaneously
- **Real-time**: Continuous streaming support
- **Offline**: Batch file processing

## 🔌 Hardware Interface

### Serial Communication
- **Protocol**: RS-232/RS-485
- **Baud Rates**: 9600, 19200, 38400, 57600, 115200
- **Data Bits**: 7 or 8
- **Parity**: None, Even, Odd
- **Stop Bits**: 1, 1.5, 2

### ECG Module Support
- **Data Format**: Binary wave data (300 bytes per packet)
- **Markers**: 0xF8 (wave), 0xFA (pulse), 0xFB (info)
- **Sampling**: Continuous real-time acquisition
- **Compatibility**: Standard ECG modules

## 🧪 Testing Specifications

### Unit Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_encryption.py

# Run with coverage
pytest --cov=src tests/
```

### Integration Testing
- **Data Flow**: End-to-end signal processing
- **GUI Functionality**: User interface testing
- **Serial Communication**: Hardware interface testing
- **Performance**: Load and stress testing

### Security Testing
- **Entropy Analysis**: Randomness validation
- **Correlation Testing**: Security strength evaluation
- **Attack Simulation**: Brute force and CPA testing
- **Parameter Validation**: Key generation testing

## 📚 API Reference

### Core Functions
```python
# Signal Processing
extract_signal_features(signal)
butter_bandpass_filter(data, lowcut, highcut, fs, order=4)

# Encryption
chaotic_encrypt(signal, r, x0)
chaotic_decrypt(encrypted_signal, r, x0, perm_indices)
biometric_encrypt(signal, r, x0)
ml_enhanced_encrypt(signal, r, x0, alpha, eta)

# Security Analysis
calculate_entropy(signal)
analyze_correlation(original, encrypted)
perform_security_analysis(signal)
```

### Class Methods
```python
class ECGEncryptionGUI:
    def encrypt_signal(self)
    def decrypt_signal(self)
    def analyze_entropy(self)
    def generate_security_report(self)
    def start_monitoring(self)
    def connect_serial(self)
```

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt

# Or install specific package
pip install numpy pandas matplotlib
```

#### Serial Port Issues
- **Port Not Found**: Check device manager and refresh ports
- **Permission Denied**: Run as administrator (Windows)
- **Connection Failed**: Verify baud rate and settings

#### Performance Issues
- **Slow Processing**: Reduce signal length or sampling rate
- **High Memory Usage**: Process signals in smaller batches
- **GUI Lag**: Close unnecessary applications

#### Data Loading Errors
- **File Not Found**: Verify `processed_data.csv` location
- **Format Error**: Check CSV structure and data types
- **Memory Error**: Reduce file size or use data streaming

### Debug Mode
```bash
# Enable debug logging
python src/ecg_gui_all.py --debug

# Verbose output
python src/ecg_gui_all.py --verbose
```

## 📞 Support and Maintenance

### Getting Help
1. **Documentation**: Check this technical specification
2. **Issues**: Report bugs on GitHub
3. **Discussions**: Use GitHub Discussions
4. **Email**: Contact research team directly

### Maintenance
- **Updates**: Regular security and performance updates
- **Dependencies**: Monthly dependency updates
- **Testing**: Continuous integration testing
- **Documentation**: Regular documentation updates

---

*For technical support or feature requests, please create an issue on the GitHub repository.*
