# BGG Scrapper

BGG Scrapper is a Python-based package designed to scrape data from the BoardGameGeek (BGG) website using the BGG XML API2 and web scraping technologies. The extracted data is processed, stored in a SQLite database, and Ecel files.

![BGG Scrapper](https://github.com/weter123/bgg_scrapper/assets/17746651/83cde9f3-38ec-48ab-a8e5-fefd7952a9c4)

---

## ✨ Features

- **Data Extraction**: Fetch board game collection data using the BGG XML API.
- **Database Storage**: Store board games, mechanics, and designers in a structured SQLite database.
- **Excel Export**: Generate Excel files with multiple sheets for collections, mechanics, and designers.
- **Web Scraping**: Scrape advanced search results directly from the BGG website using `BeautifulSoup`.
- **Reports**: Display top game mechanics, board games, and designers based on the extracted data.

---

## 📋 Requirements

- **Python Version**: Python 3.x
- **Dependencies**:
  - `pandas`
  - `requests`
  - `sqlite3`
  - `openpyxl`
  - `BeautifulSoup` (for advanced web scraping)

---

## 🚀 Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/weter123/bgg_scrapper.git
   cd bgg_scrapper
2. **Install Required Packages**: Ensure you have `pip` installed. Then, run:
   ```bash
   pip install pandas requests openpyxl beautifulsoup4

## 🛠️ How to Use

### Extract Collection Data via BGG XML API

1. **Run the Main Script**:
   Execute the following command in your terminal:
   ```bash
   python extract_from_api.py

2. **Enter Your BGG Username**: When prompted, provide your BoardGameGeek username.

    When prompted, enter your BGG username.

3. **View Results**

   - The script will extract your game collection data.
   - It will store the data in:
      - A SQLite database: {username}.db
      - An Excel file: {username}.xlsx
---

### Scrape Advanced Search Results

1. **Run the Web Scraper Script**:
   Execute the following command in your terminal:
   ```bash
   python extract_from_bgg_table.py
2. **Input a Valid BGG Advanced Search URL**: Provide a valid URL from the advanced search page of the BoardGameGeek website.

3. View Results:
   - The script will extract and process the search results.
   - It will save the data to a timestamped Excel file, e.g., search_result_YYYY-MM-DD-HHMMSS.xlsx.
---

## Project Structure

- `extract_from_api.py`: Main script to extract and display BGG data.
- `bgg_log.txt`: Log file to track the progress of operations.
- `{username}.db`: SQLite database generated for each BGG username entered.
- `{username}.xlsx`: Excel file generated for each BGG username entered.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.



