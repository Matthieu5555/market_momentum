import yfinance as yf
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from prettytable import PrettyTable
from colorama import Fore, Style, init

def main():
    # Initialize color settings for the console output using Colorama.
    init()
    # Display a banner with program information at the start of the application.
    print_banner()
    # Print the introductory instructions for using the program.
    print_instructions()

    # Interactively request from the user to choose the source of ticker symbols, either from S&P500 or a CSV file.
    tickers = get_tickers_yfinance()
    # Ask the user to specify the time period over which historical data should be analyzed.
    period = request_long_period_for_average()
    # Request from the user to choose a specific recent period for comparing recent trading volumes.
    comparison_slice, comparison_desc = request_recent_volume()
    # Request how many tickers the user wants to see results for in terms of volume extremity.
    extremes_count = request_extremes_count()
    # Fetch the volume data for the specified tickers and time period.
    volume_data = fetch_volume_data(tickers, period)
    # Analyze the fetched volume data to compute various statistics and metrics.
    results = analyze_volumes(volume_data, comparison_slice)
    # Sort the analysis results by the extremity of their volume percentiles to find the most significant outliers.
    sorted_results = sort_by_volume_extremity(results, extremes_count)
    
    # Fetch additional data like P/E ratio and industry for the tickers identified as having extreme volumes.
    additional_data = fetch_additional_data([result[0] for result in sorted_results])
    # Merge the additional data fetched into the sorted results to enhance the information available in the final display.
    merge_results(sorted_results, additional_data)
    # Display the final results in a formatted table, showing all relevant metrics and information.
    display_results(sorted_results)


def print_banner():
    #https://patorjk.com/software/taag/#p=display&f=Big&t=MarketMomentum%20v1.2
    banner_text = r"""
  __  __            _        _   __  __                            _                          __   ___  
 |  \/  |          | |      | | |  \/  |                          | |                        /_ | |__ \ 
 | \  / | __ _ _ __| | _____| |_| \  / | ___  _ __ ___   ___ _ __ | |_ _   _ _ __ ___   __   _| |    ) |
 | |\/| |/ _` | '__| |/ / _ \ __| |\/| |/ _ \| '_ ` _ \ / _ \ '_ \| __| | | | '_ ` _ \  \ \ / / |   / / 
 | |  | | (_| | |  |   <  __/ |_| |  | | (_) | | | | | |  __/ | | | |_| |_| | | | | | |  \ V /| |_ / /_ 
 |_|  |_|\__,_|_|  |_|\_\___|\__|_|  |_|\___/|_| |_| |_|\___|_| |_|\__|\__,_|_| |_| |_|   \_/ |_(_)____|
    """
    print(Fore.WHITE + banner_text + Style.RESET_ALL)

def print_instructions():
    print("\nThis program calculates statistics on trading volumes for selected tickers.")
    print("It will yield a list of companies based on their current momentum.\n")

def get_tickers_yfinance():
    # Print options for the user to select the source of ticker symbols.
    print("Choose your source of tickers:")
    print("1. Wikipedia S&P500 tickers")  # Option 1: Get tickers from Wikipedia's list of S&P 500 companies.
    print("2. Load a list from a CSV file")  # Option 2: Load tickers from a user-provided CSV file.
    
    # Prompt the user to make a choice between the two options.
    choice = input("Enter '1' for S&P500 or '2' for CSV file: ")

    # Validate user input. The loop continues to prompt the user until a valid input ('1' or '2') is received.
    while choice not in ['1', '2']:
        print("Invalid choice. Please enter '1' for S&P500 or '2' for CSV file.")
        choice = input("Enter your choice: ")

    # Depending on the user's choice, call the appropriate function:
    # If the user chooses '1', fetch tickers from Wikipedia using the `fetch_sp500_tickers` function.
    # If the user chooses '2', prompt for a CSV file path and load tickers from it using the `load_tickers_from_csv` function.
    return fetch_sp500_tickers() if choice == '1' else load_tickers_from_csv()


