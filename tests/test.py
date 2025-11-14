import pandas as pd
from datetime import datetime, timedelta
from fmri_plots import create_time_series_chart

def generate_test_data():
    base_date = datetime(2025, 1, 1)
    data = []
    waves = ['Wave1', 'Wave2', 'Wave3']

    for idx, wave in enumerate(waves):
        for i in range(8):
            # shift start date and vary frequency per wave
            date = base_date + timedelta(days=(idx * 3) + 7 * i)
            # vary the number of subjects per wave-week
            for j in range(idx + 1):
                data.append({
                    "ID": f"{wave}_S{i+1}_{j+1}",
                    "wave": wave,
                    "created_at": date
                })

    data.append({"ID": "Wave1_S9", "wave": "Wave1", "created_at": base_date + timedelta(days=120)})
    return pd.DataFrame(data)

def test_time_series_chart():
    df = generate_test_data()
    print(df.head())

    fig = create_time_series_chart(df)
    print(f"Number of traces: {len(fig.data)}")
    fig.show()

if __name__ == "__main__":
    test_time_series_chart()