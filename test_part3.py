import pytest
import pandas as pd
import geopandas as gpd
from unittest.mock import patch, MagicMock

import part3_step01   # your script


# ---------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------

@pytest.fixture
def mock_map_df():
    return gpd.GeoDataFrame({
        "NAME": ["camden", "hackney", "islington"],
        "geometry": [None, None, None]
    })


@pytest.fixture
def mock_crime_df():
    df = pd.DataFrame({
        "Month_Year": pd.to_datetime(["2024-03-01", "2024-03-01", "2024-04-01"]),
        "Area_name": ["Camden", "Hackney", "Islington"],
        "Offence_Group": ["Violence", "Violence", "Burglary"],
        "Offences": [10, 20, None],
        "Positive_Outcomes": [None, None, None],
        "Success_Ratio": [None, None, None]
    })

    df["month_lower"] = df["Month_Year"].dt.month_name().str.lower()
    df["offence_lower"] = df["Offence_Group"].str.lower()
    df["borough_lower"] = df["Area_name"].str.lower()

    df["measure_lower"] = df.apply(
        lambda row: "offences" if not pd.isna(row["Offences"]) else
                    "positive outcomes" if not pd.isna(row["Positive_Outcomes"]) else
                    "success ratio",
        axis=1
    )

    return df


# ---------------------------------------------------------
# TEST: load_and_prepare_data()
# ---------------------------------------------------------

@patch("part3_step01.gpd.read_file")
@patch("part3_step01.pd.read_excel")
def test_load_and_prepare_data(mock_read_excel, mock_read_file):

    mock_read_file.return_value = gpd.GeoDataFrame({"NAME": ["Camden"]})
    mock_read_excel.return_value = pd.DataFrame({
        "Month_Year": ["2024-03-01"],
        "Area_name": ["Camden"],
        "Offence_Group": ["Violence"],
        "Offences": [10],
        "Positive_Outcomes": [None],
        "Success_Ratio": [None]
    })

    map_df, crime_df = part3_step01.load_and_prepare_data("map.shp", "crime.xlsx")

    assert "month_lower" in crime_df.columns
    assert "offence_lower" in crime_df.columns
    assert "measure_lower" in crime_df.columns
    assert len(map_df) == 1
    assert len(crime_df) == 1


# ---------------------------------------------------------
# TEST: filter_crime_data()
# ---------------------------------------------------------

def test_filter_crime_data(mock_crime_df, mock_map_df):

    filtered = part3_step01.filter_crime_data(
        mock_crime_df, mock_map_df,
        month="march", year=2024,
        offence="violence", measure="offences"
    )

    assert len(filtered) == 2
    assert set(filtered["Area_name"]) == {"Camden", "Hackney"}


# ---------------------------------------------------------
# TEST: compute_global_scale()
# ---------------------------------------------------------

def test_compute_global_scale(mock_crime_df):

    vmin, vmax = part3_step01.compute_global_scale(
        mock_crime_df, "violence", "offences"
    )

    assert vmin == 10
    assert vmax == 20


# ---------------------------------------------------------
# TEST: merge_for_static_map()
# ---------------------------------------------------------

def test_merge_for_static_map(mock_map_df, mock_crime_df):

    filtered = mock_crime_df[["Area_name", "Offences"]]
    merged = part3_step01.merge_for_static_map(mock_map_df, filtered)

    assert "Offences" in merged.columns
    assert len(merged) == 3


# ---------------------------------------------------------
# TEST: create_static_choropleth()
# ---------------------------------------------------------

@patch("part3_step01.plt")
def test_create_static_choropleth(mock_plt, mock_map_df, mock_crime_df):

    mock_plt.subplots.return_value = (MagicMock(), MagicMock())

    merged = part3_step01.merge_for_static_map(mock_map_df, mock_crime_df)
    merged.plot = MagicMock()

    part3_step01.create_static_choropleth(
        merged,
        "violence",
        "offences",
        "march",
        2024,
        vmin=0,
        vmax=20,
        value_column="Offences"
    )

    mock_plt.savefig.assert_called_once()


# ---------------------------------------------------------
# TEST: prepare_animation_data()
# ---------------------------------------------------------

def test_prepare_animation_data(mock_crime_df):

    df_anim, timeline = part3_step01.prepare_animation_data(
        mock_crime_df,
        "violence",
        "offences"
    )

    assert len(df_anim) == 2
    assert len(timeline) == 1
    assert timeline[0] == pd.Timestamp("2024-03-01")


# ---------------------------------------------------------
# TEST: create_animation()
# ---------------------------------------------------------

@patch("part3_step01.FuncAnimation")
def test_create_animation(mock_anim, mock_map_df, mock_crime_df):

    df_anim, timeline = part3_step01.prepare_animation_data(
        mock_crime_df,
        "violence",
        "offences"
    )

    part3_step01.create_animation(
        mock_map_df,
        df_anim,
        timeline,
        vmin=0,
        vmax=20,
        offence="violence",
        measure="offences",
        value_column="Offences"
    )

    mock_anim.assert_called_once()


# ---------------------------------------------------------
# TEST: save_animation()
# ---------------------------------------------------------

@patch("part3_step01.FFMpegWriter")
def test_save_animation(mock_writer):

    anim = MagicMock()
    writer_instance = MagicMock()
    mock_writer.return_value = writer_instance

    part3_step01.save_animation(anim)

    anim.save.assert_called_once_with(
        "crime_animation.mp4",
        writer=writer_instance
    )


if __name__ == "__main__":
    pytest.main(["-q"])
