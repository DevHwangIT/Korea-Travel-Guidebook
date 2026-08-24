# -*- coding: utf-8 -*-
"""Add meals/desserts/convenience hubs for 2026-08-20 batch."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import urllib.request

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.content import create_dish  # noqa: E402
from lib.paths import VERSION_FILE  # noqa: E402
from lib.scaffold import current_asset_version  # noqa: E402

UA = "KoreaTravelGuidebook/1.0 (https://korea-guidebook.cloud; guidebook@local)"

DISHES = [
    {
        "kind": "meals",
        "slug": "jogae-gui",
        "emoji": "🦪",
        "texts": {
            "ko": {
                "title": "조개구이",
                "desc": "바닷가에서 즐기는 조개 구이 코스",
                "about": "조개구이는 가리비·바지락·키조개 등을 숯불이나 철판에 구워 먹는 한국 해변·포차 스타일 요리입니다. 버터·치즈·마늘을 올려 굽는 곳이 많고, 친구·가족 모임이나 여행지 저녁 코스로 인기입니다.",
            },
            "en": {
                "title": "Grilled clams (jogaegui)",
                "desc": "Seaside clam bake—butter, cheese, and garlic",
                "about": "Jogaegui is a Korean grilled-clam spread—scallops, manila clams, and similar shellfish cooked over charcoal or a griddle. Many spots add butter, cheese, or garlic. It is a favorite for groups and beach-town dinners.",
            },
            "ja": {
                "title": "チョゲグイ（貝焼き）",
                "desc": "海辺で楽しむ韓国風貝の炭火焼き",
                "about": "チョゲグイはホタテやアサリなどを炭火や鉄板で焼く韓国の海鮮料理です。バター・チーズ・ニンニクを乗せる店が多く、旅行先の夕食や少人数の集まりで人気です。",
            },
            "zh": {
                "title": "烤蛤蜊（조개구이）",
                "desc": "海边炭火烤贝类，常配黄油奶酪",
                "about": "烤蛤蜊是把扇贝、花蛤等放在炭火或铁板上烤的韩国海边料理。店家常加黄油、奶酪或蒜蓉，适合结伴旅行时的晚餐。",
            },
            "zh-Hant": {
                "title": "烤蛤蜊（조개구이）",
                "desc": "海邊炭火烤貝類，常配奶油起司",
                "about": "烤蛤蜊是把扇貝、花蛤等放在炭火或鐵板上烤的韓國海邊料理。店家常加奶油、起司或蒜蓉，適合結伴旅行時的晚餐。",
            },
            "vi": {
                "title": "Nghêu nướng (jogaegui)",
                "desc": "Hải sản nướng kiểu Hàn — bơ, phô mai, tỏi",
                "about": "Jogaegui là món nghêu/sò nướng than hoặc trên chảo của Hàn Quốc. Nhiều quán thêm bơ, phô mai, tỏi. Phù hợp ăn tối nhóm khi đi biển.",
            },
            "th": {
                "title": "หอยย่าง (โจแกกุย)",
                "desc": "หอยย่างถ่านแบบเกาหลี เนย ชีส กระเทียม",
                "about": "โจแกกุยคือหอยเชลล์ หอยลาย ฯลฯ ย่างถ่านหรือกระทะเหล็กสไตล์เกาหลี ร้านมักใส่เนย ชีส กระเทียม เป็นมื้อเย็นยอดนิยมตอนเที่ยวทะเล",
            },
            "ru": {
                "title": "Жареные моллюски (чогэгуи)",
                "desc": "Морской набор: моллюски на углях с маслом и сыром",
                "about": "Чогэгуи — корейская подача моллюсков на углях или противне. Часто добавляют масло, сыр и чеснок. Популярный ужин для компаний на побережье.",
            },
        },
    },
    {
        "kind": "meals",
        "slug": "korean-pasta",
        "emoji": "🍝",
        "texts": {
            "ko": {
                "title": "한국식 파스타",
                "desc": "크림·로제·해물 등 한국에서 즐기는 파스타",
                "about": "한국식 파스타는 이탈리아 원형보다 크림·로제·짬뽕 해물·불닭 등 한국 입맛에 맞춘 면 요리입니다. 패밀리 레스토랑과 캐주얼 이탈리안에서 쉽게 만날 수 있고, 밥·김치와 함께 내는 집도 있습니다.",
            },
            "en": {
                "title": "Korean-style pasta",
                "desc": "Cream, rose, and seafood pasta popular in Korea",
                "about": "Korean-style pasta leans cream, rose sauce, seafood jjamppong flavors, or spicy ‘buldak’ twists rather than strict Italian recipes. Family restaurants and casual Italian spots serve it widely—sometimes even with rice or kimchi on the side.",
            },
            "ja": {
                "title": "韓国風パスタ",
                "desc": "クリーム・ロゼ・海鮮など韓国で人気のパスタ",
                "about": "韓国風パスタはクリームやロゼ、海鮮チャンポン風、ブルダック風など韓国の味に合わせた麺料理です。ファミリーレストランやカジュアルなイタリアンでよく見かけます。",
            },
            "zh": {
                "title": "韩式意面",
                "desc": "奶油、玫瑰酱、海鲜等韩国常见意面",
                "about": "韩式意面更偏奶油、玫瑰酱、海鲜汤面风或辣火鸡面口味，不完全按意大利做法。家庭餐厅和休闲意面店很容易吃到。",
            },
            "zh-Hant": {
                "title": "韓式義大利麵",
                "desc": "奶油、玫瑰醬、海鮮等韓國常見義大利麵",
                "about": "韓式義大利麵偏奶油、玫瑰醬、海鮮湯麵風或辣雞麵口味，不完全按義式做法。家庭餐廳與休閒義麵店很容易吃到。",
            },
            "vi": {
                "title": "Pasta kiểu Hàn",
                "desc": "Sốt kem, rose, hải sản — phổ biến ở Hàn",
                "about": "Pasta kiểu Hàn nghiêng về sốt kem, rose, vị hải sản hoặc cay buldak hơn là công thức Ý chuẩn. Có ở nhà hàng gia đình và quán Italian casual.",
            },
            "th": {
                "title": "พาสต้าเกาหลี",
                "desc": "ครีม โรเซ่ ซีฟู้ด สไตล์เกาหลี",
                "about": "พาสต้าแบบเกาหลีเน้นซอสครีม โรเซ่ ซีฟู้ด หรือรสเผ็ดบุลดาค ไม่ยึดสูตรอิตาลีเป๊ะ พบได้ตามร้านแฟมิลี่และอิตาเลียนสบาย ๆ",
            },
            "ru": {
                "title": "Корейская паста",
                "desc": "Сливочный, розе и морепродукты по-корейски",
                "about": "Корейская паста чаще со сливочным или розовым соусом, морепродуктами или острым «пульдак», а не строго итальянская. Её легко найти в семейных и casual-ресторанах.",
            },
        },
    },
    {
        "kind": "desserts",
        "slug": "tteok",
        "emoji": "🍡",
        "texts": {
            "ko": {
                "title": "떡집",
                "desc": "인절미·가래떡·찰떡 등 전통 떡 가게",
                "about": "떡집은 인절미, 가래떡, 송편, 백설기 같은 한국 전통 떡을 파는 가게입니다. 명절·제사뿐 아니라 간식·선물용으로도 사고, 요즘 카페형 떡집에서는 아이스크림·앙버터 떡도 만납니다.",
            },
            "en": {
                "title": "Rice-cake shops (tteokjip)",
                "desc": "Injeolmi, garaetteok, and other traditional tteok",
                "about": "A tteokjip sells Korean rice cakes such as injeolmi, garaetteok, songpyeon, and baekseolgi. People buy them for holidays, snacks, and gifts. Newer café-style shops also serve ice-cream or butter-cream tteok.",
            },
            "ja": {
                "title": "トッ（餅）店",
                "desc": "インジョルミや棒餅など伝統トッ",
                "about": "トッ집은 인절미、棒餅、松餅など韓国の伝統餅を売る店です。祝日や贈り物だけでなくおやつにも買います。カフェ風の店ではアイスやあんバター餅もあります。",
            },
            "zh": {
                "title": "糕饼店（떡집）",
                "desc": "引切米、条糕等传统韩式糕",
                "about": "떡집卖引切米、条糕、松饼、白雪糕等韩国传统糕点。过节、送礼和当零食都会买。新式咖啡馆风的店也有冰淇淋或奶油夹心糕。",
            },
            "zh-Hant": {
                "title": "糕餅店（떡집）",
                "desc": "引切米、條糕等傳統韓式糕",
                "about": "떡집賣引切米、條糕、松餅、白雪糕等韓國傳統糕點。過節、送禮與當零食都會買。新式咖啡廳風的店也有冰淇淋或奶油夾心糕。",
            },
            "vi": {
                "title": "Tiệm bánh tteok",
                "desc": "Injeolmi, bánh gạo thanh và tteok truyền thống",
                "about": "Tiệm tteok bán bánh gạo Hàn như injeolmi, garaetteok, songpyeon. Mua vào lễ, làm quà hoặc ăn vặt. Tiệm kiểu cà phê còn có kem hoặc tteok bơ.",
            },
            "th": {
                "title": "ร้านต็อก",
                "desc": "อินจอลมี แถบต็อก และขนมข้าวเกาหลี",
                "about": "ร้านต็อกขายขนมข้าวเกาหลี เช่น อินจอลมี แถบต็อก ซงพยอน ซื้อช่วงเทศกาล ของฝาก หรือของว่าง ร้านสไตล์คาเฟ่มีไอศกรีมหรือต็อกเนยด้วย",
            },
            "ru": {
                "title": "Лавка тток (떡집)",
                "desc": "Инджольми, караэтток и другая рисовая выпечка",
                "about": "Ттокчип продаёт корейские рисовые пирожные: инджольми, караэтток, сонпхён. Их берут на праздники, в подарок и как перекус. В кафе-формате бывает тток с мороженым или маслом.",
            },
        },
    },
    {
        "kind": "desserts",
        "slug": "hotteok",
        "emoji": "🥞",
        "texts": {
            "ko": {
                "title": "호떡",
                "desc": "길거리 겨울 간식, 속은 흑임자·설탕·견과",
                "about": "호떡은 반죽을 둥글게 펴 속에 흑임자·설탕·견과를 넣고 철판에 지진 길거리 간식입니다. 겨울에 특히 따뜻하고, 명동·시장·포장마차에서 쉽게 만날 수 있습니다.",
            },
            "en": {
                "title": "Hotteok",
                "desc": "Stuffed Korean pancakes—brown sugar and nuts",
                "about": "Hotteok is a street pancake filled with brown sugar, cinnamon, seeds, or nuts, then pressed on a griddle. It is especially popular in winter at markets and stalls such as Myeongdong.",
            },
            "ja": {
                "title": "ホットク",
                "desc": "黒糖・ナッツ入りの屋台焼き餅",
                "about": "ホットクは生地に黒糖やナッツを入れて鉄板で焼く韓国の屋台スイーツです。冬に特に人気で、明洞や市場でよく見かけます。",
            },
            "zh": {
                "title": "糖饼（호떡）",
                "desc": "街头热饼，内馅红糖坚果",
                "about": "糖饼是把面皮摊开、包入红糖籽仁坚果后在铁板上烙的街头小吃。冬天尤其受欢迎，明洞和市场摊位很容易买到。",
            },
            "zh-Hant": {
                "title": "糖餅（호떡）",
                "desc": "街頭熱餅，內餡紅糖堅果",
                "about": "糖餅是把麵皮攤開、包入紅糖籽仁堅果後在鐵板上烙的街頭小吃。冬天尤其受歡迎，明洞與市場攤位很容易買到。",
            },
            "vi": {
                "title": "Hotteok",
                "desc": "Bánh rán đường nâu, hạt — món vỉa hè mùa đông",
                "about": "Hotteok là bánh rán nhân đường nâu, hạt, đổ trên chảo. Đặc biệt hợp mùa đông, dễ tìm ở Myeongdong và chợ.",
            },
            "th": {
                "title": "โฮต็อก",
                "desc": "แพนเค้กไส้น้ำตาลทรายแดง ถั่ว",
                "about": "โฮต็อกคือแพนเค้กเกาหลีไส้น้ำตาล งา ถั่ว ทอดบนกระทะ นิยมฤดูหนาว หาง่ายที่เมียงดงและตลาด",
            },
            "ru": {
                "title": "Хотток",
                "desc": "Уличная лепёшка с коричневым сахаром и орехами",
                "about": "Хотток — уличная лепёшка с коричневым сахаром, семенами и орехами, жареная на противне. Особенно зимой, легко найти в Мёндоне и на рынках.",
            },
        },
    },
    {
        "kind": "desserts",
        "slug": "eomuk-kkochi",
        "emoji": "🍢",
        "texts": {
            "ko": {
                "title": "어묵꼬치",
                "desc": "포장마차 국물 어묵, 길거리 간식",
                "about": "어묵꼬치는 꼬치에 꿴 어묵을 따뜻한 국물에 담가 파는 길거리 음식입니다. 포장마차·시장·편의점 핫바까지 종류가 다양하고, 추운 날 산책하며 먹기 좋습니다.",
            },
            "en": {
                "title": "Fish-cake skewers (eomuk)",
                "desc": "Pojangmacha broth fish cakes on a stick",
                "about": "Eomuk-kkochi is fish cake on a skewer, often kept in a hot savory broth at street stalls. You will also find grilled ‘hotbar’ versions at convenience stores. It is a classic cold-weather snack.",
            },
            "ja": {
                "title": "オムク串（魚肉練り串）",
                "desc": "屋台の出汁に浸した韓国風おでん串",
                "about": "オムク串は練り物を串に刺し、温かい出汁に入れて売る屋台フードです。市場やコンビニのホットバーもあり、寒い日の散歩おやつにぴったりです。",
            },
            "zh": {
                "title": "鱼饼串（어묵꼬치）",
                "desc": "路边摊热汤鱼饼串",
                "about": "鱼饼串是把鱼饼穿在签上、泡在热汤里卖的街头小吃。市场和便利店烤肠式‘핫바’也很多，适合冬天边走边吃。",
            },
            "zh-Hant": {
                "title": "魚餅串（어묵꼬치）",
                "desc": "路邊攤熱湯魚餅串",
                "about": "魚餅串是把魚餅穿在籤上、泡在熱湯裡賣的街頭小吃。市場與便利商店烤腸式「핫바」也很多，適合冬天邊走邊吃。",
            },
            "vi": {
                "title": "Xiên chả cá (eomuk)",
                "desc": "Chả cá nhúng nước dùng — món vỉa hè",
                "about": "Eomuk-kkochi là chả cá xiên, thường ngâm nước dùng nóng ở quán vỉa hè. Cửa hàng tiện lợi cũng bán loại nướng. Hợp ăn khi trời lạnh.",
            },
            "th": {
                "title": "เออมุกเสียบไม้",
                "desc": "ลูกชิ้นปลาเสียบไม้ในน้ำซุปข้างทาง",
                "about": "เออมุกคือลูกชิ้นปลาเสียบไม้แช่น้ำซุปร้อนตามร้านแผงลอย ร้านสะดวกซื้อก็มีแบบย่าง กินเพลินวันหนาว",
            },
            "ru": {
                "title": "Шашлычки омук",
                "desc": "Рыбные палочки в бульоне с уличной палатки",
                "about": "Омук-ккочи — рыбные палочки в горячем бульоне на уличных лотках. В магазинах бывает жареный «хотбар». Удобный зимний перекус.",
            },
        },
    },
    {
        "kind": "desserts",
        "slug": "sipwon-ppang",
        "emoji": "🍞",
        "texts": {
            "ko": {
                "title": "십원빵",
                "desc": "10원 주화 모양을 찍은 부드러운 크림 빵",
                "about": "십원빵은 빵 위에 10원짜리 주화 문양을 눌러 만든 비주얼 디저트입니다. 부드러운 빵과 생크림·커스터드가 들어가 기념 사진용·선물용으로 유명하고, 관광지 베이커리에서 자주 만납니다.",
            },
            "en": {
                "title": "Sipwon bread (10-won bun)",
                "desc": "Soft cream bun stamped with a 10-won coin",
                "about": "Sipwon-ppang is a soft bun pressed with the pattern of a 10-won coin. It is usually filled with cream or custard and is popular for photos and gifts at tourist bakeries.",
            },
            "ja": {
                "title": "10ウォンパン",
                "desc": "10ウォン硬貨の模様を押したクリームパン",
                "about": "10ウォンパンはパンに10ウォン硬貨の模様を押したビジュアルスイーツです。生クリームやカスタード入りが多く、観光地のベーカリーで写真映え・お土産として人気です。",
            },
            "zh": {
                "title": "十元面包",
                "desc": "压上10韩元硬币图案的奶油面包",
                "about": "十元面包是在面包上压出10韩元硬币花纹的网红甜点，多为鲜奶油或卡仕达馅，适合拍照和当伴手礼，旅游区面包店常见。",
            },
            "zh-Hant": {
                "title": "十元麵包",
                "desc": "壓上10韓元硬幣圖案的奶油麵包",
                "about": "十元麵包是在麵包上壓出10韓元硬幣花紋的網紅甜點，多為鮮奶油或卡士達餡，適合拍照與當伴手禮，觀光區麵包店常見。",
            },
            "vi": {
                "title": "Bánh 10 won",
                "desc": "Bánh kem đóng dấu đồng 10 won",
                "about": "Sipwon-ppang là bánh mềm đóng họa tiết đồng 10 won, thường nhân kem. Nổi tiếng để chụp ảnh và làm quà ở tiệm bánh khu du lịch.",
            },
            "th": {
                "title": "ขนมปังสิบวอน",
                "desc": "ขนมปังครีมปั๊มลายเหรียญ 10 วอน",
                "about": "ขนมปังสิบวอนคือขนมปังนุ่มปั๊มลายเหรียญ 10 วอน ไส้ครีมหรือคัสตาร์ด ฮิตสำหรับถ่ายรูปและของฝากตามร้านในแหล่งท่องเที่ยว",
            },
            "ru": {
                "title": "Хлеб «10 вон»",
                "desc": "Булочка с оттиском монеты в 10 вон",
                "about": "Сипвон-ппан — мягкая булочка с оттиском монеты 10 вон, обычно с кремом. Популярна для фото и сувениров в туристических пекарнях.",
            },
        },
    },
]

CONV = {
    "slug": "ice-cup-ade",
    "ko": {
        "Title": "얼음컵 에이드",
        "Desc": "편의점 얼음컵에 에이드·음료를 부어 먹는 여름 꿀조합",
        "pageTitle": "얼음컵 에이드 — 편의점 여름 음료",
        "lead": "한국 편의점에서는 큰 얼음컵을 산 뒤, 같은 매장의 에이드·탄산·커피를 부어 마시는 조합이 유명합니다. 더운 날 관광 중에 시원하게 들고 다니기 좋아요.",
        "tipTitle": "팁",
        "tip": "얼음컵은 계산대·냉동 코너에 있습니다. 에이드 원액은 너무 진하면 얼음이 녹으며 연해지니, 취향에 맞춰 양을 조절하세요. 매장 내 음료를 컵에 옮길 때 직원 안내를 따르는 것이 좋습니다.",
    },
    "en": {
        "Title": "Ice-cup ade",
        "Desc": "Convenience-store ice cup filled with ade or soda",
        "pageTitle": "Ice-cup ade — summer convenience drink",
        "lead": "In Korean convenience stores, people buy a large cup of ice and pour in bottled ade, soda, or coffee. It is a cheap way to stay cool while sightseeing.",
        "tipTitle": "Tip",
        "tip": "Ice cups are at the register or freezer. Ade gets milder as ice melts, so don’t overfill. Follow staff guidance if you pour drinks in-store.",
    },
    "ja": {
        "Title": "アイスカップ エイド",
        "Desc": "コンビニの氷カップにエイドや炭酸を注ぐ夏の組み合わせ",
        "pageTitle": "アイスカップ エイド — コンビニ夏ドリンク",
        "lead": "韓国のコンビニでは大きな氷カップを買い、同じ店のエイド・炭酸・コーヒーを注いで飲む組み合わせが人気です。暑い日の観光に持ち歩きやすいです。",
        "tipTitle": "ヒント",
        "tip": "氷カップはレジや冷凍コーナーにあります。氷が溶けると薄まるので量は調整を。店内で移すときは店員の案内に従ってください。",
    },
    "zh": {
        "Title": "冰杯汽水/果汁",
        "Desc": "便利店大冰杯倒入汽水或浓缩果汁",
        "pageTitle": "冰杯汽水 — 便利店夏日饮料",
        "lead": "韩国便利店可以买一大杯冰块，再把店里的果汁浓缩、汽水或咖啡倒进去喝。炎热观光时很方便随身带着。",
        "tipTitle": "提示",
        "tip": "冰杯在收银台或冷冻区。冰块融化会变淡，别倒太满。在店内倒饮料时请听店员说明。",
    },
    "zh-Hant": {
        "Title": "冰杯汽水／果汁",
        "Desc": "便利商店大冰杯倒入汽水或濃縮果汁",
        "pageTitle": "冰杯汽水 — 便利商店夏日飲料",
        "lead": "韓國便利商店可以買一大杯冰塊，再把店裡的果汁濃縮、汽水或咖啡倒進去喝。炎熱觀光時很方便隨身帶著。",
        "tipTitle": "提示",
        "tip": "冰杯在收銀台或冷凍區。冰塊融化會變淡，別倒太滿。在店內倒飲料時請聽店員說明。",
    },
    "vi": {
        "Title": "Ly đá ade",
        "Desc": "Ly đá cửa hàng tiện lợi đổ ade/nước ngọt",
        "pageTitle": "Ly đá ade — đồ uống mùa hè",
        "lead": "Ở cửa hàng tiện lợi Hàn, người ta mua ly đá lớn rồi đổ ade, soda hoặc cà phê. Tiện mang đi khi trời nóng.",
        "tipTitle": "Mẹo",
        "tip": "Ly đá ở quầy hoặc tủ đông. Đá tan sẽ loãng hơn. Làm theo hướng dẫn nhân viên nếu đổ tại quán.",
    },
    "th": {
        "Title": "แก้วน้ำแข็งเอด",
        "Desc": "แก้วน้ำแข็งร้านสะดวกซื้อเทน้ำเอด/โซดา",
        "pageTitle": "แก้วน้ำแข็งเอด — เครื่องดื่มฤดูร้อน",
        "lead": "ที่ร้านสะดวกซื้อเกาหลี นิยมซื้อแก้วน้ำแข็งใหญ่แล้วเทน้ำเอด โซดา หรือกาแฟ พกเดินเที่ยววันร้อนได้",
        "tipTitle": "ทิป",
        "tip": "แก้วน้ำแข็งอยู่ที่แคชเชียร์หรือช่องแช่แข็ง น้ำแข็งละลายจะจาง ทำตามคำแนะนำพนักงานถ้าเทในร้าน",
    },
    "ru": {
        "Title": "Ледяной стакан с айдом",
        "Desc": "Большой стакан льда из магазина + лимонад/газировка",
        "pageTitle": "Ледяной стакан с айдом — летний напиток",
        "lead": "В корейских магазинах берут большой стакан льда и наливают бутылочный айд, газировку или кофе. Удобно в жару на прогулке.",
        "tipTitle": "Совет",
        "tip": "Стаканы со льдом у кассы или в морозилке. По мере таяния напиток слабеет. Следуйте подсказкам персонала, если наливаете в магазине.",
    },
}

COVER_CANDIDATES = {
    "jogae-gui": [
        "https://commons.wikimedia.org/wiki/Special:FilePath/Grilled_scallops.jpg?width=1600",
        "https://commons.wikimedia.org/wiki/Special:FilePath/Barbecued_clams.jpg?width=1600",
        "https://upload.wikimedia.org/wikipedia/commons/8/8e/Grilled_scallops.jpg",
    ],
    "korean-pasta": [
        "https://commons.wikimedia.org/wiki/Special:FilePath/Spaghetti_alla_crema.jpg?width=1600",
        "https://commons.wikimedia.org/wiki/Special:FilePath/Pasta_with_cream_sauce.jpg?width=1600",
        "https://commons.wikimedia.org/wiki/Special:FilePath/Cream_spaghetti.jpg?width=1600",
    ],
    "tteok": [
        "https://commons.wikimedia.org/wiki/Special:FilePath/Injeolmi.jpg?width=1600",
        "https://commons.wikimedia.org/wiki/Special:FilePath/Korean.food-Tteok-01.jpg?width=1600",
        "https://upload.wikimedia.org/wikipedia/commons/4/4a/Injeolmi.jpg",
    ],
    "hotteok": [
        "https://commons.wikimedia.org/wiki/Special:FilePath/Hotteok_2.jpg?width=1600",
        "https://commons.wikimedia.org/wiki/Special:FilePath/Hotteok.jpg?width=1600",
        "https://commons.wikimedia.org/wiki/Special:FilePath/Korean_snack-Hotteok-01.jpg?width=1600",
    ],
    "eomuk-kkochi": [
        "https://commons.wikimedia.org/wiki/Special:FilePath/Korean_fishcake_bunsik_eoumuk_01.jpg?width=1600",
        "https://commons.wikimedia.org/wiki/Special:FilePath/Assorted_Eomuk.jpg?width=1600",
        "https://commons.wikimedia.org/wiki/Special:FilePath/Eomuk.jpg?width=1600",
    ],
    "sipwon-ppang": [],
    "ice-cup-ade": [],
}


def _download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=40) as res:
            data = res.read()
            ctype = (res.headers.get("Content-Type") or "").lower()
        if len(data) < 4000:
            return False
        if "html" in ctype or data[:15].lstrip().lower().startswith(b"<!doctype") or data[:6].lower().startswith(b"<html"):
            return False
        dest.write_bytes(data)
        return True
    except Exception as exc:  # noqa: BLE001
        print("download fail", url, exc)
        return False


def _ensure_analytics(html_path: Path) -> None:
    text = html_path.read_text(encoding="utf-8")
    if "js/analytics.js" in text:
        return
    needle = 'js/i18n.js'
    idx = text.find(needle)
    if idx < 0:
        return
    # find full script tag
    start = text.rfind("<script", 0, idx)
    end = text.find("</script>", idx)
    if start < 0 or end < 0:
        return
    tag = text[start : end + len("</script>")]
    prefix = tag.split("js/i18n.js")[0].rsplit('src="', 1)[-1]
    ver = ""
    if "?v=" in tag:
        ver = "?v=" + tag.split("?v=", 1)[1].split('"', 1)[0]
    insert = f'{tag}\n  <script src="{prefix}js/analytics.js{ver}"></script>'
    html_path.write_text(text.replace(tag, insert, 1), encoding="utf-8")


def add_convenience() -> None:
    slug = CONV["slug"]
    page_dir = ROOT / "pages" / "convenience-store" / slug
    page = page_dir / "index.html"
    version = current_asset_version() if VERSION_FILE.exists() else "0"
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "media").mkdir(exist_ok=True)
    page.write_text(
        f"""<!DOCTYPE html>
