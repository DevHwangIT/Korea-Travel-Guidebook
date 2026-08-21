# -*- coding: utf-8 -*-
"""Long-form curated translations for remaining EN-copy strings."""
from __future__ import annotations

LONG: dict[str, dict[str, str]] = {}


def L(en: str, ja: str, zh: str, zht: str, vi: str, th: str, ru: str) -> None:
    LONG[en] = {"ja": ja, "zh": zh, "zh-Hant": zht, "vi": vi, "th": th, "ru": ru}


# Americano / sesame / Gyeongju
L(
    "Americano cooling candy packs coffee flavor with a cooling finish in a pocket tin. Sugar-free xylitol versions became a convenience-store trend.",
    "アメリカーノクーリングキャンディは、コーヒー風味と清涼感のティン缶キャンディ。無糖（キシリトール）表記が多く、携帯・記念おやつとしてコンビニで話題になりました。",
    "美式咖啡清凉糖是装在小铁盒里的咖啡味清凉糖果。无糖（木糖醇）款很多，作为便携纪念零食在便利店很火。",
    "美式咖啡清涼糖是裝在小鐵盒裡的咖啡味清涼糖果。無糖（木糖醇）款很多，作為便攜紀念零食在便利商店很夯。",
    "Kẹo làm mát Americano mang vị cà phê và cảm giác mát trong hộp thiếc bỏ túi. Bản không đường (xylitol) thành xu hướng ở cửa hàng tiện lợi.",
    "ลูกอมเย็นอเมริกาโน่ใส่รสกาแฟกับความเย็นในกระป๋องพกพา รุ่นไม่มีน้ำตาล (ไซลิทอล) ฮิตในร้านสะดวกซื้อ",
    "Охлаждающие конфеты Americano — кофейный вкус и свежесть в карманной банке. Безсахарные варианты с ксилитом стали трендом магазинов у дома.",
)
L(
    "Sugar-free is not calorie-free. High xylitol can upset the stomach if you eat too much—read the label.",
    "糖類0gでもカロリーがあることがあり、キシリトールを一度に多く摂るとお腹が痛くなることも。ラベルの量・注意を確認を。",
    "无糖不等于无热量。木糖醇一次吃太多可能闹肚子——请看标签。",
    "無糖不等於無熱量。木糖醇一次吃太多可能鬧肚子——請看標籤。",
    "Không đường không có nghĩa là không calo. Xylitol nhiều có thể đau bụng — đọc nhãn.",
    "ไม่มีน้ำตาลไม่ได้แปลว่าไม่มีแคลอรี ไซลิทอลเยอะอาจปวดท้อง — อ่านฉลาก",
    "Без сахара ≠ без калорий. Много ксилита может расстроить желудок — читайте этикетку.",
)
L(
    "Bangatgan (mill) sesame oil is pressed sesame oil used in namul, bibimbap, and marinades. Gift sets and small bottles are easy to find in markets and Korean grocery aisles.",
    "パンアッカン（搾油所）のごま油はナムル・ビビンバ・肉の下味に使う定番。ギフトセットや小瓶がマート・韓国食材コーナーに多いです。",
    "bangatgan（榨油坊）香油是拌菜、拌饭、腌肉常用的压榨芝麻油。礼盒和小瓶在超市、韩食货架很好找。",
    "bangatgan（榨油坊）香油是拌菜、拌飯、醃肉常用的壓榨芝麻油。禮盒和小瓶在超市、韓食貨架很好找。",
    "Dầu mè bangatgan (xưởng ép) dùng cho namul, bibimbap và ướp. Set quà và chai nhỏ dễ thấy ở chợ và kệ đồ Hàn.",
    "น้ำมันงา bangatgan (โรงคั้น) ใช้กับนามุล บิบิมบับ และหมัก มีชุดของขวัญและขวดเล็กในตลาด/มุมอาหารเกาหลี",
    "Кунжутное масло bangatgan (маслодавильня) — для намуль, пибимпапа и маринадов. Наборы и маленькие бутылки легко найти на рынках и в корейских рядах.",
)
L(
    "Store cool and away from light; use soon after opening. For flights, check liquids rules—checked baggage is safer than cabin for larger bottles.",
    "直射日光を避け涼しく保管し、開封後は早めに。航空の液体ルールを確認し、大きい瓶は預け入れが安全です。",
    "避光阴凉存放，开封后尽快用完。登机请核对液体规定——大瓶更适合托运。",
    "避光陰涼存放，開封後儘快用完。登機請核對液體規定——大瓶更適合托運。",
    "Bảo quản mát, tránh sáng; dùng sớm sau mở. Kiểm tra quy định chất lỏng — hành lý ký gửi an toàn hơn với chai lớn.",
    "เก็บเย็นห่างแสง ใช้เร็วหลังเปิด ตรวจกฎของเหลว — กระเป๋าโหลดปลอดภัยกว่าสำหรับขวดใหญ่",
    "Храните в прохладе без света; после вскрытия используйте быстрее. На рейсе смотрите правила жидкостей — крупные бутылки лучше в багаж.",
)
L(
    "Gyeongju sipwon (10-won) bread is a souvenir bake stamped like the 10-won coin—popular around downtown Gyeongju bakeries and tourist spots.",
    "慶州の十ウォンパンは10ウォン硬貨モチーフの記念パン。慶州市内のベーカリーや観光スポットで人気です。",
    "庆州十元面包是印有十元硬币图案的纪念烘焙，庆州市区面包店和景点很常见。",
    "慶州十元麵包是印有十元硬幣圖案的紀念烘焙，慶州市區麵包店和景點很常見。",
    "Bánh sipwon (10 won) Gyeongju là bánh kỷ niệm in hình đồng 10 won — phổ biến ở tiệm bánh và điểm du lịch trung tâm Gyeongju.",
    "ขนมปังสิบวอนเมืองคยองจูเป็นของฝากปั๊มลายเหรียญ 10 วอน — นิยมตามเบเกอรีและจุดท่องเที่ยวในเมือง",
    "Хлеб «сипвон» (10 вон) в Кёнджу — выпечка с оттиском монеты; популярен в пекарнях центра и у туристических точек.",
)
L(
    "Often same-day fresh with a short shelf life—eat soon. Harder to find outside Gyeongju.",
    "当日焼き・賞味が短いことが多いので早めに。慶州以外では手に入りにくいです。",
    "多为当日新鲜、保质期短——尽快吃。庆州以外较难买到。",
    "多為當日新鮮、保存期限短——儘快吃。慶州以外較難買到。",
    "Thường làm trong ngày, hạn ngắn — ăn sớm. Ngoài Gyeongju khó tìm hơn.",
    "มักสดวันเดียวกันอายุสั้น — กินเร็ว นอกคยองจูหายาก",
    "Часто свежий в день выпечки, короткий срок — ешьте скорее. Вне Кёнджу найти сложнее.",
)

# Continue with remaining via exec of embedded JSON built from hand map file
# Import companion dict if present
try:
    from _rest_long2 import LONG2  # type: ignore

    LONG.update(LONG2)
except ImportError:
    pass
