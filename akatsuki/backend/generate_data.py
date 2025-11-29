
import csv
import random
import math
from datetime import datetime, timedelta
import pandas as pd

HOSPITALS = [
    {"id": "city_general", "name": "City General"},
    {"id": "st_marys", "name": "St Marys"},
    {"id": "metrocare", "name": "MetroCare"},
    {"id": "govt_hospital", "name": "Govt Hospital"}
]

ROWS = []
start_date = datetime(2024,1,1)

for day_offset in range(0, 180):  
    day = start_date + timedelta(days=day_offset)
    weekday = day.weekday()  
    for hour in range(0,24):
        for h in HOSPITALS:

            base = 20
            if 8 <= hour <= 11:
                base += 40
            if 17 <= hour <= 20:
                base += 50
            if weekday >= 5: 
                base = int(base * 0.7)

            count = max(1, int(random.gauss(base, 10)))
            emergency = max(0, int(random.gauss(count * 0.15, 3)))
            wait = int(5 + (count / 10) + random.gauss(0, 4))

            ROWS.append({
                'hospital_id': h['id'],
                'hour': hour,
                'weekday': weekday,
                'patient_count': count,
                'emergency_count': emergency,
                'wait_minutes': wait
            })

df = pd.DataFrame(ROWS)
df.to_csv("dataset.csv", index=False)

print("dataset.csv created →", len(df), "rows")
