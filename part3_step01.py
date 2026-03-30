import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter


# ---------------------------------------------------------
# 1. LOAD + CLEAN DATA
# ---------------------------------------------------------
def load_and_prepare_data(map_path, crime_path):
    map_df = gpd.read_file(map_path)
    crime_df = pd.read_excel(crime_path)

    crime_df["Month_Year"] = pd.to_datetime(crime_df["Month_Year"])
    crime_df["month_lower"] = crime_df["Month_Year"].dt.month_name().str.lower()
    crime_df["offence_lower"] = crime_df["Offence_Group"].str.lower()
    crime_df["borough_lower"] = crime_df["Area_name"].str.lower()

    crime_df = crime_df.drop_duplicates()
    crime_df["measure_lower"] = crime_df.apply(
        lambda row: "offences" if not pd.isna(row["Offences"]) else
                    "positive outcomes" if not pd.isna(row["Positive_Outcomes"]) else
                    "success ratio",
        axis=1
    )

    crime_df = crime_df.dropna(subset=["Area_name"])
    return map_df, crime_df




# ---------------------------------------------------------
# 3. FILTERING LOGIC
# ---------------------------------------------------------
def filter_crime_data(crime_df, map_df, month, year, offence, measure):
    value_column = {
        "offences": "Offences",
        "positive outcomes": "Positive_Outcomes",
        "success ratio": "Success_Ratio"
    }[measure]

    
    filtered = crime_df[
        (crime_df["month_lower"] == month) &
        (crime_df["Month_Year"].dt.year == year) &
        (crime_df["offence_lower"] == offence) &
        (crime_df["measure_lower"] == measure)
    ][["Area_name", value_column]]


    valid_boroughs = map_df["NAME"].str.lower().unique()
    filtered = filtered[filtered["Area_name"].str.lower().isin(valid_boroughs)]

    return filtered


# ---------------------------------------------------------
# 4. STATIC MAP HELPERS
# ---------------------------------------------------------
def compute_global_scale(crime_df, offence, measure):
    df_global = crime_df[
        (crime_df["offence_lower"] == offence) &
        (crime_df["measure_lower"] == measure)
    ]

    value_column = {
        "offences": "Offences",
        "positive outcomes": "Positive_Outcomes",
        "success ratio": "Success_Ratio"
    }[measure]

    return df_global[value_column].min(), df_global[value_column].max()


def merge_for_static_map(map_df, filtered):
    return map_df.merge(
        filtered,
        left_on="NAME",
        right_on="Area_name",
        how="left"
    )


