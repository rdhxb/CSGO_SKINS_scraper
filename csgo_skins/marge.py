import pandas as pd

def merge_csv_files():
    # marge cases csv and expected values csv
    cases_df = pd.read_csv("data/cases.csv")
    expected_values_df = pd.read_csv("data/expected_values.csv")

    # Merge on 'Case Name' and 'Case Link'
    merged_df = pd.merge(
        cases_df, expected_values_df, left_on="case_link", right_on="case_link", how="outer"
    )

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv("data/merged_cases_expected_values.csv", index=False)
    print("Merged CSV file created: 'merged_cases_expected_values.csv'")
