import requests
import pandas as pd
from bs4 import BeautifulSoup
from src.config import DATA_DIR

url = "https://www.myh.se/yrkeshogskolan/ansok-om-att-bedriva-utbildning/ansokan-kurser/statsbidrag-och-schablonnivaer"
response = requests.get(url)
soup = BeautifulSoup(response.content, "lxml")

table = soup.find("table")
rows = table.find_all("tr")

data = []
for row in rows[1:]: 
    cols = row.find_all("td")
    data.append([col.get_text(strip=True) for col in cols])

df = pd.DataFrame(data, columns=["Utbildningsområde", "Utan momskompensation", "Med momskompensation"])

# ✅ Spara till korrekt plats
output_path = DATA_DIR / "schablonnivaer.csv"
df.to_csv(output_path, index=False)

print(df)