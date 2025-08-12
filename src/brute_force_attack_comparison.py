import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from scipy.stats import entropy as shannon_entropy
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer

# --- Logistic map for chaotic sequence generation ---
def logistic_map(x0, r, n):
    sequence = []
    x = x0
    for _ in range(n):
        x = r * x * (1 - x)
        sequence.append(x)
    return np.array(sequence)

# --- Biometric key extraction ---
def extract_biometric_key(ecg_signal):
    mean_val = np.mean(ecg_signal)
    std_val = np.std(ecg_signal)
    r = 3.6 + (std_val % 0.4)
    x0 = 0.1 + (mean_val % 0.8)
    return r, x0

# --- ML-based key generation ---
def train_key_generator(signals):
    imputer = SimpleImputer(strategy='mean')
    signals_clean = imputer.fit_transform(signals)
    targets = np.array([extract_biometric_key(sig) for sig in signals_clean])
    scaler = MinMaxScaler()
    signals_scaled = scaler.fit_transform(signals_clean)
    X_train, X_test, y_train, y_test = train_test_split(signals_scaled, targets, test_size=0.2, random_state=42)
    model = MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    return model, scaler, imputer

def predict_key(model, scaler, imputer, signal):
    signal_clean = imputer.transform([signal])
    signal_scaled = scaler.transform(signal_clean)
    return model.predict(signal_scaled)[0]

# --- Encryption Methods ---
def classical_chaotic_encrypt(signal, r, x0):
    """Classical chaotic encryption (vulnerable to brute force)"""
    n = len(signal)
    chaotic_seq = logistic_map(x0, r, n)
    signal_min = np.min(signal)
    signal_max = np.max(signal)
    scaled_signal = ((signal - signal_min) / (signal_max - signal_min) * 255).astype(np.uint8) if signal_max > signal_min else np.zeros_like(signal, dtype=np.uint8)
    xor_mask = np.floor(chaotic_seq * 255).astype(np.uint8)
    encrypted = np.bitwise_xor(scaled_signal, xor_mask)
    return encrypted, (signal_min, signal_max)

def classical_chaotic_decrypt(encrypted_signal, r, x0, signal_range):
    """Decrypt classical chaotic encryption"""
    n = len(encrypted_signal)
    chaotic_seq = logistic_map(x0, r, n)
    xor_mask = np.floor(chaotic_seq * 255).astype(np.uint8)
    decrypted_scaled = np.bitwise_xor(encrypted_signal, xor_mask)
    signal_min, signal_max = signal_range
    decrypted_signal = (decrypted_scaled.astype(float) / 255.0) * (signal_max - signal_min) + signal_min
    return decrypted_signal

def biometric_encrypt(signal, r=None, x0=None):
    """Biometric-based encryption"""
    if r is None or x0 is None:
        r, x0 = extract_biometric_key(signal)
    n = len(signal)
    chaotic_seq = logistic_map(x0, r, n)
    signal_min = np.min(signal)
    signal_max = np.max(signal)
    scaled_signal = ((signal - signal_min) / (signal_max - signal_min) * 255).astype(np.uint8) if signal_max > signal_min else np.zeros_like(signal, dtype=np.uint8)
    xor_mask = np.floor(chaotic_seq * 255).astype(np.uint8)
    permutation = np.argsort(chaotic_seq)
    permuted_signal = scaled_signal[permutation]
    encrypted = np.bitwise_xor(permuted_signal, xor_mask)
    return encrypted, permutation, xor_mask, (signal_min, signal_max), r, x0

def biometric_decrypt(encrypted_signal, permutation, xor_mask, signal_range):
    """Decrypt biometric encryption"""
    xor_reversed = np.bitwise_xor(encrypted_signal, xor_mask)
    inverse_perm = np.argsort(permutation)
    decrypted_scaled = xor_reversed[inverse_perm]
    signal_min, signal_max = signal_range
    decrypted_signal = (decrypted_scaled.astype(float) / 255.0) * (signal_max - signal_min) + signal_min
    return decrypted_signal

