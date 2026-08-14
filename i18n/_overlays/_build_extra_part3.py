#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def w(lang, sec, data):
    path = ROOT / f"{lang}_{sec}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{path.name}: {len(data)}")

# VI fun (hub-visible strings; include bodies for main cards)
w("vi", "fun", {
    "backHub": "← Mua sắm & vui chơi",
    "tipTitle": "Mẹo",
    "readMore": "Đọc thêm →",
    "pcbangTitle": "PC bang (quán net)",
    "pcbangDesc": "Quán PC 24 giờ với máy mạnh và mạng nhanh — chơi game hoặc làm việc.",
    "noraebangTitle": "Karaoke xu",
    "noraebangDesc": "Noraebang tính theo bài bằng xu — dễ đi một mình hoặc nhóm nhỏ.",
    "escapeTitle": "Phòng thoát hiểm",
    "escapeDesc": "Giải đố trong thời gian giới hạn. Nhiều quán ở Hongdae và Gangnam.",
    "jjimTitle": "Jjimjilbang (spa)",
    "jjimDesc": "Văn hóa nhà tắm Hàn — xông hơi, sàn nóng và nghỉ qua đêm.",
    "pcbangBody1": "PC bang cho thuê máy cấu hình cao theo giờ. Du khách dùng để chơi game, gọi video, giấy tờ và sạc thiết bị. Quán 24 giờ phổ biến gần khu vui chơi, trường và ga.",
    "pcbangBody2": "Nhân viên hoặc kiosk xếp chỗ; trả trước bằng tiền mặt, thẻ hoặc QR. Gia hạn ở quầy khi đồng hồ trên màn hình sắp hết. Nhiều quán gọi đồ uống, ramyeon hoặc snack từ bàn.",
    "pcbangPrice": "Khoảng giá\n\nKhoảng ₩1,000–₩2,000/giờ (đêm khuya hoặc ghế cao cấp đắt hơn). Đồ ăn uống tính riêng.",
    "pcbangTip": "Mẹo\n\nÍt khi cần giấy tờ. Giữ yên cho hàng xóm, đăng xuất tài khoản và xóa USB. Một số quán có khu hút thuốc — theo biển.",
    "noraebangBody1": "Karaoke xu trả theo bài (hoặc gói ngắn) — dễ hơn phòng theo giờ cho một mình/nhóm nhỏ. Phổ biến ở Hongdae, Gangnam, khu trường và gần ga.",
    "noraebangBody2": "Bỏ tiền hoặc nạp thẻ/QR, rồi tìm bài — catalog Anh/Nhật thường có. Theo dõi số bài/thời gian còn lại.",
    "noraebangPrice": "Khoảng giá\n\nKhoảng ₩500–₩1,000/bài, hoặc gói thời gian ngắn — tùy quán và giờ.",
    "noraebangTip": "Mẹo\n\nĐêm cuối tuần có thể phải chờ. Giữ âm lượng vừa và nhẹ nhàng với micro/thiết bị.",
    "escapeBody1": "Phòng thoát hiểm đưa nhóm vào phòng chủ đề giải đố trong khoảng 60 phút. Cụm quán ở Hongdae, Gangnam, Konkuk, Daehangno; nhiều nơi có gợi ý tiếng Anh.",
    "escapeBody2": "Đặt chủ đề, giờ và số người online. Nhân viên hướng dẫn luật và nút khẩn. Xem độ khó và thể loại (kinh dị, bí ẩn, nhẹ) trước. Gợi ý thường qua bộ đàm hoặc màn hình.",
    "escapePrice": "Khoảng giá\n\nThường khoảng ₩20,000–₩30,000/người. Một số chủ đề tính thêm cho cặp — xem trang đặt.",
    "escapeTip": "Mẹo\n\nĐến sớm vài phút. Không phá đạo cụ. Chụp ảnh sau khi chơi theo quy định quán.",
    "jjimBody1": "Jjimjilbang là tổ hợp nhà tắm/xông hơi Hàn với khu nghỉ, đồ ăn nhẹ và đôi khi ngủ qua đêm. Cởi quần áo ở khu tắm theo giới; khu chung mặc đồng phục.",
    "jjimBody2": "Mua vé ở quầy, nhận chìa tủ và đồng phục. Tắm sạch trước khi vào bồn/xông. Khu chung có sàn nóng, phòng chủ đề và đồ ăn.",
    "jjimPrice": "Khoảng giá\n\nVào cửa khoảng ₩10,000–₩20,000; qua đêm/gói cao hơn. Đồ ăn tính riêng.",
    "jjimTip": "Mẹo\n\nMang đồ dùng nhẹ nếu muốn; nhiều nơi bán trong. Tôn trọng khu yên tĩnh và quy tắc theo giới.",
    "mangaTitle": "Quán truyện (manga café)",
    "mangaDesc": "Đọc manga/webtoon theo giờ, có chỗ nằm và đồ uống.",
    "boardTitle": "Board game café",
    "boardDesc": "Mượn board game, gọi đồ uống — hợp nhóm nhỏ.",
    "photoTitle": "Photo booth",
    "photoDesc": "Chụp ảnh 4-cut kiểu Hàn — Myeongdong, Hongdae có nhiều máy.",
    "unmannedTitle": "Cửa hàng không người",
    "unmannedDesc": "Vào bằng QR/thẻ, lấy đồ và thanh toán tự phục vụ.",
    "everlandTitle": "Everland",
    "everlandDesc": "Công viên giải trí lớn gần Yongin — tàu lượn, vườn thú và lễ hội theo mùa.",
    "lotteTitle": "Lotte World",
    "lotteDesc": "Công viên trong/ngoài trời ở Seoul — thuận tiện từ tàu điện.",
    "coinTitle": "Noraebang xu",
    "coinDesc": "Karaoke tính xu theo bài — dễ thử nhanh.",
})

w("vi", "transport", {
    "mapTitle": "Bản đồ điểm tham quan Hàn",
    "mapAlt": "Bản đồ tương tác toàn màn hình các địa điểm ở Hàn Quốc",
    "mapCaption": "Chạm ghim để xem giới thiệu địa điểm tại đây",
    "tabSubway": "Bản đồ tàu điện",
    "tabRoutes": "Điểm nổi bật",
    "tabsHelp": "Chạm tab để xem chi tiết.",
    "subwayIntro": "Mỗi tuyến Seoul Metro có màu riêng. Tên ga và biển chuyển tuyến thường có tiếng Anh.",
    "officialMapTitle": "Bản đồ chính thức (Seoul Metro)",
    "officialMapDesc": "Xem sơ đồ chính thức để nắm màu tuyến và điểm chuyển.",
    "officialMapCta": "Mở bản đồ chính thức →",
    "interactiveMapTitle": "Bản đồ tương tác",
    "interactiveMapHelp": "Phóng to và chạm ga hoặc điểm để xem nhanh.",
    "mapSource": "Nguồn bản đồ",
    "lineAll": "Tất cả tuyến",
    "arexChip": "AREX",
    "linePickHint": "Chọn tuyến để lọc",
    "diagramSummary": "Sơ đồ tuyến và mẹo chuyển tuyến",
    "subwayTipTitle": "Mẹo tàu điện",
    "subwayTip1": "Kiểm tra số lối ra trên Naver/Kakao Map trước khi ra ga.",
    "subwayTip2": "Giờ cao điểm sáng/tối rất đông — tránh nếu mang hành lý nặng.",
    "subwayTip3": "Thẻ T-money giúp lên xuống nhanh hơn mua vé từng lần.",
    "lineLabel": "Tuyến",
})

print("vi fun/transport done")
