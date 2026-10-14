
import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://www.python.org/jobs/"

pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Output file paths
raw_file_path = r"D:\Data Engineer\Job portal\job_info_raw.csv"
final_file_path = r"D:\Data Engineer\Job portal\job_posts.csv"


try:
    # Step 1: Fetch website data
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        print("Website connected successfully")

    except requests.exceptions.Timeout:
        print("Error: Website request timed out")
        raise

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        raise

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        raise

    # Step 2: Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Step 3: Find job container
    job_container = soup.find(
        "ol",
        class_="list-recent-jobs"
    )

    if not job_container:
        raise ValueError("Jobs container not found")

    jobs = job_container.find_all("li")

    print("Total jobs found:", len(jobs))

    # Step 4: Extract raw job information
    job_info = []

    for job in jobs:
        job_info.append(' '.join(job.prettify().split()))

    job_df = pd.DataFrame(job_info, columns=["Info"])

    job_df["Info"] = job_df["Info"].replace("", None)
    job_df = job_df.dropna(subset=["Info"])

    # Step 5: Save raw data to CSV
    try:
        job_df.to_csv(
            raw_file_path,
            index=False,
            encoding="utf-8-sig"
        )

        print("Raw data stored successfully")
        print("Raw file:", raw_file_path)

    except OSError as e:
        print(f"Error saving raw CSV file: {e}")
        raise

    # Step 6: Prepare lists for extracted fields
    job_titles = []
    companies = []
    posted_dates = []
    locations = []

    # Step 7: Extract job details from raw HTML
    for element in job_df["Info"]:

        try:
            job_soup = BeautifulSoup(
                str(element),
                "html.parser"
            )

            # Job title
            title_tag = job_soup.find("a")

            if title_tag:
                job_titles.append(
                    title_tag.get_text(strip=True)
                )
            else:
                job_titles.append("-")

            # Company
            company_tag = job_soup.find(
                "span",
                class_="listing-company-name"
            )

            if company_tag:
                company_lines = company_tag.get_text(
                    "\n",
                    strip=True
                ).split("\n")

                cleaned = []

                for item in company_lines:
                    item = item.strip()

                    if item and item != "New":
                        cleaned.append(item)

                if len(cleaned) >= 2:
                    companies.append(cleaned[-1])
                elif len(cleaned) == 1:
                    companies.append(cleaned[0])
                else:
                    companies.append("-")

            else:
                companies.append("-")

            # Posted date
            posted_tag = job_soup.find("time")

            if posted_tag:
                posted_dates.append(
                    posted_tag.get_text(strip=True)
                )
            else:
                posted_dates.append("-")

            # Location
            location_tag = job_soup.find(
                "span",
                class_="listing-location"
            )

            if location_tag:
                locations.append(
                    location_tag.get_text(" ", strip=True)
                )
            else:
                locations.append("-")

        except Exception as e:
            print(f"Error processing job: {e}")

            # Keep all lists aligned
            job_titles.append("-")
            companies.append("-")
            posted_dates.append("-")
            locations.append("-")

    # Step 8: Create cleaned DataFrame
    job_df = pd.DataFrame({
        "Job Title": job_titles,
        "Company": companies,
        "Posted Date": posted_dates,
        "Location": locations
    })

    print("\nExtracted Job Details:")
    print(job_df)

    # Step 9: Save final cleaned data to CSV
    try:
        job_df.to_csv(
            final_file_path,
            index=False,
            encoding="utf-8-sig"
        )

        print("\nJob data stored successfully")
        print("Final file:", final_file_path)

    except OSError as e:
        print(f"Error saving final CSV file: {e}")
        raise


except ValueError as e:
    print(f"Data or HTML error: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
