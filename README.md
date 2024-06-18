# BGG Scrapper
the goal is to create a package of python scripts that will be used to web scrap BoardGameGeek website using BGG XML API2 and web scrapping technology and load the extracted data into a database

![image](https://github.com/weter123/bgg_scrapper/assets/17746651/83cde9f3-38ec-48ab-a8e5-fefd7952a9c4)
# Extract Collection Data BoardGameGeek XML API 2 (extract_from_api.py)

This Python script extracts collection data from the BoardGameGeek (BGG) XML API, stores the data in a SQLite database, and displays tables of the top game mechanics, board games, and designers.

## Features

- Extracts game collection data from the BGG XML API.
- Stores data in a SQLite database.
- Displays top mechanics, board games, and designers based on the data.

## Requirements

- Python 3.x
- Required Python packages:
  - `pandas`
  - `requests`
  - `sqlite3`

## Setup Instructions

1. **Clone the Repository**

    ```bash
    git clone https://github.com/weter123/bgg_scrapper.git
    cd bgg_scrapper
    ```

2. **Install Required Packages**

    Ensure you have `pip` installed. If not, install it first. Then, run:

    ```bash
    pip install pandas requests
    ```

3. **Run the Script**

    ```bash
    python bgg_data_extractor.py
    ```

## How to Use

1. **Run the Script**

    Execute the script in your terminal or command prompt:

    ```bash
    python extract_from_api.py
    ```

2. **Enter Username**

    When prompted, enter your BGG username.

3. **View Results**

    The script will extract your game collection data, store it in a SQLite database named after your username, and display tables of the top mechanics, games, and designers.

## Project Structure

- `extract_from_api.py`: Main script to extract and display BGG data.
- `bgg_log.txt`: Log file to track the progress of operations.
- `{username}.db`: SQLite database generated for each BGG username entered.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any inquiries or support, please contact [your email](mailto:your.email@example.com).