def fetch_sp500_tickers():
    # Use pandas to read HTML tables directly from the Wikipedia page listing S&P 500 companies.
    # This function grabs the first table encountered, which contains the list of companies.
    tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    
    # The 'Symbol' column in the DataFrame is where the ticker symbols are found. However, some symbols
    # may have dots ('.') which are typically replaced with hyphens ('-') for compatibility with certain 
    # finance APIs that expect hyphenated symbols. Here, a lambda function is applied to each symbol
    # to perform this replacement.
    return tickers['Symbol'].apply(lambda x: x.replace('.', '-')).tolist()


def load_tickers_from_csv():
    # Prompt the user to enter the path to a CSV file that contains ticker symbols.
    # This allows the user to utilize their own data source.
    file_path = input("\nEnter the path to your CSV file: ")
    
    # Check if the provided file path exists in the file system. If not, the user is prompted again.
    # This loop continues until a valid file path is provided, ensuring that the program does not proceed with an invalid path.
    while not os.path.exists(file_path):
        print("File not found. Please check whether your CSV is in the program's root.")
        file_path = input("Enter the path to your CSV file: ")
    
    # Once a valid file path is confirmed, the CSV file is read into a pandas DataFrame.
    # This function assumes that the ticker symbols are located in the first column of the CSV (hence `iloc[:, 0]`)
    # and returns a list of these symbols.
    return pd.read_csv(file_path, header=None).iloc[:, 0].tolist()


def request_long_period_for_average():
    # Display a message to guide the user in choosing the period for which the data's central tendency (mean or median) will be calculated.
    print ("\nYou're now choosing the period over which the central tendency will be computed.")
    print ("Be careful if you choose a short period, the central limit theorem will be 'less true' so to speak: ")
    
    # Define a list of valid time periods that the user can choose from. These are the time intervals accepted by yfinance for data retrieval.
    valid_formats = ['1mo', '2mo', '3mo', '4mo', '5mo', '6mo', '7mo', '8mo', '9mo', '10mo', '11mo', '1y', '2y', '3y', '4y', '5y', '6y', '7y', '8y', '9y', '10y', 'max']
    
    # Prompt the user to input a time period for the analysis. The input is normalized by stripping whitespace and converting to lower case to facilitate comparison.
    user_input = input("\nEnter the long period you want considered (1mo, 1y, max, etc.): ").strip().lower()

    # Keep requesting input from the user until a valid format is entered. This loop ensures the user adheres to the expected format, preventing errors in data retrieval.
    while user_input not in valid_formats:
        print("Please follow the formats accepted by yfinance")
        user_input = input("Enter the period again: ").strip().lower()
    
    # Once a valid period is entered, it is returned for use in fetching data.
    return user_input

def request_recent_volume():
    # Display options to the user for choosing the time period over which to analyze recent trading volumes.
    print("\nChoose the recent period for companies:")
    print("1. Yesterday's trading volume.")  # Option 1: Use yesterday's trading volume.
    print("2. Last three days' average.")    # Option 2: Use the average trading volume of the last three days.
    print("3. Last five days' average.")     # Option 3: Use the average trading volume of the last five days.
    
    # Prompt the user to select one of the given options by entering '1', '2', or '3'.
    choice = input("Enter '1', '2', or '3': ").strip()

    # If the user's input is not one of the valid choices, prompt them again until a valid input is provided.
    while choice not in ['1', '2', '3']:
        print("Invalid input. Please enter '1', '2', or '3'.")
        choice = input("Enter your choice again: ").strip()

    # Map the user's choice to a tuple that describes the slice of the dataset to use for calculations.
    # These slices are indices for pandas slicing to select the right days' volumes.
    slices = {'1': (-2, -1), '2': (-4, -1), '3': (-6, -1)}
    
    # Provide descriptions for each choice to use later in output or logging to clarify which period was selected.
    descriptions = {'1': "yesterday", '2': "last three days", '3': "last five days"}
    
    # Return the selected slice and its description based on the user's choice.
    return slices[choice], descriptions[choice]