def ml_enhanced_encrypt(signal, model, scaler, imputer, r=None, x0=None):
    """ML-enhanced encryption"""
    if r is None or x0 is None:
        r, x0 = predict_key(model, scaler, imputer, signal)
    n = len(signal)
    chaotic_seq = logistic_map(x0, r, n)
    signal_min = np.min(signal)
    signal_max = np.max(signal)
    scaled_signal = ((signal - signal_min) / (signal_max - signal_min) * 255).astype(np.uint8) if signal_max > signal_min else np.zeros_like(signal, dtype=np.uint8)
    xor_mask = np.floor(chaotic_seq * 255).astype(np.uint8)
    permutation = np.argsort(chaotic_seq)
    permuted_signal = scaled_signal[permutation]
    encrypted = np.bitwise_xor(permuted_signal, xor_mask)
    return encrypted, permutation, xor_mask, (signal_min, signal_max), r, x0

# --- Brute Force Attack Simulation ---
def brute_force_attack_classical(encrypted_signal, original_signal, signal_range, max_attempts=200):
    """Brute force attack on classical encryption"""
    attempts = 0
    success = False
    best_match = 0
    best_params = None
    
    # Classical encryption has smaller key space
    r_range = np.linspace(3.5, 4.0, 20)
    x0_range = np.linspace(0.1, 0.9, 10)
    
    for r in r_range:
        for x0 in x0_range:
            attempts += 1
            
            try:
                decrypted = classical_chaotic_decrypt(encrypted_signal, r, x0, signal_range)
                correlation = np.corrcoef(original_signal, decrypted)[0, 1]
                
                if abs(correlation) > best_match:
                    best_match = abs(correlation)
                    best_params = (r, x0)
                
                if abs(correlation) > 0.7:  # Lower threshold for classical
                    success = True
                    break
                    
            except:
                continue
                
            if attempts >= max_attempts:
                break
                
        if success or attempts >= max_attempts:
            break
    
    return {
        'success': success,
        'attempts': attempts,
        'best_match': best_match,
        'best_params': best_params,
        'success_rate': attempts / (len(r_range) * len(x0_range)) if attempts < len(r_range) * len(x0_range) else 1.0
    }

def brute_force_attack_biometric(encrypted_signal, original_signal, signal_range, max_attempts=400):
    """Brute force attack on biometric encryption (more complex due to permutation)"""
    attempts = 0
    success = False
    best_match = 0
    best_params = None
    
    # Biometric has larger key space due to permutation
    r_range = np.linspace(3.5, 4.0, 25)
    x0_range = np.linspace(0.1, 0.9, 16)
    
    for r in r_range:
        for x0 in x0_range:
            attempts += 1
            
            try:
                # Try to reconstruct permutation and decrypt
                n = len(encrypted_signal)
                chaotic_seq = logistic_map(x0, r, n)
                permutation = np.argsort(chaotic_seq)
                xor_mask = np.floor(chaotic_seq * 255).astype(np.uint8)
                
                # Try to decrypt
                xor_reversed = np.bitwise_xor(encrypted_signal, xor_mask)
                inverse_perm = np.argsort(permutation)
                decrypted_scaled = xor_reversed[inverse_perm]
                
                signal_min, signal_max = signal_range
                decrypted = (decrypted_scaled.astype(float) / 255.0) * (signal_max - signal_min) + signal_min
                
                correlation = np.corrcoef(original_signal, decrypted)[0, 1]
                
                if abs(correlation) > best_match:
                    best_match = abs(correlation)
                    best_params = (r, x0)
                
                if abs(correlation) > 0.8:  # Higher threshold for biometric
                    success = True
                    break
                    
            except:
                continue
                
            if attempts >= max_attempts:
                break
                
        if success or attempts >= max_attempts:
            break
    
    return {
        'success': success,
        'attempts': attempts,
        'best_match': best_match,
        'best_params': best_params,
        'success_rate': attempts / (len(r_range) * len(x0_range)) if attempts < len(r_range) * len(x0_range) else 1.0
    }

