#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill remaining zh-Hant body blocks that only had ko/en/ja."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
hant = json.loads((ROOT / "zh-Hant.json").read_text(encoding="utf-8"))

FILLS = {
    ("beforeTrip", "packBody", 4): "回國前請在行李箱留購物空間。Olive Young、Daiso、零食禮物體積容易快速佔滿。",
    ("beforeTrip", "soloBody", 5): "小貼士：歡迎獨食的店家（吧台座、一人套餐）越來越多。可在地圖搜尋「혼밥／honbap」或「1人座」。",
    ("tips", "restaurantBody", 2): "重點：韓國餐廳通常不給小費。請在櫃檯依收據金額結帳即可。",
    ("souvenir", "maskBody", 2): "購買提示\n\n請確認 KF94 標示與包裝日期。大量送禮時，藥局整包通常最穩妥。",
    ("souvenir", "stationeryBody", 2): "購買提示\n\n送禮選附盒套組；自用則選補充包／單品較划算。",
    ("souvenir", "oliveBody", 2): "購買提示\n\n明洞、弘大、江南大型店庫存通常比機場店充足。可向店員詢問 App 優惠券與贈品組合。",
    ("souvenir", "daisoBody", 2): "購買提示\n\n結帳前先秤重，優先挑選能塞進行李箱縫隙的小物。",
    ("souvenir", "snackBody", 2): "購買提示\n\n獨立包裝的 Pepero 多入組方便分送。注意航空行李重量與體積限制。",
    ("souvenir", "ramenBody", 2): "購買提示\n\n先逛 Emart／Homeplus 泡麵特價區，便利商店只當補缺。",
    ("souvenir", "teaBody", 2): "購買提示\n\n正官庄建議在官方或大型通路購買，降低買到仿冒的風險。",
    ("souvenir", "honeyBody", 2): "購買提示\n\n有密封標籤與有效期限的瓶裝，比市場散裝更適合送禮與通關。",
    ("souvenir", "socksBody", 2): "購買提示\n\n3／5 雙組合包通常比單雙划算，也容易塞進行李箱縫隙。",
    ("souvenir", "sheetBody", 2): "購買提示\n\n送禮優先選有效期限清楚、附英文說明的套組。",
    ("souvenir", "sunscreenBody", 2): "購買提示\n\n先看 Olive Young 防曬區的「Olive Young Picks」與迷你組合。",
    ("souvenir", "lipstickBody", 2): "購買提示\n\n可請店員推薦 mute／暖色調。注意試用衛生，並保留收據以利退換。",
    ("souvenir", "kpopBody", 2): "購買提示\n\n高價二手小卡請仔細確認是否為正品。",
    ("fun", "noraebangBody", 2): "價格感覺\n\n約每首歌 ₩500–₩1,000，或短時段套票——依店家與時段而異。",
    ("fun", "noraebangBody", 3): "使用提示\n\n週末夜晚可能需等候。請控制音量、愛惜麥克風與設備。",
    ("fun", "mangaBody", 2): "價格感覺\n\n多為每小時數千韓元加飲料；部分店有深夜／全日票。",
    ("fun", "mangaBody", 3): "使用提示\n\n遵守飲食規定，保持安靜，拍照前先詢問。離開前請到櫃檯結帳。",
    ("fun", "boardgameBody", 2): "價格感覺\n\n常見為每人每小時數千至約 ₩10,000，並需點飲料。",
    ("fun", "boardgameBody", 3): "使用提示\n\n注意零件是否齊全；可先問是否有英文規則書。",
    ("fun", "unmannedBody", 2): "價格感覺\n\n與便利商店相近（有時稍便宜）。部分深夜仍營業。",
    ("fun", "unmannedBody", 3): "使用提示\n\n外國卡若刷不過請備替代支付。門鎖著時請閱讀門上貼紙的入場說明。",
    ("fun", "photoboothBody", 2): "價格感覺\n\n多為每組（4 姿勢）₩4,000–₩6,000。加洗／周邊依店而異。",
    ("fun", "photoboothBody", 3): "使用提示\n\n整理隨身行李、遵守使用時間，照片請平放打包當紀念品。",
}

n = 0
for (sec, key, idx), text in FILLS.items():
    hant[sec][key][idx]["zh-Hant"] = text
    n += 1

(ROOT / "zh-Hant.json").write_text(
    json.dumps(hant, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(f"filled {n} bodies")