def request_extremes_count():
    # Loop indefinitely until a valid input is received from the user.
    while True:
        try:
            # Prompt the user to enter the number of tickers they want to analyze in the final output table.
            count = int(input("\nHow many tickers would you like in the final table: "))
            
            # Check if the entered number is greater than 1. This is necessary as the analysis requires at least two tickers to make any comparative sense.
            if count > 1:
                # If a valid number is provided, exit the loop and return the count.
                return count
            # If the number is not greater than 1, prompt the user again.
            print("Please enter an integer greater than 1.")
        except ValueError:
            # If a ValueError occurs because the user input is not an integer, inform the user and continue prompting.
            print("Invalid input. Please enter a valid integer.")


def fetch_volume_data(tickers, period):
    # Initialize an empty dictionary to store volume data for each ticker.
    volume_data = {}

    # Iterate over each ticker symbol provided in the tickers list. The tqdm function is used to create a progress bar that shows the data fetching progress.
    for ticker in tqdm(tickers, desc="Fetching Volume Data"):
        try:
            # Retrieve historical data for the given ticker from Yahoo Finance, filtering for the 'Volume' column over the specified period.
            data = yf.Ticker(ticker).history(period=period)['Volume']
            
            # If the retrieved data is not empty, add it to the volume_data dictionary under the ticker's key.
            volume_data[ticker] = data if not data.empty else pd.Series()
        except Exception as e:
            # If an error occurs during data fetching (e.g., network issues, invalid ticker symbol), print an error message and continue with an empty series for that ticker.
            print(f"An error occurred for {ticker}: {e}")
            volume_data[ticker] = pd.Series()

    # Return the dictionary containing all fetched volume data.
    return volume_data

def analyze_volumes(volume_data, comparison_slice):
    # Initialize an empty dictionary to store results for each ticker.
    results = {}
    
    # Iterate over each ticker and its associated volume data provided in the volume_data dictionary.
    for ticker, data in volume_data.items():
        # Check if the data series for the ticker is not empty to prevent calculations on empty data.
        if not data.empty:
            # Calculate the mean of the volume data for the recent period specified by comparison_slice.
            recent_volume_mean = calculate_recent_volume_mean(data, comparison_slice)
            
            # Compute the median of the volume data to assess its central tendency.
            median_volume = np.median(data)
            
            # Compute the arithmetic mean of the volume data for overall understanding of volume magnitude.
            arithmetic_mean = np.mean(data)
            
            # Calculate the Z-score of the recent volume mean compared to the historical data to measure its deviation from the mean.
            z_score = calculate_z_score(data, recent_volume_mean)
            
            # Determine the percentile of the recent volume mean within the historical volume data, providing a position context.
            percentile = calculate_volume_percentile(data, recent_volume_mean)
            
            # Store the calculated metrics in the results dictionary under the ticker's key.
            results[ticker] = {
                "Percentile": percentile,
                "Z-score": z_score,
                "Median Volume": median_volume,
                "Arithmetic Mean": arithmetic_mean,
                "Recent Volumes": recent_volume_mean
            }
    
    # Return the dictionary containing all the analyzed results for each ticker.
    return results


def calculate_recent_volume_mean(data, period_slice):
    # Use pandas iloc indexing to slice the data series according to the period_slice tuple.
    # Calculate the mean of the specified slice of volume data.
    return data.iloc[period_slice[0]:period_slice[1]].mean()

def calculate_z_score(data, recent_volume):
    # Calculate the arithmetic mean of the entire data series for volume.
    arithmetic_mean = data.mean()
    
    # Calculate the standard deviation of the volume data. Using ddof=0 for population standard deviation.
    std_dev = data.std(ddof=0)
    
    # Compute the Z-score by subtracting the mean from the recent_volume and dividing by the standard deviation.
    # The Z-score indicates how many standard deviations an element is from the mean.
    return (recent_volume - arithmetic_mean) / std_dev

