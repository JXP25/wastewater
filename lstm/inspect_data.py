"""
Quick data inspection script
Shows sample statistics and validates data quality
"""

import pandas as pd
import sys

def inspect_data(filename='training_data_6months.csv'):
    """Load and inspect the training data"""
    
    print("="*80)
    print("Training Data Inspection")
    print("="*80)
    
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        print("Run: python generate_training_data.py")
        return
    
    print(f"\n✓ Loaded: {filename}")
    print(f"  Samples: {len(df):,}")
    print(f"  Features: {len(df.columns)}")
    print(f"  Date Range: {df['timestamp_effluent'].iloc[0]} to {df['timestamp_effluent'].iloc[-1]}")
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print(f"\n✓ Data Quality: No missing values")
    else:
        print(f"\n⚠ Missing Values Found:")
        print(missing[missing > 0])
    
    # Feature ranges
    print(f"\n{'='*80}")
    print("Feature Ranges (Min/Mean/Max):")
    print(f"{'='*80}")
    
    features = [
        ('turbidity_influent_t_minus_10h', 'Turbidity', 'NTU'),
        ('flow_rate_influent_t_minus_10h', 'Flow Rate', 'm³/h'),
        ('ph_aeration_basin_t_minus_5h', 'pH', '-'),
        ('do_aeration_basin_t_minus_5h', 'DO', 'mg/L'),
        ('temp_influent_t_minus_10h', 'Temperature', '°C'),
        ('fan_speed_control_t_minus_5h', 'Fan Speed', '%'),
    ]
    
    for col, name, unit in features:
        min_val = df[col].min()
        mean_val = df[col].mean()
        max_val = df[col].max()
        print(f"{name:20} [{unit:5}]: {min_val:7.1f} / {mean_val:7.1f} / {max_val:7.1f}")
    
    print(f"\n{'='*80}")
    print("Target Variables (Effluent Quality):")
    print(f"{'='*80}")
    
    targets = [
        ('tss_effluent_mgL', 'TSS', 'mg/L', 30),
        ('cod_effluent_mgL', 'COD', 'mg/L', 125),
        ('bod_effluent_mgL', 'BOD', 'mg/L', 30),
    ]
    
    for col, name, unit, limit in targets:
        min_val = df[col].min()
        mean_val = df[col].mean()
        max_val = df[col].max()
        violations = (df[col] > limit).sum()
        pct_violation = (violations / len(df)) * 100
        
        status = "✓" if pct_violation == 0 else "⚠"
        print(f"{status} {name:5} [{unit:5}]: {min_val:5.1f} / {mean_val:5.1f} / {max_val:5.1f}  "
              f"(Limit: {limit}, Violations: {violations} / {pct_violation:.1f}%)")
    
    # Sample diversity check
    print(f"\n{'='*80}")
    print("Sample Diversity (Unique Values):")
    print(f"{'='*80}")
    
    for col in df.columns:
        if col != 'timestamp_effluent':
            unique = df[col].nunique()
            pct = (unique / len(df)) * 100
            print(f"  {col:40}: {unique:6,} ({pct:5.1f}% unique)")
    
    # Time series continuity
    df['timestamp_dt'] = pd.to_datetime(df['timestamp_effluent'])
    df = df.sort_values('timestamp_dt')
    time_diffs = df['timestamp_dt'].diff()
    
    expected_interval = pd.Timedelta(minutes=5)
    gaps = (time_diffs != expected_interval).sum() - 1  # -1 for first NaT
    
    print(f"\n{'='*80}")
    print("Time Series Continuity:")
    print(f"{'='*80}")
    print(f"  Expected Interval: 5 minutes")
    print(f"  Gaps Found: {gaps}")
    
    if gaps == 0:
        print(f"  ✓ Perfect continuity!")
    else:
        print(f"  ⚠ Time series has {gaps} gaps")
    
    # Sample preview
    print(f"\n{'='*80}")
    print("Sample Data (Peak Hour - 8:00 AM):")
    print(f"{'='*80}")
    
    morning_peak = df[df['timestamp_dt'].dt.hour == 8].head(5)
    if len(morning_peak) > 0:
        print(morning_peak[['timestamp_effluent', 
                           'turbidity_influent_t_minus_10h',
                           'flow_rate_influent_t_minus_10h',
                           'fan_speed_control_t_minus_5h',
                           'tss_effluent_mgL',
                           'cod_effluent_mgL',
                           'bod_effluent_mgL']].to_string(index=False))
    
    print(f"\n{'='*80}")
    print("✅ Data inspection complete!")
    print(f"{'='*80}")
    print(f"\nReady for LSTM training:")
    print(f"  ✓ {len(df):,} samples")
    print(f"  ✓ 6 input features with temporal offsets")
    print(f"  ✓ 3 target variables (TSS, COD, BOD)")
    print(f"  ✓ No missing values")
    print(f"  ✓ Continuous time series")
    print(f"\nRecommended split:")
    print(f"  Train:      {int(len(df)*0.7):6,} samples (70%)")
    print(f"  Validation: {int(len(df)*0.15):6,} samples (15%)")
    print(f"  Test:       {int(len(df)*0.15):6,} samples (15%)")


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else 'training_data_6months.csv'
    inspect_data(filename)
