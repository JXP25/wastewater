"""
Historical Training Data Generator for LSTM Model
Generates realistic wastewater treatment data with temporal offsets and correlations
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random


class HistoricalDataGenerator:
    """
    Generates historical wastewater treatment data with:
    - Temporal offsets (10h for influent sensors, 5h for aeration basin)
    - Realistic correlations between inputs and effluent quality
    - Daily and weekly patterns
    - Seasonal variations
    """
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_base_influent_pattern(self, timestamps):
        """Generate base influent patterns with daily and weekly cycles"""
        patterns = []
        
        for ts in timestamps:
            hour = ts.hour
            day_of_week = ts.weekday()  # 0=Monday, 6=Sunday
            
            # Daily pattern (morning and evening peaks)
            if 6 <= hour <= 9:  # Morning peak
                daily_factor = 1.4
            elif 17 <= hour <= 20:  # Evening peak
                daily_factor = 1.5
            elif 23 <= hour or hour <= 5:  # Night low
                daily_factor = 0.6
            else:
                daily_factor = 1.0
            
            # Weekly pattern (lower on weekends)
            if day_of_week >= 5:  # Saturday or Sunday
                weekly_factor = 0.8
            else:
                weekly_factor = 1.0
            
            patterns.append(daily_factor * weekly_factor)
        
        return np.array(patterns)
    
    def generate_influent_data(self, timestamps, base_turbidity=55.0, base_flow=500.0):
        """Generate influent sensor data with realistic patterns"""
        n = len(timestamps)
        patterns = self.generate_base_influent_pattern(timestamps)
        
        # Turbidity (NTU) - correlates with organic load
        turbidity = base_turbidity * patterns
        turbidity += np.random.normal(0, 3.5, n)  # Noise
        turbidity += np.cumsum(np.random.normal(0, 0.1, n))  # Drift
        turbidity = np.clip(turbidity, 10, 150)
        
        # Flow rate (m³/h) - follows similar pattern
        flow_rate = base_flow * patterns
        flow_rate += np.random.normal(0, 30, n)
        flow_rate += np.cumsum(np.random.normal(0, 0.5, n))
        flow_rate = np.clip(flow_rate, 100, 1200)
        
        # Temperature (°C) - slower variation, some correlation with time of day
        temp_base = 20.0 + 2.0 * np.sin(2 * np.pi * np.arange(n) / (24 * 12))  # Daily cycle
        temperature = temp_base + np.random.normal(0, 1.0, n)
        temperature = np.clip(temperature, 15, 25)
        
        return turbidity, flow_rate, temperature
    
    def generate_aeration_basin_data(self, timestamps, turbidity_influent, flow_rate_influent):
        """Generate aeration basin sensor data (5h after influent)"""
        n = len(timestamps)
        
        # pH - relatively stable, slight response to load
        load_factor = (turbidity_influent / 55.0) * (flow_rate_influent / 500.0)
        ph = 7.25 + 0.05 * (load_factor - 1.0)
        ph += np.random.normal(0, 0.08, n)
        ph = np.clip(ph, 6.8, 7.6)
        
        # Dissolved Oxygen (mg/L) - inversely related to load (more load = more O2 consumed)
        do = 2.5 - 0.3 * (load_factor - 1.0)
        do += np.random.normal(0, 0.15, n)
        do = np.clip(do, 0.5, 4.0)
        
        return ph, do
    
    def generate_control_actions(self, timestamps, turbidity_influent, flow_rate_influent, do):
        """Generate control actions (fan speed responds to load and DO)"""
        n = len(timestamps)
        
        # Fan speed (%) - operators increase speed when load is high or DO is low
        load_factor = (turbidity_influent / 55.0) * (flow_rate_influent / 500.0)
        do_factor = 2.5 / do  # Lower DO needs more aeration
        
        fan_speed = 65.0 * load_factor * (do_factor ** 0.3)
        fan_speed += np.random.normal(0, 3, n)  # Operator adjustments
        fan_speed = np.clip(fan_speed, 40, 95)
        
        return fan_speed
    
    def calculate_effluent_quality(self, turbidity_influent, flow_rate_influent, 
                                   ph, do, fan_speed, temp):
        """
        Calculate effluent quality (TSS, COD, BOD) based on process parameters
        Key relationships:
        - Higher influent load (turbidity × flow) → higher effluent values
        - Better aeration (higher fan speed, optimal DO) → lower effluent values
        - pH stability → better treatment
        - Temperature affects biological activity
        """
        n = len(turbidity_influent)
        
        # Influent load indicator
        load = (turbidity_influent / 55.0) * (flow_rate_influent / 500.0)
        
        # Treatment efficiency factors
        aeration_efficiency = (fan_speed / 65.0) * (do / 2.5)
        ph_efficiency = 1.0 - 0.3 * np.abs(ph - 7.25)
        temp_efficiency = 0.7 + 0.3 * (temp - 15.0) / 10.0  # Better at higher temps
        
        overall_efficiency = aeration_efficiency * ph_efficiency * temp_efficiency
        overall_efficiency = np.clip(overall_efficiency, 0.4, 1.6)
        
        # TSS (Total Suspended Solids) - mg/L
        # Base removal: 95% under optimal conditions
        tss_influent = turbidity_influent * 1.8  # Rough correlation
        removal_rate_tss = 0.95 * overall_efficiency
        removal_rate_tss = np.clip(removal_rate_tss, 0.85, 0.98)
        
        tss_effluent = tss_influent * (1 - removal_rate_tss)
        tss_effluent += np.random.normal(0, 0.5, n)  # Measurement noise
        tss_effluent = np.clip(tss_effluent, 2.0, 15.0)
        
        # COD (Chemical Oxygen Demand) - mg/L
        # Typically 5-6x TSS, better removal than TSS
        cod_influent = tss_influent * 5.5
        removal_rate_cod = 0.93 * overall_efficiency
        removal_rate_cod = np.clip(removal_rate_cod, 0.82, 0.97)
        
        cod_effluent = cod_influent * (1 - removal_rate_cod)
        cod_effluent += np.random.normal(0, 2.0, n)
        cod_effluent = np.clip(cod_effluent, 15.0, 50.0)
        
        # BOD (Biochemical Oxygen Demand) - mg/L
        # Typically 0.6-0.7x COD, best removal rate
        removal_rate_bod = 0.97 * overall_efficiency
        removal_rate_bod = np.clip(removal_rate_bod, 0.90, 0.99)
        
        bod_effluent = cod_effluent * 0.65 * (1 - removal_rate_bod)
        bod_effluent += np.random.normal(0, 0.3, n)
        bod_effluent = np.clip(bod_effluent, 2.0, 8.0)
        
        return tss_effluent, cod_effluent, bod_effluent
    
    def generate_dataset(self, start_date, days, interval_minutes=5):
        """
        Generate complete training dataset
        
        Parameters:
        - start_date: Starting date (datetime object)
        - days: Number of days to generate
        - interval_minutes: Sampling interval (default 5 minutes)
        
        Returns:
        - DataFrame with all features and targets in proper format
        """
        # Generate timestamps
        total_samples = int(days * 24 * 60 / interval_minutes)
        timestamps = [start_date + timedelta(minutes=i*interval_minutes) 
                     for i in range(total_samples)]
        
        print(f"Generating {total_samples:,} samples over {days} days...")
        
        # Generate influent data (for t-10h)
        turbidity_inf, flow_inf, temp_inf = self.generate_influent_data(timestamps)
        
        # Generate aeration basin data (for t-5h)
        ph_aer, do_aer = self.generate_aeration_basin_data(timestamps, turbidity_inf, flow_inf)
        
        # Generate control actions (for t-5h)
        fan_speed = self.generate_control_actions(timestamps, turbidity_inf, flow_inf, do_aer)
        
        # Calculate effluent quality (at time t)
        tss_eff, cod_eff, bod_eff = self.calculate_effluent_quality(
            turbidity_inf, flow_inf, ph_aer, do_aer, fan_speed, temp_inf
        )
        
        # Create DataFrame with proper column names
        df = pd.DataFrame({
            'timestamp_effluent': timestamps,
            'turbidity_influent_t_minus_10h': turbidity_inf,
            'flow_rate_influent_t_minus_10h': flow_inf,
            'ph_aeration_basin_t_minus_5h': ph_aer,
            'do_aeration_basin_t_minus_5h': do_aer,
            'temp_influent_t_minus_10h': temp_inf,
            'fan_speed_control_t_minus_5h': fan_speed,
            'tss_effluent_mgL': tss_eff,
            'cod_effluent_mgL': cod_eff,
            'bod_effluent_mgL': bod_eff
        })
        
        # Round to appropriate precision
        df['turbidity_influent_t_minus_10h'] = df['turbidity_influent_t_minus_10h'].round(2)
        df['flow_rate_influent_t_minus_10h'] = df['flow_rate_influent_t_minus_10h'].round(1)
        df['ph_aeration_basin_t_minus_5h'] = df['ph_aeration_basin_t_minus_5h'].round(2)
        df['do_aeration_basin_t_minus_5h'] = df['do_aeration_basin_t_minus_5h'].round(2)
        df['temp_influent_t_minus_10h'] = df['temp_influent_t_minus_10h'].round(1)
        df['fan_speed_control_t_minus_5h'] = df['fan_speed_control_t_minus_5h'].round(0).astype(int)
        df['tss_effluent_mgL'] = df['tss_effluent_mgL'].round(1)
        df['cod_effluent_mgL'] = df['cod_effluent_mgL'].round(1)
        df['bod_effluent_mgL'] = df['bod_effluent_mgL'].round(1)
        
        # Format timestamp as ISO 8601
        df['timestamp_effluent'] = df['timestamp_effluent'].apply(
            lambda x: x.strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        
        return df


def main():
    print("="*70)
    print("Historical Training Data Generator for LSTM Model")
    print("="*70)
    
    generator = HistoricalDataGenerator(seed=42)
    
    # Generate 6 months of data (good balance for LSTM training)
    # 5-minute intervals = 12 samples/hour × 24 hours × 180 days = 51,840 samples
    start_date = datetime(2025, 4, 1, 0, 0, 0)  # April 1, 2025
    days = 180  # 6 months
    
    print(f"\nConfiguration:")
    print(f"  Start Date: {start_date.strftime('%Y-%m-%d')}")
    print(f"  Duration: {days} days (6 months)")
    print(f"  Sampling Interval: 5 minutes")
    print(f"  Expected Samples: {days * 24 * 12:,}")
    print()
    
    # Generate dataset
    df = generator.generate_dataset(start_date, days, interval_minutes=5)
    
    print(f"\n✓ Generated {len(df):,} samples")
    print(f"\nDataset Summary:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Save to CSV
    output_file = 'training_data_6months.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")
    
    # Show sample statistics
    print(f"\n{'='*70}")
    print("Feature Statistics:")
    print(f"{'='*70}")
    print(df.describe().round(2))
    
    # Show first few rows
    print(f"\n{'='*70}")
    print("Sample Data (first 10 rows):")
    print(f"{'='*70}")
    print(df.head(10).to_string(index=False))
    
    # Show correlations with target variables
    print(f"\n{'='*70}")
    print("Correlations with Effluent Quality:")
    print(f"{'='*70}")
    
    numeric_df = df.drop('timestamp_effluent', axis=1)
    correlations = numeric_df.corr()[['tss_effluent_mgL', 'cod_effluent_mgL', 'bod_effluent_mgL']]
    print(correlations.round(3))
    
    print(f"\n{'='*70}")
    print("✅ Training data generation complete!")
    print(f"{'='*70}")
    print(f"\nNext steps:")
    print(f"  1. Review the data: {output_file}")
    print(f"  2. Create train/validation/test splits")
    print(f"  3. Build and train LSTM model")
    print(f"  4. Validate predictions against actual lab results")


if __name__ == "__main__":
    main()