def calculate_volume_percentile(data, recent_volume_mean):
    # Calculate the percentile of the recent_volume_mean within the volume data.
    # This is done by finding the proportion of data points that are less than or equal to the recent_volume_mean and converting it to a percentage.
    return 100 * (np.sum(data <= recent_volume_mean) / len(data))


def sort_by_volume_extremity(results, count):
    # Sort the results dictionary by the extremity of volume percentile.
    # The key for sorting is the minimum of the percentile and 100 minus the percentile,
    # which effectively sorts tickers by how extreme their recent volume is compared to historical data.
    sorted_results = sorted(results.items(), key=lambda x: min(x[1]['Percentile'], 100 - x[1]['Percentile']))
    
    # Return the top 'count' entries from the sorted list, which contains the most extreme cases.
    return sorted_results[:count]

def fetch_additional_data(tickers):
    # Initialize a dictionary to store additional data for each ticker.
    additional_data = {}
    
    # Iterate over each ticker and fetch additional data such as P/E ratio and industry using Yahoo Finance's API.
    for ticker in tqdm(tickers, desc="Fetching P/E & Industry"):
        try:
            # Retrieve the ticker information from Yahoo Finance.
            info = yf.Ticker(ticker).info
            
            # Store the P/E Ratio and Industry in the additional_data dictionary under the ticker's key.
            # If data is not available, use numpy's nan for P/E and "Unknown" for Industry.
            additional_data[ticker] = {'PE Ratio': info.get('trailingPE', np.nan), 'Industry': info.get('industry', "Unknown")}
        except Exception as e:
            # If an error occurs during data fetching, print an error message and store nan and "Error" for P/E and Industry respectively.
            print(f"An error occurred fetching additional data for {ticker}: {e}")
            additional_data[ticker] = {'PE Ratio': np.nan, 'Industry': "Error"}
    
    # Return the dictionary containing the fetched additional data for each ticker.
    return additional_data


def merge_results(sorted_results, additional_data):
    # Update each entry in sorted_results with corresponding additional data fetched separately.
    for result in sorted_results:
        ticker = result[0]  # Extract the ticker symbol from the result tuple.
        # Update the results dictionary for this ticker with the additional data (P/E ratio and Industry).
        result[1].update(additional_data[ticker])

def display_results(results):
    # Create an instance of PrettyTable, which will be used to display the results in a tabular format.
    table = PrettyTable()
    # Define the column headers for the table that will display various financial metrics.
    table.field_names = ["Ticker", "Percentile of Volume", "Z-score", "P/E Ratio", "Industry", "Median Volume", "Arithmetic Mean", "Recent Vol. of Ex."]
    # Set the alignment of the entries in the table to right-aligned.
    table.align = "r"
    
    # Iterate through each ticker and its corresponding statistics in the results list.
    for ticker, stats in results:
        # Add a row to the table for each ticker, formatting numbers as needed and handling NaN values for the P/E ratio.
        table.add_row([
            ticker,
            f"{stats['Percentile']:.2f}",  # Format the percentile to two decimal places.
            f"{stats['Z-score']:.2f}",  # Format the Z-score to two decimal places.
            f"{stats['PE Ratio']:.2f}" if not np.isnan(stats['PE Ratio']) else "N/A",  # Check for NaN values in P/E Ratio.
            stats['Industry'],  # Include the industry information.
            f"{stats['Median Volume']:,.2f}",  # Format the median volume with comma separators.
            f"{stats['Arithmetic Mean']:,.2f}",  # Format the arithmetic mean with comma separators.
            f"{stats['Recent Volumes']:,.2f}"  # Format the recent mean volume with comma separators.
        ])
    
    # Print a header for the table display.
    print("\nStock Volume Analysis Results:")
    # Output the formatted table with all tickers and their respective metrics.
    print(table)


if __name__ == "__main__":
    main()
