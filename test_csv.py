from app.services.csv_processor import analyze_csv

result = analyze_csv("uploads/transactions.csv")

print(result)