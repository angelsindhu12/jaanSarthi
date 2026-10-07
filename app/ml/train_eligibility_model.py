import os
import json
import random
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np

# Set seeds for reproducibility
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

QUALIFICATION_MAP = {
    "None": 0,
    "8th": 1,
    "10th": 2,
    "12th": 3,
    "Diploma": 4,
    "Graduate": 5,
    "Post Graduate": 6
}

GENDER_MAP = {"All": 0, "Others": 0, "Other": 0, "Male": 1, "Female": 2}
CATEGORY_MAP = {"General": 0, "OBC": 1, "SC": 2, "ST": 3, "EWS": 4}
OCCUPATION_MAP = {"Any": 0, "Farmer": 1, "Student": 2, "Artisan": 3, "Unemployed": 4, "Self-employed": 5}

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

class EligibilityNeuralNet(nn.Module):
    """
    Deep Neural Network for predicting citizen scheme & job eligibility.
    Combines user demographic & qualification features with scheme/job requirements.
    """
    def __init__(self, input_dim: int = 16):
        super(EligibilityNeuralNet, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.25),
            
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(64, 32),
            nn.ReLU(),
            
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)

def extract_feature_vector(user: dict, target: dict, is_job: bool = False) -> List[float]:
    """
    Extracts normalized numerical features representing the match between user and target.
    """
    u_age = float(user.get("age", 25)) / 100.0
    u_qual = float(QUALIFICATION_MAP.get(user.get("qualification", "12th"), 3)) / 6.0
    u_gender = float(GENDER_MAP.get(user.get("gender", "All"), 0)) / 2.0
    u_income = float(user.get("annual_income", 150000) or 150000) / 1000000.0  # normalized to 10 Lakh
    u_cat = float(CATEGORY_MAP.get(user.get("caste_category", "General"), 0)) / 4.0
    u_occ = float(OCCUPATION_MAP.get(user.get("occupation", "Any"), 0)) / 5.0

    if is_job:
        req_min_age = float(target.get("min_age", 18)) / 100.0
        req_max_age = float(target.get("max_age", 35)) / 100.0
        req_qual = float(QUALIFICATION_MAP.get(target.get("qualification_required", "10th"), 2)) / 6.0
        req_gender = 0.0
        income_cap = 1.0  # jobs don't have max income cap
        cat_match = 1.0
        occ_match = 1.0
        is_job_flag = 1.0
    else:
        elig = target.get("eligibility", {})
        req_min_age = float(elig.get("min_age", 0)) / 100.0
        req_max_age = float(elig.get("max_age", 100)) / 100.0
        req_qual = float(QUALIFICATION_MAP.get(elig.get("min_qualification", "None"), 0)) / 6.0
        req_gender = float(GENDER_MAP.get(elig.get("gender", "All"), 0)) / 2.0
        
        max_inc = elig.get("max_annual_income")
        income_cap = float(max_inc) / 1000000.0 if max_inc else 1.0
        
        allowed_cats = elig.get("caste_category", ["All"])
        cat_match = 1.0 if ("All" in allowed_cats or user.get("caste_category") in allowed_cats) else 0.0
        
        req_occ = elig.get("occupation", "Any")
        occ_match = 1.0 if (req_occ == "Any" or user.get("occupation") == req_occ) else 0.0
        is_job_flag = 0.0

    # Interaction / delta features
    age_valid = 1.0 if (req_min_age <= u_age <= req_max_age) else 0.0
    qual_valid = 1.0 if (u_qual >= req_qual) else 0.0
    gender_valid = 1.0 if (req_gender == 0.0 or req_gender == u_gender) else 0.0
    income_valid = 1.0 if (u_income <= income_cap) else 0.0

    return [
        u_age, u_qual, u_gender, u_income, u_cat, u_occ,
        req_min_age, req_max_age, req_qual, req_gender, income_cap,
        age_valid, qual_valid, gender_valid, income_valid, is_job_flag
    ]

