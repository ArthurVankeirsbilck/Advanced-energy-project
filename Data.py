import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('WIOT2014_Nov16_ROW.csv',sep = ';')
df  = df.iloc[: , :4]
print(df)