<html lang="ko" data-i18n-title="convenience.{slug}_pageTitle">
<head>
  <!-- asset-v: {version} -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{slug}</title>
  <link rel="stylesheet" href="../../../styles.css?v={version}">
</head>
<body>
  <nav class="lang-switch" aria-label="Language"></nav>
  <header class="site-header">
    <a href="../../../index.html" class="site-brand" data-i18n="common.brand">Korea Travel Guide</a>
  </header>
  <main class="page article-page">
    <p class="back-link"><a href="../index.html" data-i18n="convenience.backProducts"></a></p>
    <article class="combo-article">
      <img class="combo-article-hero" src="media/cover.jpg" alt="" data-i18n-attr="alt:convenience.{slug}_pageTitle">
      <h1 data-i18n="convenience.{slug}_pageTitle"></h1>
      <p class="article-lead" data-i18n="convenience.{slug}_lead"></p>
      <div class="tip">
        <h3 data-i18n="convenience.{slug}_tipTitle"></h3>
        <p data-i18n="convenience.{slug}_tip"></p>
      </div>
    </article>
  </main>
  <footer class="site-footer">
    <hr>
    <img src="../../../Images/cover/footer-korea.png" width="100%" alt="Korea Travel">
    <p class="footer-note" data-i18n="common.footer"></p>
  </footer>
  <script src="../../../i18n/messages.js?v={version}"></script>
  <script src="../../../js/i18n.js?v={version}"></script>
  <script src="../../../js/analytics.js?v={version}"></script>