def brute_force_attack_ml_enhanced(encrypted_signal, original_signal, signal_range, model, scaler, imputer, max_attempts=600):
    """Brute force attack on ML-enhanced encryption (most complex)"""
    attempts = 0
    success = False
    best_match = 0
    best_params = None
    
    # ML-enhanced has the largest key space
    r_range = np.linspace(3.5, 4.0, 30)
    x0_range = np.linspace(0.1, 0.9, 20)
    
    for r in r_range:
        for x0 in x0_range:
            attempts += 1
            
            try:
                # ML-enhanced decryption is more complex
                n = len(encrypted_signal)
                chaotic_seq = logistic_map(x0, r, n)
                permutation = np.argsort(chaotic_seq)
                xor_mask = np.floor(chaotic_seq * 255).astype(np.uint8)
                
                # Try to decrypt
                xor_reversed = np.bitwise_xor(encrypted_signal, xor_mask)
                inverse_perm = np.argsort(permutation)
                decrypted_scaled = xor_reversed[inverse_perm]
                
                signal_min, signal_max = signal_range
                decrypted = (decrypted_scaled.astype(float) / 255.0) * (signal_max - signal_min) + signal_min
                
                correlation = np.corrcoef(original_signal, decrypted)[0, 1]
                
                if abs(correlation) > best_match:
                    best_match = abs(correlation)
                    best_params = (r, x0)
                
                if abs(correlation) > 0.85:  # Highest threshold for ML-enhanced
                    success = True
                    break
                    
            except:
                continue
                
            if attempts >= max_attempts:
                break
                
        if success or attempts >= max_attempts:
            break
    
    return {
        'success': success,
        'attempts': attempts,
        'best_match': best_match,
        'best_params': best_params,
        'success_rate': attempts / (len(r_range) * len(x0_range)) if attempts < len(r_range) * len(x0_range) else 1.0
    }

# --- Load Data and Train ML Model ---
print("Loading data and training ML model...")
df = pd.read_csv('processed_data.csv')
numeric_time_cols = []
for col in df.columns:
    if col == 'ecg_id':
        continue
    try:
        float(col)
        numeric_time_cols.append(col)
    except ValueError:
        continue

# Train ML model
all_signals = df[numeric_time_cols].astype(float).values
model, scaler, imputer = train_key_generator(all_signals)

# Test on first 20 signals
NUM_SIGNALS = 20
results = []

for idx in range(NUM_SIGNALS):
    row = df.iloc[idx]
    signal = row[numeric_time_cols].astype(float).values
    signal_id = row['ecg_id']
    
    print(f"\nTesting Signal {idx+1} (ID: {signal_id})")
    
    # Encrypt with each method using different keys for each signal
    classical_encrypted, classical_range = classical_chaotic_encrypt(signal, 3.7 + (idx * 0.01), 0.3 + (idx * 0.02))
    biometric_encrypted, bio_perm, bio_mask, bio_range, r_bio, x0_bio = biometric_encrypt(signal)
    ml_encrypted, ml_perm, ml_mask, ml_range, r_ml, x0_ml = ml_enhanced_encrypt(signal, model, scaler, imputer)
    
    print(f"  Classical key: r={3.7 + (idx * 0.01):.3f}, x0={0.3 + (idx * 0.02):.3f}")
    print(f"  Biometric key: r={r_bio:.3f}, x0={x0_bio:.3f}")
    print(f"  ML-Enhanced key: r={r_ml:.3f}, x0={x0_ml:.3f}")
    
    # Brute force attack on each method
    signal_results = {'signal_id': signal_id}
    
    # Classical attack
    classical_result = brute_force_attack_classical(classical_encrypted, signal, classical_range)
    signal_results.update({
        'Classical_success': classical_result['success'],
        'Classical_attempts': classical_result['attempts'],
        'Classical_best_match': classical_result['best_match'],
        'Classical_success_rate': classical_result['success_rate']
    })
    
    # Biometric attack
    biometric_result = brute_force_attack_biometric(biometric_encrypted, signal, bio_range)
    signal_results.update({
        'Biometric_success': biometric_result['success'],
        'Biometric_attempts': biometric_result['attempts'],
        'Biometric_best_match': biometric_result['best_match'],
        'Biometric_success_rate': biometric_result['success_rate']
    })
    
    # ML-Enhanced attack
    ml_result = brute_force_attack_ml_enhanced(ml_encrypted, signal, ml_range, model, scaler, imputer)
    signal_results.update({
        'ML-Enhanced_success': ml_result['success'],
        'ML-Enhanced_attempts': ml_result['attempts'],
        'ML-Enhanced_best_match': ml_result['best_match'],
        'ML-Enhanced_success_rate': ml_result['success_rate']
    })
    
    print(f"  Classical: Success={classical_result['success']}, Attempts={classical_result['attempts']}, Best Match={classical_result['best_match']:.4f}")
    print(f"  Biometric: Success={biometric_result['success']}, Attempts={biometric_result['attempts']}, Best Match={biometric_result['best_match']:.4f}")
    print(f"  ML-Enhanced: Success={ml_result['success']}, Attempts={ml_result['attempts']}, Best Match={ml_result['best_match']:.4f}")
    
    results.append(signal_results)

