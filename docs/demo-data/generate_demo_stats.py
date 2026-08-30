"""
ダッシュボードのスクリーンショット撮影用に、架空だが自然な値のCSVを生成するスクリプト。

apex_stats.csv と同じ列構成(config.jsonのregions + season)で、実データは一切使わない。
season_*は乱数で生成し、career_*はseason_*を シーズン10以前の仮の起点値に積み上げて
算出するため、値同士の整合性(単調増加等)は実データと同様に保たれる。

実行方法:
    python docs/demo-data/generate_demo_stats.py
"""
import os

import numpy as np
import pandas as pd

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "demo_apex_stats.csv")

SEASONS = list(range(10, 25))  # 15シーズン分

# シーズン10より前の累積値の仮の起点(架空の値)
BASE = {
    "games": 12000,
    "wins": 620,
    "top5": 4100,
    "damage": 5_400_000,
    "kills": 11800,
    "deaths": 15200,
    "knockdowns": 15800,
    "assists": 9600,
    "revives": 5800,
    "respawns": 1500,
}


def generate():
    rng = np.random.default_rng(20260830)

    rows = []
    running = dict(BASE)
    running["damage_max"] = 0
    running["max_kills"] = 0
    running["win_streak"] = 0

    for season in SEASONS:
        season_games = int(rng.integers(300, 750))
        season_wins = int(rng.integers(8, 40))
        season_top5 = int(rng.integers(60, 220))
        season_damage = int(rng.integers(60_000, 300_000))
        season_damage_max = int(rng.integers(1200, 2500))
        season_damage_avg = round(float(rng.uniform(280, 520)), 2)
        season_kills = int(rng.integers(100, 550))
        season_deaths = int(rng.integers(200, 750))
        season_kdr = round(float(rng.uniform(0.35, 0.95)), 2)
        season_max_kills = int(rng.integers(4, 10))
        season_knockdowns = int(rng.integers(100, 750))
        season_assists = int(rng.integers(80, 550))
        season_win_streak = int(rng.integers(1, 4))
        season_revives = int(rng.integers(40, 350))
        season_respawns = int(rng.integers(8, 110))

        running["games"] += season_games
        running["wins"] += season_wins
        running["top5"] += season_top5
        running["damage"] += season_damage
        running["kills"] += season_kills
        running["deaths"] += season_deaths
        running["knockdowns"] += season_knockdowns
        running["assists"] += season_assists
        running["revives"] += season_revives
        running["respawns"] += season_respawns
        running["damage_max"] = max(running["damage_max"], season_damage_max)
        running["max_kills"] = max(running["max_kills"], season_max_kills)
        running["win_streak"] = max(running["win_streak"], season_win_streak)

        rows.append({
            "season": season,
            "career_games": running["games"],
            "career_wins": running["wins"],
            "career_top5": running["top5"],
            "career_damage": running["damage"],
            "career_damage_max": running["damage_max"],
            "career_damage_avg": round(running["damage"] / running["games"], 2),
            "career_kills": running["kills"],
            "career_deaths": running["deaths"],
            "career_kdr": round(running["kills"] / running["deaths"], 2),
            "career_max_kills": running["max_kills"],
            "career_knockdowns": running["knockdowns"],
            "career_assists": running["assists"],
            "career_win_streak": running["win_streak"],
            "career_revives": running["revives"],
            "career_respawns": running["respawns"],
            "season_games": season_games,
            "season_wins": season_wins,
            "season_top5": season_top5,
            "season_damage": season_damage,
            "season_damage_max": season_damage_max,
            "season_damage_avg": season_damage_avg,
            "season_kills": season_kills,
            "season_deaths": season_deaths,
            "season_kdr": season_kdr,
            "season_max_kills": season_max_kills,
            "season_knockdowns": season_knockdowns,
            "season_assists": season_assists,
            "season_win_streak": season_win_streak,
            "season_revives": season_revives,
            "season_respawns": season_respawns,
        })

    return pd.DataFrame(rows)


def main():
    df = generate()
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"生成: {OUTPUT_PATH}")
    print(df)


if __name__ == "__main__":
    main()
