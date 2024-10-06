import pandas as pd
import re

df = pd.read_excel('brokers_data.xlsx')
print(df.head())
def clean_phone(phone):
    cleaned_phone = re.sub(r'\D', '', phone)
    if len(cleaned_phone) == 10: 
        return cleaned_phone
    elif len(cleaned_phone) == 11 and cleaned_phone.startswith('1'): 
        return cleaned_phone[1:]
    elif len(cleaned_phone) == 12 and cleaned_phone.startswith('+1'): 
        return cleaned_phone[2:]
    else:
        return None 


df['Phone'] = df['Phone'].apply(clean_phone)

df.drop_duplicates(inplace=True)

print(df)

df.to_excel('clean_broker.xlsx', index=False)