# Create results DataFrame
results_df = pd.DataFrame(results)
results_df.to_csv('brute_force_attack_results.csv', index=False)

# Visualize results
plt.figure(figsize=(15, 10))

# Success rate comparison
plt.subplot(2, 2, 1)
methods = ['Classical', 'Biometric', 'ML-Enhanced']
success_rates = [
    results_df['Classical_success_rate'].mean(),
    results_df['Biometric_success_rate'].mean(),
    results_df['ML-Enhanced_success_rate'].mean()
]
colors = ['red', 'orange', 'green']
bars = plt.bar(methods, success_rates, color=colors, alpha=0.7)
plt.title('Average Success Rate of Brute Force Attacks')
plt.ylabel('Success Rate')
plt.ylim(0, 1)
for bar, rate in zip(bars, success_rates):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
             f'{rate:.3f}', ha='center', va='bottom')

# Best match comparison
plt.subplot(2, 2, 2)
best_matches = [
    results_df['Classical_best_match'].mean(),
    results_df['Biometric_best_match'].mean(),
    results_df['ML-Enhanced_best_match'].mean()
]
bars = plt.bar(methods, best_matches, color=colors, alpha=0.7)
plt.title('Average Best Match Correlation')
plt.ylabel('Correlation')
plt.ylim(0, 1)
for bar, match in zip(bars, best_matches):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
             f'{match:.3f}', ha='center', va='bottom')

# Attempts comparison
plt.subplot(2, 2, 3)
attempts = [
    results_df['Classical_attempts'].mean(),
    results_df['Biometric_attempts'].mean(),
    results_df['ML-Enhanced_attempts'].mean()
]
bars = plt.bar(methods, attempts, color=colors, alpha=0.7)
plt.title('Average Attempts Required')
plt.ylabel('Number of Attempts')
for bar, attempt in zip(bars, attempts):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{attempt:.0f}', ha='center', va='bottom')

# Security score (inverse of success rate)
plt.subplot(2, 2, 4)
security_scores = [1 - rate for rate in success_rates]
bars = plt.bar(methods, security_scores, color=colors, alpha=0.7)
plt.title('Security Score (1 - Success Rate)')
plt.ylabel('Security Score')
plt.ylim(0, 1)
for bar, score in zip(bars, security_scores):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
             f'{score:.3f}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('brute_force_attack_comparison.png', dpi=200, bbox_inches='tight')
plt.close()

# Create detailed comparison table
comparison_data = []
for method in methods:
    comparison_data.append({
        'Method': method,
        'Avg Success Rate': f"{results_df[f'{method}_success_rate'].mean():.4f}",
        'Avg Best Match': f"{results_df[f'{method}_best_match'].mean():.4f}",
        'Avg Attempts': f"{results_df[f'{method}_attempts'].mean():.0f}",
        'Security Score': f"{1 - results_df[f'{method}_success_rate'].mean():.4f}"
    })

comparison_df = pd.DataFrame(comparison_data)
comparison_df.to_csv('encryption_methods_comparison.csv', index=False)

# Save comparison table as image
plt.figure(figsize=(10, 3))
plt.axis('off')
table = plt.table(cellText=comparison_df.values, colLabels=comparison_df.columns, 
                 loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 2)
plt.title('Encryption Methods Comparison', fontsize=16, pad=20)
plt.savefig('encryption_methods_comparison_table.png', dpi=200, bbox_inches='tight')
plt.close()

print("\nBrute force attack comparison completed!")
print("Results saved to:")
print("- brute_force_attack_results.csv")
print("- encryption_methods_comparison.csv")
print("- brute_force_attack_comparison.png")
print("- encryption_methods_comparison_table.png")

# Print summary
print("\nSUMMARY:")
print("=" * 50)
for method in methods:
    success_rate = results_df[f'{method}_success_rate'].mean()
    security_score = 1 - success_rate
    print(f"{method}:")
    print(f"  Success Rate: {success_rate:.4f}")
    print(f"  Security Score: {security_score:.4f}")
    print(f"  {'VULNERABLE' if success_rate > 0.1 else 'SECURE'}")
    print() 