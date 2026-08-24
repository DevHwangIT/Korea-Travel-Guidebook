#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build vi/th/ru priority section overlays from embedded translations."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EN = json.loads((ROOT / "_en_priority_plain.json").read_text(encoding="utf-8"))


def save(lang: str, data: dict) -> None:
    # Split into section files expected by _apply_locale_overlays.py
    for sec, payload in data.items():
        path = ROOT / f"{lang}_{sec}.json"
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {path.name} ({len(payload)} keys)")


# --- Vietnamese ---
VI = {
    "beforeTrip": {
        "pageTitle": "Trước khi đi | Korea Travel Guide",
        "title": "Trước khi đi",
        "intro": "Hướng dẫn những việc cần chuẩn bị và kiểm tra trước khi khởi hành. Mẹo trong chuyến đi xem mục Mẹo du lịch.",
        "backHub": "← Trước khi đi",
        "tabDocs": "Giấy tờ",
        "tabMoney": "Tiền mặt · Thẻ",
        "tabConnect": "Data · Viễn thông",
        "tabPower": "Điện · Phích cắm",
        "tabPack": "Hành lý · Đặt chỗ",
        "tabTaxi": "Taxi",
        "docsTitle": "Giấy tờ du lịch",
        "docs1": "Kiểm tra hộ chiếu còn hạn (thường ≥6 tháng sau ngày về) và xem có cần visa hoặc K-ETA không.",
        "docs2": "Chuẩn bị địa chỉ khách sạn, mục đích lưu trú và vé khứ hồi. Khai e-Arrival (ERI) ở tab riêng.",
        "docs3": "Bảo hiểm du lịch giúp chi phí y tế, mất đồ và chậm chuyến.",
        "moneyTitle": "Tiền mặt, thẻ, giao thông",
        "money1": "Thẻ phổ biến, nhưng chợ và một số quán cần tiền mặt — mang khoảng ₩50,000–100,000.",
        "money2": "So sánh đổi tiền sân bay/trung tâm và ATM; kiểm tra phí giao dịch nước ngoài.",
        "money3": "Mua thẻ giao thông kiểu T-money ngay ngày đầu. Xem tab Wow Pass cho thẻ trả trước du khách.",
        "connectTitle": "SIM, eSIM, data",
        "connect1": "Lấy eSIM hoặc SIM để có data — chỉ Wi-Fi miễn phí thường không đủ cho bản đồ.",
        "connect2": "Cài và đăng nhập bản đồ (Naver/Kakao), dịch (Papago) và nhắn tin trước khi bay.",
        "connect3": "Ghi lại bước cài và kích hoạt eSIM để bản đồ chạy ngay khi hạ cánh.",
        "powerTitle": "Điện và phích cắm",
        "power1": "Hàn Quốc dùng 220V và phích Type C/F (chân tròn). Khách sạn cũng vậy.",
        "power2": "Thiết bị Type A (chân dẹt) cần đầu chuyển. Hầu hết sạc 100–240V nên chỉ cần adapter.",
        "power3": "Sạc dự phòng và củ sạc nhiều cổng giúp dùng app cả ngày.",
        "packTitle": "Hành lý, chỗ ở, thời tiết",
        "pack1": "Seoul đi bộ nhiều — mang đồ theo mùa và giày êm.",
        "pack2": "Mùa cao điểm đặt sớm; ghi giờ nhận phòng và gửi hành lý.",
        "pack3": "Mang thuốc quen dùng, đồ vệ sinh và khẩu trang dự phòng.",
        "pack4": "Chừa chỗ vali cho Olive Young, Daiso và snack mang về — dễ đầy nhanh.",
        "taxiTitle": "Giá taxi & mẹo",
        "taxi1": "Từ 2026, taxi trung (thường) ở Seoul mở cửa ₩4,800 cho 1,6 km đầu, sau đó tính theo quãng đường và thời gian.",
        "taxi2": "Đêm khuya (22:00–4:00) phụ khoảng 20% hoặc 40% tùy giờ. Thành phố khác có thể khác giá.",
        "taxi3": "Bắt ngoài đường hoặc gọi Kakao T. Thẻ phổ biến; không cần tip.",
        "taxi4": "Chỉ đường ô tô trên Naver/Kakao Map thường hiện ước tính cước. Chặt chém hiếm; app là lựa chọn an tâm.",
        "tabSolo": "Ăn một mình",
        "soloTitle": "Ăn một mình ở Hàn Quốc",
        "solo1": "Vì sao ăn một mình có thể khó\n\nVăn hóa ăn uống Hàn thường giả định chia sẻ. Suất tối thiểu 2 người (samgyeopsal, dakgalbi), bàn đầy món và chuẩn mực xã hội khiến vào quán một mình hơi ngại.",
        "solo2": "Nếu phải đi một mình\n\nChọn quán thân thiện 1 người: kimbap, quán ăn vặt, set đơn giản, stay-café, fast-casual, đồ tiện lợi. Nói ngắn “một người” thường được xếp chỗ. Kiosk/đặt qua app cũng giúp.",
        "solo3": "Hẹn bạn nếu được\n\nĂn với bạn bản địa, bạn học hoặc partner trao đổi ngôn ngữ dễ hơn và mở thêm nhiều quán. Hẹn trước chuyến đi để tránh stress ăn một mình.",
        "tabImmigration": "Nhập cảnh (SES)",
        "immigrationTitle": "Nhập cảnh tự động (SES)",
        "immigration1": "SES (Smart Entry Service) là nhập cảnh tự động qua cổng riêng bằng hộ chiếu và sinh trắc. Nếu đủ điều kiện thường nhanh hơn quầy nhân viên.",
        "immigration2": "Dành cho người nước ngoài đã đăng ký, một số quốc tịch và khách đăng ký trước. Có thể gắn tem/nhãn SES trên hộ chiếu. Xác nhận trên trang Immigration / Hi Korea.",
        "immigration3": "Ở sân bay, theo biển SES / nhập cảnh tự động. Nếu không đủ điều kiện, dùng quầy người nước ngoài thường.",
        "catEntry": "Nhập cảnh",
        "catMoney": "Tiền bạc",
        "catLife": "Đời sống",
        "catDining": "Ăn uống",
        "catEntryIntro": "Giấy tờ, e-Arrival (ERI) và nhập cảnh sân bay — kiểm tra trước khi hạ cánh.",
        "catMoneyIntro": "Tiền mặt, thẻ, thẻ giao thông và Wow Pass cho du khách.",
        "catLifeIntro": "Data và điện, hành lý và chỗ ở, giao thông và taxi, cùng vài lời chào cơ bản cho ngày đầu.",
        "catDiningIntro": "Văn hóa ăn uống và ăn một mình — nên biết trước khi đến.",
        "tabEri": "e-Arrival (ERI)",
        "tabWowpass": "Wow Pass",
        "eriTitle": "Thẻ e-Arrival (ERI)",
        "wowpassTitle": "Wow Pass",
        "eri1": "e-Arrival Card là tờ khai nhập cảnh trực tuyến của Hàn (thường gọi ERI). Tách biệt với K-ETA và Q-CODE thời COVID.",
        "eri2": "Khai từ 3 ngày trước khi đến (giờ Hàn). Hiệu lực hết sau 72 giờ kể từ lúc gửi. Cổng chính thức miễn phí.",
        "eri3": "Nộp tại https://www.e-arrivalcard.go.kr với hộ chiếu và thông tin lưu trú. Số tờ khai sẽ gửi email.",
        "wowpass1": "Wow Pass là thẻ trả trước cho du khách, thường dùng mua sắm và đi lại kiểu T-money.",
        "wowpass2": "Phát hành/nạp tại kiosk sân bay/ga/khách sạn; xem số dư trong app. Ví mua sắm và giao thông thường tách.",
        "wowpass3": "Nếu đã có thẻ không phí FX, thẻ T-money đơn giản có thể đủ — chọn theo nhu cầu.",
        "catPickLabel": "Chủ đề",
        "catSchedule": "Lịch trình",
        "catScheduleIntro": "Ngày lễ và giai đoạn đi lại khó hơn — hữu ích khi chọn ngày.",
        "tabHolidays": "Ngày lễ",
        "tabAvoid": "Giai đoạn khó hơn",
        "holidaysTitle": "Ngày lễ Hàn Quốc",
        "avoidTitle": "Thời điểm đi khó hơn",
        "holidays1": "Ngày dương cố định: Tết Dương lịch (1/1), Ngày Phong trào Độc lập (3/1), Ngày Thiếu nhi (5/5), Ngày Tưởng niệm (6/6), Ngày Giải phóng (8/15), Ngày Quốc khánh (10/3), Ngày Hangul (10/9), Giáng sinh (12/25).",
        "holidays2": "Seollal, Chuseok và Phật Đản theo âm lịch, đổi năm — thường Seollal tháng 1–2, Chuseok 9–10, Phật Đản 4–5. Xem lịch năm đó trước khi bay.",
        "holidays3": "Cuối tuần dài, giao thông và chỗ ở đông, một số quán đóng. Đặt sớm như mùa cao điểm.",
        "avoid1": "Giữa hè (7–8) nóng ẩm — lịch ngoài trời dày có thể nặng với lần đầu.",
        "avoid2": "Mùa mưa jangma khoảng cuối 6–7, mưa thường. Ưu tiên kế hoạch trong nhà và lịch linh hoạt.",
        "avoid3": "Giữa đông (12–2) lạnh và gió, nhất là nội địa. Không phải “đừng đến” — chỉ cần chuẩn bị hơn nếu mới đi hoặc nhiều hoạt động ngoài trời.",
        "tabTransit": "Giao thông công cộng",
        "transitTitle": "Giao thông công cộng",
        "transit1": "Ở Seoul, tàu điện và xe buýt thường dễ và ổn định hơn thuê xe/tự lái — ít kẹt xe và đỗ xe.",
        "transit2": "Dùng lộ trình công cộng Naver/Kakao Map cho chuyển tuyến và lối ra. Hành lý nặng hoặc đêm khuya xem thêm tab Taxi.",
        "transit3": "Mua/nạp T-money, Cashbee hoặc Climate Card nằm ở Tiền bạc và Wow Pass. Mẹo chạm thẻ xuống xe trong Mẹo du lịch.",
        "transit4": "Một số vùng (và Jeju) hợp thuê xe. Chỉ dùng công cộng ở Seoul cũng khiến ngày đầu nhẹ hơn.",
        "tabCulture": "Văn hóa ăn uống",
        "cultureTitle": "Văn hóa ăn uống",
        "culture1": "Muỗng cho cơm/canh, đũa cho banchan và thịt là tự nhiên. Tránh cắm đũa đứng trong cơm.",
        "culture2": "Banchan dùng chung; đặt món cùng nhau khi đi nhóm. Xin cay nhẹ nếu cần.",
        "culture3": "Bấm chuông gọi hoặc nói nhẹ “저기요.” Nước/banchan thường tự lấy. Thanh toán ở quầy; không tip.",
        "culture4": "Nhìn quanh một lần hữu ích hơn nghi thức hoàn hảo.",
        "tabKorean": "Chào hỏi cơ bản",
        "koreanTitle": "Chào hỏi & câu đơn giản",
        "korean1": "Trước khi bay, học vài lời chào, cảm ơn và câu ngắn. Bắt đầu với “안녕하세요,” “감사합니다,” “죄송합니다” — không cần câu dài.",
        "korean2": "Người Hàn hiểu khách có thể chưa biết tiếng Hàn. Hỏi lịch sự, thân thiện thường được đáp lại ấm hơn.",
        "korean3": "Câu dùng ngay ở nhà hàng, giao thông, mua sắm xem Tiếng Hàn hữu ích. Xem nhanh trước khi đi rất giúp.",
        "koreanLink": "→ Xem thêm Tiếng Hàn hữu ích",
    },
}

# Continue building VI tips etc in second chunk via exec of rest file
print("partial VI beforeTrip keys", len(VI["beforeTrip"]))
(ROOT / "_partial_vi.json").write_text(json.dumps(VI, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved partial")
