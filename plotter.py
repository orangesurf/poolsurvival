import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

plt.figure(figsize=(10, 6))

year_colors = {'1': 'blue', '2': 'red'}
survival_styles = {'95': '-', '99': '--'}
file_pattern = 'data/*_*-*_*_*.csv'
files = sorted(glob.glob(file_pattern))

grouped_files = {}
for file in files:
    base_name = os.path.basename(file)
    survival_rate, year_runs, _, _ = base_name.split('_')
    year = year_runs.split('-')[0] 
    key = survival_rate + '_' + year 
    if key not in grouped_files:
        grouped_files[key] = []
    grouped_files[key].append(file)

for key, file_group in grouped_files.items():
    data_frames = []
    for file in file_group:
        df = pd.read_csv(file)
        data_frames.append(df)
    full_data = pd.concat(data_frames)
    averaged_data = full_data.groupby('Hashrate').agg({'Min_Reserve': 'mean'}).reset_index()
    survival_rate, year = key.split('_')
    color = year_colors.get(year, 'gray') 
    linestyle = survival_styles.get(survival_rate, '-')  
    label = f"Year {year}, Survival {survival_rate}%"
    plt.plot(averaged_data['Hashrate'] * 100, averaged_data['Min_Reserve'], label=label, color=color, linestyle=linestyle)
    
plt.legend()
plt.title('Required Initial Reserve for Different Survival Rates')
plt.xlabel('Hashrate Percentage (%)')
plt.ylabel('Required Initial Reserve (BTC)')
plt.ylim(0, 800)
plt.grid(True)
plt.savefig("plot.png", dpi=500)
