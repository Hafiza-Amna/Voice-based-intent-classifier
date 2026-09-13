import pandas as pd
from sklearn.model_selection import train_test_split
import os

# Set paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INTENTS_DATASET = os.path.join(DATA_DIR, 'intents_dataset.csv')
TEST_SET = os.path.join(DATA_DIR, 'test_set.csv')

def main():
    # Load data
    # We skip rows starting with '#' if they exist, but initially it's just a regular CSV
    df = pd.read_csv(INTENTS_DATASET, comment='#')
    
    # Perform an 80/20 train-test split stratified by intent_label
    # Fixed random seed for reproducibility
    train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['intent_label'], random_state=42)
    
    # Save test set with a warning comment at the top
    # NOTE: data/test_set.csv must remain untouched for the rest of development — 
    # it is only to be used for final evaluation, never for training or prompt examples.
    
    with open(TEST_SET, 'w', encoding='utf-8') as f:
        f.write("# IMPORTANT NOTE: data/test_set.csv must remain untouched for the rest of development — it is only to be used for final evaluation, never for training or prompt examples.\n")
    test_df.to_csv(TEST_SET, mode='a', index=False)
    
    # Save training set back to intents_dataset.csv (overwriting it)
    train_df.to_csv(INTENTS_DATASET, index=False)
    
    # Print summary
    print("Train set row counts per intent:")
    print(train_df['intent_label'].value_counts())
    print("\nTest set row counts per intent:")
    print(test_df['intent_label'].value_counts())
    print(f"\nTotal train rows: {len(train_df)}")
    print(f"Total test rows: {len(test_df)}")

if __name__ == '__main__':
    main()
