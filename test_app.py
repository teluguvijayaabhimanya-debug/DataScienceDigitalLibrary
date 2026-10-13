import io
import json
from app import app

client = app.test_client()

# 1. Test GET /
res = client.get("/")
assert res.status_code == 200, f"GET / failed with {res.status_code}"
assert b"DS LAB" in res.data, "DS LAB not in response"
print("[OK] GET / test passed")

# 2. Test GET /api/student
res = client.get("/api/student")
assert res.status_code == 200
data = res.get_json()
assert data["success"] is True
assert data["student"]["name"] == "K. Sai Venkatesh"
print("[OK] GET /api/student passed")

# 3. Test POST /api/student
res = client.post("/api/student", data={
    "name": "K. Sai Venkatesh Updated",
    "roll_no": "22A91A0542",
    "section": "DS-A",
    "branch": "Data Science & AI",
    "assistant_professor": "Dr. P. Rajesh Kumar",
    "github_url": "https://github.com/saivenkatesh/ds-laboratory"
})
assert res.status_code == 200
data = res.get_json()
assert data["student"]["name"] == "K. Sai Venkatesh Updated"
print("[OK] POST /api/student passed")

# 4. Test GET /api/experiments
res = client.get("/api/experiments")
assert res.status_code == 200
data = res.get_json()
assert data["success"] is True
assert len(data["experiments"]) >= 1
print(f"[OK] GET /api/experiments passed (count: {len(data['experiments'])})")

# 5. Test POST /api/experiments (Add experiment)
dummy_img = (io.BytesIO(b"fake image data"), "test_cover.png")
res = client.post("/api/experiments", data={
    "experiment_no": "2",
    "title": "Supervised Machine Learning - Classification",
    "short_description": "Building and evaluating Logistic Regression and Random Forest models on credit dataset.",
    "d2_heading": "Classification Analysis",
    "long_content": "AIM:\nTo train and evaluate classification algorithms.\n\nPROCEDURE:\n1. Load dataset.\n2. Train test split.\n3. Model training.\n\nCONCLUSION:\nAccuracy reached 92%.",
    "github_url": "https://github.com/saivenkatesh/exp2",
    "cover_image": dummy_img
}, content_type="multipart/form-data")
assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.data}"
new_exp = res.get_json()["experiment"]
new_id = new_exp["id"]
print("[OK] POST /api/experiments passed, created id:", new_id)

# 6. Test GET /api/experiments/<id>
res = client.get(f"/api/experiments/{new_id}")
assert res.status_code == 200
assert res.get_json()["experiment"]["title"] == "Supervised Machine Learning - Classification"
print("[OK] GET /api/experiments/<id> passed")

# 7. Test search filter
res = client.get("/api/experiments?q=Classification")
assert res.status_code == 200
assert len(res.get_json()["experiments"]) == 1
print("[OK] GET /api/experiments?q=Classification search passed")

# 8. Test DELETE /api/experiments/<id>
res = client.delete(f"/api/experiments/{new_id}")
assert res.status_code == 200
assert res.get_json()["success"] is True
print("[OK] DELETE /api/experiments/<id> passed")

# Confirm deletion
res = client.get(f"/api/experiments/{new_id}")
assert res.status_code == 404
print("[OK] Verified deletion with 404 passed")

print("\nALL BACKEND API TESTS COMPLETED SUCCESSFULLY!")