</body>
</html>
""",
        encoding="utf-8",
        newline="\n",
    )

    hub = ROOT / "pages" / "convenience-store" / "index.html"
    html = hub.read_text(encoding="utf-8")
    card = f"""      <a class="combo-card" href="./{slug}/index.html">
        <img src="./{slug}/media/cover.jpg" alt="" data-i18n-attr="alt:convenience.{slug}Title">
        <div class="combo-body">
          <h3 data-i18n="convenience.{slug}Title"></h3>
          <p data-i18n="convenience.{slug}Desc"></p>
          <span class="combo-more" data-i18n="convenience.readMore"></span>
        </div>
      </a>
"""
    if f"./{slug}/index.html" not in html:
        marker = '      </a>\n    </div>\n\n    <h2 class="section-heading" data-i18n="convenience.comboTitle">'
        if marker not in html:
            raise SystemExit("convenience hub marker not found")
        html = html.replace(marker, "      </a>\n" + card + '    </div>\n\n    <h2 class="section-heading" data-i18n="convenience.comboTitle">', 1)
        hub.write_text(html, encoding="utf-8", newline="\n")

    bundle = i18n_store.load_all()
    for lang in i18n_store.LANGS:
        block = CONV.get(lang) or CONV["en"]
        conv = bundle[lang].setdefault("convenience", {})
        conv[f"{slug}Title"] = block["Title"]
        conv[f"{slug}Desc"] = block["Desc"]
        conv[f"{slug}_pageTitle"] = block["pageTitle"]
        conv[f"{slug}_lead"] = block["lead"]
        conv[f"{slug}_tipTitle"] = block["tipTitle"]
        conv[f"{slug}_tip"] = block["tip"]
    i18n_store.save_all(bundle)
    print("convenience", slug)


def main() -> None:
    missing_covers: list[str] = []
    for item in DISHES:
        slug, kind = item["slug"], item["kind"]
        page = ROOT / "pages" / "foods" / kind / slug / "index.html"
        if page.exists():
            print("exists", kind, slug)
        else:
            notes, _status = create_dish(kind, slug, item["texts"], emoji=item["emoji"])
            print("created", kind, slug, notes[-1] if notes else "")
        _ensure_analytics(page)
        dest = ROOT / "pages" / "foods" / kind / slug / "media" / "cover.jpg"
        ok = dest.is_file() and dest.stat().st_size > 4000
        if not ok:
            for url in COVER_CANDIDATES.get(slug, []):
                if _download(url, dest):
                    print("cover", slug, dest.stat().st_size)
                    ok = True
                    break
        if not ok:
            missing_covers.append(f"{kind}/{slug}")

    conv_page = ROOT / "pages" / "convenience-store" / CONV["slug"] / "index.html"
    if not conv_page.exists():
        add_convenience()
    else:
        print("exists convenience", CONV["slug"])
    conv_cover = conv_page.parent / "media" / "cover.jpg"
    if not (conv_cover.is_file() and conv_cover.stat().st_size > 4000):
        missing_covers.append("convenience/" + CONV["slug"])

    tags_path = ROOT / "data" / "food" / "recommend-tags.json"
    tags = json.loads(tags_path.read_text(encoding="utf-8"))
    items = tags.setdefault("items", {})
    items["jogae-gui"] = {"tags": ["seafood", "grill", "warm", "nosoup", "hearty"]}
    items["korean-pasta"] = {"tags": ["noodles", "mild", "nosoup", "warm"]}
    items["tteok"] = {"tags": ["sweet", "bakery", "mild", "portable"]}
    items["hotteok"] = {"tags": ["sweet", "street", "warm", "quickbite"]}
    items["eomuk-kkochi"] = {"tags": ["street", "warm", "quickbite", "portable"]}
    items["sipwon-ppang"] = {"tags": ["sweet", "bakery", "quickbite"]}
    items["ice-cup-ade"] = {"tags": ["drink", "cold", "sweet"]}
    tags_path.write_text(json.dumps(tags, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    out = ROOT / "tool" / "_missing_covers.json"
    out.write_text(json.dumps(missing_covers, ensure_ascii=False, indent=2), encoding="utf-8")
    print("MISSING", missing_covers)


if __name__ == "__main__":
    main()
