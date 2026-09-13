"""
evaluate.py

This script evaluates the intent classification model against the held-out test set.
It should be re-run after any change to app/services/intent_service.py or the dataset
to ensure the model meets the required accuracy target.
"""

import os
import sys
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

ACCURACY_TARGET = 0.85

def main():
    try:
        from app.services.intent_service import classify_intent
    except ImportError:
        print("intent_service.classify_intent() is not yet implemented — evaluation will run once classification logic is added.")
        return

    # Check if classify_intent is a stub that raises NotImplementedError
    try:
        classify_intent("test")
    except NotImplementedError:
        print("intent_service.classify_intent() is not yet implemented — evaluation will run once classification logic is added.")
        return
    except Exception:
        # Ignore other exceptions for the stub check
        pass
        
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    test_set_path = os.path.join(data_dir, 'test_set.csv')
    
    if not os.path.exists(test_set_path):
        print(f"Test set not found at {test_set_path}")
        return
        
    df = pd.read_csv(test_set_path, comment='#')
    
    if df.empty:
        print("Test set is empty.")
        return
        
    print("Evaluating intent classifier...")
    
    y_true = df['intent_label'].tolist()
    y_pred = []
    
    for text in df['text']:
        try:
            pred = classify_intent(text)['intent']
            y_pred.append(pred)
        except NotImplementedError:
             print("intent_service.classify_intent() is not yet implemented — evaluation will run once classification logic is added.")
             return
        except Exception as e:
             # Default fallback on error
             print(f"Error classifying text: '{text}' - {e}")
             y_pred.append('unknown_intent')
             
    accuracy = accuracy_score(y_true, y_pred)
    
    print("\n--- Evaluation Results ---")
    print(classification_report(y_true, y_pred, zero_division=0))
    
    print("\nConfusion Matrix:")
    labels = sorted(list(set(y_true) | set(y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    print(cm_df)
    
    print("\n--- Final Target Check ---")
    if accuracy >= ACCURACY_TARGET:
        print(f"[PASS] Accuracy {accuracy:.2f} meets target of {ACCURACY_TARGET}")
    else:
        print(f"[FAIL] Accuracy {accuracy:.2f} below target of {ACCURACY_TARGET}")

if __name__ == '__main__':
    # Add root dir to sys.path so 'app' can be resolved
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    main()
