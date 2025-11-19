"""
LSTM Model Training for Wastewater Treatment Prediction
Predicts TSS, COD, and BOD from time-series sensor data
"""

import os
# Force CPU-only to avoid CuDNN/CUDA mismatches during training
# (set before importing TensorFlow so TF won't initialize GPUs)
os.environ.setdefault('CUDA_VISIBLE_DEVICES', '')
print("INFO: Forcing TensorFlow to CPU by setting CUDA_VISIBLE_DEVICES=''")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json
from datetime import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
DATA_FILE = 'training_data_6months.csv'
MODEL_SAVE_PATH = 'model/wtp_lstm_model.keras'
SCALER_SAVE_PATH = 'model/scalers.npz'
HISTORY_SAVE_PATH = 'model/training_history.json'
PLOTS_DIR = 'plots/'

# LSTM Hyperparameters
TIME_STEPS = 120      # Look back 10 hours (120 samples × 5 min = 600 min = 10 hours)
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001
VALIDATION_SPLIT = 0.15

# Features (Inputs) - These match your specific lagged columns
FEATURE_COLS = [
    'turbidity_influent_t_minus_10h',
    'flow_rate_influent_t_minus_10h',
    'ph_aeration_basin_t_minus_5h',
    'do_aeration_basin_t_minus_5h',
    'temp_influent_t_minus_10h',
    'fan_speed_control_t_minus_5h'
]

# Targets (Outputs)
TARGET_COLS = [
    'tss_effluent_mgL',
    'cod_effluent_mgL',
    'bod_effluent_mgL'
]

# ==========================================
# 2. SETUP
# ==========================================
def setup_directories():
    """Create necessary directories for saving outputs"""
    os.makedirs('model', exist_ok=True)
    os.makedirs('plots', exist_ok=True)
    print("✓ Directories created")

# ==========================================
# 3. DATA PREPROCESSING
# ==========================================
def load_and_preprocess_data():
    """Load and preprocess the training data"""
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"Data file '{DATA_FILE}' not found!\n"
            f"Please run: python generate_training_data.py"
        )
    
    # Load Data
    print(f"\nLoading data from {DATA_FILE}...")
    df = pd.read_csv(DATA_FILE)
    df['timestamp_effluent'] = pd.to_datetime(df['timestamp_effluent'])
    df = df.sort_values('timestamp_effluent')
    
    print(f"✓ Data loaded: {len(df):,} samples")
    print(f"  Date range: {df['timestamp_effluent'].min()} to {df['timestamp_effluent'].max()}")
    print(f"  Features: {len(FEATURE_COLS)}")
    print(f"  Targets: {len(TARGET_COLS)}")
    
    # Split into Features (X) and Targets (y)
    X_raw = df[FEATURE_COLS].values
    y_raw = df[TARGET_COLS].values
    timestamps = df['timestamp_effluent'].values
    
    # Check for any NaN or Inf values
    if np.any(np.isnan(X_raw)) or np.any(np.isnan(y_raw)):
        raise ValueError("Data contains NaN values!")
    if np.any(np.isinf(X_raw)) or np.any(np.isinf(y_raw)):
        raise ValueError("Data contains Inf values!")
    
    # Scaling (Crucial for LSTMs)
    # We use separate scalers for X and y so we can inverse_transform predictions later
    print("\nScaling data...")
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    
    X_scaled = scaler_X.fit_transform(X_raw)
    y_scaled = scaler_y.fit_transform(y_raw)
    
    print(f"✓ Data scaled to [0, 1] range")
    
    return X_scaled, y_scaled, scaler_X, scaler_y, timestamps

def create_sequences(X, y, time_steps=1):
    """
    Converts flat data into 3D sequences for LSTM.
    
    Parameters:
    - X: Feature array (Samples, Features)
    - y: Target array (Samples, Targets)
    - time_steps: Number of historical timesteps to use
    
    Returns:
    - X_seq: (Samples, TimeSteps, Features)
    - y_seq: (Samples, Targets)
    """
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        v = X[i:(i + time_steps)]
        Xs.append(v)
        ys.append(y[i + time_steps])
    return np.array(Xs), np.array(ys)

def split_train_val_test(X_seq, y_seq, train_ratio=0.70, val_ratio=0.15):
    """
    Split time-series data temporally (no shuffling)
    
    Returns:
    - X_train, y_train: Training set (70%)
    - X_val, y_val: Validation set (15%)
    - X_test, y_test: Test set (15%)
    """
    n = len(X_seq)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    X_train = X_seq[:train_end]
    y_train = y_seq[:train_end]
    
    X_val = X_seq[train_end:val_end]
    y_val = y_seq[train_end:val_end]
    
    X_test = X_seq[val_end:]
    y_test = y_seq[val_end:]
    
    return X_train, y_train, X_val, y_val, X_test, y_test

