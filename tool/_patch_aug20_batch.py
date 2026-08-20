#!/usr/bin/env python3
"""Patch travel tips + remove sipwon-ppang (Aug 20 batch)."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIPS_DIR = ROOT / "i18n" / "pages" / "travel-tips"
FOODS_DIR = ROOT / "i18n" / "pages" / "foods"
ROOT_I18N = ROOT / "i18n"

LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")

NEW_TIPS = {
    "ko": {
        "tabSurvey": "설문·개인정보",
        "surveyTitle": "설문·개인정보",
        "surveyMistake": "캠페인·기부 명목 설문에 개인정보를 무조건 적어 주는 것",
        "surveyBody": "거리나 역에서 캠페인·기부를 목적으로 설문이나 개인정보 작성을 강요하는 경우가 있습니다. 좋은 취지의 행사도 있지만, 가끔 개인정보를 부당하게 모으려는 경우도 있으니 내용을 확인한 뒤 신중하게 참여하세요. 불편하면 정중히 거절해도 됩니다.",
        "tabDelivery": "배달",
        "deliveryTitle": "늦은 시간 배달",
        "deliveryMistake": "피곤해도 꼭 식당에 가야 한다고 생각하는 것",
        "deliveryBody": "한국은 늦은 시간까지 배달이 잘 됩니다. 하루 종일 관광하거나 너무 힘들어 식당을 가기 어렵다면 배달앱(배민·쿠팡이츠 등)을 활용해 보세요. 숙소 주소만 정확히 입력하면 편하게 식사할 수 있습니다.",
        "tabSmoking": "흡연",
        "smokingTitle": "실내 금연·흡연장",
        "smokingMistake": "실내 식당·카페에서도 흡연해도 된다고 생각하는 것",
        "smokingBody": "한국은 법적으로 모든 실내가 금연 구역입니다. 담배는 건물 밖 지정 흡연장이나 별도 흡연 부스를 이용해 주세요. 실내에서 흡연하면 벌금 대상이 될 수 있습니다.",
        "tabSolicitation": "권유·구걸",
        "solicitationTitle": "지하철 권유·구걸",
        "solicitationMistake": "강요에 계속 맞서 대응하려는 것",
        "solicitationBody": "아주 드물지만 지하철 안에서 상품 권유나 구걸을 하는 경우가 있습니다. 응대하지 않아도 되며, 무시하고 자리를 옮기면 됩니다. 지나치게 따라오거나 불편하면 해당 역 무인민원센터나 지하철 고객센터(1577-1234)로 연락하세요.",
        "tabNoise": "소음",
        "noiseTitle": "대중교통 소음",
        "noiseMistake": "여행 중이라며 동행과 큰 소리로 떠드는 것",
        "noiseBody": "해외여행이라 기분이 들뜨더라도 지하철·버스 안에서는 목소리를 낮춰 주세요. 적당한 대화는 괜찮지만, 통화·영상·웃음소리가 크면 주변 승객에게 피해가 됩니다. 이어폰을 쓰고 볼륨을 조절하면 서로 편합니다.",
        "tabPriority": "임산부 배려석",
        "priorityTitle": "임산부 배려석",
        "priorityMistake": "분홍색 배려석에 그대로 앉아 있는 것",
        "priorityBody": "지하철·버스에는 분홍색 임산부 배려석이 있습니다. 임산부 배지를 착용한 분을 위한 좌석이므로, 해당하지 않으면 가급적 비워 두세요. 배지를 단 임산부·노약자 등이 필요할 때 양보해 주면 좋습니다.",
        "dailyCardDesc": "지도·쓰레기·주말 숙소·설문·배달·비 오는 날",
        "restaurantCardDesc": "주문·웨이팅·물·반찬·흡연",
        "transportCardDesc": "하차·환승·출퇴근·출구·매너·소음·배려석·권유",
        "catDailyIntro": "지도·쓰레기·주말 요금·설문·배달·비 오는 날처럼, 여행 중에 자주 맞닥뜨리는 일상 팁입니다.",
        "catRestaurantIntro": "주문·팁·웨이팅·셀프 코너·흡연 — 식당에서 바로 써먹는 팁입니다.",
        "catTransportIntro": "하차·환승, 출퇴근 혼잡, 지하철 출구, 매너·소음·배려석·권유 — 이동 중에 쓰는 팁입니다. 요금·카드 준비는 ‘떠나기 전에’를 보세요.",
    },
    "en": {
        "tabSurvey": "Surveys & privacy",
        "surveyTitle": "Street surveys & personal info",
        "surveyMistake": "Filling out every clipboard survey without checking why",
        "surveyBody": "You may be asked on the street or at stations to join a campaign or donation drive and write down personal details. Some are legitimate, but occasionally people push forms mainly to collect data. Read what it is for, and politely decline if you are unsure.",
        "tabDelivery": "Delivery",
        "deliveryTitle": "Late-night delivery",
        "deliveryMistake": "Thinking you must eat out even when exhausted",
        "deliveryBody": "Delivery works well in Korea late into the night. If you have been sightseeing all day or are too tired to go out, try apps like Baemin or Coupang Eats. Enter your lodging address correctly and you can eat comfortably in your room.",
        "tabSmoking": "Smoking",
        "smokingTitle": "Indoor smoking ban",
        "smokingMistake": "Assuming smoking is allowed inside restaurants or cafés",
        "smokingBody": "By law, smoking is banned in all indoor spaces in Korea. Use outdoor designated smoking areas or separate smoking booths. Smoking indoors can lead to fines.",
        "tabSolicitation": "Solicitation",
        "solicitationTitle": "Subway solicitation",
        "solicitationMistake": "Engaging repeatedly with aggressive solicitors",
        "solicitationBody": "Rarely, people may sell items or ask for money on the subway. You do not need to respond — ignore them or move seats. If someone follows you or makes you uncomfortable, contact the station office or subway customer center (1577-1234).",
        "tabNoise": "Noise",
        "noiseTitle": "Transit noise",
        "noiseMistake": "Talking loudly with friends as if the train is a party",
        "noiseBody": "It is fine to be excited on a trip, but keep your voice down on subways and buses. Normal conversation is okay; loud calls, videos, or laughter bother other riders. Earphones and lower volume help everyone.",
        "tabPriority": "Priority seats",
        "priorityTitle": "Pregnancy priority seats",
        "priorityMistake": "Sitting in pink priority seats when you do not need them",
        "priorityBody": "Subways and buses have pink priority seats for pregnant riders wearing a pregnancy badge. If that is not you, try to leave them empty. Offer the seat when someone who needs it boards.",
        "dailyCardDesc": "Maps, trash, weekend lodging, surveys, delivery, rain",
        "restaurantCardDesc": "Ordering, waiting, water, sides, smoking",
        "transportCardDesc": "Tap-out, rush hour, exits, etiquette, noise, priority seats, solicitation",
        "catDailyIntro": "Everyday tips you will run into while traveling — maps, trash, weekend rates, surveys, delivery, and rainy days.",
        "catRestaurantIntro": "Practical dining tips — ordering, tipping, waiting, self-serve corners, and smoking rules.",
        "catTransportIntro": "Getting around — tap-out, rush hour, exits, manners, noise, priority seats, and rare subway solicitation. For fares and cards, see Before You Go.",
    },
    "ja": {
        "tabSurvey": "アンケート・個人情報",
        "surveyTitle": "アンケート・個人情報",
        "surveyMistake": "キャンペーン名義のアンケートに無条件で個人情報を書くこと",
        "surveyBody": "街や駅でキャンペーン・寄付目的のアンケートや個人情報記入を強く勧められることがあります。善意の活動もありますが、個人情報収集が目的の場合もあるので内容を確認し、不安なら丁寧に断って構いません。",
        "tabDelivery": "デリバリー",
        "deliveryTitle": "夜遅いデリバリー",
        "deliveryMistake": "疲れていても必ず外食しなければならないと思うこと",
        "deliveryBody": "韓国は夜遅くまで配達が便利です。一日中観光して疲れたときは、バーミン・クーパンイーツなどの配達アプリを試してみてください。宿の住所を正確に入力すれば、部屋で食事できます。",
        "tabSmoking": "喫煙",
        "smokingTitle": "屋内禁煙・喫煙所",
        "smokingMistake": "店内レストラン・カフェでも喫煙できると思うこと",
        "smokingBody": "韓国では法律上、すべての屋内が禁煙です。たばこは屋外の指定喫煙所や喫煙ブースを利用してください。屋内喫煙は罰金の対象になることがあります。",
        "tabSolicitation": "勧誘・物乞い",
        "solicitationTitle": "地下鉄の勧誘・物乞い",
        "solicitationMistake": "しつこい勧誘に付き合い続けること",
        "solicitationBody": "ごく稀に、地下鉄内で物売りや物乞いをする人がいます。応じなくて大丈夫です。無視するか席を移動してください。つきまとわれたり不快なら、駅の案内所または地下鉄コールセンター（1577-1234）へ連絡を。",
        "tabNoise": "騒音",
        "noiseTitle": "公共交通の騒音",
        "noiseMistake": "旅行中だからと大声で騒ぐこと",
        "noiseBody": "旅行で盛り上がるのは自然ですが、地下鉄・バス内では声を控えめに。普通の会話は問題ありませんが、通話・動画・大きな笑い声は周囲の迷惑になります。イヤホンと音量調整を。",
        "tabPriority": "妊婦優先席",
        "priorityTitle": "妊婦優先席",
        "priorityMistake": "ピンク色の優先席にそのまま座ること",
        "priorityBody": "地下鉄・バスにはピンク色の妊婦優先席があります。妊婦バッジを付けた方のための席なので、該当しなければ空けておきましょう。必要な方が乗ったら譲ると良いです。",
        "dailyCardDesc": "地図・ゴミ・週末宿・アンケート・配達・雨の日",
        "restaurantCardDesc": "注文・待ち・水・おかず・喫煙",
        "transportCardDesc": "降車・乗換・ラッシュ・出口・マナー・騒音・優先席・勧誘",
        "catDailyIntro": "地図・ゴミ・週末料金・アンケート・配達・雨の日など、旅中によく出会う日常のヒントです。",
        "catRestaurantIntro": "注文・チップ・待ち・セルフコーナー・喫煙 — 食事場で使えるヒントです。",
        "catTransportIntro": "降車・乗換、ラッシュ、出口、マナー・騒音・優先席・勧誘 — 移動中のヒントです。運賃・カードは「出発前に」を参照。",
    },
    "zh": {
        "tabSurvey": "问卷·个人信息",
        "surveyTitle": "问卷与个人信息",
        "surveyMistake": "在活动或募捐名义的问卷上无条件填写个人信息",
        "surveyBody": "街上或车站可能有人以活动或募捐为由，要求填写问卷或个人信息。有些是正当活动，但也偶尔有人借此收集数据。请先看清内容，不确定时可以礼貌拒绝。",
        "tabDelivery": "外卖",
        "deliveryTitle": "深夜外卖",
        "deliveryMistake": "再累也必须去餐厅吃饭",
        "deliveryBody": "韩国深夜外卖很方便。如果整天观光太累，可以用 Baemin、Coupang Eats 等外卖 App，准确填写住宿地址即可在房间用餐。",
        "tabSmoking": "吸烟",
        "smokingTitle": "室内禁烟·吸烟区",
        "smokingMistake": "以为餐厅、咖啡馆室内可以吸烟",
        "smokingBody": "韩国法律规定所有室内场所禁烟。请在室外指定吸烟区或吸烟 booth 吸烟。室内吸烟可能被罚款。",
        "tabSolicitation": "推销·乞讨",
        "solicitationTitle": "地铁推销·乞讨",
        "solicitationMistake": "与强行推销或乞讨者持续纠缠",
        "solicitationBody": "极少见，但地铁上可能有人推销或乞讨。不必回应，忽略或换座位即可。若被纠缠或感到不安，请联系车站无人信访中心或地铁客服（1577-1234）。",
        "tabNoise": "噪音",
        "noiseTitle": "公共交通噪音",
        "noiseMistake": "旅行兴奋时与同伴大声喧哗",
        "noiseBody": "旅行心情可以理解，但在地铁、公交上请降低音量。普通交谈没问题，但大声通话、看视频或笑会打扰他人。请戴耳机并调低音量。",
        "tabPriority": "孕妇专座",
        "priorityTitle": "孕妇优先座",
        "priorityMistake": "占用粉色孕妇专座",
        "priorityBody": "地铁、公交有粉色孕妇优先座，供佩戴孕妇徽章的乘客使用。若不符合条件，请尽量空出。有需要的人上车时请让座。",
        "dailyCardDesc": "地图、垃圾、周末住宿、问卷、外卖、雨天",
        "restaurantCardDesc": "点餐、等位、水、小菜、吸烟",
        "transportCardDesc": "下车刷卡、高峰、出口、礼仪、噪音、专座、推销",
        "catDailyIntro": "旅行中常见的日常提示：地图、垃圾、周末房价、问卷、外卖、雨天等。",
        "catRestaurantIntro": "点餐、小费、等位、自助角、吸烟 — 在餐厅就能用的提示。",
        "catTransportIntro": "下车、换乘、高峰、出口、礼仪、噪音、专座、推销 — 出行提示。票价与交通卡见「出发前」。",
    },
    "zh-Hant": {
        "tabSurvey": "問卷·個人資訊",
        "surveyTitle": "問卷與個人資訊",
        "surveyMistake": "在活動或募捐名義的問卷上無條件填寫個人資訊",
        "surveyBody": "街上或車站可能有人以活動或募捐為由，要求填寫問卷或個人資訊。有些是正當活動，但也偶爾有人借此收集資料。請先看清楚內容，不確定時可以禮貌拒絕。",
        "tabDelivery": "外送",
        "deliveryTitle": "深夜外送",
        "deliveryMistake": "再累也必須去餐廳吃飯",
        "deliveryBody": "韓國深夜外送很方便。如果整天觀光太累，可以用 Baemin、Coupang Eats 等外送 App，準確填寫住宿地址即可在房間用餐。",
        "tabSmoking": "吸菸",
        "smokingTitle": "室內禁菸·吸菸區",
        "smokingMistake": "以為餐廳、咖啡館室內可以吸菸",
        "smokingBody": "韓國法律規定所有室內場所禁菸。請在室外指定吸菸區或吸菸 booth 吸菸。室內吸菸可能被罰款。",
        "tabSolicitation": "推銷·乞討",
        "solicitationTitle": "地鐵推銷·乞討",
        "solicitationMistake": "與強行推銷或乞討者持續糾纏",
        "solicitationBody": "極少見，但地鐵上可能有人推銷或乞討。不必回應，忽略或換座位即可。若被糾纏或感到不安，請聯絡車站無人信訪中心或地鐵客服（1577-1234）。",
        "tabNoise": "噪音",
        "noiseTitle": "大眾運輸噪音",
        "noiseMistake": "旅行興奮時與同伴大聲喧嘩",
        "noiseBody": "旅行心情可以理解，但在地鐵、公車上請降低音量。普通交談沒問題，但大聲通話、看影片或笑會打擾他人。請戴耳機並調低音量。",
        "tabPriority": "孕婦專座",
        "priorityTitle": "孕婦優先座",
        "priorityMistake": "占用粉色孕婦專座",
        "priorityBody": "地鐵、公車有粉色孕婦優先座，供佩戴孕婦徽章的乘客使用。若不符合條件，請盡量空出。有需要的人上車時請讓座。",
        "dailyCardDesc": "地圖、垃圾、週末住宿、問卷、外送、雨天",
        "restaurantCardDesc": "點餐、等位、水、小菜、吸菸",
        "transportCardDesc": "下車刷卡、高峰、出口、禮儀、噪音、專座、推銷",
        "catDailyIntro": "旅行中常見的日常提示：地圖、垃圾、週末房價、問卷、外送、雨天等。",
        "catRestaurantIntro": "點餐、小費、等位、自助角、吸菸 — 在餐廳就能用的提示。",
        "catTransportIntro": "下車、換乘、高峰、出口、禮儀、噪音、專座、推銷 — 出行提示。票價與交通卡見「出發前」。",
    },
    "vi": {
        "tabSurvey": "Khảo sát & thông tin cá nhân",
        "surveyTitle": "Khảo sát & thông tin cá nhân",
        "surveyMistake": "Điền thông tin cá nhân vào mọi phiếu khảo sát mà không kiểm tra",
        "surveyBody": "Trên phố hoặc ở ga, đôi khi người ta mời tham gia chiến dịch/từ thiện và yêu cầu điền thông tin cá nhân. Có hoạt động tốt, nhưng cũng có trường hợp thu thập dữ liệu không minh bạch. Hãy đọc kỹ và từ chối lịch sự nếu không chắc chắn.",
        "tabDelivery": "Giao đồ ăn",
        "deliveryTitle": "Giao đồ ăn khuya",
        "deliveryMistake": "Nghĩ rằng dù mệt cũng phải ra nhà hàng",
        "deliveryBody": "Hàn Quốc giao đồ ăn rất tốt cả khuya. Nếu đi tham quan cả ngày hoặc quá mệt, hãy thử Baemin, Coupang Eats… Nhập đúng địa chỉ chỗ ở là có thể ăn thoải mái trong phòng.",
        "tabSmoking": "Hút thuốc",
        "smokingTitle": "Cấm hút thuốc trong nhà",
        "smokingMistake": "Nghĩ có thể hút thuốc trong nhà hàng, quán cà phê",
        "smokingBody": "Theo luật Hàn Quốc, mọi không gian trong nhà đều cấm hút thuốc. Hãy dùng khu hút thuốc ngoài trời hoặc booth riêng. Hút trong nhà có thể bị phạt.",
        "tabSolicitation": "Chào hàng·xin tiền",
        "solicitationTitle": "Chào hàng·xin tiền trên tàu điện ngầm",
        "solicitationMistake": "Tiếp tục đối đáp với người chào hàng hoặc xin tiền",
        "solicitationBody": "Hiếm khi có người bán hàng hoặc xin tiền trên tàu điện ngầm. Bạn không cần phản hồi — bỏ qua hoặc đổi chỗ. Nếu bị theo hoặc khó chịu, liên hệ quầy dịch vụ ga hoặc tổng đài tàu điện ngầm (1577-1234).",
        "tabNoise": "Tiếng ồn",
        "noiseTitle": "Tiếng ồn trên phương tiện công cộng",
        "noiseMistake": "Nói to với bạn bè vì đang du lịch vui vẻ",
        "noiseBody": "Du lịch vui là đương nhiên, nhưng trên tàu điện ngầm và xe buýt hãy giữ giọng nhỏ. Trò chuyện bình thường được, nhưng gọi điện, xem video hay cười to sẽ làm phiền người khác. Dùng tai nghe và giảm âm lượng.",
        "tabPriority": "Ghế ưu tiên",
        "priorityTitle": "Ghế ưu tiên phụ nữ mang thai",
        "priorityMistake": "Ngồi ghế màu hồng dành cho phụ nữ mang thai",
        "priorityBody": "Tàu điện ngầm và xe buýt có ghế màu hồng dành cho phụ nữ mang thai đeo huy hiệu. Nếu không phải bạn, hãy để trống. Nhường ghế khi có người cần.",
        "dailyCardDesc": "Bản đồ, rác, chỗ ở cuối tuần, khảo sát, giao đồ ăn, ngày mưa",
        "restaurantCardDesc": "Gọi món, chờ, nước, món kèm, hút thuốc",
        "transportCardDesc": "Chạm thẻ xuống xe, giờ cao điểm, lối ra, phép lịch sự, tiếng ồn, ghế ưu tiên, chào hàng",
        "catDailyIntro": "Mẹo hàng ngày khi du lịch — bản đồ, rác, giá cuối tuần, khảo sát, giao đồ ăn, ngày mưa.",
        "catRestaurantIntro": "Mẹo ăn uống — gọi món, tip, chờ, tự phục vụ, hút thuốc.",
        "catTransportIntro": "Di chuyển — chạm thẻ, giờ cao điểm, lối ra, phép lịch sự, tiếng ồn, ghế ưu tiên, chào hàng. Về vé và thẻ, xem Trước khi đi.",
    },
    "th": {
        "tabSurvey": "แบบสอบถาม·ข้อมูลส่วนตัว",
        "surveyTitle": "แบบสอบถาม·ข้อมูลส่วนตัว",
        "surveyMistake": "กรอกข้อมูลส่วนตัวในแบบสอบถามทุกครั้งโดยไม่ตรวจสอบ",
        "surveyBody": "บนถนนหรือที่สถานี อาจมีคนชวนทำแคมเปญ/บริจาคและให้กรอกข้อมูลส่วนตัว มีทั้งกิจกรรมดีๆ และบางครั้งเก็บข้อมูลไม่โปร่งใส อ่านให้ชัดและปฏิเสธอย่างสุภาพหากไม่มั่นใจ",
        "tabDelivery": "เดลิเวอรี่",
        "deliveryTitle": "เดลิเวอรี่ดึก",
        "deliveryMistake": "คิดว่าแม้เหนื่อยก็ต้องไปร้านอาหาร",
        "deliveryBody": "เกาหลีส่งอาหารได้ดีแม้ดึก หากเที่ยวทั้งวันหรือเหนื่อยเกินไป ลอง Baemin, Coupang Eats ใส่ที่อยู่ที่พักให้ถูกต้องก็ทานในห้องได้สบาย",
        "tabSmoking": "การสูบบุหรี่",
        "smokingTitle": "ห้ามสูบในร่ม·จุดสูบบุหรี่",
        "smokingMistake": "คิดว่าสูบในร้านอาหารหรือคาเฟ่ได้",
        "smokingBody": "ตามกฎหมายเกาหลี ห้ามสูบในที่ในร่มทั้งหมด ใช้จุดสูบกลางแจ้งหรือบูธสูบบุหรี่ สูบในร่มอาจถูกปรับ",
        "tabSolicitation": "ชักชวน·ขอทาน",
        "solicitationTitle": "ชักชวน·ขอทานในรถไฟใต้ดิน",
        "solicitationMistake": "คุยโต้ตอบกับคนชักชวนหรือขอทานอย่างต่อเนื่อง",
        "solicitationBody": "หายาก แต่บางครั้งมีคนขายของหรือขอทานในรถไฟใต้ดิน ไม่ต้องตอบ — เพ игнорหรือย้ายที่นั่ง หากถูกตามหรือไม่สบายใจ ติดต่อเคาน์เตอร์สถานีหรือศูนย์ลูกค้ารถไฟใต้ดิน (1577-1234)",
        "tabNoise": "เสียงดัง",
        "noiseTitle": "เสียงดังบนขนส่งสาธารณะ",
        "noiseMistake": "คุยเสียงดังกับเพื่อนเพราะตื่นเต้นจากการเที่ยว",
        "noiseBody": "เที่ยวสนุกได้ แต่ในรถไฟใต้ดินและรถบัสควรลดเสียง คุยปกติได้ แต่โทรศัพท์ วิดีโอ หรือหัวเราะดังรบกวนผู้โดยสาร ใส่หูฟังและลดเสียง",
        "tabPriority": "ที่นั่งพิเศษ",
        "priorityTitle": "ที่นั่งพิเศษสำหรับคนท้อง",
        "priorityMistake": "นั่งที่นั่งสีชมพูสำหรับคนท้องทั้งที่ไม่ได้ท้อง",
        "priorityBody": "รถไฟใต้ดินและรถบัสมีที่นั่งสีชมพูสำหรับคนท้องที่สวมป้าย หากไม่ใช่คุณ ควรเว้นว่าง และให้ที่นั่งเมื่อมีคนต้องการ",
        "dailyCardDesc": "แผนที่ ถังขยะ ที่พักวันหยุด แบบสอบถาม เดลิเวอรี่ วันที่ฝนตก",
        "restaurantCardDesc": "สั่งอาหาร รอคิว น้ำ เครื่องเคียง สูบบุหรี่",
        "transportCardDesc": "แตะบัตรตอนลง ชั่วโมงเร่งด่วน ทางออก มารยาท เสียงดัง ที่นั่งพิเศษ ชักชวน",
        "catDailyIntro": "เคล็ดลับประจำวันระหว่างเที่ยว — แผนที่ ถังขยะ ราคาวันหยุด แบบสอบถาม เดลิเวอรี่ วันที่ฝนตก",
        "catRestaurantIntro": "เคล็ดลับร้านอาหาร — สั่ง ทิป รอคิว มุมบริการตนเอง สูบบุหรี่",
        "catTransportIntro": "การเดินทาง — แตะบัตร ชั่วโมงเร่งด่วน ทางออก มารยาท เสียงดัง ที่นั่งพิเศษ ชักชวน ดูค่าโดยสารที่ก่อนออกเดินทาง",
    },
    "ru": {
        "tabSurvey": "Опросы и личные данные",
        "surveyTitle": "Опросы и личные данные",
        "surveyMistake": "Заполнять любую анкету с личными данными без проверки",
        "surveyBody": "На улице или в метро могут просить участвовать в кампании или пожертвовании и оставить личные данные. Бывают благие акции, но иногда цель — сбор информации. Прочитайте, зачем это, и вежливо откажитесь, если сомневаетесь.",
        "tabDelivery": "Доставка",
        "deliveryTitle": "Доставка еды поздно вечером",
        "deliveryMistake": "Думать, что даже устав нужно идти в ресторан",
        "deliveryBody": "В Корее доставка работает хорошо и поздно ночью. Если вы устали после экскурсий, попробуйте Baemin, Coupang Eats — укажите адрес жилья и поешьте в номере.",
        "tabSmoking": "Курение",
        "smokingTitle": "Запрет курения в помещениях",
        "smokingMistake": "Думать, что в ресторане или кафе можно курить",
        "smokingBody": "По закону в Корее курение запрещено во всех помещениях. Пользуйтесь уличными зонами или будками для курения. Курение внутри может повлечь штраф.",
        "tabSolicitation": "Навязчивые просьбы",
        "solicitationTitle": "Навязчивые просьбы в метро",
        "solicitationMistake": "Долго вступать в разговор с навязчивыми людьми",
        "solicitationBody": "Редко, но в метро могут что-то продавать или просить деньги. Отвечать не обязательно — проигнорируйте или смените место. Если преследуют или некомфортно, обратитесь в офис станции или в кол-центр метро (1577-1234).",
        "tabNoise": "Шум",
        "noiseTitle": "Шум в транспорте",
        "noiseMistake": "Громко разговаривать с друзьями от радости путешествия",
        "noiseBody": "Радость понятна, но в метро и автобусах говорите тише. Обычный разговор допустим, но громкие звонки, видео и смех мешают другим. Наушники и тише — лучше для всех.",
        "tabPriority": "Приоритетные места",
        "priorityTitle": "Места для беременных",
        "priorityMistake": "Сидеть на розовых местах для беременных без нужды",
        "priorityBody": "В метро и автобусах есть розовые места для беременных со значком. Если это не вы, постарайтесь их не занимать. Уступайте, когда кто-то нуждается.",
        "dailyCardDesc": "Карты, мусор, жильё на выходные, опросы, доставка, дождь",
        "restaurantCardDesc": "Заказ, ожидание, вода, гарниры, курение",
        "transportCardDesc": "Выход, час пик, выходы, этикет, шум, приоритетные места, навязчивые просьбы",
        "catDailyIntro": "Повседневные советы в поездке — карты, мусор, цены на выходные, опросы, доставка, дождь.",
        "catRestaurantIntro": "Советы по ресторанам — заказ, чаевые, очередь, самообслуживание, курение.",
        "catTransportIntro": "Транспорт — выход, час пик, выходы, этикет, шум, места для беременных, навязчивые просьбы. Тарифы и карты — в разделе «Перед поездкой».",
    },
}

COVERS = {
    "surveyCover": "Images/travel-tips/survey.jpg",
    "deliveryCover": "Images/travel-tips/delivery.jpg",
    "smokingCover": "Images/travel-tips/smoking.jpg",
    "solicitationCover": "Images/travel-tips/solicitation.jpg",
    "noiseCover": "Images/travel-tips/noise.jpg",
    "priorityCover": "Images/travel-tips/priority.jpg",
}

BODY_LANGS = ("ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru")


def _body_block(prefix: str) -> dict:
    entry: dict = {"type": "text"}
    for lang in BODY_LANGS:
        p = NEW_TIPS[lang]
        entry[lang] = (
            f"{p[f'{prefix}Title']}\n\n{p[f'{prefix}Mistake']}\n\n{p[f'{prefix}Body']}"
        )
    return entry


NEW_DAILY_BLOCKS = [_body_block("survey"), _body_block("delivery")]
NEW_RESTAURANT_BLOCKS = [_body_block("smoking")]
NEW_TRANSPORT_BLOCKS = [
    _body_block("noise"),
    _body_block("priority"),
    _body_block("solicitation"),
]


def patch_travel_tips() -> None:
    for lang in LANGS:
        path = TIPS_DIR / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        tips = data["tips"]
        tips.update(NEW_TIPS[lang])
        for cover_key, src in COVERS.items():
            tips[cover_key] = [{"type": "image", "src": src}]

        tips.setdefault("dailyBody", []).extend(NEW_DAILY_BLOCKS)
        tips.setdefault("restaurantBody", []).extend(NEW_RESTAURANT_BLOCKS)
        tips.setdefault("transportBody", []).extend(NEW_TRANSPORT_BLOCKS)

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("patched tips", lang)


def remove_sipwon_from_json(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "sipwon-ppang" not in text:
        return False
    data = json.loads(text)
    changed = False
    for key in ("dishes",):
        block = data.get(key)
        if isinstance(block, dict) and "sipwon-ppang" in block:
            del block["sipwon-ppang"]
            changed = True
    items = data.get("items")
    if isinstance(items, dict) and "sipwon-ppang" in items:
        del items["sipwon-ppang"]
        changed = True
    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def remove_sipwon() -> None:
    sip_dir = ROOT / "pages" / "foods" / "desserts" / "sipwon-ppang"
    if sip_dir.exists():
        shutil.rmtree(sip_dir)
        print("removed", sip_dir)

    desserts_index = ROOT / "pages" / "foods" / "desserts" / "index.html"
    html = desserts_index.read_text(encoding="utf-8")
    block = re.search(
        r"\s*<article class=\"card\">\s*<a href=\"\./sipwon-ppang/index\.html\">.*?</article>",
        html,
        re.S,
    )
    if block:
        html = html[: block.start()] + html[block.end() :]
        desserts_index.write_text(html, encoding="utf-8")
        print("removed sipwon card from desserts index")

    for lang in LANGS:
        p = FOODS_DIR / f"{lang}.json"
        if remove_sipwon_from_json(p):
            print("removed sipwon from", p)

    for p in ROOT_I18N.glob("*.json"):
        if p.name.startswith("_"):
            continue
        if remove_sipwon_from_json(p):
            print("removed sipwon from", p)

    tags_path = ROOT / "data" / "food" / "recommend-tags.json"
    remove_sipwon_from_json(tags_path)


def main() -> None:
    patch_travel_tips()
    remove_sipwon()
    print("done")


if __name__ == "__main__":
    main()