def generate_training_data(schemes: list, jobs: list, num_samples: int = 5000):
    """
    Generates synthetic realistic user profiles paired with schemes and jobs,
    with calculated ground truth eligibility labels (1 for eligible, 0 for not).
    """
    X = []
    y = []

    qualifications = list(QUALIFICATION_MAP.keys())
    genders = ["Male", "Female"]
    categories = list(CATEGORY_MAP.keys())
    occupations = list(OCCUPATION_MAP.keys())

    for _ in range(num_samples):
        # Generate random user profile
        user = {
            "age": random.randint(14, 70),
            "gender": random.choice(genders),
            "qualification": random.choice(qualifications),
            "annual_income": random.choice([50000, 120000, 200000, 350000, 500000, 800000]),
            "caste_category": random.choice(categories),
            "occupation": random.choice(occupations)
        }

        # 50% chance to pair with Scheme, 50% with Job
        if random.random() < 0.5:
            target = random.choice(schemes)
            is_job = False
            elig = target.get("eligibility", {})
            
            # Ground truth rules
            age_ok = elig["min_age"] <= user["age"] <= elig["max_age"]
            qual_ok = QUALIFICATION_MAP[user["qualification"]] >= QUALIFICATION_MAP.get(elig.get("min_qualification", "None"), 0)
            gender_ok = elig["gender"] == "All" or elig["gender"] == user["gender"]
            income_ok = (elig["max_annual_income"] is None) or (user["annual_income"] <= elig["max_annual_income"])
            cat_ok = ("All" in elig.get("caste_category", ["All"])) or (user["caste_category"] in elig.get("caste_category", []))
            occ_ok = (elig.get("occupation", "Any") == "Any") or (user["occupation"] == elig.get("occupation", "Any"))

            label = 1.0 if (age_ok and qual_ok and gender_ok and income_ok and cat_ok and occ_ok) else 0.0
        else:
            target = random.choice(jobs)
            is_job = True
            age_ok = target["min_age"] <= user["age"] <= target["max_age"]
            qual_ok = QUALIFICATION_MAP[user["qualification"]] >= QUALIFICATION_MAP.get(target.get("qualification_required", "10th"), 2)
            label = 1.0 if (age_ok and qual_ok) else 0.0

        feat = extract_feature_vector(user, target, is_job)
        X.append(feat)
        y.append([label])

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)

def train_model():
    from app.ml.data_loader import DatasetLoader

    schemes = DatasetLoader.load_schemes()
    jobs = DatasetLoader.load_jobs()
    print(f"[Train] Loaded {len(schemes)} schemes and {len(jobs)} jobs for training generator.")

    print("[Train] Generating 8,000 synthetic profile-scheme & profile-job pairs...")
    X, y = generate_training_data(schemes, jobs, num_samples=8000)

    # Split train / validation
    split_idx = int(len(X) * 0.8)
    X_train, X_val = torch.tensor(X[:split_idx]), torch.tensor(X[split_idx:])
    y_train, y_val = torch.tensor(y[:split_idx]), torch.tensor(y[split_idx:])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train] Training Neural Network on device: {device}")

    model = EligibilityNeuralNet(input_dim=16).to(device)
    criterion = nn.BCELoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.003, weight_decay=1e-4)

    dataset = torch.utils.data.TensorDataset(X_train, y_train)
    loader = torch.utils.data.DataLoader(dataset, batch_size=64, shuffle=True)

    model.train()
    epochs = 25
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        for batch_X, batch_y in loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            optimizer.zero_grad()
            preds = model(batch_X)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if epoch % 5 == 0 or epoch == epochs:
            model.eval()
            with torch.no_grad():
                val_preds = model(X_val.to(device))
                val_loss = criterion(val_preds, y_val.to(device)).item()
                val_acc = ((val_preds > 0.5).float() == y_val.to(device)).float().mean().item()
            model.train()
            print(f"Epoch {epoch:02d}/{epochs} | Train Loss: {total_loss/len(loader):.4f} | Val Loss: {val_loss:.4f} | Val Accuracy: {val_acc*100:.2f}%")

    # Save trained weights
    model_path = MODELS_DIR / "eligibility_classifier.pt"
    torch.save(model.state_dict(), model_path)
    print(f"[Train] Model saved successfully to {model_path}")

    # Save metadata
    meta = {
        "input_dim": 16,
        "qualification_map": QUALIFICATION_MAP,
        "gender_map": GENDER_MAP,
        "category_map": CATEGORY_MAP,
        "occupation_map": OCCUPATION_MAP
    }
    with open(MODELS_DIR / "feature_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("[Train] Metadata saved to models/feature_metadata.json")

if __name__ == "__main__":
    train_model()