# ==========================================
# 4. MODEL DEFINITION
# ==========================================
def build_lstm_model(input_shape, output_units):
    """
    Build LSTM model for multi-output time-series prediction
    
    Architecture:
    - LSTM Layer 1: 64 units with return sequences
    - Dropout: 0.2
    - LSTM Layer 2: 32 units
    - Dropout: 0.2
    - Dense: 16 units (ReLU)
    - Output: 3 units (TSS, COD, BOD)
    """
    model = tf.keras.Sequential([
        # 1st LSTM Layer
        tf.keras.layers.LSTM(
            64, 
            return_sequences=True, 
            input_shape=input_shape,
            name='lstm_1'
        ),
        tf.keras.layers.Dropout(0.2, name='dropout_1'),
        
        # 2nd LSTM Layer
        tf.keras.layers.LSTM(
            32, 
            return_sequences=False,
            name='lstm_2'
        ),
        tf.keras.layers.Dropout(0.2, name='dropout_2'),
        
        # Dense Layers for Output
        tf.keras.layers.Dense(16, activation='relu', name='dense_1'),
        
        # Output Layer (3 units for TSS, COD, BOD)
        tf.keras.layers.Dense(output_units, name='output')
    ])
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE)
    model.compile(
        optimizer=optimizer,
        loss='mse',
        metrics=['mae', 'mape']  # Mean Absolute Error, Mean Absolute Percentage Error
    )
    
    return model

# ==========================================
# 5. TRAINING CALLBACKS
# ==========================================
def create_callbacks():
    """Create training callbacks for model checkpointing and early stopping"""
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        ),
        tf.keras.callbacks.ModelCheckpoint(
            'model/best_model.keras',
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]
    return callbacks