def create_static_choropleth(merged_static, offence, measure, month, year, vmin, vmax, value_column):
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    merged_static.plot(
        column=value_column,
        cmap="PuRd",
        linewidth=0.8,
        ax=ax,
        edgecolor="0.8",
        legend=True,
        vmin=vmin,
        vmax=vmax,
        missing_kwds={"color": "lightgrey", "label": "No data"}
    )

    plt.title(f"{offence.title()} — {measure.title()} — {month.title()} {year}")
    plt.axis("off")
    plt.savefig("static_choropleth.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------
# 5. ANIMATION LOGIC
# ---------------------------------------------------------
def prepare_animation_data(crime_df, offence, measure):
    df_anim = crime_df[
        (crime_df["offence_lower"] == offence) &
        (crime_df["measure_lower"] == measure)
    ].copy()

    timeline = (
        df_anim["Month_Year"]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    return df_anim, timeline


def create_animation(map_df, df_anim, timeline, vmin, vmax, offence, measure, value_column):
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    sm = plt.cm.ScalarMappable(cmap="PuRd", norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("Crime Count")

    def update(frame_index):
        ax.clear()
        current_date = timeline[frame_index]

        df_month = df_anim[
            df_anim["Month_Year"] == current_date
        ][["Area_name", value_column]]

        merged = map_df.merge(
            df_month,
            left_on="NAME",
            right_on="Area_name",
            how="left"
        )

        merged.plot(
            column=value_column,
            cmap="PuRd",
            linewidth=0.8,
            ax=ax,
            edgecolor="0.8",
            vmin=vmin,
            vmax=vmax,
            missing_kwds={"color": "lightgrey", "label": "No data"}
        )

        ax.set_title(
            f"{offence.title()} — {measure.title()} — {current_date.strftime('%B %Y')}"
        )
        ax.axis("off")

    anim = FuncAnimation(fig, update, frames=len(timeline), interval=1200, repeat=False)
    return anim


def save_animation(anim):
    writer = FFMpegWriter(fps=3)
    anim.save("crime_animation.mp4", writer=writer)

# ---------------------------------------------------------
# 6. MAIN RUNNER
# ---------------------------------------------------------
def main():

    # Paths
    map_path = "resources/London_Borough_Excluding_MHW.shp"
    crime_path = "resources/final_cleaned_crime_data.xlsx"

    # Load data
    map_df, crime_df = load_and_prepare_data(map_path, crime_path)

    print("\n--- Crime Data Explorer ---")

    # ---------------------------------------------------------
    # 2. USER INPUT VALIDATION
    # ---------------------------------------------------------
    # 1. MONTH SELECTION
    valid_months = sorted(
        crime_df["Month_Year"].dt.month_name().unique(),
        key=lambda x: pd.to_datetime(x, format="%B").month
    )
    
    print("\nSelect a month:")
    for i, m in enumerate(valid_months, 1):
        print(f"{i}. {m}")
    
    while True:
        try:
            month_choice = int(input("Enter month number: ").strip())
            if 1 <= month_choice <= len(valid_months):
                month = valid_months[month_choice - 1].lower()
                break
            else:
                print("Invalid selection. Choose a number from the list.")
        except ValueError:
            print("Please enter a valid number.")
    
    # 2. YEAR SELECTION
    valid_years = sorted(crime_df["Month_Year"].dt.year.unique())
    
    print("\nSelect a year:")
    for i, y in enumerate(valid_years, 1):
        print(f"{i}. {y}")

    while True:
        try:
            year_choice = int(input("Enter year number: ").strip())
            if 1 <= year_choice <= len(valid_years):
                year = valid_years[year_choice - 1]
                break
            else:
                print("Invalid selection. Choose a number from the list.")
        except ValueError:
            print("Please enter a valid number.")

        # 3. OFFENCE GROUP SELECTION
    valid_offences = sorted(crime_df["Offence_Group"].str.lower().unique())
    
    print("\nSelect an offence group:")
    for i, o in enumerate(valid_offences, 1):
        print(f"{i}. {o.title()}")
    
    while True:
        try:
            offence_choice = int(input("Enter offence number: ").strip())
            if 1 <= offence_choice <= len(valid_offences):
                offence = valid_offences[offence_choice - 1]
                break
            else:
                print("Invalid selection. Choose a number from the list.")
        except ValueError:
            print("Please enter a valid number.")
    
    # 4. MEASURE SELECTION
    valid_measures = ["offences", "positive outcomes", "success ratio"]
    
    print("\nSelect a measure:")
    for i, m in enumerate(valid_measures, 1):
        print(f"{i}. {m.title()}")
    
    while True:
        try:
            measure_choice = int(input("Enter measure number: ").strip())
            if 1 <= measure_choice <= len(valid_measures):
                measure = valid_measures[measure_choice - 1]
                break
            else:
                print("Invalid selection. Choose a number from the list.")
        except ValueError:
            print("Please enter a valid number.")

    value_column = {
        "offences": "Offences",
        "positive outcomes": "Positive_Outcomes",
        "success ratio": "Success_Ratio"
    }[measure]

    # Filter
    filtered = filter_crime_data(crime_df, map_df, month, year, offence, measure)
    filtered.to_excel("London_crime_data.xlsx", index=False)
    print("\nSaved filtered dataset as London_crime_data.xlsx")

    # Static map
    vmin, vmax = compute_global_scale(crime_df, offence, measure)
    merged_static = merge_for_static_map(map_df, filtered)
    create_static_choropleth(merged_static, offence, measure, month, year, vmin, vmax, value_column)
    print("Static choropleth saved as static_choropleth.png")

    # Animation across all years
    df_anim, timeline = prepare_animation_data(crime_df, offence, measure)
    anim = create_animation(map_df, df_anim, timeline, vmin, vmax, offence, measure, value_column)
    save_animation(anim)
    print("MP4 animation saved as crime_animation.mp4")


# Run the program
if __name__ == "__main__":
    main()