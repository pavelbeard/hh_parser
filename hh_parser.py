import json
import random
import time
import pandas as pd
import requests
import user_agent
import tqdm

url = "https://api.hh.ru/vacancies"
headers = {
    "User-Agent": user_agent.generate_user_agent(),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}


def save_data(filename, data):
    """Saving data in a json file"""
    with open(filename, mode="w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def parse_hh(text="python", experience=None, employment=None, schedule=None) -> dict:
    """Download a data from HeadHunter.ru"""
    params = {
        "per_page": 100,
        "page": 0,
        "text": text,
        "experience": experience,
        "employment": employment,
        "schedule": schedule,
    }

    res = requests.get(url=url, headers=headers, params=params)

    if not res.ok:
        print("Error: ", res)
        return {}

    vacancies = res.json()["items"]
    pages = res.json()["pages"]

    for page in tqdm.trange(1, pages):
        params["page"] = page
        res = requests.get(url=url, headers=headers, params=params)

        if res.ok:
            res_data = res.json()
            vacancies.extend(res_data["items"])
        else:
            print(res)

    save_data(filename="vacancies.json", data=vacancies)

    return vacancies


def get_full_descriptions(vacancies):
    """Download full descriptions of the vacations (it works may be to 20 min)"""
    vacancies_full = []

    for entry in tqdm.tqdm(vacancies):
        vacancy_id = entry["id"]
        description = requests.get(url=f"{url}/{vacancy_id}")
        vacancies_full.append(description.json())
        print(description.json())
        time.sleep(random.uniform(0.2, 1))

    save_data("vacancies_full.json", vacancies_full)

    return vacancies_full


def main():
    """main function that do a parsing a site with vacancies HeadHunter.ru"""
    vacancies = parse_hh(text="python")
    vacancies_full = get_full_descriptions(vacancies)

    # creating files with list of vacancies and their descriptions
    pd.DataFrame(vacancies).to_excel("List of vacancies.xlsx")
    pd.DataFrame(vacancies_full).to_excel("List of vacancies description.xlsx")


if __name__ == "__main__":
    main()