# ==========================================
# 6. EVALUATION & VISUALIZATION
# ==========================================
def plot_training_history(history):
    """Plot training and validation loss"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Loss
    axes[0].plot(history.history['loss'], label='Train Loss', linewidth=2)
    axes[0].plot(history.history['val_loss'], label='Val Loss', linewidth=2)
    axes[0].set_title('Model Training Loss (MSE)', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Epochs')
    axes[0].set_ylabel('Loss (MSE)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # MAE
    axes[1].plot(history.history['mae'], label='Train MAE', linewidth=2)
    axes[1].plot(history.history['val_mae'], label='Val MAE', linewidth=2)
    axes[1].set_title('Mean Absolute Error', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Epochs')
    axes[1].set_ylabel('MAE')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{PLOTS_DIR}training_history.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved training history plot: {PLOTS_DIR}training_history.png")
    plt.close()

def plot_predictions(y_actual, y_pred, dataset_name='Test'):
    """Plot actual vs predicted values for all targets"""
    target_names = ['TSS', 'COD', 'BOD']
    
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    
    # Limit to first 500 samples for visibility
    n_samples = min(500, len(y_actual))
    
    for idx, (ax, name) in enumerate(zip(axes, target_names)):
        ax.plot(y_actual[:n_samples, idx], label=f'Actual {name}', 
                color='blue', alpha=0.7, linewidth=2)
        ax.plot(y_pred[:n_samples, idx], label=f'Predicted {name}', 
                color='red', linestyle='--', alpha=0.8, linewidth=2)
        ax.set_title(f'{name} Prediction Results ({dataset_name} Set)', 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel('Time Steps (5 min intervals)')
        ax.set_ylabel(f'{name} (mg/L)')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{PLOTS_DIR}predictions_{dataset_name.lower()}.png', 
                dpi=300, bbox_inches='tight')
    print(f"✓ Saved prediction plots: {PLOTS_DIR}predictions_{dataset_name.lower()}.png")
    plt.close()

def evaluate_model(y_actual, y_pred, dataset_name='Test'):
    """Calculate and print evaluation metrics"""
    target_names = ['TSS', 'COD', 'BOD']
    
    print(f"\n{'='*70}")
    print(f"{dataset_name} Set Evaluation Metrics")
    print(f"{'='*70}")
    
    metrics_dict = {}
    
    for idx, name in enumerate(target_names):
        rmse = np.sqrt(mean_squared_error(y_actual[:, idx], y_pred[:, idx]))
        mae = mean_absolute_error(y_actual[:, idx], y_pred[:, idx])
        r2 = r2_score(y_actual[:, idx], y_pred[:, idx])
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_actual[:, idx] - y_pred[:, idx]) / y_actual[:, idx])) * 100
        
        metrics_dict[name] = {
            'RMSE': float(rmse),
            'MAE': float(mae),
            'R2': float(r2),
            'MAPE': float(mape)
        }
        
        print(f"\n{name}:")
        print(f"  RMSE: {rmse:.3f} mg/L")
        print(f"  MAE:  {mae:.3f} mg/L")
        print(f"  R²:   {r2:.4f}")
        print(f"  MAPE: {mape:.2f}%")
    
    return metrics_dict

def save_training_info(history, metrics_train, metrics_val, metrics_test, scalers):
    """Save training information and metadata"""
    info = {
        'training_date': datetime.now().isoformat(),
        'model_architecture': {
            'time_steps': TIME_STEPS,
            'batch_size': BATCH_SIZE,
            'epochs': EPOCHS,
            'learning_rate': LEARNING_RATE
        },
        'features': FEATURE_COLS,
        'targets': TARGET_COLS,
        'final_loss': float(history.history['loss'][-1]),
        'final_val_loss': float(history.history['val_loss'][-1]),
        'metrics': {
            'train': metrics_train,
            'validation': metrics_val,
            'test': metrics_test
        }
    }
    
    with open(HISTORY_SAVE_PATH, 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"\n✓ Saved training info: {HISTORY_SAVE_PATH}")
    
    # Save scalers
    np.savez(SCALER_SAVE_PATH,
             scaler_X_min=scalers[0].data_min_,
             scaler_X_max=scalers[0].data_max_,
             scaler_y_min=scalers[1].data_min_,
             scaler_y_max=scalers[1].data_max_)
    
    print(f"✓ Saved scalers: {SCALER_SAVE_PATH}")

# ==========================================
# 7. MAIN EXECUTION
# ==========================================
def main():
    print("="*70)
    print("LSTM Model Training - Wastewater Treatment Prediction")
    print("="*70)
    
    # Setup
    setup_directories()
    
    # A. Load & Preprocess
    X_scaled, y_scaled, scaler_X, scaler_y, timestamps = load_and_preprocess_data()
    
    # B. Create Sequences
    print(f"\nCreating sequences with time_steps={TIME_STEPS} (10 hours)...")
    X_seq, y_seq = create_sequences(X_scaled, y_scaled, TIME_STEPS)
    print(f"✓ X Sequence Shape: {X_seq.shape} (Samples, TimeSteps, Features)")
    print(f"✓ y Sequence Shape: {y_seq.shape} (Samples, Targets)")
    
    # C. Train/Val/Test Split
    print("\nSplitting data...")
    X_train, y_train, X_val, y_val, X_test, y_test = split_train_val_test(X_seq, y_seq)
    
    print(f"✓ Training Samples:   {len(X_train):,} (70%)")
    print(f"✓ Validation Samples: {len(X_val):,} (15%)")
    print(f"✓ Testing Samples:    {len(X_test):,} (15%)")
    
    # D. Build Model
    print("\nBuilding LSTM model...")
    model = build_lstm_model((X_train.shape[1], X_train.shape[2]), y_train.shape[1])
    model.summary()
    
    # E. Train Model
    print(f"\n{'='*70}")
    print("Starting Training...")
    print(f"{'='*70}")
    
    callbacks = create_callbacks()
    
    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        shuffle=False,  # Maintain temporal order
        verbose=1
    )
    
    # F. Save Model
    model.save(MODEL_SAVE_PATH)
    print(f"\n✓ Model saved to {MODEL_SAVE_PATH}")
    
    # G. Visualize Training
    print("\nGenerating training visualizations...")
    plot_training_history(history)
    
    # H. Evaluate on All Sets
    print("\nEvaluating model performance...")
    
    # Training set
    y_train_pred_scaled = model.predict(X_train, verbose=0)
    y_train_pred = scaler_y.inverse_transform(y_train_pred_scaled)
    y_train_actual = scaler_y.inverse_transform(y_train)
    metrics_train = evaluate_model(y_train_actual, y_train_pred, 'Training')
    
    # Validation set
    y_val_pred_scaled = model.predict(X_val, verbose=0)
    y_val_pred = scaler_y.inverse_transform(y_val_pred_scaled)
    y_val_actual = scaler_y.inverse_transform(y_val)
    metrics_val = evaluate_model(y_val_actual, y_val_pred, 'Validation')
    
    # Test set
    y_test_pred_scaled = model.predict(X_test, verbose=0)
    y_test_pred = scaler_y.inverse_transform(y_test_pred_scaled)
    y_test_actual = scaler_y.inverse_transform(y_test)
    metrics_test = evaluate_model(y_test_actual, y_test_pred, 'Test')
    
    # I. Generate Prediction Plots
    print("\nGenerating prediction visualizations...")
    plot_predictions(y_test_actual, y_test_pred, 'Test')
    
    # J. Save Training Info
    save_training_info(history, metrics_train, metrics_val, metrics_test, 
                      (scaler_X, scaler_y))
    
    # K. Final Summary
    print(f"\n{'='*70}")
    print("✅ Training Complete!")
    print(f"{'='*70}")
    print(f"\nModel Performance Summary (Test Set):")
    print(f"  TSS - R²: {metrics_test['TSS']['R2']:.4f}, MAE: {metrics_test['TSS']['MAE']:.3f} mg/L")
    print(f"  COD - R²: {metrics_test['COD']['R2']:.4f}, MAE: {metrics_test['COD']['MAE']:.3f} mg/L")
    print(f"  BOD - R²: {metrics_test['BOD']['R2']:.4f}, MAE: {metrics_test['BOD']['MAE']:.3f} mg/L")
    
    print(f"\nSaved Files:")
    print(f"  Model:    {MODEL_SAVE_PATH}")
    print(f"  Scalers:  {SCALER_SAVE_PATH}")
    print(f"  History:  {HISTORY_SAVE_PATH}")
    print(f"  Plots:    {PLOTS_DIR}")
    
    print(f"\n{'='*70}")
    print("Model is ready for deployment! 🚀")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
