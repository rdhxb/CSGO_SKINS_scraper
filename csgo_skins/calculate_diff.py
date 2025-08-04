import pandas as pd

def calculate_diff():
    merged_df = pd.read_csv("data/merged_cases_expected_values.csv")
    merged_df["case_total_expected_value"] = merged_df["case_total_expected_value"].astype(float)
    merged_df.loc[merged_df["case_price"] == "Free", "case_price"] = 0.0
    merged_df["case_price"] = merged_df["case_price"].str.replace("zł", "").astype(float)
    merged_df["Difference"] = merged_df["case_total_expected_value"] - merged_df["case_price"]

    merged_df.to_csv("data/cases_with_differences.csv", index=False)

    sorted_df = merged_df.sort_values(by="Difference", ascending=False)

    sorted_df.to_csv("data/cases_sorted_by_profitability.csv", index=False)

    merged_df = merged_df[merged_df["case_price"] > 0]

    merged_df["Profitability (%)"] = (
        merged_df["Difference"] / merged_df["case_price"]
    ) * 100

    sorted_by_profitability = merged_df.sort_values(by="Profitability (%)", ascending=False)

    sorted_by_profitability.to_csv(
        "data/cases_sorted_by_profitability_percentage.csv", index=False
    )

    # Print the sorted DataFrame
    print("\n=== Cases Sorted by Profitability (%) ===")
    pd.options.display.max_columns = None  # Show all columns
    pd.options.display.max_rows = None  # Show all rows
    pd.set_option("display.max_colwidth", None)  # Show full column width
    pd.set_option("display.width", 1000)  # Set display width for better readability
    pd.set_option("display.expand_frame_repr", False)  # Prevent DataFrame from being split
    pd.set_option("display.show_dimensions", False)  # Hide DataFrame dimensions

    print(
        sorted_by_profitability[
            [
                "case_price",
                "case_total_expected_value",
                "Difference",
                "Profitability (%)",
            ]
        ]
    )
