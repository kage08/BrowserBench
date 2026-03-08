import os

import pandas as pd


def generate_report():
    """Generate a power consumption report from the CSV data"""

    file_name = "browser_power_results2.csv"

    # Check if file exists and has data
    if not os.path.exists(file_name):
        print(f"❌ Error: {file_name} not found!")
        print("Please run the benchmark first: python browser_bench2.py")
        return

    try:
        # Load the CSV
        df = pd.read_csv(file_name)

        # Check if we have any data
        if df.empty or len(df) == 0:
            print(f"❌ No data found in {file_name}")
            print("The CSV file exists but contains no power measurements.")
            print("Please run the benchmark first: python browser_bench2.py")
            return

        # Check if we have the expected columns
        required_columns = {
            "Browser",
            "Timestamp",
            "Total Power(mW)",
            "Idle Baseline(mW)",
            "Net Browser Power(mW)",
        }
        if not required_columns.issubset(set(df.columns)):
            print("❌ Invalid CSV format!")
            print(
                "Expected columns: Browser, Timestamp, Total Power(mW), Idle Baseline(mW), Net Browser Power(mW)"
            )
            print(f"Found columns: {list(df.columns)}")
            return

        # Group by browser and calculate statistics on Net Browser Power
        summary: pd.DataFrame = df.groupby("Browser")["Net Browser Power(mW)"].agg(
            Mean_mW="mean",
            Median_mW="median",
            Min_mW="min",
            Max_mW="max",
            StdDev_mW="std",
        )  # type: ignore

        # Print results
        print("🔋 Enhanced Browser Power Consumption Report")
        print("=" * 50)
        print(f"📊 Total measurements: {len(df)}")
        print(f"🌐 Browsers tested: {', '.join(summary.index)}")
        print(
            f"📈 Data collected from: {df['Timestamp'].min()} to {df['Timestamp'].max()}"
        )
        print(
            "🧾 Snapshot scope: latest run for browsers tested most recently, with prior rows retained for browsers not re-run."
        )
        print()

        # Print markdown-style table
        print(
            "| Browser | Net Mean Power (mW) | Net Median Power (mW) | Net Min Power (mW) | Net Max Power (mW) | Std Dev (mW) | Measurements |"
        )
        print(
            "|---------|---------------------|-----------------------|--------------------|--------------------|--------------|--------------|"
        )

        for browser, row in summary.iterrows():
            count = len(df[df["Browser"] == browser])
            print(
                f"| {browser} | {row['Mean_mW']:.2f} | {row['Median_mW']:.2f} | {row['Min_mW']:.0f} | {row['Max_mW']:.0f} | {row['StdDev_mW']:.2f} | {count} |"
            )

        print()

        # Calculate efficiency comparison if we have multiple browsers
        if len(summary) > 1:
            print("⚡ Efficiency Analysis (Based on Net Browser Power):")
            most_efficient = summary["Mean_mW"].idxmin()
            least_efficient = summary["Mean_mW"].idxmax()

            efficiency_diff = (
                summary.loc[least_efficient, "Mean_mW"]
                - summary.loc[most_efficient, "Mean_mW"]
            )

            # Avoid divide by zero
            denom = summary.loc[least_efficient, "Mean_mW"]
            efficiency_percent = (efficiency_diff / denom) * 100 if denom > 0 else 0

            print(
                f"🏆 Most efficient: {most_efficient} ({summary.loc[most_efficient, 'Mean_mW']:.0f} mW net avg)"
            )
            print(
                f"🔥 Least efficient: {least_efficient} ({summary.loc[least_efficient, 'Mean_mW']:.0f} mW net avg)"
            )
            print(
                f"💡 Efficiency difference: {efficiency_diff:.0f} mW ({efficiency_percent:.1f}% improvement)"
            )

            # Battery life estimation (assuming 50Wh battery and some average total power)
            battery_wh = 50
            print(
                "\n🔋 Estimated total battery life (50Wh battery) during active browsing:"
            )

            # For battery life, we use Total Power(mW)
            total_power_summary: pd.DataFrame = df.groupby("Browser")[
                "Total Power(mW)"
            ].agg(Mean_mW="mean", Median_mW="median")  # type: ignore

            for browser, row in total_power_summary.iterrows():
                hours_mean = (
                    battery_wh / (row["Mean_mW"] / 1000)
                    if row["Mean_mW"] > 0
                    else float("inf")
                )
                hours_median = (
                    battery_wh / (row["Median_mW"] / 1000)
                    if row["Median_mW"] > 0
                    else float("inf")
                )
                print(
                    f"   {browser}: ~{hours_mean:.1f}h (mean), ~{hours_median:.1f}h (median)"
                )

    except Exception as e:
        print(f"❌ Error processing data: {e}")
        print("Please check the CSV file format and try again.")


if __name__ == "__main__":
    generate_report()
